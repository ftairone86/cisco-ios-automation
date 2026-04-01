# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'conexao_page.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFormLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QSpinBox, QVBoxLayout, QWidget)

class Ui_ConexaoPage(object):
    def setupUi(self, ConexaoPage):
        if not ConexaoPage.objectName():
            ConexaoPage.setObjectName(u"ConexaoPage")
        ConexaoPage.resize(680, 588)
        self.layoutRaiz = QVBoxLayout(ConexaoPage)
        self.layoutRaiz.setSpacing(16)
        self.layoutRaiz.setObjectName(u"layoutRaiz")
        self.layoutRaiz.setContentsMargins(20, 20, 20, 20)
        self.grpCredenciais = QGroupBox(ConexaoPage)
        self.grpCredenciais.setObjectName(u"grpCredenciais")
        font = QFont()
        font.setFamilies([u"Consolas"])
        font.setPointSize(10)
        font.setBold(True)
        self.grpCredenciais.setFont(font)
        self.formCredenciais = QFormLayout(self.grpCredenciais)
        self.formCredenciais.setObjectName(u"formCredenciais")
        self.formCredenciais.setLabelAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.formCredenciais.setHorizontalSpacing(12)
        self.formCredenciais.setVerticalSpacing(12)
        self.formCredenciais.setContentsMargins(12, 16, 12, 16)
        self.lblHost = QLabel(self.grpCredenciais)
        self.lblHost.setObjectName(u"lblHost")

        self.formCredenciais.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lblHost)

        self.lineHost = QLineEdit(self.grpCredenciais)
        self.lineHost.setObjectName(u"lineHost")

        self.formCredenciais.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lineHost)

        self.lblPorta = QLabel(self.grpCredenciais)
        self.lblPorta.setObjectName(u"lblPorta")

        self.formCredenciais.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lblPorta)

        self.spinPorta = QSpinBox(self.grpCredenciais)
        self.spinPorta.setObjectName(u"spinPorta")
        self.spinPorta.setMinimum(1)
        self.spinPorta.setMaximum(65535)
        self.spinPorta.setValue(22)

        self.formCredenciais.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinPorta)

        self.lblUsuario = QLabel(self.grpCredenciais)
        self.lblUsuario.setObjectName(u"lblUsuario")

        self.formCredenciais.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lblUsuario)

        self.lineUsuario = QLineEdit(self.grpCredenciais)
        self.lineUsuario.setObjectName(u"lineUsuario")

        self.formCredenciais.setWidget(2, QFormLayout.ItemRole.FieldRole, self.lineUsuario)

        self.lblSenha = QLabel(self.grpCredenciais)
        self.lblSenha.setObjectName(u"lblSenha")

        self.formCredenciais.setWidget(3, QFormLayout.ItemRole.LabelRole, self.lblSenha)

        self.lineSenha = QLineEdit(self.grpCredenciais)
        self.lineSenha.setObjectName(u"lineSenha")
        self.lineSenha.setEchoMode(QLineEdit.EchoMode.Password)

        self.formCredenciais.setWidget(3, QFormLayout.ItemRole.FieldRole, self.lineSenha)

        self.lblSecret = QLabel(self.grpCredenciais)
        self.lblSecret.setObjectName(u"lblSecret")

        self.formCredenciais.setWidget(4, QFormLayout.ItemRole.LabelRole, self.lblSecret)

        self.lineSecret = QLineEdit(self.grpCredenciais)
        self.lineSecret.setObjectName(u"lineSecret")
        self.lineSecret.setEchoMode(QLineEdit.EchoMode.Password)

        self.formCredenciais.setWidget(4, QFormLayout.ItemRole.FieldRole, self.lineSecret)


        self.layoutRaiz.addWidget(self.grpCredenciais)

        self.lblStatus = QLabel(ConexaoPage)
        self.lblStatus.setObjectName(u"lblStatus")
        font1 = QFont()
        font1.setFamilies([u"Consolas"])
        font1.setPointSize(11)
        font1.setBold(True)
        self.lblStatus.setFont(font1)
        self.lblStatus.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layoutRaiz.addWidget(self.lblStatus)

        self.layoutBotoes = QHBoxLayout()
        self.layoutBotoes.setObjectName(u"layoutBotoes")
        self.btnConectar = QPushButton(ConexaoPage)
        self.btnConectar.setObjectName(u"btnConectar")

        self.layoutBotoes.addWidget(self.btnConectar)

        self.btnDesconectar = QPushButton(ConexaoPage)
        self.btnDesconectar.setObjectName(u"btnDesconectar")
        self.btnDesconectar.setEnabled(False)

        self.layoutBotoes.addWidget(self.btnDesconectar)


        self.layoutRaiz.addLayout(self.layoutBotoes)

        self.Espaco = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.layoutRaiz.addItem(self.Espaco)


        self.retranslateUi(ConexaoPage)

        QMetaObject.connectSlotsByName(ConexaoPage)
    # setupUi

    def retranslateUi(self, ConexaoPage):
        ConexaoPage.setWindowTitle(QCoreApplication.translate("ConexaoPage", u"Conex\u00e3o SSH", None))
        self.grpCredenciais.setTitle(QCoreApplication.translate("ConexaoPage", u"Credenciais SSH \u2014 Switch Cisco", None))
        self.lblHost.setText(QCoreApplication.translate("ConexaoPage", u"IP / Host:", None))
        self.lineHost.setText(QCoreApplication.translate("ConexaoPage", u"172.20.16.2", None))
        self.lineHost.setPlaceholderText(QCoreApplication.translate("ConexaoPage", u"IP ou hostname do switch", None))
        self.lblPorta.setText(QCoreApplication.translate("ConexaoPage", u"Porta SSH:", None))
        self.lblUsuario.setText(QCoreApplication.translate("ConexaoPage", u"Usu\u00e1rio:", None))
        self.lineUsuario.setText(QCoreApplication.translate("ConexaoPage", u"admin", None))
        self.lblSenha.setText(QCoreApplication.translate("ConexaoPage", u"Senha:", None))
        self.lineSenha.setPlaceholderText(QCoreApplication.translate("ConexaoPage", u"Senha SSH", None))
        self.lblSecret.setText(QCoreApplication.translate("ConexaoPage", u"Enable Secret:", None))
        self.lineSecret.setPlaceholderText(QCoreApplication.translate("ConexaoPage", u"Deixe vazio se n\u00e3o usar", None))
        self.lblStatus.setText(QCoreApplication.translate("ConexaoPage", u"\u25cf DESCONECTADO", None))
        self.btnConectar.setText(QCoreApplication.translate("ConexaoPage", u" \U0001f517 CONECTAR", None))
        self.btnDesconectar.setText(QCoreApplication.translate("ConexaoPage", u"\U0001f51a  DESCONECTAR", None))
    # retranslateUi

