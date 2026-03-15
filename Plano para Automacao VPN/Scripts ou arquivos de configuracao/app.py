import sys
import os
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTextEdit, QMessageBox, 
                             QGroupBox, QFormLayout, QFileDialog)
from PySide6.QtCore import Qt, Signal, QObject, QThread




class VPNGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Automação VPN IPSec & Firewall Policies')
        self.setGeometry(300, 300, 600, 750)
        
        main_layout = QVBoxLayout()
        
        # Grupo de Entradas de Dados
        input_group = QGroupBox("Parâmetros da Conexão VPN")
        form = QFormLayout()
        
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

        form.addRow("IP WAN Fortigate:", self.ip_forti)
        form.addRow("IP WAN Palo Alto:", self.ip_palo)
        form.addRow("Pre-Shared Key:", self.psk)
        form.addRow("Rede LAN (Forti):", self.lan_local)
        form.addRow("Rede LAN (Palo):", self.lan_remote)
        input_group.setLayout(form)

        # Botões de ação do click
        self.btn_generate = QPushButton('Gerar Scripts e Salvar Arquivos')
        self.btn_generate.setStyleSheet("background-color: #3e4452; color: white; height: 40px; border-radius: 5px;")
        self.btn_generate.clicked.connect(self.generate_configs)

        self.btn_send = QPushButton('Enviar para os Firewalls')
        self.btn_send.setStyleSheet("background-color: #fc4116; color: white; height: 32px; border-radius: 16px; padding: 5px 15px;")
        self.btn_send.clicked.connect(self.send_to_firewalls)

        # Área de Resultado
        self.output = QTextEdit()
        self.output.setReadOnly(True)

        main_layout.addWidget(input_group)
        main_layout.addWidget(self.btn_generate)
        main_layout.addWidget(self.btn_send)
        main_layout.addWidget(self.output)
        self.setLayout(main_layout)

    def send_to_firewalls(self):
        content = self.output.toPlainText().strip()
        if not content:
            QMessageBox.warning(self, "Atenção", "Gere as configurações antes de enviar!")
            return

        QMessageBox.information(
            self,
            "Enviar para os Firewalls",
            "Botão criado e exibido na interface.\n\nAinda falta implementar o envio (SSH/API) para Fortigate/Palo Alto.",
        )

    def generate_configs(self):
        # Captura os dados da interface
        f_ip = self.ip_forti.text()
        p_ip = self.ip_palo.text()
        key = self.psk.text()
        lan_f = self.lan_local.text()
        lan_p = self.lan_remote.text()

        # Validação simples
        if not all([f_ip, p_ip, key, lan_f, lan_p]):
            QMessageBox.warning(self, "Atenção", "Preencha todos os campos antes de gerar!")
            return

        # Template Fortigate
        forti_script = f"""
#      FORTIGATE CLI
config vpn ipsec phase1-interface
    edit "VPN-TO-PALO"
        set interface "wan1"
        set peertype any
        set proposal aes256-sha256
        set dhgrp 14
        set remote-gw {p_ip}
        set psksecret {key}
    next
end

config vpn ipsec phase2-interface
    edit "VPN-TO-PALO_P2"
        set phase1name "VPN-TO-PALO"
        set proposal aes256-sha256
        set dhgrp 14
        set src-subnet {lan_f}
        set dst-subnet {lan_p}
    next
end

config firewall policy
    edit 0
        set name "VPN_ALLOW_OUT"
        set srcintf "internal"
        set dstintf "VPN-TO-PALO"
        set srcaddr "all"
        set dstaddr "all"
        set action accept
        set schedule "always"
        set service "ALL"
    next
end
"""

        # Template Palo Alto
        palo_script = f"""
#      PALO ALTO 
set network ike gateway GW-TO-FORTI protocol ikev2 ike-crypto-profile default local-address {p_ip} protocol-common psk {key} peer-address {f_ip}
set network interface tunnel units tunnel.1 ip 169.255.20.65/30
set network ipsec tunnel VPN-TO-FORTI tunnel-interface tunnel.1 ak-ike-gateway GW-TO-FORTI ak-ipsec-crypto-profile default

set rulebase security rules "ALLOW-VPN-IN" from VPN to Trust source any destination any action allow
"""
        
        content = forti_script + "\n" + palo_script
        self.output.setText(content)

        # Permite escolher onde salvar o arquivo
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VPNGenerator()
    window.show()
    sys.exit(app.exec())
