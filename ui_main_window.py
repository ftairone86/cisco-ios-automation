# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QMainWindow,
    QPushButton, QSizePolicy, QSpacerItem, QTabWidget,
    QTextEdit, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1100, 680)
        MainWindow.setMinimumSize(QSize(1100, 680))
        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        self.rootLayout = QHBoxLayout(self.centralWidget)
        self.rootLayout.setSpacing(0)
        self.rootLayout.setObjectName(u"rootLayout")
        self.rootLayout.setContentsMargins(0, 0, 0, 0)
        self.tabWidget = QTabWidget(self.centralWidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabConexao = QWidget()
        self.tabConexao.setObjectName(u"tabConexao")
        self.tabWidget.addTab(self.tabConexao, "")
        self.tabVlans = QWidget()
        self.tabVlans.setObjectName(u"tabVlans")
        self.tabWidget.addTab(self.tabVlans, "")
        self.tabDeploy = QWidget()
        self.tabDeploy.setObjectName(u"tabDeploy")
        self.tabWidget.addTab(self.tabDeploy, "")

        self.rootLayout.addWidget(self.tabWidget)

        self.logLayout = QVBoxLayout()
        self.logLayout.setObjectName(u"logLayout")
        self.logLayout.setContentsMargins(8, 8, 8, 8)
        self.logCabLayout = QHBoxLayout()
        self.logCabLayout.setObjectName(u"logCabLayout")
        self.lblLog = QLabel(self.centralWidget)
        self.lblLog.setObjectName(u"lblLog")

        self.logCabLayout.addWidget(self.lblLog)

        self.Espaco = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.logCabLayout.addItem(self.Espaco)

        self.btnLimparLog = QPushButton(self.centralWidget)
        self.btnLimparLog.setObjectName(u"btnLimparLog")

        self.logCabLayout.addWidget(self.btnLimparLog)


        self.logLayout.addLayout(self.logCabLayout)

        self.txtLog = QTextEdit(self.centralWidget)
        self.txtLog.setObjectName(u"txtLog")
        font = QFont()
        font.setFamilies([u"Consolas"])
        font.setPointSize(10)
        self.txtLog.setFont(font)
        self.txtLog.setReadOnly(True)

        self.logLayout.addWidget(self.txtLog)


        self.rootLayout.addLayout(self.logLayout)

        MainWindow.setCentralWidget(self.centralWidget)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(2)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Gerenciador de VLAN \u2014 Cisco IOS 15.1", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabConexao), QCoreApplication.translate("MainWindow", u"\U0001f5a7 Conex\U000000e3o", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabVlans), QCoreApplication.translate("MainWindow", u"\U0001f56e VLANs", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabDeploy), QCoreApplication.translate("MainWindow", u"\U0001f585 Deploy", None))
        self.lblLog.setText(QCoreApplication.translate("MainWindow", u"Log de opera\u00e7\u00f5es:", None))
        self.btnLimparLog.setText(QCoreApplication.translate("MainWindow", u"Limpar", None))
    # retranslateUi

