# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'vlans_page.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QGroupBox, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QSpacerItem, QSpinBox, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_VlansPage(object):
    def setupUi(self, VlansPage):
        if not VlansPage.objectName():
            VlansPage.setObjectName(u"VlansPage")
        VlansPage.resize(680, 620)
        self.layoutRaiz = QVBoxLayout(VlansPage)
        self.layoutRaiz.setSpacing(12)
        self.layoutRaiz.setObjectName(u"layoutRaiz")
        self.layoutRaiz.setContentsMargins(20, 20, 20, 20)
        self.lblInstrucao = QLabel(VlansPage)
        self.lblInstrucao.setObjectName(u"lblInstrucao")
        font = QFont()
        font.setFamilies([u"Consolas"])
        font.setPointSize(10)
        self.lblInstrucao.setFont(font)

        self.layoutRaiz.addWidget(self.lblInstrucao)

        self.tableVlans = QTableWidget(VlansPage)
        if (self.tableVlans.columnCount() < 2):
            self.tableVlans.setColumnCount(2)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableVlans.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableVlans.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        if (self.tableVlans.rowCount() < 3):
            self.tableVlans.setRowCount(3)
        __qtablewidgetitem2 = QTableWidgetItem()
        __qtablewidgetitem2.setTextAlignment(Qt.AlignCenter);
        self.tableVlans.setItem(0, 0, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tableVlans.setItem(0, 1, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        __qtablewidgetitem4.setTextAlignment(Qt.AlignCenter);
        self.tableVlans.setItem(1, 0, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tableVlans.setItem(1, 1, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        __qtablewidgetitem6.setTextAlignment(Qt.AlignCenter);
        self.tableVlans.setItem(2, 0, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.tableVlans.setItem(2, 1, __qtablewidgetitem7)
        self.tableVlans.setObjectName(u"tableVlans")
        self.tableVlans.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableVlans.setColumnCount(2)

        self.layoutRaiz.addWidget(self.tableVlans)

        self.grpAdicionar = QGroupBox(VlansPage)
        self.grpAdicionar.setObjectName(u"grpAdicionar")
        self.layoutAdicionar = QHBoxLayout(self.grpAdicionar)
        self.layoutAdicionar.setSpacing(8)
        self.layoutAdicionar.setObjectName(u"layoutAdicionar")
        self.lblId = QLabel(self.grpAdicionar)
        self.lblId.setObjectName(u"lblId")

        self.layoutAdicionar.addWidget(self.lblId)

        self.spinVid = QSpinBox(self.grpAdicionar)
        self.spinVid.setObjectName(u"spinVid")
        self.spinVid.setMinimum(1)
        self.spinVid.setMaximum(4094)
        self.spinVid.setValue(60)

        self.layoutAdicionar.addWidget(self.spinVid)

        self.lblNome = QLabel(self.grpAdicionar)
        self.lblNome.setObjectName(u"lblNome")

        self.layoutAdicionar.addWidget(self.lblNome)

        self.lineVnome = QLineEdit(self.grpAdicionar)
        self.lineVnome.setObjectName(u"lineVnome")

        self.layoutAdicionar.addWidget(self.lineVnome)

        self.btnAdicionar = QPushButton(self.grpAdicionar)
        self.btnAdicionar.setObjectName(u"btnAdicionar")

        self.layoutAdicionar.addWidget(self.btnAdicionar)

        self.btnRemoverLista = QPushButton(self.grpAdicionar)
        self.btnRemoverLista.setObjectName(u"btnRemoverLista")

        self.layoutAdicionar.addWidget(self.btnRemoverLista)

        self.btnRestaurar = QPushButton(self.grpAdicionar)
        self.btnRestaurar.setObjectName(u"btnRestaurar")

        self.layoutAdicionar.addWidget(self.btnRestaurar)


        self.layoutRaiz.addWidget(self.grpAdicionar)

        self.grpExcluir = QGroupBox(VlansPage)
        self.grpExcluir.setObjectName(u"grpExcluir")
        self.layoutExcluir = QHBoxLayout(self.grpExcluir)
        self.layoutExcluir.setSpacing(8)
        self.layoutExcluir.setObjectName(u"layoutExcluir")
        self.lblInfoExcluir = QLabel(self.grpExcluir)
        self.lblInfoExcluir.setObjectName(u"lblInfoExcluir")
        self.lblInfoExcluir.setWordWrap(True)

        self.layoutExcluir.addWidget(self.lblInfoExcluir)

        self.spacerItem = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layoutExcluir.addItem(self.spacerItem)

        self.btnExcluirSwitch = QPushButton(self.grpExcluir)
        self.btnExcluirSwitch.setObjectName(u"btnExcluirSwitch")

        self.layoutExcluir.addWidget(self.btnExcluirSwitch)


        self.layoutRaiz.addWidget(self.grpExcluir)


        self.retranslateUi(VlansPage)

        QMetaObject.connectSlotsByName(VlansPage)
    # setupUi

    def retranslateUi(self, VlansPage):
        VlansPage.setWindowTitle(QCoreApplication.translate("VlansPage", u"VLANs", None))
        self.lblInstrucao.setText(QCoreApplication.translate("VlansPage", u"VLANs a configurar no switch:", None))
        ___qtablewidgetitem = self.tableVlans.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("VlansPage", u"ID da VLAN", None));
        ___qtablewidgetitem1 = self.tableVlans.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("VlansPage", u"Nome da VLAN", None));

        __sortingEnabled = self.tableVlans.isSortingEnabled()
        self.tableVlans.setSortingEnabled(False)
        ___qtablewidgetitem2 = self.tableVlans.item(0, 0)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("VlansPage", u"10", None));
        ___qtablewidgetitem3 = self.tableVlans.item(0, 1)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("VlansPage", u"VLAN_DADOS", None));
        ___qtablewidgetitem4 = self.tableVlans.item(1, 0)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("VlansPage", u"20", None));
        ___qtablewidgetitem5 = self.tableVlans.item(1, 1)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("VlansPage", u"VLAN_VOZ", None));
        ___qtablewidgetitem6 = self.tableVlans.item(2, 0)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("VlansPage", u"50", None));
        ___qtablewidgetitem7 = self.tableVlans.item(2, 1)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("VlansPage", u"VLAN_SEGURANCA", None));
        self.tableVlans.setSortingEnabled(__sortingEnabled)

        self.grpAdicionar.setTitle(QCoreApplication.translate("VlansPage", u"Adicionar VLAN \u00e0 lista", None))
        self.lblId.setText(QCoreApplication.translate("VlansPage", u"ID:", None))
        self.spinVid.setPrefix(QCoreApplication.translate("VlansPage", u"VLAN ", None))
        self.lblNome.setText(QCoreApplication.translate("VlansPage", u"Nome:", None))
        self.lineVnome.setPlaceholderText(QCoreApplication.translate("VlansPage", u"Nome (ex: VLAN_TI)", None))
        self.btnAdicionar.setText(QCoreApplication.translate("VlansPage", u"+ Adicionar", None))
        self.btnRemoverLista.setText(QCoreApplication.translate("VlansPage", u"\u2212 Remover da lista", None))
        self.btnRestaurar.setText(QCoreApplication.translate("VlansPage", u"\u21ba Restaurar padr\u00f5es", None))
        self.grpExcluir.setTitle(QCoreApplication.translate("VlansPage", u"Excluir VLAN no Switch", None))
        self.lblInfoExcluir.setText(QCoreApplication.translate("VlansPage", u"Selecione uma VLAN na tabela e clique em 'Excluir no Switch'\n"
"para enviar o comando  no vlan <id>  ao equipamento.", None))
        self.btnExcluirSwitch.setText(QCoreApplication.translate("VlansPage", u"\U0001f5d1  Excluir no Switch", None))
    # retranslateUi

