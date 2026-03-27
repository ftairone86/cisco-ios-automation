# VPN_FortIOS_Palo_Auto

Aplicação GUI (PySide6) para **gerar**, **visualizar**, **salvar** e **enviar via SSH** configurações de VPN IPSec *site-to-site* entre **FortiGate** e **Palo Alto**.

---

## Requisitos

- Python 3.10+
- Interface gráfica:
  - `PySide6`
- Envio SSH (modo real):
  - `netmiko`

```bash
pip install -r requirements.txt
```

---

## Como executar

```bash
python main.py
```

> Antes de rodar pela primeira vez, apague a pasta `__pycache__` caso encontre `NameError` em imports.

---

## Interface — Abas

### Aba 1 · Geração de Config

Preencha os parâmetros e clique em **Gerar Scripts e Salvar Arquivos**:

| Campo | Descrição |
| --- | --- |
| IP WAN Fortigate | Endereço público do Fortigate (peer remoto no Palo) |
| IP WAN Palo Alto | Endereço público do Palo Alto (peer remoto no Forti) |
| Pre-Shared Key | Chave secreta da VPN (campo oculto) |
| Rede LAN (Forti) | Subnet local do Fortigate (src-subnet na fase 2) |
| Rede LAN (Palo) | Subnet local do Palo Alto (dst-subnet na fase 2) |
| Nome do Tunnel | Identificador do túnel (padrão: `VPN-TO-PALO`) |
| Criptografia | `aes128` / `aes192` / `aes256` |
| Hash / Integridade | `sha1` / `sha256` / `sha384` / `sha512` |
| DH Group | `2` / `5` / `14` / `15` / `16` |
| Lifetime SA | Segundos (300 – 86 400, padrão: 3 600) |

O script gerado (blocos Fortigate + Palo Alto) é exibido na área de texto e salvo em arquivo `.txt` escolhido pelo usuário.

---

### Aba 2 · Conexão & Envio

**Credenciais SSH** — preencha host de gerenciamento, usuário, senha e porta (padrão 22) para cada firewall.

**Testar conexão** — abre e fecha uma sessão SSH e exibe o status (conectado / desconectado).

**Opções de envio:**

- `Commit no Palo Alto` — executa `commit` após enviar os comandos (marcado por padrão).
- `Simulação (não conecta)` — imprime os comandos que seriam enviados sem abrir SSH.

**Enviar para os Firewalls** — separa o script gerado em dois blocos e envia cada um para o respectivo dispositivo em background. Falhas em um firewall não interrompem o envio para o outro.

**Teste do túnel IPSec:**

| Campo | Descrição |
| --- | --- |
| Ping Forti (dest) | IP de destino para ping disparado pelo Fortigate |
| Ping Forti (src) | IP de origem (amarra o ping ao túnel, opcional) |
| Ping Palo (dest) | IP de destino para ping disparado pelo Palo Alto |
| Ping Palo (src) | IP de origem (opcional) |

Clique em **Testar túnel IPSec** para:

1. Verificar o estado das SAs (control-plane) — `get vpn ipsec tunnel summary`, `diagnose vpn ike gateway list`, `show vpn ike-sa`, `show vpn ipsec-sa`.
2. Disparar ping opcional pelo túnel (data-plane).
3. Atualizar os indicadores **Túnel: UP / DOWN / desconhecido** em cada caixa de firewall.

---

### Aba 3 · Logs

Exibe todos os eventos de conexão, envio e teste de túnel em ordem cronológica. Botão **Limpar Logs** apaga o painel.

> Sempre que uma operação começa, a aplicação redireciona automaticamente para esta aba.

---

## Modo CLI (send.py)

Simulação (não conecta):

```bash
python send.py --config-file config_vpn_gerada.txt --sim
```

Envio real (Fortigate + Palo Alto):

```bash
python send.py \
  --config-file config_vpn_gerada.txt \
  --forti-host 10.0.0.1 --forti-user admin --forti-pass 'SENHA' \
  --palo-host  10.0.0.2 --palo-user admin --palo-pass 'SENHA'
```

Enviar sem commit no Palo Alto:

```bash
python send.py --config-file config_vpn_gerada.txt \
  --palo-host 10.0.0.2 --palo-user admin --palo-pass 'SENHA' \
  --no-commit
```

---

## Estrutura dos arquivos

```text
.
├── main.py                   # Ponto de entrada — MainWindow (QWidget)
├── qt_core.py                # Imports centralizados do PySide6
├── send.py                   # Lógica SSH (Netmiko) + modo CLI
├── conexao_thread.py         # Worker: teste de conexão SSH
├── envio_thread.py           # Worker: envio de configuração
├── teste_conexao_thread.py   # Worker: teste de túnel IPSec
└── gui/
    └── ui_window.py          # VPNGenerator — widget das 3 abas
```

---

## Problemas comuns

| Sintoma | Verificação |
| --- | --- |
| `NameError: QComboBox is not defined` | Apague a pasta `__pycache__` e execute novamente |
| Timeout / SSH falhando | Verifique rota, ACL, credenciais, porta e se SSH está habilitado |
| Commit no Palo Alto demora | Desmarque **Commit no Palo Alto** e faça commit manual depois |
| `netmiko` não instalado | Execute `pip install netmiko` ou use o modo **Simulação** |
