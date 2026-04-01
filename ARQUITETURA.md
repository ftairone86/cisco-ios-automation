# Arquitetura — Cisco IOS Automation

## Diagrama de camadas

```
                    FRONTEND

   main.py  ──►  JanelaPrincipal (QMainWindow + Ui_MainWindow)
                 ├── AbaConexao  (QWidget + Ui_ConexaoPage)   — conexao.py
                 ├── AbaVlans    (QWidget + Ui_VlansPage)     — vlans.py
                 └── AbaDeploy   (QWidget + Ui_DeployPage)    — deploy.py

   Sinais (sinais.py) ──QueuedConnection──► WorkerRede (worker_rede.py / QThread)

                          │  chama métodos de
                          ▼

                    BACKEND

   gerenciador.py  →  GerenciadorSwitch
                       ├── conectar() / desconectar()
                       ├── configurar_vlans()
                       ├── excluir_vlan()
                       ├── configurar_hostname()
                       ├── salvar_nvram()
                       ├── backup_config()
                       └── validar_config()

                          │  SSH via Netmiko
                          ▼

                    Switch Cisco IOS (hardware / GNS3)
```

---

## Módulos e responsabilidades

| Arquivo | Responsabilidade |
|---|---|
| `main.py` | Ponto de entrada — instancia `QApplication` e `JanelaPrincipal` |
| `conexao.py` | Aba de conexão SSH: formulário, botão conectar/desconectar, status |
| `vlans.py` | Aba de VLANs: tabela editável, adicionar/remover/excluir no switch |
| `deploy.py` | Aba de deploy: hostname, NVRAM, backup, validação |
| `gerenciador.py` | `GerenciadorSwitch` — toda a lógica Netmiko/IOS, sem GUI |
| `worker_rede.py` | `WorkerRede` — executa qualquer callable em `QThread` |
| `sinais.py` | Sinais Qt (`log`, `concluido`) para comunicação entre threads |
| `qt_core.py` | Importações centralizadas do PySide6 |
| `ui/ui_*.py` | Layout gerado por `pyside6-uic` — não editar manualmente |
| `ui/*.ui` | Fontes do Qt Designer — editar aqui |

---

## Padrão de amarração UI → código

```python
class AbaConexao(QWidget, Ui_ConexaoPage):  # herança dupla
    def __init__(self, log_fn):
        super().__init__()
        self.setupUi(self)   # popula self com widgets do .ui
        self._wire()         # conecta sinais aos slots

    def _wire(self):
        self.btnConectar.clicked.connect(self._on_conectar)
```

---

## Fluxo de operação em thread

```
Thread principal (Qt)          WorkerRede (QThread)
        │                               │
        │── WorkerRede(fn, sinais) ────►│
        │── worker.start() ────────────►│── fn()  (ex: gerenciador.conectar)
        │                               │── sinais.log.emit("mensagem")
        │◄── sinais.log [QueuedConn] ───│
        │── log_fn("mensagem") ─────────│
        │                               │── sinais.concluido.emit(resultado)
        │◄── sinais.concluido ──────────│
        │── atualiza widget ────────────│
```

> O Qt proíbe acesso a widgets fora da thread principal.
> `QueuedConnection` enfileira o slot no event loop principal — tornando seguro atualizar qualquer widget.

---

## Regenerar arquivos UI

Após editar um `.ui` no Qt Designer:

```bash
venv/bin/pyside6-uic ui/main_window.ui   -o ui/ui_main_window.py
venv/bin/pyside6-uic ui/conexao_page.ui  -o ui/ui_conexao_page.py
venv/bin/pyside6-uic ui/vlans_page.ui    -o ui/ui_vlans_page.py
venv/bin/pyside6-uic ui/deploy_page.ui   -o ui/ui_deploy_page.py
```
