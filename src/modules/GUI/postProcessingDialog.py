from PyQt5.QtWidgets import (QApplication, QCheckBox, QDialog, QGridLayout,
                             QGroupBox, QHBoxLayout, QLabel, QPushButton,
                             QStyleFactory, QVBoxLayout, QListWidget, QListWidgetItem,
                             QAbstractItemView, QRadioButton, QProgressDialog,
                             QMainWindow, QWidget, QSlider, QLCDNumber, QMessageBox)
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
from PyQt5.QtCore import Qt, QSize, QThreadPool, QTimer
import darkdetect

import utils.config
from utils.utils import WINDOWS, MAC

class LLMDialog(QDialog):
    def __init__(self, parent, status_queue):
        super(LLMDialog, self).__init__(parent,
                                          flags=Qt.Window |
                                          Qt.WindowTitleHint |
                                          Qt.CustomizeWindowHint |
                                          Qt.WindowCloseButtonHint |
                                          Qt.WindowMinimizeButtonHint
                                          )
        self.status_queue = status_queue
        self.setWindowTitle("New Window")
        if WINDOWS:
            self.resize(360, 320)

        if WINDOWS:
            monospaceFont = 'Lucida Console'
            fontSize = 10
        elif MAC:
            monospaceFont = 'Monaco'
            fontSize = 13
        else:
            monospaceFont = 'monospace'
            fontSize = 13
        # Create the main layout
        font = QFont(monospaceFont, fontSize, QFont.Normal)

        self.process_discovery_cb = QCheckBox(
            "Enable Process Discovery \nanalysis on event log")
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.process_discovery_cb)