# Gerenciador de VLANs — Cisco IOS 15.1

Aplicação desktop em Python com interface gráfica (PySide6) para configuração
automatizada de VLANs em switches Cisco IOS 15.1 via SSH/Netmiko.

---

## Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| **Conexão SSH** | Conecta ao switch com usuário, senha e enable secret |
| **Configuração de VLANs** | Aplica IDs e nomes de VLANs diretamente no switch |
| **Hostname** | Altera o hostname do switch para um valor definido pelo usuário |
| **Salvar NVRAM** | Executa `write memory` para persistir a configuração |
| **Backup** | Salva a running-config em arquivo local `<hostname>_<timestamp>.txt` |
| **Validação** | Compara a config atual do switch com a desejada e alerta divergências |
| **Modo simulação** | Funciona sem switch real (Netmiko não instalado ou sem conexão) |
| **Bonus** | Excluir Vlans |

---

## Estrutura do projeto

```
cisco-ios-automation/
├── main.py            # Ponto de entrada — inicializa a aplicação PySide6
├── conexao.py         # Aba de conexão SSH (widget + lógica)
├── deploy.py          # Aba de deploy de configurações
├── vlans.py           # Aba de gerenciamento de VLANs
├── gerenciador.py     # GerenciadorSwitch — operações Netmiko no switch
├── worker_rede.py     # WorkerRede — execução SSH em QThread
├── sinais.py          # Sinais Qt para comunicação entre threads
├── qt_core.py         # Importações centralizadas do PySide6
│
├── ui/                # Arquivos de interface gerados pelo Qt Designer
│   ├── main_window.ui        ← fonte Qt Designer
│   ├── conexao_page.ui       ← fonte Qt Designer
│   ├── vlans_page.ui         ← fonte Qt Designer
│   ├── deploy_page.ui        ← fonte Qt Designer
│   ├── ui_main_window.py     ← gerado pelo pyside6-uic
│   ├── ui_conexao_page.py    ← gerado pelo pyside6-uic
│   ├── ui_vlans_page.py      ← gerado pelo pyside6-uic
│   └── ui_deploy_page.py     ← gerado pelo pyside6-uic
│
├── bkp/               # Backups de running-config gerados pelo app
├── Imagens_Telas/     # Capturas de tela da interface
├── Imagens_arquitetura/  # Diagramas de arquitetura e lab GNS3
├── Plano para Automacao VPN/  # Planejamento de automação VPN/IPsec
├── ARQUITETURA.md     # Documentação técnica da arquitetura
├── COMMITS.md         # Histórico e padrões de commits
├── requirements.txt
└── README.md
```

> Para regenerar os arquivos `ui_*.py` após editar um `.ui` no Qt Designer:
> ```bash
> venv/bin/pyside6-uic ui/main_window.ui    -o ui/ui_main_window.py
> venv/bin/pyside6-uic ui/conexao_page.ui   -o ui/ui_conexao_page.py
> venv/bin/pyside6-uic ui/vlans_page.ui     -o ui/ui_vlans_page.py
> venv/bin/pyside6-uic ui/deploy_page.ui    -o ui/ui_deploy_page.py
> ```

---

## Instalação

### 1. Pré-requisitos

- Python 3.10 ou superior
- pip

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

Conteúdo do `requirements.txt`:

```
PySide6>=6.6
netmiko>=4.3
```

## Execução

```bash
python app.py
```

---

## Como usar o frontend

### Aba Conexão

1. Preencha o **IP / Host** do switch (ex: `192.168.1.1`)
2. Confirme a **porta SSH** (padrão: `22`)
3. Informe **usuário** e **senha**
4. Se o switch exigir, preencha o **Enable Secret**
5. Clique em **⚡ CONECTAR**

O status na tela muda para `● ONLINE — <hostname>` ao conectar com sucesso.

---

### Aba VLANs

A tabela vem pré-carregada com as VLANs padrão do projeto:

| ID | Nome |
|----|------|
| 10 | VLAN_DADOS |
| 20 | VLAN_VOZ |
| 50 | VLAN_SEGURANCA |

Você pode:
- **Editar** qualquer célula diretamente na tabela
- **Adicionar** novas VLANs pelo formulário inferior
- **Remover** a linha selecionada
- **Restaurar padrões** para voltar às 3 VLANs originais

---

### Aba Deploy

Configure as opções antes de aplicar:

| Opção | Descrição |
|---|---|
| **Hostname** | Nome a aplicar no switch (padrão: `SWITCH_AUTOMATIZADO`) |
| **Aplicar hostname** | Marque para alterar o hostname |
| **Salvar na NVRAM** | Executa `write memory` automaticamente após o deploy |
| **Validar após deploy** | Compara a config aplicada com a desejada |

Botões disponíveis:

- **APLICAR CONFIGURAÇÕES** — executa o fluxo completo
- **Salvar NVRAM** — salva manualmente sem reconfigurar
- **Backup Config** — escolhe pasta e salva o arquivo de backup
- **Validar Config** — compara sem aplicar nada

Para as imagens dos botoes e status usei caracteres especiais como este 🎮 só copiar do mapa no POP OS

---

### Painel de Log

Exibe todas as operações com timestamp e cores:

| Cor | Significado |
|-----|-------------|
| Cinza | Informação geral |
| Verde | Operação bem-sucedida |
| Vermelho | Erro |
| Laranja | Alerta / divergência |

---

## Modo Simulação

Se o Netmiko não estiver instalado **ou** a conexão ao switch falhar,
o app entra em **modo simulação**:

- Os comandos IOS são apenas exibidos no log (não enviados)
- O backup gera um arquivo `.txt` com configuração fictícia
- A validação retorna "sem divergências" automaticamente

Isso permite testar a interface sem acesso a hardware real.

---

## Exemplo de arquivo de backup

Nome gerado automaticamente:

```
SWITCH_AUTOMATIZADO_20250315_143022.txt
```

Conteúdo: a saída completa de `show running-config` do switch.

---

## Desafios de implementação

- Todas as operações SSH rodam em `QThread` para não travar a interface ( Antes de pesquisar sobre esse classe o código trava)
- Timeout em 10s porém depende da latência de onde o equipamento está testei real em um ambiente de produção
- A validação usa expressões regulares para comparar a running-config então na hora de puxar achei melhor dar o comando     "show vlan brief"
- Para atualizar a interface toda vez que alterar algum componente tem que aplicar o comando "venv/bin/pyside6-uic main_window.ui -o ui_main_window.py"

- O campo Enable Secret pode ficar vazio se o switch não exigir
- A parte do Timeout importante pois Switchs em outras localidades do Brasil apresentão latência maior na VPN
- Quebrei muito a cabeça com a parte gráfica no Python, diferente do java onde dentro do componente eu inseria o código java da ação do botão ou da exibição de lista, aqui tive que buscar na mão os componentes do QTDesigner
-  cmd_verify=False previne falsos timeouts em IOS que ecoam os comandos de forma diferente do esperado pelo Netmiko 
-  Sinais emitidos pela thread de rede e recebidos na thread principal.
- O Qt proíbe acesso a widgets fora da thread principal. Ao conectar um sinal com QueuedConnection, o Qt enfileira o slot no vent loop da thread principal — tornando seguro atualizar qualquer widget.
- """ Aprendendo a comitar melhor no código """
    
