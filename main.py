"""
app.py — Interface gráfica do Gerenciador de VLANs integrada aos arquivos
gerados pelo Qt Designer (pyside6-uic).

Arquivos de UI utilizados (pasta ui/):
    ui_main_window.py   →  Ui_MainWindow    (janela + abas + log)
    ui_conexao_page.py  →  Ui_ConexaoPage   (formulário SSH)
    ui_vlans_page.py    →  Ui_VlansPage     (tabela de VLANs)
    ui_deploy_page.py   →  Ui_DeployPage    (opções, botões, validação)

Padrão de amarração — herança dupla:
    class MinhaAba(QWidget, Ui_MinhaAba):
        def __init__(self):
            super().__init__()
            self.setupUi(self)   # popula self com todos os widgets do .ui
            self._wire()         # conecta sinais dos botões aos slots

Segurança de threads:
    Operações de rede rodam em QThread separada.
    A GUI é atualizada EXCLUSIVAMENTE via Signal com QueuedConnection.
    Widgets NUNCA são acessados diretamente de dentro das threads.
"""

from qt_core import *

# Adiciona a pasta ui/ ao sys.path para localizar os ui_*.py
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "ui"))

from ui.ui_main_window import Ui_MainWindow
from conexao import AbaConexao
from vlans import AbaVlans
from deploy import AbaDeploy

class JanelaPrincipal(QMainWindow, Ui_MainWindow):
    """
    Janela raiz integrada ao Ui_MainWindow gerado pelo Qt Designer.

    Após setupUi(self), os seguintes widgets estão disponíveis:
        tabWidget    — QTabWidget com as 3 abas
        tabConexao   — QWidget placeholder da aba Conexão
        tabVlans     — QWidget placeholder da aba VLANs
        tabDeploy    — QWidget placeholder da aba Deploy
        txtLog       — QTextEdit somente leitura (painel de log)
        btnLimparLog — limpa o conteúdo do txtLog

    As abas (AbaConexao, AbaVlans, AbaDeploy) são instanciadas separadamente
    e inseridas nos placeholders via QVBoxLayout sem margens, preenchendo
    todo o espaço da aba.
    """

    # Mapeamento nível → cor HTML para o painel de log
    _CORES_LOG = {
        "info":  "#888888",   # cinza  — informação geral
        "ok":    "#33aa33",   # verde  — operação bem-sucedida
        "erro":  "#ee3333",   # vermelho — erro
        "aviso": "#cc8800",   # laranja  — divergência / alerta
    }

    def __init__(self):
        super().__init__()
        self.setupUi(self)          # amarra o layout do Ui_MainWindow
        self._injetar_abas()        # instancia e posiciona as 3 abas
        self._wire()                # conecta o botão de log

        # Força iniciar na aba Conexão (mesmo que o .ui esteja selecionando outra)
        self.tabWidget.setCurrentWidget(self.tabConexao)

        # Mensagens de boas-vindas
        self.escrever_log("Gerenciador de VLANs iniciado.", "info")
        self.escrever_log(
            "Preencha as credenciais na aba 'Conexão' e clique em CONECTAR.",
            "info",
        )

    def _injetar_abas(self):
        """
        Instancia AbaConexao, AbaVlans e AbaDeploy e as insere nos QWidget
        placeholder (tabConexao, tabVlans, tabDeploy) do Ui_MainWindow.

        Cada placeholder recebe um QVBoxLayout com margem zero para que a
        aba preencha todo o espaço disponível na tab.
        """
        # ── Aba Conexão ───────────────────────────────────────────────────────
        self.pg_conn = AbaConexao(log_fn=self.escrever_log)
        lay_conn = QVBoxLayout(self.tabConexao)
        lay_conn.setContentsMargins(0, 0, 0, 0)
        lay_conn.addWidget(self.pg_conn)

        # ── Aba VLANs ─────────────────────────────────────────────────────────
        self.pg_vlans = AbaVlans(log_fn=self.escrever_log)
        self.pg_vlans.set_aba_conn(self.pg_conn)   # injeta referência cruzada
        lay_vlans = QVBoxLayout(self.tabVlans)
        lay_vlans.setContentsMargins(0, 0, 0, 0)
        lay_vlans.addWidget(self.pg_vlans)

        # ── Aba Deploy ────────────────────────────────────────────────────────
        self.pg_deploy = AbaDeploy(
            aba_conn  = self.pg_conn,
            aba_vlans = self.pg_vlans,
            log_fn    = self.escrever_log,
        )
        lay_deploy = QVBoxLayout(self.tabDeploy)
        lay_deploy.setContentsMargins(0, 0, 0, 0)
        lay_deploy.addWidget(self.pg_deploy)
        
    # Em vez de espalhar as conexões por todo o código, você centraliza a "fiação" (daí o nome wire) em um só lugar. 
    # Isso facilita muito a manutenção
    def _wire(self):
        """Conecta o btnLimparLog gerado pelo Ui_MainWindow ao txtLog."""
        self.btnLimparLog.clicked.connect(self.txtLog.clear)

    # ── painel de log ─────────────────────────────────────────────────────────

    def escrever_log(self, mensagem: str, nivel: str = "info"):
        """
        Acrescenta uma linha colorida ao txtLog com timestamp.

        Este método deve ser chamado APENAS na thread principal.
        Para chamadas cross-thread, conecte via QueuedConnection:
            sinais.log.connect(janela.escrever_log,
                               Qt.ConnectionType.QueuedConnection)
        """
        ts  = datetime.datetime.now().strftime("%H:%M:%S")
        cor = self._CORES_LOG.get(nivel, "#888888")
        html = (
            f'<span style="color:#555;">[{ts}]</span> '
            f'<span style="color:{cor};">{mensagem}</span><br>'
        )
        # Rola para o final antes e depois para garantir visibilidade
        self.txtLog.moveCursor(QTextCursor.MoveOperation.End)
        self.txtLog.insertHtml(html)
        self.txtLog.moveCursor(QTextCursor.MoveOperation.End)


# ════════════════════════════════════════════════════════════════════════════
# PONTO DE ENTRADA
# ════════════════════════════════════════════════════════════════════════════

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Gerenciador de VLANs")
    janela = JanelaPrincipal()
    janela.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()