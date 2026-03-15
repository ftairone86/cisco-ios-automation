# Arquitetura — VLAN Manager

## Diagrama de camadas


                    FRONTEND  (src/app.py)                
                                                         
   JanelaPrincipal (QMainWindow + Ui_MainWindow)          
   ├── AbaConexao  (QWidget + Ui_ConexaoPage)             
   ├── AbaVlans    (QWidget + Ui_VlansPage)                
   └── AbaDeploy   (QWidget + Ui_DeployPage)              
                                                           
   Sinais ──QueuedConnection──► Workers (QThread)          

                     │  chama métodos de
                     ▼
                   BACKEND  (src/core.py)                 
                                                         
   GerenciadorSwitch                                      
   ├── conectar() / desconectar()                         
   ├── configurar_vlans()                                 
   ├── excluir_vlan()    **Bonus**                                   
   ├── configurar_hostname()                               
   ├── salvar_nvram()                                      
   ├── backup_config()                                    
   └── validar_config()                                    

                     │  SSH via
                     ▼
               Switch Cisco IOS (hardware)                


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

## Módulos e responsabilidades

| Arquivo | Responsabilidade |
|---------|-----------------|
| `src/app.py` | Apresentação: widgets, sinais, threads, log |
| `src/core.py` | Rede: SSH, IOS, validação, backup |
| `ui/ui_*.py` | Layout gerado por `pyside6-uic` — não editar |
| `ui/*.ui` | Fontes do Qt Designer — editar aqui |
