
import sys
import os
import datetime
import re

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QTableWidgetItem, QFileDialog, QMessageBox, QHeaderView,
)
from PySide6.QtCore import Qt, Signal, QObject, QThread
from PySide6.QtGui  import QColor, QTextCursor


# Tenta importar Netmiko - Isso aqui é legal parece o try catch do java evita erros
try:
    from netmiko import ConnectHandler
    NETMIKO_DISPONIVEL = True
except ImportError:
    NETMIKO_DISPONIVEL = False # neste caso aqui achei legal colocar uma variável de controle para o código saber que o 
                               # Netmiko não
