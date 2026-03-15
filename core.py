"""
Este módulo é responsável por:
  - Conectar ao switch via SSH (usando Netmiko)
  - Configurar VLANs e hostname
  - Excluir VLANs do switch
  - Salvar configuração na NVRAM
  - Realizar backup da configuração
  - Validar se a configuração aplicada corresponde ao esperado

Sobre a validação:
  A running-config do IOS armazena VLANs no formato:
      vlan 10  name VLAN_DADOS
  Usando o comando "show vlan brief" é mais confiável para validar pois apresenta
  cada VLAN em uma linha única no formato:
      10   VLAN_DADOS   active   ...
  Isso evita falsos positivos causados por variações de espaçamento/newline.

Em modo de SIMULAÇÃO (sem Netmiko ou sem hardware real), todas as operações
retornam resultados fictícios para testes.
"""

import os
import re
import datetime

# Tenta importar Netmiko - Isso aqui é legal parece o try catch do java evita erros
try:
    from netmiko import ConnectHandler
    NETMIKO_DISPONIVEL = True
except ImportError:
    NETMIKO_DISPONIVEL = False # neste caso aqui achei legal colocar uma variável de controle para o código saber que o 
                               # Netmiko não

# Constantes padrão PRÉ DEFINIDO NO ESCOPO DO PROJETO

VLANS_PADRAO = [
    {"id": 10, "nome": "VLAN_DADOS"},
    {"id": 20, "nome": "VLAN_VOZ"},
    {"id": 50, "nome": "VLAN_SEGURANCA"},
]

# Hostname padrão a ser aplicado no switch
HOSTNAME_PADRAO = "SWITCH_AUTOMATIZADO"



# CLASSE PRINCIPAL do PROJETO


class GerenciadorSwitch:
   
    def __init__(self, host: str, porta: int, usuario: str,
                 senha: str, secret: str = ""):
        # Isso aqui e muito louco "Pegue esse endereço de host que recebi e salve-o "Comparando com java"
        # nesta instância para que outros métodos desta classe possam acessá-lo"
        # O mesmo vale para os outros parâmetros, é uma forma de armazenar as credenciais e informações de conexão
        self.host    = host 
        self.porta   = porta
        self.usuario = usuario
        self.senha   = senha
        self.secret  = secret

        self._conn = None
        self._sim  = not NETMIKO_DISPONIVEL  # True quando está sem o Netmiko

        # Conexão

    def conectar(self) -> str:
        """
        Abre a conexão SSH. Retorna o hostname do switch.
        Em simulação retorna 'SWITCH_SIMULADO'.
        """
        if self._sim:
            return "SWITCH_SIMULADO" #self._sim define se o comando vai para um equipamento real ou se apenas 
                                     # "fingirá" a execução (útil para testar o código sem derrubar a rede)

        params = {
            "device_type": "cisco_ios",
            "host":        self.host,
            "port":        self.porta,
            "username":    self.usuario,
            "password":    self.senha,
            "secret":      self.secret,
            "timeout":     10, # Isso aqui salvou pensando no meu ambiente de produção onde eu tenho filiais espalhadas
                                # a latência pode ser maior, então aumentei o timeout para evitar falhas de conexão por 
                                # timeout curto demais. aqui da para implementar uma outra função que testa a latencia com
                                # base nos Estados do Brasil.
        }
        self._conn = ConnectHandler(**params)
        if self.secret:
            self._conn.enable()

        saida    = self._conn.send_command("show running-config | include hostname")
        hostname = saida.split()[-1] if saida.strip() else self.host
        return hostname
    
           # Desconexão
    def desconectar(self):
        #Encerra a sessão SSH se estiver ativa
        if self._conn:
            self._conn.disconnect()
            self._conn = None

    # Configurar VLANs 

    def configurar_vlans(self, vlans: list) -> str:
        """
        Cria/atualiza as VLANs no switch.

        Parâmetro:
            vlans — [{"id": int, "nome": str}, ...]

        IOS 15.1 aceita os comandos em sequência dentro de 'conf t':
            vlan 10
             name VLAN_DADOS
            vlan 20
             name VLAN_VOZ
        """
        if self._sim:
            linhas = ["[SIMULAÇÃO] Comandos que seriam enviados:", "conf t"]
            for v in vlans:
                linhas += [f"  vlan {v['id']}", f"   name {v['nome']}"]
            linhas.append("end")
            return "\n".join(linhas)

        comandos = []
        for v in vlans:
            comandos.append(f"vlan {v['id']}")
            comandos.append(f" name {v['nome']}")

        # cmd_verify=False previne falsos timeouts em IOS que ecoam
        # os comandos de forma diferente do esperado pelo Netmiko
        return self._conn.send_config_set(comandos, cmd_verify=False)

    # Excluir VLAN como bonus, isso aqui não estava no escopo inicial 
    # mas achei interessante implementar para ter a funcionalidade

    def excluir_vlan(self, vid: int) -> str:
        """
        Remove uma VLAN do switch pelo seu ID.

        O comando IOS para excluir é:
            conf t
            no vlan id
            end

        VLANs reservadas (1 e 1002-1005) não podem ser removidas.
        Retorna a saída do switch ou mensagem de simulação.
        """
        # Impede remoção de VLANs reservadas pelo IOS
        RESERVADAS = {1, 1002, 1003, 1004, 1005}
        if vid in RESERVADAS:
            raise ValueError( # Já retrona um erro exibindo uma mensagem
                f"VLAN {vid} é reservada pelo IOS e não pode ser excluída."
            )

        if self._sim:
            return f"[SIMULAÇÃO] no vlan {vid} — VLAN {vid} removida do switch"

        # cmd_verify=False evita que o Netmiko re-leia o comando ecoado
        # e tente verificar o prompt, o que pode falhar em alguns IOS
        saida = self._conn.send_config_set(
            [f"no vlan {vid}"],
            cmd_verify=False,
        )
        return saida

    # Hostname

    def configurar_hostname(self, hostname: str) -> str:
        
        if self._sim:
            return f"[SIMULAÇÃO] hostname {hostname}"

        # Aplica o hostname no switch
        saida = self._conn.send_config_set([f"hostname {hostname}"])

        # Re-aprende o novo prompt (ex: SWITCH_AUTOMATIZADO#)
        # Isso é necessário sempre que o hostname muda durante a sessão
        self._conn.set_base_prompt()

        return saida

    # Salvar memoria do Switch

    def salvar_nvram(self) -> str:
        """
        Executa 'write memory' para persistir a configuração na NVRAM.

        Usa send_command_timing() em vez de send_command() para evitar
        que o Netmiko tente detectar o prompt — o 'write memory' no IOS
        pode exibir mensagens intermediárias como:
            Building configuration...
            [OK]
        que não são o prompt e causam timeout com expect_string customizado.
        """
        if self._sim:
            return "[SIMULAÇÃO] write memory — configuração salva na NVRAM"

        # send_command_timing aguarda um tempo fixo após o comando
        # em vez de detectar o prompt — mais confiável para write memory
        saida = self._conn.send_command_timing(
            "write memory",
            strip_prompt=False,
            strip_command=False,
            read_timeout=30,   # NVRAM write pode demorar em switches maiores
        )
        return saida

    # ── Backup ───────────────────────────────────────────────────────────────

    def backup_config(self, pasta_destino: str = ".") -> tuple[str, str]:
        """
        Salva a running-config em arquivo local.
        Nome: <hostname>_<YYYYMMDD_HHMMSS>.txt
        Retorna (caminho, conteudo).
        """
        if self._sim:
            hostname   = "SWITCH_SIMULADO"
            config_txt = (
                "! Configuração simulada\n"
                "hostname SWITCH_SIMULADO\n!\n"
                "vlan 10\n name VLAN_DADOS\n"
                "vlan 20\n name VLAN_VOZ\n"
                "vlan 50\n name VLAN_SEGURANCA\n!\nend\n"
            )
        else:
            config_txt = self._conn.send_command("show running-config")
            match      = re.search(r"^hostname (.+)$", config_txt, re.MULTILINE)
            hostname   = match.group(1).strip() if match else self.host

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        caminho   = os.path.join(pasta_destino, f"{hostname}_{timestamp}.txt")
        os.makedirs(pasta_destino, exist_ok=True)

        with open(caminho, "w", encoding="utf-8") as f: # aqui eu codifiquei para utf8 para garantir caracteres
            f.write(config_txt)

        return caminho, config_txt

    # ── Validação ────────────────────────────────────────────────────────────

    def validar_config(self, vlans_esperadas: list,
                       hostname_esperado: str) -> list[dict]:
        """
        Compara a configuração atual do switch com a desejada.

        ESTRATÉGIA DE VALIDAÇÃO:
          - Hostname: lido de "show running-config | include hostname"
          - VLANs: lidas de "show vlan brief" (mais confiável que a running-config
            pois cada VLAN aparece em uma linha única sem variações de espaçamento)

        Formato de "show vlan brief":
            VLAN  Name                Status    Ports
            ----  ------------------- --------- -----
            1     default             active
            10    VLAN_DADOS          active
            20    VLAN_VOZ            active
            50    VLAN_SEGURANCA      active

        Retorna lista de dicts {"item", "esperado", "encontrado"}.
        Lista vazia = tudo conforme esperado.
        """
        divergencias = []

        if self._sim:
            # Simulação: sem divergências (tudo considerado correto)
            return divergencias

        # ── 1. Valida hostname ───────────────────────────────────────────────
        saida_hn   = self._conn.send_command(
            "show running-config | include hostname"
        )
        # A saída é "hostname NOME" — pega a última palavra
        hostname_atual = saida_hn.strip().split()[-1] if saida_hn.strip() else ""

        if hostname_atual.lower() != hostname_esperado.lower():
            divergencias.append({
                "item":       "Hostname",
                "esperado":   hostname_esperado,
                "encontrado": hostname_atual or "NÃO ENCONTRADO",
            })

        # ── 2. Valida VLANs via "show vlan brief" ───────────────────────────
        saida_vlan = self._conn.send_command("show vlan brief")

        # Monta dicionário {vlan_id: nome_atual} a partir da saída
        # Linha típica: "10    VLAN_DADOS          active    Gi0/1"
        # O regex captura o ID (grupo 1) e o nome (grupo 2)
        vlans_no_switch: dict[int, str] = {}
        for linha in saida_vlan.splitlines():
            m = re.match(r"^\s*(\d+)\s+(\S+)\s+\w", linha)
            if m:
                vlans_no_switch[int(m.group(1))] = m.group(2)

        # Compara cada VLAN esperada com o que está no switch
        for v in vlans_esperadas:
            vid        = int(v["id"])
            nome_esp   = v["nome"].upper()   # IOS armazena em maiúsculo
            nome_atual = vlans_no_switch.get(vid)

            if nome_atual is None:
                # VLAN não encontrada no switch
                divergencias.append({
                    "item":       f"VLAN {vid}",
                    "esperado":   nome_esp,
                    "encontrado": "NÃO ENCONTRADO",
                })
            elif nome_atual.upper() != nome_esp:
                # VLAN existe mas com nome diferente
                divergencias.append({
                    "item":       f"VLAN {vid}",
                    "esperado":   nome_esp,
                    "encontrado": nome_atual,
                })

        return divergencias
