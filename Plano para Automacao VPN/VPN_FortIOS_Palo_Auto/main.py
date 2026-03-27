
import sys
import os   

from qt_core import *
from gui.ui_window import VPNGenerator

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerador de Configurações VPN FortiOS e Palo Alto")
        self.setMinimumSize(900, 600)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

       # self.title_label = QLabel("Gerador de Configurações VPN FortiOS e Palo Alto")
       # self.title_label.setAlignment(Qt.AlignCenter)
       # self.layout.addWidget(self.title_label)

        self.vpn_generator = VPNGenerator()
        self.layout.addWidget(self.vpn_generator)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())