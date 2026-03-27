import os
from envio_thread import SendWorker
from qt_core import *
from send import FirewallSSHConfig
from conexao_thread import ConnectionWorker
from envio_thread import SendWorker
from teste_conexao_thread import TunnelTestWorker

class VPNGenerator(QWidget):
    """Janela principal.

    A UI é composta por três abas:
    - Aba 1 "Geração de Config": parâmetros da VPN + script gerado
    - Aba 2 "Conexão & Envio": credenciais SSH, opções de envio, teste de túnel
    - Aba 3 "Logs": saída de eventos e operações

    Fluxo:
    - `generate_configs()` cria os blocos e popula `script_output`.
    - `test_connection(device)` cria um `ConnectionWorker` e atualiza o status.
    - `send_to_firewalls()` cria um `SendWorker` e registra o resultado.

    Detalhe de correlação:
    - `ConnectionWorker` e `SendWorker` usam as classes de `send.py`.
    - O status exibido na GUI vem de sinais emitidos pelos workers.
    """

    def __init__(self):
        super().__init__()
        self._active_thread: QThread | None = None
        self.initUI()

    def initUI(self):
        """Monta a interface em abas e conecta os botões aos handlers."""
        self.setWindowTitle("Automação VPN IPSec & Firewall Policies")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(6)

        # ── QTabWidget principal ──────────────────────────────────────────────
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        self.tabs.addTab(self._build_tab_config(), "  Geração de Config  ")
        self.tabs.addTab(self._build_tab_conexao(), "  Conexão & Envio  ")
        self.tabs.addTab(self._build_tab_logs(), "  Logs  ")

        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

    # ── Aba 1: Parâmetros da VPN + Script gerado ──────────────────────────────
    def _build_tab_config(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Parâmetros
        input_group = QGroupBox("Parâmetros da Conexão VPN")
        form = QFormLayout()
        form.setVerticalSpacing(8)

        self.ip_forti = QLineEdit()
        self.ip_forti.setPlaceholderText("Digite o IP da WAN do Fortigate")

        self.ip_palo = QLineEdit()
        self.ip_palo.setPlaceholderText("Digite o IP da WAN do Palo Alto")

        self.psk = QLineEdit()
        self.psk.setPlaceholderText("Chave Secreta da VPN")
        self.psk.setEchoMode(QLineEdit.Password)

        self.lan_local = QLineEdit()
        self.lan_local.setPlaceholderText("Digite o IP da Rede LAN (Fortigate)")

        self.lan_remote = QLineEdit()
        self.lan_remote.setPlaceholderText("Digite o IP da Rede LAN (Palo Alto)")

              # Campos adicionais
        self.tunnel_name = QLineEdit()
        self.tunnel_name.setText("VPN-TO-PALO")
        self.tunnel_name.setPlaceholderText("Nome do Tunnel")

        self.encryption = QComboBox()
        self.encryption.addItems(["aes128", "aes192", "aes256"])
        self.encryption.setCurrentText("aes256")

        self.hashing = QComboBox()
        self.hashing.addItems(["sha1", "sha256", "sha384", "sha512"])
        self.hashing.setCurrentText("sha256")

        self.dh_group = QComboBox()
        self.dh_group.addItems(["2", "5", "14", "15", "16"])
        self.dh_group.setCurrentText("14")

        self.lifetime = QSpinBox()
        self.lifetime.setValue(3600)
        self.lifetime.setSuffix(" segundos")
        self.lifetime.setRange(300, 86400)

        form.addRow("IP WAN Fortigate:", self.ip_forti)
        form.addRow("IP WAN Palo Alto:", self.ip_palo)
        form.addRow("Pre-Shared Key:", self.psk)
        form.addRow("Rede LAN (Forti):", self.lan_local)
        form.addRow("Rede LAN (Palo):", self.lan_remote)
        form.addRow("Criptografia:", self.encryption)
        form.addRow("Hash/Integridade:", self.hashing)
        form.addRow("DH Group:", self.dh_group)
        form.addRow("Lifetime SA:", self.lifetime)
        input_group.setLayout(form)

        # Botão gerar
        self.btn_generate = QPushButton("Gerar Scripts e Salvar Arquivos")
        self.btn_generate.setStyleSheet(
            "background-color: #3e4452; color: white; height: 40px; border-radius: 5px; font-weight: bold;"
        )
        self.btn_generate.clicked.connect(self.generate_configs)

        # Script gerado
        script_group = QGroupBox("Configuração gerada")
        script_layout = QVBoxLayout()
        self.script_output = QTextEdit()
        self.script_output.setReadOnly(True)
        self.script_output.setFont(QFont("Monospace", 10))
        script_layout.addWidget(self.script_output)
        script_group.setLayout(script_layout)

        layout.addWidget(input_group)
        layout.addWidget(self.btn_generate)
        layout.addWidget(script_group, stretch=1)
        tab.setLayout(layout)
        return tab

    # ── Aba 2: Conexão SSH + Envio + Teste de Túnel ───────────────────────────
    def _build_tab_conexao(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Credenciais lado a lado
        creds_layout = QHBoxLayout()
        creds_layout.setSpacing(10)
        creds_layout.addWidget(self._build_forti_box())
        creds_layout.addWidget(self._build_palo_box())

        # Opções de envio
        opts_group = QGroupBox("Opções de Envio")
        opts_row = QHBoxLayout()
        self.chk_commit_palo = QCheckBox("Commit no Palo Alto")
        self.chk_commit_palo.setChecked(True)
        self.chk_simulacao = QCheckBox("Simulação (não conecta)")
        opts_row.addWidget(self.chk_commit_palo)
        opts_row.addWidget(self.chk_simulacao)
        opts_row.addStretch()
        opts_group.setLayout(opts_row)

        # Botão enviar
        self.btn_send = QPushButton("Enviar para os Firewalls")
        self.btn_send.setStyleSheet(
            "background-color: #c0392b; color: white; height: 40px; border-radius: 5px; font-weight: bold;"
        )
        self.btn_send.clicked.connect(self.send_to_firewalls)

        # Teste do túnel IPSec
        ipsec_group = self._build_ipsec_group()

        layout.addLayout(creds_layout)
        layout.addWidget(opts_group)
        layout.addWidget(self.btn_send)
        layout.addWidget(ipsec_group)
        layout.addStretch()
        tab.setLayout(layout)
        return tab

    def _build_forti_box(self) -> QGroupBox:
        forti_box = QGroupBox("Fortigate")
        forti_form = QFormLayout()
        forti_form.setVerticalSpacing(6)

        self.forti_host = QLineEdit()
        self.forti_host.setPlaceholderText("Host/IP de gerenciamento (SSH)")
        self.forti_user = QLineEdit()
        self.forti_user.setPlaceholderText("Usuário")
        self.forti_pass = QLineEdit()
        self.forti_pass.setPlaceholderText("Senha")
        self.forti_pass.setEchoMode(QLineEdit.Password)
        self.forti_port = QSpinBox()
        self.forti_port.setRange(1, 65535)
        self.forti_port.setValue(22)

        self.lbl_status_forti = QLabel("Status: desconectado")
        self.lbl_status_forti.setStyleSheet("color: #b00020;")
        self.btn_test_forti = QPushButton("Testar conexão")
        self.btn_test_forti.clicked.connect(lambda: self.test_connection("fortigate"))

        self.lbl_tunnel_forti = QLabel("Túnel: desconhecido")
        self.lbl_tunnel_forti.setStyleSheet("color: #616161;")

        forti_form.addRow("Host:", self.forti_host)
        forti_form.addRow("Usuário:", self.forti_user)
        forti_form.addRow("Senha:", self.forti_pass)
        forti_form.addRow("Porta:", self.forti_port)

        btn_status_row = QHBoxLayout()
        btn_status_row.addWidget(self.btn_test_forti)
        btn_status_row.addWidget(self.lbl_status_forti, 1, Qt.AlignRight)
        btn_w = QWidget()
        btn_w.setLayout(btn_status_row)
        forti_form.addRow("", btn_w)
        forti_form.addRow("", self.lbl_tunnel_forti)

        forti_box.setLayout(forti_form)
        return forti_box

    def _build_palo_box(self) -> QGroupBox:
        palo_box = QGroupBox("Palo Alto")
        palo_form = QFormLayout()
        palo_form.setVerticalSpacing(6)

        self.palo_host = QLineEdit()
        self.palo_host.setPlaceholderText("Host/IP de gerenciamento (SSH)")
        self.palo_user = QLineEdit()
        self.palo_user.setPlaceholderText("Usuário")
        self.palo_pass = QLineEdit()
        self.palo_pass.setPlaceholderText("Senha")
        self.palo_pass.setEchoMode(QLineEdit.Password)
        self.palo_port = QSpinBox()
        self.palo_port.setRange(1, 65535)
        self.palo_port.setValue(22)

        self.lbl_status_palo = QLabel("Status: desconectado")
        self.lbl_status_palo.setStyleSheet("color: #b00020;")
        self.btn_test_palo = QPushButton("Testar conexão")
        self.btn_test_palo.clicked.connect(lambda: self.test_connection("paloalto"))

        self.lbl_tunnel_palo = QLabel("Túnel: desconhecido")
        self.lbl_tunnel_palo.setStyleSheet("color: #616161;")

        palo_form.addRow("Host:", self.palo_host)
        palo_form.addRow("Usuário:", self.palo_user)
        palo_form.addRow("Senha:", self.palo_pass)
        palo_form.addRow("Porta:", self.palo_port)

        btn_status_row = QHBoxLayout()
        btn_status_row.addWidget(self.btn_test_palo)
        btn_status_row.addWidget(self.lbl_status_palo, 1, Qt.AlignRight)
        btn_w = QWidget()
        btn_w.setLayout(btn_status_row)
        palo_form.addRow("", btn_w)
        palo_form.addRow("", self.lbl_tunnel_palo)

        palo_box.setLayout(palo_form)
        return palo_box

    def _build_ipsec_group(self) -> QGroupBox:
        ipsec_group = QGroupBox("Teste do túnel IPSec")
        ipsec_form = QFormLayout()
        ipsec_form.setVerticalSpacing(6)

        self.forti_ping_dest = QLineEdit()
        self.forti_ping_dest.setPlaceholderText("Destino para ping via túnel (ex: host na rede remota)")
        self.forti_ping_source = QLineEdit()
        self.forti_ping_source.setPlaceholderText("Origem do ping (opcional; ajuda a amarrar ao túnel)")

        self.palo_ping_dest = QLineEdit()
        self.palo_ping_dest.setPlaceholderText("Destino para ping via túnel (ex: host na rede remota)")
        self.palo_ping_source = QLineEdit()
        self.palo_ping_source.setPlaceholderText("Origem do ping (opcional)")

        ipsec_form.addRow("Ping Forti (dest):", self.forti_ping_dest)
        ipsec_form.addRow("Ping Forti (src):", self.forti_ping_source)
        ipsec_form.addRow("Ping Palo (dest):", self.palo_ping_dest)
        ipsec_form.addRow("Ping Palo (src):", self.palo_ping_source)

        self.btn_test_tunnel = QPushButton("Testar túnel IPSec")
        self.btn_test_tunnel.clicked.connect(self.test_ipsec_tunnel)
        ipsec_form.addRow("", self.btn_test_tunnel)

        ipsec_group.setLayout(ipsec_form)
        return ipsec_group

    # ── Função Aba 3: Logs ───────────────────────────────────────────────────────────
    def _build_tab_logs(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFont(QFont("Monospace", 10))
        self.log_output.setPlaceholderText("Eventos de conexão e saída do envio aparecem aqui.")

        btn_clear = QPushButton("Limpar Logs")
        btn_clear.setFixedWidth(120)
        btn_clear.clicked.connect(self.log_output.clear)

        layout.addWidget(self.log_output, stretch=1)
        layout.addWidget(btn_clear, alignment=Qt.AlignRight)
        tab.setLayout(layout)
        return tab

    # ── Helpers internos ──────────────────────────────────────────────────────

    def _append_log(self, text: str) -> None:
        """Acrescenta uma linha no painel de logs."""
        self.log_output.append(text)

    def _set_status_label(self, device: str, connected: bool, detail: str) -> None:
        if device == "fortigate":
            label = self.lbl_status_forti
        elif device == "paloalto":
            label = self.lbl_status_palo
        else:
            return
        label.setText(f"Status: {'conectado' if connected else 'desconectado'} ({detail})")
        label.setStyleSheet("color: #1b5e20;" if connected else "color: #b00020;")

    def _set_tunnel_label(self, device: str, state: int, detail: str) -> None:
        if device == "fortigate":
            label = self.lbl_tunnel_forti
        elif device == "paloalto":
            label = self.lbl_tunnel_palo
        else:
            return

        if state == 1:
            label.setText(f"Túnel: UP ({detail})")
            label.setStyleSheet("color: #1b5e20;")
        elif state == 0:
            label.setText(f"Túnel: DOWN ({detail})")
            label.setStyleSheet("color: #b00020;")
        else:
            label.setText(f"Túnel: desconhecido ({detail})")
            label.setStyleSheet("color: #616161;")

    def _build_cfg(self, device: str) -> FirewallSSHConfig | None:
        if device == "fortigate":
            host = self.forti_host.text().strip()
            user = self.forti_user.text().strip()
            passwd = self.forti_pass.text()
            port = int(self.forti_port.value())
        elif device == "paloalto":
            host = self.palo_host.text().strip()
            user = self.palo_user.text().strip()
            passwd = self.palo_pass.text()
            port = int(self.palo_port.value())
        else:
            return None

        if not (host and user and passwd):
            return None

        return FirewallSSHConfig(host=host, username=user, password=passwd, port=port)
    
    #Função para habilitar/desabilitar botões durante operações de background, evitando múltiplas execuções simultâneas.

    def _set_busy(self, busy: bool) -> None:
        self.btn_send.setEnabled(not busy)
        self.btn_generate.setEnabled(not busy)
        self.btn_test_forti.setEnabled(not busy)
        self.btn_test_palo.setEnabled(not busy)
        self.btn_test_tunnel.setEnabled(not busy)

        #Start no processso para rodar em backgroud

    def _start_worker(self, worker: QObject, *, on_finished) -> None:
        if self._active_thread is not None:
            QMessageBox.warning(self, "Atenção", "Já existe uma operação em andamento.")
            return

        thread = QThread()
        self._active_thread = thread

        worker.moveToThread(thread)
        thread.started.connect(worker.run)  # type: ignore[attr-defined]

        worker.finished.connect(lambda *args: thread.quit())  # type: ignore[attr-defined]
        worker.finished.connect(lambda *args: worker.deleteLater())  # type: ignore[attr-defined]
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._on_thread_done)

        worker.finished.connect(on_finished)  # type: ignore[attr-defined]

        thread.start()

    def _on_thread_done(self) -> None:
        self._active_thread = None
        self._set_busy(False)

    # ── Handlers de ação ─────────────────────────────────────────────────────

    def test_connection(self, device: str) -> None:
        cfg = self._build_cfg(device)
        if not cfg:
            QMessageBox.warning(self, "Atenção", f"Preencha host/usuário/senha do {device} para testar.")
            return

        simulacao = bool(self.chk_simulacao.isChecked())
        self._set_busy(True)
        self._append_log(f"==== Teste de conexão: {device} ====")
        # Redireciona para aba de Logs para acompanhar
        self.tabs.setCurrentIndex(2)

        worker = ConnectionWorker(device, cfg, simulacao=simulacao)
        worker.log.connect(self._append_log)
        worker.status.connect(self._set_status_label)

        self._start_worker(worker, on_finished=lambda: self._append_log(f"==== Fim teste: {device} ===="))

        #Tenta montar as credenciais SSH dos dois firewalls chamando _build_cfg para cada um build_cfg retorna 
        #None se host/usuário/senha não estiverem preenchidos
        #Se ambos retornarem None (nenhum firewall tem credenciais), exibe um aviso e aborta o teste do túnel

    def test_ipsec_tunnel(self) -> None:
        forti_cfg = self._build_cfg("fortigate")
        palo_cfg = self._build_cfg("paloalto")
        if not forti_cfg and not palo_cfg:
            QMessageBox.warning(
                self,
                "Atenção","Informe as credenciais de pelo menos um firewall antes de testar o túnel.",
            )
            return

        simulacao = bool(self.chk_simulacao.isChecked())

        forti_ping_dest = self.forti_ping_dest.text().strip() or None
        forti_ping_source = self.forti_ping_source.text().strip() or None
        palo_ping_dest = self.palo_ping_dest.text().strip() or None
        palo_ping_source = self.palo_ping_source.text().strip() or None

        self._set_busy(True)
        self._append_log("==== Teste do túnel IPSec ====")
        self.tabs.setCurrentIndex(2)

        worker = TunnelTestWorker(
            forti_cfg=forti_cfg,
            palo_cfg=palo_cfg,
            simulacao=simulacao,
            forti_ping_dest=forti_ping_dest,
            forti_ping_source=forti_ping_source,
            palo_ping_dest=palo_ping_dest,
            palo_ping_source=palo_ping_source,
        )
        worker.log.connect(self._append_log)
        worker.tunnel_status.connect(self._set_tunnel_label)

        def _done(resultados: dict) -> None:
            self._append_log("==== Resultado do teste IPSec ====")
            for dev in ("fortigate", "paloalto"):
                info = resultados.get(dev)
                if not isinstance(info, dict):
                    continue
                self._append_log(f"----- {dev.upper()} -----")
                saidas = info.get("saidas")
                if isinstance(saidas, dict):
                    for k, v in saidas.items():
                        self._append_log(f"[{dev}] {k}:")
                        self._append_log(str(v).rstrip())
            if "info" in resultados:
                self._append_log(str(resultados["info"]))
            self._append_log("==== Fim do teste IPSec ====")

        self._start_worker(worker, on_finished=_done)

    def send_to_firewalls(self):
        content = self.script_output.toPlainText().strip()
        if not content:
            QMessageBox.warning(self, "Atenção", "Gere as configurações antes de enviar!")
            return

        forti_cfg = self._build_cfg("fortigate")
        palo_cfg = self._build_cfg("paloalto")
        if not forti_cfg and not palo_cfg:
            QMessageBox.warning(
                self,
                "Atenção",
                "Informe as credenciais de pelo menos um firewall (Fortigate e/ou Palo Alto) antes de enviar.",
            )
            return

        simulacao = bool(self.chk_simulacao.isChecked())
        commit_palo = bool(self.chk_commit_palo.isChecked())

        self._set_busy(True)
        self._append_log("==== Envio para os firewalls ====")
        self.tabs.setCurrentIndex(2)

        worker = SendWorker(
            content,
            forti_cfg,
            palo_cfg,
            commit_palo=commit_palo,
            simulacao=simulacao,
        )
        worker.log.connect(self._append_log)
        worker.status.connect(self._set_status_label)

        def _done(resultados: dict) -> None:
            self._append_log("==== Resultado ====")
            for k, v in resultados.items():
                self._append_log(f"----- {k.upper()} -----")
                self._append_log(str(v).rstrip())
            self._append_log("==== Fim do envio ====")

        self._start_worker(worker, on_finished=_done)

    def generate_configs(self):
        f_ip = self.ip_forti.text()
        p_ip = self.ip_palo.text()
        key = self.psk.text()
        lan_f = self.lan_local.text()
        lan_p = self.lan_remote.text()
        tunnel = self.tunnel_name.text().strip()
        enc = self.encryption.currentText()
        hash_alg = self.hashing.currentText()
        dh = self.dh_group.currentText()
        lifetime = self.lifetime.value()

        if not all([f_ip, p_ip, key, lan_f, lan_p]):
            QMessageBox.warning(self, "Atenção", "Preencha todos os campos antes de gerar!")
            return

         # Template Fortigate
        forti_script = f"""
# ========================================
# FORTIGATE - VPN IPSec Configuration
# ========================================

config vpn ipsec phase1-interface
    edit "{tunnel}"
        set interface "wan1"
        set peertype any
        set proposal {enc}-{hash_alg}
        set dhgrp {dh}
        set remote-gw {p_ip}
        set psksecret {key}
        set lifetime {lifetime}
    next
end

config vpn ipsec phase2-interface
    edit "{tunnel}_P2"
        set phase1name "{tunnel}"
        set proposal {enc}-{hash_alg}
        set dhgrp {dh}
        set src-subnet {lan_f}
        set dst-subnet {lan_p}
        set lifetime {lifetime}
    next
end

config firewall policy
    edit 0
        set name "VPN_ALLOW_OUT"
        set srcintf "internal"
        set dstintf "{tunnel}"
        set srcaddr "all"
        set dstaddr "all"
        set action accept
        set schedule "always"
        set service "ALL"
        set logtraffic all
    next
end

# Backup config
execute backup config flash forti_backup.conf
"""

        # Template Palo Alto
        palo_script = f"""
# ========================================
# PALO ALTO - IKE and IPSec Configuration
# ========================================

set network ike crypto ike-crypto-profiles default dh-groups [ group{dh} ]
set network ike crypto ike-crypto-profiles default encryptions [ {enc} ]
set network ike crypto ike-crypto-profiles default hash-algorithms [ {hash_alg} ]

set network ike gateway GW-TO-FORTI protocol ikev2 ike-crypto-profile default local-address {p_ip}
set network ike gateway GW-TO-FORTI protocol-common psk {key}
set network ike gateway GW-TO-FORTI protocol-common lifetime seconds {lifetime}
set network ike gateway GW-TO-FORTI peer-address {f_ip}

set network ipsec crypto ipsec-crypto-profiles default dh-groups [ group{dh} ]
set network ipsec crypto ipsec-crypto-profiles default encryptions [ {enc} ]
set network ipsec crypto ipsec-crypto-profiles default hash-algorithms [ {hash_alg} ]

set network interface tunnel units tunnel.1 ip 169.255.20.65/30
set network ipsec tunnel {tunnel} tunnel-interface tunnel.1 ak-ike-gateway GW-TO-FORTI
set network ipsec tunnel {tunnel} ak-ipsec-crypto-profile default
set network ipsec tunnel {tunnel} lifetime seconds {lifetime}

set rulebase security rules "ALLOW-VPN-IN" from VPN to Trust
set rulebase security rules "ALLOW-VPN-IN" source any
set rulebase security rules "ALLOW-VPN-IN" destination any
set rulebase security rules "ALLOW-VPN-IN" action allow
set rulebase security rules "ALLOW-VPN-IN" log-setting "Traffic Logs"

# Commit configuration
commit
"""

        content = forti_script + "\n" + palo_script
        self.script_output.setText(content)

        try:
            default_path = os.path.join(os.getcwd(), "config_vpn_gerada.txt")
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Salvar configuração VPN",
                default_path,
                "Arquivo de texto (*.txt);;Todos os arquivos (*)",
            )
            if not filename:
                QMessageBox.information(self, "Cancelado", "Salvamento cancelado.")
                return

            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)

            QMessageBox.information(self, "Sucesso", f"Arquivo salvo em:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "Deu erro", f"Não foi possível salvar: {e}")
