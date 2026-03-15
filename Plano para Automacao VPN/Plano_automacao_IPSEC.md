# Plano de Automação — VPN IPSec entre FortiGate e Palo Alto

> **Documento:** Plano técnico de automação  
> **Escopo:** Configuração automatizada de VPN IPSec site-to-site  
> **Dispositivos:** FortiGate (Fortinet) ↔ Palo Alto Networks (PAN-OS)  
> **Versão:** 1.0

---

## Sumário

1. [Visão Geral](#1-visão-geral)
2. [Definição de Parâmetros](#2-definição-de-parâmetros)
3. [Ferramentas e APIs](#3-ferramentas-e-apis)
4. [Passos de Automação](#4-passos-de-automação)
5. [Considerações Específicas](#5-considerações-específicas)
6. [Validação e Alertas](#6-validação-e-alertas)
7. [Referências](#7-referências)

---

## 1. Visão Geral

Uma VPN IPSec site-to-site entre um Firewall que roda uma IOS x e outro que roda IOS y exige
configuração paralela e compatível em ambos os dispositivos — cada um com sua
própria API, modelo de dados e terminologia. O objetivo aqui é descrever
como um script de automação pode orquestrar toda essa configuração de forma
confiável, repetível e auditável, eliminando erros manuais e reduzindo o tempo
de implantação.

```
  SITE A                          SITE B
┌─────────────────┐              ┌─────────────────┐
│   FortiGate     │  IPSec IKEv2 │   Palo Alto     │
│  200.86.113.1   │◄────────────►│  187.51.100.68  │
│  192.168.20.0/24│  Túnel:      │  192.168.21.0/24│
│                 │ 169.255.65.0 │                 │
│  .1 (túnel)     │    /30       │  .2 (túnel)     │
└─────────────────┘              └─────────────────┘
```

---

## 2. Definição de Parâmetros

### 2.1 Endereços de Interface WAN1

| Parâmetro | Valor |
|-----------|-------|
| IP WAN FortiGate | '200.86.113.1' |
| IP WAN Palo Alto | '187.51.100.68' |

### 2.2 Redes Locais

| Dispositivo | Rede Local | Descrição |
|-------------|-----------|-----------|
| FortiGate | '192.168.20.0/24' | LAN do Site A |
| Palo Alto | '192.168.21.0/24'| LAN do Site B |

### 2.3 Rede de Túnel (Link-Local)

A rede '169.255.65.0/30' é usada para endereçar as interfaces de túnel,
permitindo roteamento e monitoramento de continuidade (keep-alive/BFD).

| Extremidade | IP do Túnel | Dispositivo |
|-------------|-------------|-------------|
| '.1' | '169.255.65.1/30' | FortiGate |
| '.2' | '169.255.65.2/30' | Palo Alto |

> **Por que /30?** Fornece exatamente 2 IPs utilizáveis — um por extremidade —
> sem desperdício de espaço de endereçamento, podemos considerar também a questão de segurança.

### 2.4 Phase 1 — IKE (Internet Key Exchange)

| Parâmetro | Valor |
|-----------|-------|
| Versão IKE | IKEv2 |
| Método de autenticação | Pre-Shared Key (PSK) |
| Algoritmo de criptografia | AES-256-GCM |
| Algoritmo de integridade | SHA-256 |
| Grupo Diffie-Hellman | Grupo 14 (2048-bit MODP) |
| Tempo de vida (lifetime) | 86400 segundos (24 horas) |
| Dead Peer Detection (DPD) | Habilitado — intervalo 10s, retries 3 |

### 2.5 Phase 2 — IPSec (ESP)

| Parâmetro | Valor |
|-----------|-------|
| Protocolo | ESP (Encapsulating Security Payload) |
| Algoritmo de criptografia | AES-256-GCM |
| Algoritmo de integridade | SHA-256 |
| Perfect Forward Secrecy (PFS) | Grupo 14 |
| Tempo de vida (lifetime) | 3600 segundos (1 hora) |
| Seletores de tráfego | '192.168.20.0/24' ↔ '192.168.21.0/24' |

### 2.6 Compatibilidade entre Fabricantes

> FortiGate e Palo Alto usam terminologias diferentes para os mesmos conceitos.
> A tabela abaixo mapeia os termos para garantir configurações espelhadas.
> Mismatch de DH Group: Se o Forti usar Group 14 e o Palo usar Group 2, o túnel nunca ficará "UP".
> Lifetime: O tempo de vida da Fase 1 deve ser sempre maior que o da Fase 2.
> Firewall Policies: Além desses comandos, é preciso criar regras de segurança em ambos permitindo o tráfego da zona Trust para a zona VPN (e vice-versa).

| FortiGate           | Palo Alto |
|-----------          |-----------|
| 'phase1-interface'  | 'ike-crypto-profile' + ike-gateway' |
| 'phase2-interface'  | 'ipsec-crypto-profile' + 'ipsec-tunnel |
|'interface tunnel'   | 'tunnel interface` |
|'quick-mode-selector'| 'proxy-id` |
|'static route'/'BGP' | 'static route' / 'BGP' |
|'firewall policy'    | 'security policy' |

---

## 3. Ferramentas e APIs

### 3.1 FortiGate — Fortinet

#### API REST (recomendada)
A FortiOS expõe uma API REST completa acessível via HTTPS https://pypi.org/project/fortigate-api/1.3.1/.

```
Base URL:  https://<ip-fortigate>/api/v2/
Auth:      Header  →  Authorization: Bearer <api_token>
           Ou      →  ?access_token=<api_token>
```

Endpoints relevantes:

| Operação | Método | Endpoint |
|----------|--------|----------|
| Criar Phase 1 | POST | `/api/v2/cmdb/vpn.ipsec/phase1-interface` |
| Criar Phase 2 | POST | `/api/v2/cmdb/vpn.ipsec/phase2-interface` |
| Criar objeto de endereço | POST | `/api/v2/cmdb/firewall/address` |
| Criar política de firewall | POST | `/api/v2/cmdb/firewall/policy` |
| Criar rota estática | POST | `/api/v2/cmdb/router/static` |
| Verificar status do túnel | GET | `/api/v2/monitor/vpn/ipsec` |

Biblioteca Python recomendada:
```python
# Opção 1: requests (direto)
import requests

# Opção 2: fortiosapi (wrapper oficial)
pip install fortiosapi
```

#### SSH (alternativa)
Para versões sem API REST ou configurações legadas:
```python
pip install netmiko   # suporta device_type="fortinet"
```

---

### 3.2 Palo Alto — PAN-OS

#### API XML (nativa do PAN-OS)
O PAN-OS expõe uma **API XML** acessível via HTTPS.

```
Base URL:  https://<ip-paloalto>/api/
Auth:      ?key=<api_key>   (obtida via /api/?type=keygen)
```

Endpoints relevantes:

| Operação | Tipo | XPath |
|----------|------|-------|
| Obter API key | `keygen` | — |
| Configurar IKE Crypto Profile | `config` | `/config/devices/entry/network/ike-crypto-profiles` |
| Configurar IKE Gateway | `config` | `/config/devices/entry/network/ike-gateways` |
| Configurar IPSec Crypto Profile | `config` | `/config/devices/entry/network/ipsec-crypto-profiles` |
| Configurar IPSec Tunnel | `config` | `/config/devices/entry/network/tunnel/ipsec` |
| Configurar Security Policy | `config` | `/config/devices/entry/vsys/entry/rulebase/security` |
| Commit | `commit` | — |
| Verificar status do túnel | `op` | `<show><vpn><ipsec-sa></ipsec-sa></vpn></show>` |

Biblioteca Python recomendada:
```python
# Opção 1: pan-python (oficial da Palo Alto Networks) (https://github.com/PaloAltoNetworks/pan-os-python)
pip install pan-python

# Opção 2: pandevice / pan-os-python (mais alto nível) (https://pan.dev/panos/docs/panospython/)
pip install pan-os-python
```

#### Panorama (gerenciamento centralizado)
Se os dispositivos forem gerenciados pelo **Panorama**, toda a configuração
pode ser aplicada via API do Panorama e distribuída para os dispositivos.
Isso é especialmente útil em ambientes com múltiplos firewalls.

---

### 3.3 Ferramentas Complementares

| Ferramenta | Uso |
|------------|-----|
| **Ansible** | Módulos `fortios_*` e `paloaltonetworks.panos.*` para orquestração declarativa |
| **Terraform** | Providers `fortios` e `panos` para infraestrutura como código |
| **Python `requests`** | Chamadas REST/XML diretas, máximo controle |
| **Netmiko** | Fallback via SSH para comandos CLI em ambos os dispositivos |

Se pensarmos um pouco veremos que temos diversas soluções que podem agregar para diversos tipos de ambientes
digamos que eu tenho tudo em apliance, podemos usar o IAC (infra como código) onde entra a orquestração declarada
com Ansible e Terraform para subir o ambiente em multicloud eonprimeses. 

---

## 4. Passos de Automação

O script de automação seguiu a sequência abaixo. As operações em
FortiGate e Palo Alto podem ser paralelizadas com 'concurrent.futures'
para reduzir o tempo total de configuração.

```
INÍCIO
  │
  ├─► [1] Validar parâmetros de entrada
  │
  ├─► [2] Autenticar nos dois dispositivos
  │
  ├─► [3] Configurar FortiGate (paralelo com passo 4)
  │     ├─ [3.1] Criar objetos de endereço
  │     ├─ [3.2] Criar Phase 1
  │     ├─ [3.3] Criar Phase 2
  │     ├─ [3.4] Criar interface de túnel
  │     ├─ [3.5] Criar rota estática
  │     └─ [3.6] Criar política de firewall
  │
  ├─► [4] Configurar Palo Alto (paralelo com passo 3)
  │     ├─ [4.1] Criar IKE Crypto Profile
  │     ├─ [4.2] Criar IKE Gateway
  │     ├─ [4.3] Criar IPSec Crypto Profile
  │     ├─ [4.4] Criar IPSec Tunnel
  │     ├─ [4.5] Criar interface de túnel + endereço IP
  │     ├─ [4.6] Criar rota estática
  │     ├─ [4.7] Criar Security Policy
  │     └─ [4.8] Commit das mudanças
  │
  ├─► [5] Aguardar estabelecimento do túnel (30–60s)
  │
  ├─► [6] Validar configuração nos dois dispositivos
  │
  └─► [7] Gerar relatório e alertas
```

### 4.1 Configuração do FortiGate

#### Passo 3.1 — Objetos de endereço
```python
# Rede local do FortiGate
POST /api/v2/cmdb/firewall/address
{
  "name": "NET_SITE_A",
  "subnet": "192.168.20.0/24"
}

# Rede remota (Palo Alto)
POST /api/v2/cmdb/firewall/address
{
  "name": "NET_SITE_B",
  "subnet": "192.168.21.0/24"
}
```

#### Passo 3.2 — Phase 1 (IKE)
```python
POST /api/v2/cmdb/vpn.ipsec/phase1-interface
{
  "name":            "VPN_PALOALTO",
  "type":            "static",
  "interface":       "wan1",
  "ike-version":     "2",
  "remote-gw":       "187.51.100.68",
  "psksecret":       "<PSK_SEGURO>",
  "proposal":        "aes256gcm-sha256",
  "dhgrp":           "14",
  "keylife":         86400,
  "dpd":             "on-demand",
  "dpd-retrycount":  3,
  "dpd-retryinterval": 10
}
```

#### Passo 3.3 — Phase 2 (IPSec)
```python
POST /api/v2/cmdb/vpn.ipsec/phase2-interface
{
  "name":      "VPN_PALOALTO_P2",
  "phase1name": "VPN_PALOALTO",
  "proposal":  "aes256gcm-sha256",
  "dhgrp":     "14",
  "pfs":       "enable",
  "keylife-type": "seconds",
  "keylifeseconds": 3600,
  "src-subnet": "192.168.20.0/24",
  "dst-subnet": "192.168.21.0/24"
}
```

#### Passo 3.4 — Interface de túnel
```python
POST /api/v2/cmdb/system/interface
{
  "name":         "tunnel_vpn",
  "type":         "tunnel",
  "ip":           "169.255.65.1/30",
  "remote-ip":    "169.255.65.2/30",
  "interface":    "wan1",
  "vpn-tunnel":   "VPN_PALOALTO"
}
```

#### Passo 3.5 — Rota estática
```python
POST /api/v2/cmdb/router/static
{
  "dst":       "192.168.21.0/24",
  "gateway":   "169.255.65.2",
  "device":    "tunnel_vpn"
}
```

#### Passo 3.6 — Política de firewall
```python
POST /api/v2/cmdb/firewall/policy
{
  "name":     "ALLOW_VPN_SITE_B",
  "srcintf":  [{"name": "internal"}],
  "dstintf":  [{"name": "tunnel_vpn"}],
  "srcaddr":  [{"name": "NET_SITE_A"}],
  "dstaddr":  [{"name": "NET_SITE_B"}],
  "action":   "accept",
  "schedule": "always",
  "service":  [{"name": "ALL"}],
  "logtraffic": "all"
}
```

---

### 4.2 Configuração do Palo Alto

#### Passo 4.1 — IKE Crypto Profile
```xml
POST /api/?type=config&action=set
xpath=/config/devices/entry/network/ike-crypto-profiles
element=
<entry name="IKE_PROFILE_FORTI">
  <dh-group><member>group14</member></dh-group>
  <authentication><member>sha256</member></authentication>
  <encryption><member>aes-256-gcm</member></encryption>
  <lifetime><seconds>86400</seconds></lifetime>
</entry>
```

#### Passo 4.2 — IKE Gateway
```xml
POST /api/?type=config&action=set
xpath=/config/devices/entry/network/ike-gateways
element=
<entry name="GW_FORTIGATE">
  <authentication>
    <pre-shared-key><key><PSK_SEGURO></key></pre-shared-key>
  </authentication>
  <protocol>
    <ikev2>
      <ike-crypto-profile>IKE_PROFILE_FORTI</ike-crypto-profile>
      <dpd><enable>yes</enable><interval>10</interval><retry>3</retry></dpd>
    </ikev2>
  </protocol>
  <local-address><interface>ethernet1/1</interface></local-address>
  <peer-address><ip>200.86.113.1</ip></peer-address>
</entry>
```

#### Passo 4.3 — IPSec Crypto Profile
```xml
<entry name="IPSEC_PROFILE_FORTI">
  <esp>
    <encryption><member>aes-256-gcm</member></encryption>
    <authentication><member>sha256</member></authentication>
  </esp>
  <dh-group>group14</dh-group>
  <lifetime><seconds>3600</seconds></lifetime>
</entry>
```

#### Passo 4.4 — IPSec Tunnel
```xml
<entry name="TUNNEL_FORTIGATE">
  <auto-key>
    <ike-gateway><entry name="GW_FORTIGATE"/></ike-gateway>
    <ipsec-crypto-profile>IPSEC_PROFILE_FORTI</ipsec-crypto-profile>
    <proxy-id>
      <entry name="PROXY_ID_1">
        <local>192.168.21.0/24</local>
        <remote>192.168.20.0/24</remote>
        <protocol><any/></protocol>
      </entry>
    </proxy-id>
  </auto-key>
  <tunnel-interface>tunnel.1</tunnel-interface>
</entry>
```

#### Passo 4.5 — Interface de túnel
```xml
<entry name="tunnel.1">
  <ip><entry name="169.255.65.2/30"/></ip>
  <comment>Túnel VPN para FortiGate Site A</comment>
</entry>
```

#### Passo 4.6 — Rota estática
```xml
<entry name="ROUTE_SITE_A">
  <destination>192.168.20.0/24</destination>
  <nexthop><ip-address>169.255.65.1</ip-address></nexthop>
  <interface>tunnel.1</interface>
</entry>
```

#### Passo 4.7 — Security Policy
```xml
<entry name="ALLOW_VPN_SITE_A">
  <from><member>trust</member></from>
  <to><member>vpn-zone</member></to>
  <source><member>192.168.21.0/24</member></source>
  <destination><member>192.168.20.0/24</member></destination>
  <application><member>any</member></application>
  <service><member>application-default</member></service>
  <action>allow</action>
  <log-setting>default</log-setting>
</entry>
```

#### Passo 4.8 — Commit obrigatório
```python
# No Palo Alto, NENHUMA configuração tem efeito sem commit
POST /api/?type=commit&cmd=<commit></commit>

# Verifica se o commit foi concluído (polling do job ID)
GET /api/?type=op&cmd=<show><jobs><id>{job_id}</id></jobs></show>
```

> OBS:O FortiGate aplica configurações em tempo real via API.
> O Palo Alto acumula tudo em "candidate config" e só aplica com 'commit'. 
> Bem parecido com uma Controaldora Extreme Vx9000 do qual 'commit w r'.
> O script deve aguardar o commit concluir antes de prosseguir para a validação.

---

## 5. Considerações Específicas

### 5.1 Diferenças de modelo de configuração

| Aspecto | FortiGate | Palo Alto |
|---------|-----------|-----------|
| **Aplicação de config** | Imediata (API REST) | Requer `commit` |
| **Modelo de dados** | JSON flat | XML hierárquico |
| **Autenticação API** | API Token (Bearer) | API Key (query param) |
| **Interface de túnel** | Vinculada à Phase 1 | Objeto independente |
| **Seletores de tráfego** | `quick-mode-selector` na Phase 2 | `proxy-id` no IPSec Tunnel |
| **Rollback** | Manual via API | `revert` para candidate config |

### 5.2 Gestão do Pre-Shared Key (PSK)

O PSK deve ser **idêntico** nos dois dispositivos e **nunca exposto em logs
ou código-fonte**. Estratégias recomendadas:

```python
# Opção 1: variável de ambiente
import os
psk = os.environ["VPN_PSK"]

# Opção 2: HashiCorp Vault
import hvac
client = hvac.Client(url="https://vault.empresa.com")
psk = client.secrets.kv.read_secret("vpn/ipsec")["data"]["psk"]

# Opção 3: AWS Secrets Manager / Azure Key Vault
```

### 5.3 Compatibilidade de propostas

Nem todas as combinações de algoritmos são suportadas igualmente nos dois
firewalls. A tabela abaixo lista combinações testadas e compatíveis:

| Criptografia | Integridade | DH Group | Suporte |
|---|---|---|---|
| AES-256-GCM | SHA-256 | 14 | Ambos |
| AES-256-CBC | SHA-256 | 14 | Ambos |
| AES-128-GCM | SHA-256 | 14 | Ambos |
| 3DES | SHA-1 | 2 | Legado — evitar |
| ChaCha20 | — | 20 | Não suportado no FortiOS < 7.0 |


## 6. Validação e Alertas

### 6.1 Estratégia de validação

A validação é executada em **duas camadas**:

```
Camada 1 — Validação de configuração (plano de controle)
  Verifica se os objetos foram criados corretamente na config
  Não confirma se o túnel está ativo

Camada 2 — Validação operacional (plano de dados)
  Verifica se o túnel IPSec está estabelecido (SA ativa)
  Verifica conectividade end-to-end
  Porque aqui eu vou estar esperando um GET para saber se está UP
```

### 6.2 Validação no FortiGate

#### Verificar se o túnel está UP
```python
GET /api/v2/monitor/vpn/ipsec

# Resposta esperada:
{
  "results": [
    {
      "name":          "VPN_PALOALTO",
      "rgwy":          "198.51.100.1",
      "tun_id":        "169.255.65.1",
      "proxyid": [
        {
          "proxy":     "10.10.0.0/24-10.20.0.0/24",
          "status":    "up",          # ← verificar este campo
          "incoming":  1024,
          "outgoing":  2048
        }
      ]
    }
  ]
}
```

#### Verificar Phase 1 e Phase 2
```python
# Phase 1
GET /api/v2/monitor/vpn/ipsec?filter=phase1_name==VPN_PALOALTO

# Objetos de configuração
GET /api/v2/cmdb/vpn.ipsec/phase1-interface/VPN_PALOALTO
GET /api/v2/cmdb/vpn.ipsec/phase2-interface/VPN_PALOALTO_P2
```

### 6.3 Validação no Palo Alto

#### Verificar Security Associations (SA) ativas
```python
# Chamada API operacional
POST /api/?type=op
cmd=<show><vpn><ipsec-sa></ipsec-sa></vpn></show>

# Resposta relevante:
<response status="success">
  <result>
    <entry>
      <name>TN_FORTIGATE</name>
      <gwid>1</gwid>
      <tunnel-i/f>tunnel.1</tunnel-i/f>
      <state>active</state>       # ← verificar este campo Diferente do Fortigate aqui é active també esperando um GET
      <inner-if>tunnel.1</inner-if>
      <inbound>
        <spi>0x12345678</spi>
        <encryption>AES-256-GCM</encryption>
      </inbound>
    </entry>
  </result>
</response>
```

#### Verificar IKE Phase 1
```python
POST /api/?type=op
cmd=<show><vpn><ike-sa><gateway>GW_FORTIGATE</gateway></ike-sa></vpn></show>

# Verificar: <state>active</state>
```

### 6.4 Validação de conectividade end-to-end

Após confirmar as SAs ativas, verificar se está pingando entre as redes:

```python
# FortiGate — ping pela interface de túnel
POST /api/v2/monitor/system/ping
{
  "host":      "192.168.21.1",       # IP na rede do Palo Alto
  "source":    "169.255.65.1",    # IP do túnel FortiGate
  "count":     5,
  "timeout":   3
}

# Palo Alto — ping operacional
POST /api/?type=op
cmd=<ping><source>169.255.65.2</source>
         <host>192.168.20.1</host>
         <count>5</count></ping>
```

### 6.5 Lógica de validação no script

```python
import time

def validar_vpn(fgt_client, pa_client, max_tentativas=5, intervalo=15):
    """
    Tenta validar o túnel VPN em ambos os dispositivos.
    Retorna lista de divergências ou lista vazia se tudo OK.
    """
    divergencias = []

    for tentativa in range(1, max_tentativas + 1):
        print(f"[{tentativa}/{max_tentativas}] Verificando túnel...")

        # Verifica FortiGate
        status_fgt = fgt_client.get("/api/v2/monitor/vpn/ipsec")
        tunel_fgt  = extrair_status_tunel(status_fgt, "VPN_PALOALTO")

        # Verifica Palo Alto
        status_pa = pa_client.op("<show><vpn><ipsec-sa/></vpn></show>")
        tunel_pa  = extrair_status_sa(status_pa, "TUNNEL_FORTIGATE")

        # Ambos UP — validação concluída
        if tunel_fgt == "up" and tunel_pa == "active":
            print("✔ Túnel estabelecido em ambos os dispositivos.")
            return []

        # Aguarda antes da próxima tentativa
        if tentativa < max_tentativas:
            print(f"  Aguardando {intervalo}s para nova tentativa...")
            time.sleep(intervalo)

    # Esgotou tentativas — registra divergências
    if tunel_fgt != "up":
        divergencias.append({
            "dispositivo": "FortiGate",
            "item":        "Túnel VPN_PALOALTO",
            "esperado":    "up",
            "encontrado":  tunel_fgt or "não encontrado"
        })
    if tunel_pa != "active":
        divergencias.append({
            "dispositivo": "Palo Alto",
            "item":        "SA TUNNEL_FORTIGATE",
            "esperado":    "active",
            "encontrado":  tunel_pa or "não encontrado"
        })

    return divergencias
```

### 6.6 Geração de alertas

O script deve gerar alertas em múltiplos canais conforme a severidade:

| Situação | Severidade | Canais de alerta |
|----------|-----------|-----------------|
| Túnel estabelecido com sucesso |  INFO | Log local, e-mail |
| Commit falhou no Palo Alto | CRÍTICO | Log local, e-mail, Teams/Slack, SNMP trap |
| Configuração aplicada, túnel não sobe |  CRÍTICO | Log local, e-mail, Teams/Slack |
| Phase 1 OK, Phase 2 falha |  ALERTA | Log local, e-mail |
| Divergência de configuração detectada |  ALERTA | Log local, e-mail |
| Parâmetros de entrada inválidos | CRÍTICO | Log local, aborta execução |

#### Exemplo de alerta por e-mail

```python
import smtplib
from email.mime.text import MIMEText

def enviar_alerta(divergencias: list, destinatarios: list):
    if not divergencias:
        assunto = "✔ VPN IPSec configurada com sucesso"
        corpo   = "Túnel FortiGate ↔ Palo Alto estabelecido."
    else:
        assunto = f"⚠ ALERTA: {len(divergencias)} divergência(s) na VPN IPSec"
        linhas  = [
            f"- [{d['dispositivo']}] {d['item']}: "
            f"esperado '{d['esperado']}', encontrado '{d['encontrado']}'"
            for d in divergencias
        ]
        corpo = "Divergências encontradas:\n\n" + "\n".join(linhas)

    msg            = MIMEText(corpo)
    msg["Subject"] = assunto
    msg["From"]    = "automacao@empresa.com"
    msg["To"]      = ", ".join(destinatarios)

    with smtplib.SMTP("smtp.empresa.com", 587) as smtp:
        smtp.starttls()
        smtp.login("automacao@empresa.com", os.environ["SMTP_PASSWORD"])
        smtp.send_message(msg)
```

#### Exemplo de alerta no Microsoft Teams / Slack

```python
import requests

def alerta_teams(webhook_url: str, divergencias: list):
    cor     = "00FF00" if not divergencias else "FF0000"
    titulo  = "✔ VPN OK" if not divergencias else f"⚠ VPN — {len(divergencias)} divergência(s)"
    detalhes = "\n".join(
        f"• [{d['dispositivo']}] {d['item']}: "
        f"esperado `{d['esperado']}`, encontrado `{d['encontrado']}`"
        for d in divergencias
    ) or "Nenhuma divergência encontrada."

    payload = {
        "@type": "MessageCard",
        "themeColor": cor,
        "title": titulo,
        "text": detalhes
    }
    requests.post(webhook_url, json=payload)
```

### 6.7 Relatório de execução

Ao final de cada execução, o script gera um arquivo de relatório:

```
VPN_REPORT_20250315_143022.txt
─────────────────────────────────────────────────────
RELATÓRIO DE AUTOMAÇÃO — VPN IPSec
Data/hora : 2025-03-15 14:30:22
─────────────────────────────────────────────────────
PARÂMETROS
  FortiGate WAN  : 200.86.113.1
  Palo Alto WAN  : 87.51.100.68 
  Rede túnel     : 169.255.65.0/30
  Phase 1        : AES-256-GCM / SHA-256 / DH14 / IKEv2
  Phase 2        : AES-256-GCM / SHA-256 / DH14 / 3600s

CONFIGURAÇÃO
  [14:30:24] FortiGate — objetos de endereço    ✔
  [14:30:25] FortiGate — Phase 1               ✔
  [14:30:26] FortiGate — Phase 2               ✔
  [14:30:27] FortiGate — interface de túnel    ✔
  [14:30:28] FortiGate — rota estática         ✔
  [14:30:28] FortiGate — política de firewall  ✔
  [14:30:24] Palo Alto — IKE Crypto Profile    ✔
  [14:30:25] Palo Alto — IKE Gateway           ✔
  [14:30:26] Palo Alto — IPSec Crypto Profile  ✔
  [14:30:27] Palo Alto — IPSec Tunnel          ✔
  [14:30:28] Palo Alto — interface de túnel    ✔
  [14:30:29] Palo Alto — rota estática         ✔
  [14:30:30] Palo Alto — Security Policy       ✔
  [14:30:31] Palo Alto — commit                ✔

VALIDAÇÃO
  FortiGate — SA status  : up     ✔
  Palo Alto — SA status  : active ✔
  Ping 169.255.65.1→.2   : OK     ✔

RESULTADO FINAL: SUCESSO — Nenhuma divergência encontrada.
─────────────────────────────────────────────────────
```

---

## 7. Referências

| Recurso | URL |
|---------|-----|
| FortiOS REST API Guide | https://docs.fortinet.com/document/fortigate/latest/fortios-rest-api-reference |
| FortiGate IPsec VPN | https://docs.fortinet.com/document/fortigate/latest/administration-guide/762500/ipsec-vpn |
| PAN-OS XML API Guide | https://docs.paloaltonetworks.com/pan-os/latest/pan-os-panorama-api |
| pan-os-python SDK | https://pan-os-python.readthedocs.io |
| fortiosapi SDK | https://github.com/fortinet/fortiosapi |
| IKEv2 RFC 7296 | https://datatracker.ietf.org/doc/html/rfc7296 |
| IPSec ESP RFC 4303 | https://datatracker.ietf.org/doc/html/rfc4303 |


---

*Documento mantido em: `docs/Plano_automacao_IPSEC.md`*  
*Repositório: `automacao-vpn-ipsec`*
