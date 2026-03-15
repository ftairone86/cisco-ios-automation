# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'deploy_page.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QFormLayout, QGridLayout,
    QGroupBox, QHeaderView, QLabel, QLineEdit,
    QProgressBar, QPushButton, QSizePolicy, QSpacerItem,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_DeployPage(object):
    def setupUi(self, DeployPage):
        if not DeployPage.objectName():
            DeployPage.setObjectName(u"DeployPage")
        DeployPage.resize(680, 700)
        self.layoutRaiz = QVBoxLayout(DeployPage)
        self.layoutRaiz.setSpacing(16)
        self.layoutRaiz.setObjectName(u"layoutRaiz")
        self.layoutRaiz.setContentsMargins(20, 20, 20, 20)
        self.grpOpcoes = QGroupBox(DeployPage)
        self.grpOpcoes.setObjectName(u"grpOpcoes")
        self.formOpcoes = QFormLayout(self.grpOpcoes)
        self.formOpcoes.setObjectName(u"formOpcoes")
        self.formOpcoes.setVerticalSpacing(10)
        self.formOpcoes.setContentsMargins(12, 16, 12, 16)
        self.lblHostname = QLabel(self.grpOpcoes)
        self.lblHostname.setObjectName(u"lblHostname")

        self.formOpcoes.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lblHostname)

        self.lineHostname = QLineEdit(self.grpOpcoes)
        self.lineHostname.setObjectName(u"lineHostname")

        self.formOpcoes.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lineHostname)

        self.lblChkHn = QLabel(self.grpOpcoes)
        self.lblChkHn.setObjectName(u"lblChkHn")

        self.formOpcoes.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lblChkHn)

        self.chkHostname = QCheckBox(self.grpOpcoes)
        self.chkHostname.setObjectName(u"chkHostname")
        self.chkHostname.setChecked(True)

        self.formOpcoes.setWidget(1, QFormLayout.ItemRole.FieldRole, self.chkHostname)

        self.lblChkSalvar = QLabel(self.grpOpcoes)
        self.lblChkSalvar.setObjectName(u"lblChkSalvar")

        self.formOpcoes.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lblChkSalvar)

        self.chkSalvar = QCheckBox(self.grpOpcoes)
        self.chkSalvar.setObjectName(u"chkSalvar")
        self.chkSalvar.setChecked(True)

        self.formOpcoes.setWidget(2, QFormLayout.ItemRole.FieldRole, self.chkSalvar)

        self.lblChkValidar = QLabel(self.grpOpcoes)
        self.lblChkValidar.setObjectName(u"lblChkValidar")

        self.formOpcoes.setWidget(3, QFormLayout.ItemRole.LabelRole, self.lblChkValidar)

        self.chkValidar = QCheckBox(self.grpOpcoes)
        self.chkValidar.setObjectName(u"chkValidar")
        self.chkValidar.setChecked(True)

        self.formOpcoes.setWidget(3, QFormLayout.ItemRole.FieldRole, self.chkValidar)


        self.layoutRaiz.addWidget(self.grpOpcoes)

        self.progressBar = QProgressBar(DeployPage)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(0)
        self.progressBar.setProperty(u"fixedHeight", 18)

        self.layoutRaiz.addWidget(self.progressBar)

        self.grpAcoes = QGroupBox(DeployPage)
        self.grpAcoes.setObjectName(u"grpAcoes")
        self.gridAcoes = QGridLayout(self.grpAcoes)
        self.gridAcoes.setSpacing(10)
        self.gridAcoes.setObjectName(u"gridAcoes")
        self.gridAcoes.setContentsMargins(12, 16, 12, 16)
        self.btnDeploy = QPushButton(self.grpAcoes)
        self.btnDeploy.setObjectName(u"btnDeploy")

        self.gridAcoes.addWidget(self.btnDeploy, 0, 0, 1, 2)

        self.btnSalvar = QPushButton(self.grpAcoes)
        self.btnSalvar.setObjectName(u"btnSalvar")

        self.gridAcoes.addWidget(self.btnSalvar, 1, 0, 1, 1)

        self.btnBackup = QPushButton(self.grpAcoes)
        self.btnBackup.setObjectName(u"btnBackup")

        self.gridAcoes.addWidget(self.btnBackup, 1, 1, 1, 1)

        self.btnValidar = QPushButton(self.grpAcoes)
        self.btnValidar.setObjectName(u"btnValidar")

        self.gridAcoes.addWidget(self.btnValidar, 2, 0, 1, 2)


        self.layoutRaiz.addWidget(self.grpAcoes)

        self.grpValidacao = QGroupBox(DeployPage)
        self.grpValidacao.setObjectName(u"grpValidacao")
        self.layoutValidacao = QVBoxLayout(self.grpValidacao)
        self.layoutValidacao.setSpacing(8)
        self.layoutValidacao.setObjectName(u"layoutValidacao")
        self.layoutValidacao.setContentsMargins(12, 12, 12, 12)
        self.lblResultadoVal = QLabel(self.grpValidacao)
        self.lblResultadoVal.setObjectName(u"lblResultadoVal")
        font = QFont()
        font.setFamilies([u"Consolas"])
        font.setPointSize(10)
        font.setBold(True)
        self.lblResultadoVal.setFont(font)
        self.lblResultadoVal.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layoutValidacao.addWidget(self.lblResultadoVal)

        self.tableValidacao = QTableWidget(self.grpValidacao)
        if (self.tableValidacao.columnCount() < 3):
            self.tableValidacao.setColumnCount(3)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableValidacao.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableValidacao.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tableValidacao.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        self.tableValidacao.setObjectName(u"tableValidacao")
        self.tableValidacao.setColumnCount(3)

        self.layoutValidacao.addWidget(self.tableValidacao)


        self.layoutRaiz.addWidget(self.grpValidacao)

        self.spacerItem = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.layoutRaiz.addItem(self.spacerItem)


        self.retranslateUi(DeployPage)

        QMetaObject.connectSlotsByName(DeployPage)
    # setupUi

    def retranslateUi(self, DeployPage):
        DeployPage.setWindowTitle(QCoreApplication.translate("DeployPage", u"Deploy", None))
        self.grpOpcoes.setTitle(QCoreApplication.translate("DeployPage", u"Op\u00e7\u00f5es de Configura\u00e7\u00e3o", None))
        self.lblHostname.setText(QCoreApplication.translate("DeployPage", u"Hostname:", None))
        self.lineHostname.setText(QCoreApplication.translate("DeployPage", u"SWITCH_AUTOMATIZADO", None))
        self.lblChkHn.setText("")
        self.chkHostname.setText(QCoreApplication.translate("DeployPage", u"Aplicar hostname", None))
        self.lblChkSalvar.setText("")
        self.chkSalvar.setText(QCoreApplication.translate("DeployPage", u"Salvar na NVRAM ap\u00f3s deploy", None))
        self.lblChkValidar.setText("")
        self.chkValidar.setText(QCoreApplication.translate("DeployPage", u"Validar configura\u00e7\u00e3o ap\u00f3s deploy", None))
        self.grpAcoes.setTitle(QCoreApplication.translate("DeployPage", u"A\u00e7\u00f5es", None))
        self.btnDeploy.setText(QCoreApplication.translate("DeployPage", u"\U0001f4bb APLICAR CONFIGURA\U000000c7\U000000d5ES", None))
        self.btnSalvar.setText(QCoreApplication.translate("DeployPage", u"\U0001f4be  Salvar", None))
        self.btnBackup.setText(QCoreApplication.translate("DeployPage", u"\U0001f4e6  Backup Config", None))
        self.btnValidar.setText(QCoreApplication.translate("DeployPage", u"\u2714  Validar Config", None))
        self.grpValidacao.setTitle(QCoreApplication.translate("DeployPage", u"Resultado da Valida\u00e7\u00e3o", None))
        self.lblResultadoVal.setText(QCoreApplication.translate("DeployPage", u"\u2014", None))
        ___qtablewidgetitem = self.tableValidacao.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("DeployPage", u"Item", None));
        ___qtablewidgetitem1 = self.tableValidacao.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("DeployPage", u"Esperado", None));
        ___qtablewidgetitem2 = self.tableValidacao.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("DeployPage", u"Encontrado", None));
    # retranslateUi

