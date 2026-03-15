# VPN_FortIOS_Palo_Auto

Aplicação simples (GUI em PySide6) para **gerar** um script de configuração de VPN IPSec *site-to-site* entre **FortiGate** e **Palo Alto**, **visualizar** o resultado e **salvar** o arquivo gerado.

> Estado atual do código (sem “inventar feature”):
> - O botão **Gerar Scripts e Salvar Arquivos** gera o texto e abre um diálogo para escolher onde salvar.
> - O botão **Enviar para os Firewalls** existe na interface, mas no `app.py` **ainda não faz o envio**.


---

## Requisitos

- Python 3
- Dependência da interface:
  - `PySide6`
- Dependência para envio por SSH (opcional, apenas para `send.py` em modo real):
  - `netmiko`

Instalação típica:

```bash
pip install PySide6
pip install netmiko
```

---

## Como usar (GUI)

Execute:

```bash
python3 app.py
```

1. Preencha os campos:
   - IP WAN Fortigate
   - IP WAN Palo Alto
   - Pre-Shared Key
   - Rede LAN (Forti)
   - Rede LAN (Palo)
2. Clique em **Gerar Scripts e Salvar Arquivos**.
3. Escolha o local/arquivo para salvar (por padrão sugere `config_vpn_gerada.txt`).
4. O conteúdo gerado também aparece na área de texto.

---

## Como enviar para os firewalls (CLI)


Exemplo (Fortigate + Palo Alto):

Está funcionalidade será implementada posteriormente usando netmiko

`

## Modo simulação (não conecta; apenas imprime o que enviaria):

```bash
python3 send.py --config-file config_vpn_gerada.txt --sim
```


---

## Arquivos importantes

- `app.py`: GUI (geração + salvar + placeholder do botão enviar).
- `config_vpn_gerada.txt`: exemplo de arquivo gerado.
---

## Problemas comuns

- **Timeout/SSH falhando**
  - Verifique reachability (rota/ACL), credenciais, porta (`--forti-port`/`--palo-port`) e se SSH está habilitado no firewall.


