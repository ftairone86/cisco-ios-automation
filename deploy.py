from qt_core import *

# Adiciona a pasta ui/ ao sys.path para localizar os ui_*.py
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "ui"))

from ui.ui_deploy_page import Ui_DeployPage
from conexao import AbaConexao
from vlans import AbaVlans
from worker_rede import WorkerRede
from sinais import Sinais   


class AbaDeploy(QWidget, Ui_DeployPage):
    """
    Aba de deploy gerada pelo Qt Designer.

    Após setupUi(self), os seguintes widgets estão disponíveis:
        lineHostname    — hostname a aplicar no switch
        chkHostname     — habilita aplicação do hostname
        chkSalvar       — habilita write memory após deploy
        chkValidar      — habilita validação após deploy
        progressBar     — progresso do deploy (0–100)
        btnDeploy       — executa o fluxo completo
        btnSalvar       — write memory isolado
        btnBackup       — salva running-config em arquivo local
        btnValidar      — valida sem aplicar nada
        lblResultadoVal — resultado da validação (OK / divergências)
        tableValidacao  — tabela de divergências (Item | Esperado | Encontrado)

    tableValidacao tem suas colunas configuradas para expandir após setupUi(),
    pois essa propriedade não está disponível no Qt Designer.
    """

    def __init__(self, aba_conn: AbaConexao, aba_vlans: AbaVlans, log_fn):
        super().__init__()
        self.setupUi(self)           # amarra o layout do Ui_DeployPage
        self.aba_conn  = aba_conn
        self.aba_vlans = aba_vlans
        self.log_fn    = log_fn
        self._worker   = None
        self._sinais   = None

        # Configuração pós-setupUi: colunas da tabela de validação expansíveis
        self.tableValidacao.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self._wire()

    def _wire(self):
        """Liga os botões do Ui_DeployPage aos handlers desta classe."""
        self.btnDeploy.clicked.connect(self._on_deploy)
        self.btnSalvar.clicked.connect(self._on_salvar)
        self.btnBackup.clicked.connect(self._on_backup)
        self.btnValidar.clicked.connect(self._on_validar)

    # ── helpers internos ─────────────────────────────────────────────────────

    def _gerenciador(self):
        """Retorna o GerenciadorSwitch ativo ou exibe alerta e retorna None."""
        g = self.aba_conn.gerenciador
        if not g:
            QMessageBox.warning(self, "Sem conexão",
                                "Conecte ao switch na aba 'Conexão'.")
        return g

    def _novo_sinais(self) -> Sinais:
        """
        Cria um Sinais e conecta log e progressBar com QueuedConnection.
        Centraliza a configuração de segurança de thread para todos os workers.
        """
        s = Sinais()
        s.log.connect(
            self.log_fn, Qt.ConnectionType.QueuedConnection
        )
        s.progresso.connect(
            self.progressBar.setValue, Qt.ConnectionType.QueuedConnection
        )
        return s

    # ── deploy completo ───────────────────────────────────────────────────────

    def _on_deploy(self):
        """
        Fluxo completo de deploy executado em QThread:
          1. configurar_vlans()    — sempre
          2. configurar_hostname() — se chkHostname marcado
          3. salvar_nvram()        — se chkSalvar marcado
          4. validar_config()      — se chkValidar marcado

        IMPORTANTE: os estados dos checkboxes (fazer_hostname, fazer_salvar,
        fazer_validar) e o texto do lineHostname são lidos AQUI, na thread
        principal, e passados como variáveis locais para a closure executada
        na QThread. Widgets NÃO podem ser lidos dentro de QThread.
        """
        g = self._gerenciador()
        if not g:
            return

        vlans    = self.aba_vlans.obter_vlans()
        hostname = self.lineHostname.text().strip()

        if not vlans:
            QMessageBox.warning(self, "Sem VLANs",
                                "Adicione ao menos uma VLAN na aba VLANs.")
            return

        self.btnDeploy.setEnabled(False)
        self.progressBar.setValue(0)

        # Lê opções na thread principal antes de iniciar o worker
        fazer_hostname = self.chkHostname.isChecked()
        fazer_salvar   = self.chkSalvar.isChecked()
        fazer_validar  = self.chkValidar.isChecked()

        self._sinais = self._novo_sinais()
        self._sinais.concluido.connect(
            self._apos_deploy, Qt.ConnectionType.QueuedConnection
        )

        sinais = self._sinais   # referência local capturada pela closure

        def executar():
            """
            Roda na QThread. Acessa apenas variáveis locais e sinais.
            Nunca acessa widgets diretamente.
            """
            resultado = {}
            sinais.log.emit("=== Iniciando deploy ===", "info")

            # Passo 1: configurar VLANs (sempre)
            sinais.log.emit("Configurando VLANs...", "info")
            resultado["vlans"] = g.configurar_vlans(vlans)
            sinais.progresso.emit(40)

            # Passo 2: hostname (condicional)
            if fazer_hostname and hostname:
                sinais.log.emit(f"Aplicando hostname: {hostname}", "info")
                resultado["hostname"] = g.configurar_hostname(hostname)
                sinais.progresso.emit(60)

            # Passo 3: salvar NVRAM (condicional)
            if fazer_salvar:
                sinais.log.emit("Salvando na NVRAM...", "info")
                resultado["nvram"] = g.salvar_nvram()
                sinais.progresso.emit(80)

            # Passo 4: validar (condicional)
            if fazer_validar:
                sinais.log.emit("Validando configuração...", "info")
                resultado["divergencias"] = g.validar_config(vlans, hostname)
                sinais.progresso.emit(100)

            return resultado

        self._worker = WorkerRede(executar, self._sinais)
        self._worker.start()

    def _apos_deploy(self, resultado):
        """Callback na thread principal — processa e exibe o resultado do deploy."""
        self.btnDeploy.setEnabled(True)

        if not resultado:
            self.log_fn("Deploy falhou.", "erro")
            return

        self.log_fn("VLANs configuradas com sucesso.", "ok")

        if "hostname" in resultado:
            self.log_fn("Hostname aplicado.", "ok")
        if "nvram" in resultado:
            self.log_fn("Configuração salva na NVRAM.", "ok")
        if "divergencias" in resultado:
            self._exibir_validacao(resultado["divergencias"])

        self.log_fn("=== Deploy concluído ===", "ok")

    # ── salvar NVRAM ──────────────────────────────────────────────────────────

    def _on_salvar(self):
        """Executa write memory de forma isolada, sem reconfigurar VLANs."""
        g = self._gerenciador()
        if not g:
            return

        self.log_fn("Salvando na NVRAM...", "info")
        self._sinais = self._novo_sinais()
        self._sinais.concluido.connect(
            lambda r: self.log_fn(
                "Configuração salva na NVRAM." if r else "Falha ao salvar NVRAM.",
                "ok" if r else "erro",
            ),
            Qt.ConnectionType.QueuedConnection,
        )
        self._worker = WorkerRede(g.salvar_nvram, self._sinais)
        self._worker.start()

    # ── backup ────────────────────────────────────────────────────────────────

    def _on_backup(self):
        """Abre seletor de pasta e salva a running-config em arquivo local."""
        g = self._gerenciador()
        if not g:
            return

        # Diálogo de pasta — executado na thread principal (correto)
        pasta = QFileDialog.getExistingDirectory(
            self, "Selecionar pasta para backup", os.path.expanduser("~")
        )
        if not pasta:
            return

        self.log_fn(f"Iniciando backup → {pasta}", "info")
        self._sinais = self._novo_sinais()
        self._sinais.concluido.connect(
            self._apos_backup, Qt.ConnectionType.QueuedConnection
        )
        self._worker = WorkerRede(g.backup_config, self._sinais, pasta)
        self._worker.start()

    def _apos_backup(self, resultado):
        """Exibe confirmação com o caminho do arquivo gerado."""
        if resultado:
            caminho, _ = resultado
            self.log_fn(f"Backup salvo: {caminho}", "ok")
            QMessageBox.information(
                self, "Backup concluído", f"Arquivo salvo em:\n{caminho}"
            )
        else:
            self.log_fn("Falha ao realizar backup.", "erro")

    # ── validar ───────────────────────────────────────────────────────────────

    def _on_validar(self):
        """Valida a configuração atual do switch sem aplicar alterações."""
        g = self._gerenciador()
        if not g:
            return

        vlans    = self.aba_vlans.obter_vlans()
        hostname = self.lineHostname.text().strip()

        self.log_fn("Validando configuração do switch...", "info")
        self._sinais = self._novo_sinais()
        self._sinais.concluido.connect(
            self._exibir_validacao, Qt.ConnectionType.QueuedConnection
        )
        self._worker = WorkerRede(
            g.validar_config, self._sinais, vlans, hostname
        )
        self._worker.start()

    def _exibir_validacao(self, divergencias: list):
        """
        Atualiza lblResultadoVal e tableValidacao com o resultado da validação.

        Sem divergências:
            lblResultadoVal — texto verde   ✔ Configuração OK
        Com divergências:
            lblResultadoVal — texto vermelho ⚠ N divergência(s)
            tableValidacao  — uma linha por divergência, coluna "Encontrado"
                              destacada em vermelho
        """
        self.tableValidacao.setRowCount(0)

        if not divergencias:
            self.lblResultadoVal.setText("✔  Configuração OK — sem divergências")
            self.lblResultadoVal.setStyleSheet("color: green;")
            self.log_fn("Validação: configuração conforme o esperado.", "ok")
            return

        # Alerta visual com contagem total de divergências
        self.lblResultadoVal.setText(
            f"⚠  {len(divergencias)} divergência(s) encontrada(s)!"
        )
        self.lblResultadoVal.setStyleSheet("color: red; font-weight: bold;")
        self.log_fn(
            f"ALERTA: {len(divergencias)} divergência(s) encontrada(s)!", "aviso"
        )

        # Preenche a tableValidacao linha a linha
        for div in divergencias:
            r = self.tableValidacao.rowCount()
            self.tableValidacao.insertRow(r)

            self.tableValidacao.setItem(r, 0, QTableWidgetItem(div["item"]))
            self.tableValidacao.setItem(r, 1, QTableWidgetItem(div["esperado"]))

            # Coluna "Encontrado" em vermelho para destacar a divergência
            item_enc = QTableWidgetItem(div["encontrado"])
            item_enc.setForeground(QColor("red"))
            self.tableValidacao.setItem(r, 2, item_enc)

            self.log_fn(
                f"  ✗ {div['item']}: "
                f"esperado '{div['esperado']}', "
                f"encontrado '{div['encontrado']}'",
                "aviso",
            )