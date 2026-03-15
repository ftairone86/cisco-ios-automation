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

import sys
import os
import datetime

# Adiciona a pasta ui/ ao sys.path para localizar os ui_*.py
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "ui"))

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QTableWidgetItem, QFileDialog, QMessageBox, QHeaderView,
)
from PySide6.QtCore import Qt, Signal, QObject, QThread
from PySide6.QtGui  import QColor, QTextCursor

# ── Arquivos gerados pelo pyside6-uic (seus arquivos do Qt Designer) 
from ui_main_window  import Ui_MainWindow
from ui_conexao_page import Ui_ConexaoPage
from ui_vlans_page   import Ui_VlansPage
from ui_deploy_page  import Ui_DeployPage

# Backend de rede
from core import GerenciadorSwitch, VLANS_PADRAO, HOSTNAME_PADRAO



# SINAIS — ponte segura entre QThread e a GUI

class Sinais(QObject):
   
    log       = Signal(str, str)   # (mensagem, nível: info | ok | erro | aviso)
    concluido = Signal(object)     # resultado da operação
    progresso = Signal(int)        # 0-100 para a QProgressBar

# Worker não sabe que existe uma ProgressBar; ele apenas avisa que o progresso mudou. 
# A GUI decide o que fazer com essa informação

# WORKER — executa operação de rede em QThread separada


class WorkerRede(QThread):
    
    #Executa função(*args, **kwargs) em thread secundária.
    #Comunica resultados à interface exclusivamente via sinais.
    

    def __init__(self, fn, sinais: Sinais, *args, **kwargs):
        super().__init__()
        self.fn     = fn
        self.sinais = sinais
        self.args   = args
        self.kwargs = kwargs

    def run(self):
        #Ponto de entrada da thread. Emite o resultado via sinal.
        try:
            resultado = self.fn(*self.args, **self.kwargs)
            self.sinais.concluido.emit(resultado)
        except Exception as erro:
            self.sinais.log.emit(f"ERRO: {erro}", "erro")
            self.sinais.concluido.emit(None)



# ABA CONEXÃO — integrada ao Ui_ConexaoPage


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
        self._sinais = Sinais()
        self._sinais.log.connect(
            self.log_fn, Qt.ConnectionType.QueuedConnection
        )
        self._sinais.concluido.connect(
            self._apos_conectar, Qt.ConnectionType.QueuedConnection
        )
        self._sinais.log.emit("Iniciando conexão SSH...", "info")

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



# ABA VLANS — integrada ao Ui_VlansPage
#

class AbaVlans(QWidget, Ui_VlansPage):
    """
    Aba de gerenciamento de VLANs gerada pelo Qt Designer.

    Após setupUi(self), os seguintes widgets estão disponíveis:
        tableVlans       — tabela editável com ID e Nome das VLANs
        spinVid          — seletor de ID da nova VLAN (1–4094)
        lineVnome        — campo de nome da nova VLAN
        btnAdicionar     — insere VLAN na lista local
        btnRemoverLista  — remove linha selecionada da lista (sem afetar switch)
        btnRestaurar     — recarrega as VLANs padrão
        btnExcluirSwitch — envia 'no vlan <id>' ao switch

    A coluna "Nome" (índice 1) é configurada para expandir após setupUi(),
    pois essa propriedade não está disponível no Qt Designer.
    """

    def __init__(self, log_fn):
        super().__init__()
        self.setupUi(self)          # amarra o layout do Ui_VlansPage
        self.log_fn    = log_fn
        self._aba_conn = None       # injetado via set_aba_conn()
        self._worker   = None
        self._sinais   = None

        # Configuração pós-setupUi: coluna Nome expansível
        self.tableVlans.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self._wire()
        self._carregar_padrao()

    def set_aba_conn(self, aba_conn: AbaConexao):
        """
        Injeta a referência à AbaConexao para acessar o gerenciador ativo.
        Chamado pela JanelaPrincipal após criar ambas as abas.
        """
        self._aba_conn = aba_conn

    def _wire(self):
        """Liga os botões do Ui_VlansPage aos handlers desta classe."""
        self.btnAdicionar.clicked.connect(self._adicionar)
        self.btnRemoverLista.clicked.connect(self._remover_lista)
        self.btnRestaurar.clicked.connect(self._carregar_padrao)
        self.btnExcluirSwitch.clicked.connect(self._excluir_no_switch)

    # ── gerenciamento da tableVlans ───────────────────────────────────────────

    def _carregar_padrao(self):
        """Limpa a tableVlans e recarrega as VLANs padrão de core.VLANS_PADRAO."""
        self.tableVlans.setRowCount(0)
        for v in VLANS_PADRAO:
            self._inserir_linha(v["id"], v["nome"])

    def _inserir_linha(self, vid: int, nome: str):
        """Acrescenta uma linha na tableVlans com o ID centralizado."""
        linha = self.tableVlans.rowCount()
        self.tableVlans.insertRow(linha)

        item_id = QTableWidgetItem(str(vid))
        item_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tableVlans.setItem(linha, 0, item_id)
        self.tableVlans.setItem(linha, 1, QTableWidgetItem(nome))

    def _adicionar(self):
        """
        Lê spinVid e lineVnome, valida e insere nova linha na tableVlans.
        Bloqueia IDs duplicados antes de inserir.
        """
        vid  = self.spinVid.value()
        nome = self.lineVnome.text().strip().upper()

        if not nome:
            QMessageBox.warning(self, "Campo vazio", "Informe o nome da VLAN.")
            return

        # Verifica duplicidade de ID na tabela local
        for r in range(self.tableVlans.rowCount()):
            if self.tableVlans.item(r, 0).text() == str(vid):
                QMessageBox.warning(self, "ID duplicado",
                                    f"VLAN {vid} já existe na lista.")
                return

        self._inserir_linha(vid, nome)
        self.lineVnome.clear()

    def _remover_lista(self):
        """Remove a linha selecionada da tableVlans. Não afeta o switch."""
        linha = self.tableVlans.currentRow()
        if linha >= 0:
            self.tableVlans.removeRow(linha)

    # ── excluir VLAN no switch ────────────────────────────────────────────────

    def _excluir_no_switch(self):
        """
        Envia 'no vlan <id>' ao switch para a VLAN selecionada na tableVlans.

        Fluxo de execução:
          1. Verifica conexão ativa via _aba_conn.gerenciador
          2. Lê o ID e nome da linha selecionada na tableVlans
          3. Exibe diálogo de confirmação (operação irreversível)
          4. Executa core.excluir_vlan() em WorkerRede (thread separada)
          5. Remove a linha da tableVlans SOMENTE após sucesso no switch

        Atenção — captura de variáveis locais antes da closure:
          Variáveis como _linha, _vid, _btn são capturadas na thread principal
          ANTES de entrar na closure. Nunca acesse self.tableVlans ou qualquer
          widget de dentro de uma função que rode em QThread.
        """
        # 1. Verifica se há conexão ativa
        if not self._aba_conn or not self._aba_conn.gerenciador:
            QMessageBox.warning(self, "Sem conexão",
                                "Conecte ao switch primeiro na aba 'Conexão'.")
            return

        # 2. Lê linha selecionada
        linha = self.tableVlans.currentRow()
        if linha < 0:
            QMessageBox.information(self, "Nenhuma seleção",
                                    "Selecione uma VLAN na tabela.")
            return

        try:
            vid  = int(self.tableVlans.item(linha, 0).text())
            nome = self.tableVlans.item(linha, 1).text()
        except (ValueError, AttributeError):
            return

        # 3. Confirmação — irreversível
        resp = QMessageBox.question(
            self, "Confirmar exclusão",
            f"Excluir VLAN {vid} ({nome}) do switch?\n\n"
            f"Envia  'no vlan {vid}'  ao equipamento.\n"
            f"Esta operação não pode ser desfeita.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resp != QMessageBox.StandardButton.Yes:
            return

        # 4. Captura referências locais — widgets NÃO podem ser acessados
        #    de dentro do WorkerRede (QThread)
        _linha  = linha
        _vid    = vid
        _nome   = nome
        _btn    = self.btnExcluirSwitch
        _tabela = self.tableVlans

        self.btnExcluirSwitch.setEnabled(False)
        g = self._aba_conn.gerenciador

        self._sinais = Sinais()
        self._sinais.log.connect(
            self.log_fn, Qt.ConnectionType.QueuedConnection
        )

        def apos_excluir(resultado):
            """
            Slot executado na thread principal (via QueuedConnection).
            Atualiza o botão e a tabela com segurança.
            """
            _btn.setEnabled(True)
            if resultado is not None:
                self.log_fn(f"VLAN {_vid} ({_nome}) excluída do switch.", "ok")
                # 5. Remove da tabela local somente após sucesso no switch
                _tabela.removeRow(_linha)
            else:
                self.log_fn(f"Falha ao excluir VLAN {_vid}.", "erro")

        self._sinais.concluido.connect(
            apos_excluir, Qt.ConnectionType.QueuedConnection
        )

        self.log_fn(f"Excluindo VLAN {vid} ({nome}) no switch...", "info")
        self._worker = WorkerRede(g.excluir_vlan, self._sinais, vid)
        self._worker.start()

    # ── API pública ──────────────────────────────────────────────────────────

    def obter_vlans(self) -> list:
        """
        Retorna o conteúdo da tableVlans como lista de dicionários.
        Formato: [{"id": int, "nome": str}, ...]
        Usado pela AbaDeploy para enviar as VLANs ao switch.
        """
        vlans = []
        for r in range(self.tableVlans.rowCount()):
            try:
                vid  = int(self.tableVlans.item(r, 0).text())
                nome = self.tableVlans.item(r, 1).text().strip()
                if nome:
                    vlans.append({"id": vid, "nome": nome})
            except (ValueError, AttributeError):
                pass
        return vlans


# ════════════════════════════════════════════════════════════════════════════
# ABA DEPLOY — integrada ao Ui_DeployPage
# ════════════════════════════════════════════════════════════════════════════

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


# ════════════════════════════════════════════════════════════════════════════
# JANELA PRINCIPAL — integrada ao Ui_MainWindow
# ════════════════════════════════════════════════════════════════════════════

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
