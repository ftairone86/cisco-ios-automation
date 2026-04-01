from qt_core import *

# Adiciona a pasta ui/ ao sys.path para localizar os ui_*.py
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "ui"))


from ui.ui_conexao_page import Ui_ConexaoPage
from worker_rede import WorkerRede
from sinais import Sinais
from gerenciador import GerenciadorSwitch

class AbaConexao(QWidget, Ui_ConexaoPage):
    """
    Aba de credenciais SSH gerada pelo Qt Designer.

    Após setupUi(self), os seguintes widgets estão disponíveis:
        lineHost       — IP / hostname do switch
        spinPorta      — porta SSH (padrão 22)
        lineUsuario    — usuário SSH
        lineSenha      — senha SSH (echo oculto)
        lineSecret     — enable secret (opcional)
        lblStatus      — indicador ONLINE / OFFLINE
        btnConectar    — inicia a conexão SSH
        btnDesconectar — encerra a sessão SSH

    Sinais públicos:
        conectado(str)  — emitido com o hostname após conexão bem-sucedida
        desconectado()  — emitido ao encerrar a sessão
    """

    conectado    = Signal(str)
    desconectado = Signal()

    def __init__(self, log_fn):
        super().__init__()
        self.setupUi(self)           # amarra o layout do Ui_ConexaoPage
        self.log_fn      = log_fn    # escreve no painel de log da janela principal
        self.gerenciador = None      # instância ativa de GerenciadorSwitch
        self._worker     = None      # WorkerRede em execução
        self._sinais     = None      # objeto Sinais do worker atual
        self._wire()

    def _wire(self):
        #Liga os botões do Ui_ConexaoPage aos handlers desta classe.
        self.btnConectar.clicked.connect(self._on_conectar) # no momento do "click" aqui eu chamo a função de conectar (_on_conectar)
        self.btnDesconectar.clicked.connect(self._on_desconectar)

    # Aqui eu crie funções iguais as que eu uso em java com android estabelecer conexão https e enviar parametros 

    def _on_conectar(self):
        
       # Lê os campos do formulário e inicia a conexão SSH em QThread.
        #Os valores são lidos aqui (thread principal) e passados ao worker.
        
        host = self.lineHost.text().strip()
        if not host:
            QMessageBox.warning(self, "Campo vazio","Informe o IP ou hostname do switch.") # Validando o campo
            return

        # Instancia o gerenciador com as credenciais dos widgets do .ui
        # Aqui estou criando o objeto da classe GerenciadorSwitch, que é o backend de rede. 
        self.gerenciador = GerenciadorSwitch(
            host    = host,
            porta   = self.spinPorta.value(),
            usuario = self.lineUsuario.text().strip(),
            senha   = self.lineSenha.text(),
            secret  = self.lineSecret.text(),
        )
        self.btnConectar.setEnabled(False)

        # Conecta sinais com QueuedConnection ANTES de iniciar a thread
        # Aqui estou criando o objeto Sinais, que é o meio de comunicação entre a thread de rede e a thread principal (GUI).
        self._sinais = Sinais()
        self._sinais.log.connect(
            self.log_fn, Qt.ConnectionType.QueuedConnection
        )
        self._sinais.concluido.connect(
            self._apos_conectar, Qt.ConnectionType.QueuedConnection
        )
        self._sinais.log.emit("Iniciando conexão SSH...", "info")
        
         # A mágia acontece aqui: o WorkerRede executa a função conectar() do gerenciador em uma thread secundária, e os resultados são comunicados de volta à interface via sinais.
        self._worker = WorkerRede(self.gerenciador.conectar, self._sinais)
        self._worker.start()

    def _apos_conectar(self, hostname):
        
        ##Chama executado na thread principal via QueuedConnection.
        ##Atualiza lblStatus com o resultado da tentativa de conexão.
        
        if hostname:
            self.lblStatus.setText(f"● ONLINE — {hostname}")
            self.lblStatus.setStyleSheet(
                "color: green; font-weight: bold; padding: 8px;"
            )
            self.btnDesconectar.setEnabled(True)
            self._sinais.log.emit(f"Conectado: {hostname}", "ok")
            self.conectado.emit(hostname)
        else:
            self.lblStatus.setText("● ERRO DE CONEXÃO")
            self.lblStatus.setStyleSheet(
                "color: red; font-weight: bold; padding: 8px;"
            )
            self.btnConectar.setEnabled(True)

    def _on_desconectar(self):
        """Encerra a sessão SSH e restaura os widgets ao estado inicial."""
        if self.gerenciador:
            self.gerenciador.desconectar()
            self.gerenciador = None

        self.lblStatus.setText("● DESCONECTADO")
        self.lblStatus.setStyleSheet("color: #888; padding: 8px;")
        self.btnConectar.setEnabled(True)
        self.btnDesconectar.setEnabled(False)
        self.log_fn("Sessão encerrada.", "info")
        self.desconectado.emit()