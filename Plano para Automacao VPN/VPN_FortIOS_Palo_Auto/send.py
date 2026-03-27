"""send.py

Envio de configuração (VPN) para Fortigate e Palo Alto via SSH (Netmiko).

Este módulo foi adaptado para o objetivo do projeto (VPN FortiOS + PAN-OS).
Ele funciona de duas formas:

- Modo real: usa Netmiko para conectar por SSH e enviar os comandos.
- Modo simulação: se Netmiko não estiver instalado (ou se --sim), apenas
  retorna os comandos que seriam enviados.

Observações importantes:
- Fortigate: normalmente aceita o script CLI diretamente (config/edit/set/next/end).
- Palo Alto (PAN-OS): normalmente requer entrar em modo de configuração
  (configure), aplicar "set ..." e depois "commit".

Integração com `app.py`:
- A GUI gera um texto único contendo dois blocos (Fortigate + Palo Alto).
- `extrair_blocos_forti_palo()` separa esse texto em dois scripts.
- `FortigateSender` e `PaloAltoSender` fazem a conexão e envio.
"""

from __future__ import annotations

from dataclasses import dataclass
import argparse
import re
from typing import Iterable

try:
    from netmiko import ConnectHandler

    NETMIKO_DISPONIVEL = True
except ImportError:
    NETMIKO_DISPONIVEL = False


@dataclass(frozen=True)
class FirewallSSHConfig:
    """Parâmetros mínimos de conexão SSH para um firewall."""

    host: str
    username: str
    password: str
    port: int = 22
    secret: str = ""


def _normalizar_comandos(texto: str) -> list[str]:
    """Converte um texto multi-linha em uma lista de comandos.

    Regras:
    - Remove linhas em branco.
    - Remove comentários (linhas que começam com '#').
    - Faz strip() em cada linha.

    Importante:
    - O `app.py` gera cabeçalhos comentados (ex.: "#      FORTIGATE CLI").
      Eles são ignorados aqui.
    """

    comandos: list[str] = []
    for linha in texto.splitlines():
        s = linha.strip()
        if not s:
            continue
        if s.startswith("#"):
            continue
        comandos.append(s)
    return comandos


def extrair_blocos_forti_palo(conteudo: str) -> tuple[str, str]:
    """Extrai blocos Fortigate e Palo Alto do texto combinado.

    Retorna:
        (forti_text, palo_text)

    Estratégia:
    1) Procura pelos marcadores padrão gerados pelo `app.py`:
       - "#      FORTIGATE CLI"
       - "#      PALO ALTO"
    2) Se não achar, tenta um regex mais permissivo.
    3) Se ainda assim não conseguir separar, retorna tudo em um dos lados.

    Observação:
    - Essa função é usada tanto pelo CLI (`send.py`) quanto pela GUI (`app.py`).
    """

    idx_f = conteudo.find("#      FORTIGATE CLI")
    idx_p = conteudo.find("#      PALO ALTO")

    if idx_f != -1 and idx_p != -1 and idx_f < idx_p:
        forti = conteudo[idx_f:idx_p]
        palo = conteudo[idx_p:]
        return forti, palo

    m_f = re.search(r"(?s)#\s*FORTIGATE\s*CLI\s*(.*?)#\s*PALO\s*ALTO", conteudo)
    m_p = re.search(r"(?s)#\s*PALO\s*ALTO\s*(.*)$", conteudo)
    if m_f and m_p:
        return "#      FORTIGATE CLI\n" + m_f.group(1), "#      PALO ALTO\n" + m_p.group(1)

    if idx_f != -1:
        return conteudo[idx_f:], ""
    if idx_p != -1:
        return "", conteudo[idx_p:]

    return conteudo, ""


class _BaseNetmikoSender:
    """Base comum para senders Netmiko.

    Responsabilidades:
    - Abrir/fechar conexão SSH (ou simular se `simulacao=True`).
    - Enviar uma sequência de linhas via `send_command_timing`.

    Classes filhas definem:
    - `device_type` do Netmiko
    - Como transformar o script (ex.: PAN-OS precisa entrar em `configure`).
    """

    device_type: str

    def __init__(self, cfg: FirewallSSHConfig, *, simulacao: bool = False, timeout: int = 30):
        self.cfg = cfg
        # Se Netmiko não estiver disponível, forçamos simulação.
        self.simulacao = simulacao or (not NETMIKO_DISPONIVEL)
        self.timeout = timeout
        self._conn = None

    def conectar(self) -> str:
        """Abre a conexão.

        Retorna um identificador (prompt/base_prompt) para logs.
        """

        if self.simulacao:
            return f"SIMULACAO({self.device_type})"

        params = {
            "device_type": self.device_type,
            "host": self.cfg.host,
            "port": self.cfg.port,
            "username": self.cfg.username,
            "password": self.cfg.password,
            "secret": self.cfg.secret,
            "timeout": self.timeout,
        }
        self._conn = ConnectHandler(**params)
        if self.cfg.secret:
            self._conn.enable()

        # Base prompt ajuda em alguns devices.
        try:
            self._conn.set_base_prompt()
        except Exception:
            pass

        return str(getattr(self._conn, "base_prompt", self.cfg.host))

    def desconectar(self) -> None:
        """Fecha a conexão (se estiver aberta)."""
        if self._conn:
            self._conn.disconnect()
            self._conn = None

    def _enviar_linhas_timing(self, comandos: Iterable[str], *, read_timeout: int = 60) -> str:
        """Envia comandos linha-a-linha usando `send_command_timing`.

        Motivo do `timing`:
        - Firewalls frequentemente têm prompts/tempos variáveis. O timing é
          mais tolerante para automação simples.

        `read_timeout`:
        - Aumentamos no commit do Palo Alto, pois pode demorar.
        """

        if self.simulacao:
            return "\n".join([f"[SIMULACAO] {c}" for c in comandos])

        if not self._conn:
            raise RuntimeError("Conexão não está aberta. Chame conectar() primeiro.")

        saidas: list[str] = []
        for cmd in comandos:
            saidas.append(
                self._conn.send_command_timing(
                    cmd,
                    strip_prompt=False,
                    strip_command=False,
                    read_timeout=read_timeout,
                )
            )
        return "\n".join(saidas)


class FortigateSender(_BaseNetmikoSender):
    """Sender Fortigate.

    O FortiGate normalmente aceita os comandos CLI diretamente.
    """

    device_type = "fortinet"

    def enviar_script(self, forti_script: str) -> str:
        """Normaliza e envia o script Fortigate."""
        comandos = _normalizar_comandos(forti_script)
        return self._enviar_linhas_timing(comandos, read_timeout=60)


class PaloAltoSender(_BaseNetmikoSender):
    """Sender Palo Alto (PAN-OS).

    Para PAN-OS, o fluxo típico é:
    - `configure`
    - aplicar `set ...`
    - `commit` (opcional)
    - `exit`
    """

    device_type = "paloalto"

    def enviar_script(self, palo_script: str, *, commit: bool = True) -> str:
        """Normaliza e envia o script Palo Alto, com commit opcional."""
        comandos = _normalizar_comandos(palo_script)

        fluxo: list[str] = ["configure", *comandos]
        if commit:
            fluxo.append("commit")
        fluxo.append("exit")

        return self._enviar_linhas_timing(fluxo, read_timeout=300 if commit else 60)



def _inferir_tunel_up_fortigate(saida: str) -> bool | None:
    """Heurística simples para inferir se há túneis IPsec "UP".

    O FortiOS varia bastante por versão/modelo. Por isso, aqui a intenção é:
    - Retornar True se a saída indicar explicitamente túneis "up" (>0)
    - Retornar False se indicar "up: 0" ou algo equivalente
    - Retornar None se não for possível inferir
    """

    import re

    m = re.search(r"\bup\s*:\s*(\d+)\b", saida, re.IGNORECASE)
    if m:
        try:
            return int(m.group(1)) > 0
        except ValueError:
            return None

    if re.search(r"\bstatus\s*=\s*up\b", saida, re.IGNORECASE):
        return True
    if re.search(r"\bstatus\s*=\s*down\b", saida, re.IGNORECASE):
        return False

    return None


def _inferir_tunel_up_paloalto(saida_ike: str, saida_ipsec: str) -> bool | None:
    """Heurística simples para inferir se há SAs IKE/IPsec ativas no PAN-OS."""

    import re

    combinado = f"{saida_ike}\n{saida_ipsec}".strip()
    if not combinado:
        return None

    if re.search(r"No\s+(IKE|IPsec)\s+SAs\s+found", combinado, re.IGNORECASE):
        return False

    # Saídas comuns trazem "UP" ou "ACTIVE".
    if re.search(r"\bUP\b", combinado):
        return True
    if re.search(r"\bACTIVE\b", combinado, re.IGNORECASE):
        return True

    return None


def testar_conectividade_tunel_ipsec(
    *,
    forti_cfg: FirewallSSHConfig | None = None,
    palo_cfg: FirewallSSHConfig | None = None,
    simulacao: bool = False,
    forti_ping_dest: str | None = None,
    forti_ping_source: str | None = None,
    palo_ping_dest: str | None = None,
    palo_ping_source: str | None = None,
) -> dict[str, object]:
    """Testa conectividade do túnel IPSec via SSH.

    O que esse teste faz (best-effort):

    1) **Controle-plane (estado do túnel / SAs)**
       - Fortigate: roda comandos de resumo/diagnóstico e tenta inferir se há túnel "UP".
       - Palo Alto: roda `show vpn ike-sa` e `show vpn ipsec-sa`.

    2) **Data-plane (tráfego pelo túnel) [opcional]**
       - Se você informar `*_ping_dest`, o código executa um ping a partir do firewall.
       - Para o ping realmente "atravessar" o túnel, o destino precisa ser um IP
         acessível pela rede remota do túnel.
       - Em muitos cenários, também é necessário definir `*_ping_source`.

    Parâmetros:
        forti_cfg / palo_cfg: credenciais/host/porta do SSH.
        simulacao: se True, não conecta; apenas simula os comandos.
        forti_ping_dest: IP/host para ping a partir do Fortigate.
        forti_ping_source: IP de origem (Fortigate) para amarrar o ping ao túnel.
        palo_ping_dest: IP/host para ping a partir do Palo Alto.
        palo_ping_source: IP de origem (Palo Alto) para amarrar o ping ao túnel.

    Retorno:
        dict com chaves "fortigate" e/ou "paloalto", contendo:
        - "prompt": base_prompt (ou SIMULACAO(...))
        - "saidas": dict com saídas dos comandos executados
        - "tunnel_up": bool | None (inferência simples)

    Observação:
        Esse teste não substitui validações completas (roteamento, políticas,
        selectors, NAT, etc). Ele ajuda a identificar rapidamente:
        - credenciais/SSH
        - existência de SAs
        - ping básico para gerar tráfego no túnel
    """

    resultados: dict[str, object] = {}

    if forti_cfg:
        forti_sender = FortigateSender(forti_cfg, simulacao=simulacao)
        saidas: dict[str, str] = {}
        prompt = ""
        try:
            prompt = forti_sender.conectar()

            # Comandos de estado (variam por versão; usamos alguns comuns).
            saidas["ipsec_summary"] = forti_sender._enviar_linhas_timing(
                ["get vpn ipsec tunnel summary"],
                read_timeout=60,
            )
            saidas["ike_gateways"] = forti_sender._enviar_linhas_timing(
                ["diagnose vpn ike gateway list"],
                read_timeout=60,
            )
            saidas["tunnel_list"] = forti_sender._enviar_linhas_timing(
                ["diagnose vpn tunnel list"],
                read_timeout=60,
            )

            # Ping opcional para forçar tráfego no túnel.
            if forti_ping_dest:
                cmds: list[str] = []
                if forti_ping_source:
                    cmds.append(f"execute ping-options source {forti_ping_source}")
                cmds.append("execute ping-options repeat 3")
                cmds.append(f"execute ping {forti_ping_dest}")
                saidas["ping"] = forti_sender._enviar_linhas_timing(cmds, read_timeout=60)

            tunnel_up = _inferir_tunel_up_fortigate(
                "\n".join([saidas.get("ipsec_summary", ""), saidas.get("tunnel_list", "")])
            )

            resultados["fortigate"] = {
                "prompt": prompt,
                "saidas": saidas,
                "tunnel_up": tunnel_up,
            }
        finally:
            forti_sender.desconectar()

    if palo_cfg:
        palo_sender = PaloAltoSender(palo_cfg, simulacao=simulacao)
        saidas = {}
        prompt = ""
        try:
            prompt = palo_sender.conectar()

            # Em PAN-OS, esses comandos são operacionais (não entram em configure).
            saidas["ike_sa"] = palo_sender._enviar_linhas_timing(["show vpn ike-sa"], read_timeout=60)
            saidas["ipsec_sa"] = palo_sender._enviar_linhas_timing(["show vpn ipsec-sa"], read_timeout=60)

            if palo_ping_dest:
                if palo_ping_source:
                    cmd = f"ping source {palo_ping_source} host {palo_ping_dest}"
                else:
                    cmd = f"ping host {palo_ping_dest}"
                saidas["ping"] = palo_sender._enviar_linhas_timing([cmd], read_timeout=60)

            tunnel_up = _inferir_tunel_up_paloalto(saidas.get("ike_sa", ""), saidas.get("ipsec_sa", ""))

            resultados["paloalto"] = {
                "prompt": prompt,
                "saidas": saidas,
                "tunnel_up": tunnel_up,
            }
        finally:
            palo_sender.desconectar()

    if not resultados:
        resultados["info"] = "Nada para testar (credenciais não informadas)."

    return resultados
def enviar_vpn_para_firewalls(
    conteudo_combinado: str,
    forti_cfg: FirewallSSHConfig | None,
    palo_cfg: FirewallSSHConfig | None,
    *,
    commit_palo: bool = True,
    simulacao: bool = False,
) -> dict[str, str]:
    """Função de alto nível para envio (CLI).

    Recebe o texto combinado, separa os blocos e envia para um ou ambos.

    Retorna:
        dict com chaves como:
        - "fortigate": saída do envio
        - "paloalto": saída do envio
        - "info": mensagem informativa quando não há nada para enviar

    Observação:
    - A GUI (`app.py`) usa os senders diretamente para tratar falhas
      individualmente por firewall.
    """

    if not NETMIKO_DISPONIVEL and not simulacao:
        raise RuntimeError(
            "Netmiko não está instalado. Instale netmiko ou use simulacao=True/--sim."
        )

    forti_script, palo_script = extrair_blocos_forti_palo(conteudo_combinado)
    resultados: dict[str, str] = {}

    if forti_cfg and forti_script.strip():
        forti = FortigateSender(forti_cfg, simulacao=simulacao)
        try:
            forti.conectar()
            resultados["fortigate"] = forti.enviar_script(forti_script)
        finally:
            forti.desconectar()

    if palo_cfg and palo_script.strip():
        palo = PaloAltoSender(palo_cfg, simulacao=simulacao)
        try:
            palo.conectar()
            resultados["paloalto"] = palo.enviar_script(palo_script, commit=commit_palo)
        finally:
            palo.desconectar()

    if not resultados:
        resultados["info"] = "Nada para enviar (blocos vazios ou credenciais não informadas)."

    return resultados


def _ler_config(path: str) -> str:
    """Lê o arquivo de configuração gerado pelo app."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def main(argv: list[str] | None = None) -> int:
    """Entrada CLI.

    Permite enviar a partir de um arquivo gerado (`--config-file`).

    Exemplo (simulação):
        python3 send.py --config-file config_vpn_gerada.txt --sim
    """

    parser = argparse.ArgumentParser(
        description="Envia configuração VPN para Fortigate e Palo Alto via SSH (Netmiko)."
    )
    parser.add_argument("--config-file", required=True, help="Arquivo gerado (ex: config_vpn_gerada.txt)")
    parser.add_argument("--sim", action="store_true", help="Não conecta; apenas mostra comandos que seriam enviados")

    parser.add_argument("--forti-host")
    parser.add_argument("--forti-user")
    parser.add_argument("--forti-pass")
    parser.add_argument("--forti-port", type=int, default=22)

    parser.add_argument("--palo-host")
    parser.add_argument("--palo-user")
    parser.add_argument("--palo-pass")
    parser.add_argument("--palo-port", type=int, default=22)
    parser.add_argument("--no-commit", action="store_true", help="Não executar commit no Palo Alto")

    args = parser.parse_args(argv)

    conteudo = _ler_config(args.config_file)

    forti_cfg = None
    if args.forti_host and args.forti_user and args.forti_pass:
        forti_cfg = FirewallSSHConfig(
            host=args.forti_host,
            username=args.forti_user,
            password=args.forti_pass,
            port=args.forti_port,
        )

    palo_cfg = None
    if args.palo_host and args.palo_user and args.palo_pass:
        palo_cfg = FirewallSSHConfig(
            host=args.palo_host,
            username=args.palo_user,
            password=args.palo_pass,
            port=args.palo_port,
        )

    resultados = enviar_vpn_para_firewalls(
        conteudo,
        forti_cfg,
        palo_cfg,
        commit_palo=not args.no_commit,
        simulacao=args.sim,
    )

    for k, v in resultados.items():
        print(f"===== {k.upper()} =====")
        print(v.rstrip())
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
