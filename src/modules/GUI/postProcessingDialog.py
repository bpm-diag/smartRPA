from PyQt5.QtWidgets import (QApplication, QCheckBox, QDialog, QGridLayout,
                             QGroupBox, QHBoxLayout, QLabel, QPushButton,
                             QStyleFactory, QVBoxLayout, QListWidget, QListWidgetItem,
                             QAbstractItemView, QRadioButton, QProgressDialog,
                             QMainWindow, QWidget, QSlider, QLCDNumber, QMessageBox,
                             QFileDialog, QLineEdit)
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
from PyQt5.QtCore import Qt, QSize, QThreadPool, QTimer
import darkdetect

import json
import os

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
        self.setWindowTitle("LLM Processing")
        self.config_file = 'gemini_config.json'
        self.init_ui()

    def init_ui(self):
        if WINDOWS:
            self.resize(500, 300)
            monospace_font = 'Lucida Console'
            font_size = 10
        elif MAC:
            monospace_font = 'Monaco'
            font_size = 13
        else:
            monospace_font = 'monospace'
            font_size = 13

        font = QFont(monospace_font, font_size, QFont.Normal)
        self.setFont(font)

        main_layout = QVBoxLayout(self)

        # File selection section
        file_layout = QVBoxLayout()
        self.select_file_button = QPushButton("Select File")
        self.select_file_button.clicked.connect(self.select_file)
        file_layout.addWidget(self.select_file_button)

        self.file_path_label = QLabel()
        file_layout.addWidget(self.file_path_label)
        main_layout.addLayout(file_layout)

        # API Code section
        api_layout = QVBoxLayout()
        api_label = QLabel("Gemini API Code:")
        api_layout.addWidget(api_label)

        api_input_layout = QHBoxLayout()
        self.api_input = QLineEdit()
        self.api_input.setEchoMode(QLineEdit.Password)  # Hide the API code
        api_input_layout.addWidget(self.api_input)

        self.save_api_button = QPushButton("Save API Code")
        self.save_api_button.clicked.connect(self.save_api_code)
        api_input_layout.addWidget(self.save_api_button)

        api_layout.addLayout(api_input_layout)

        self.api_status_label = QLabel()
        api_layout.addWidget(self.api_status_label)

        main_layout.addLayout(api_layout)

        self.setLayout(main_layout)

        # Load existing API code if available
        self.load_api_code()

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "All Files (*)")
        if file_path:
            self.file_path_label.setText(file_path)
            print(f"Selected file: {file_path}")

    def save_api_code(self):
        api_code = self.api_input.text()
        if api_code:
            config = {'api_code': api_code}
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
            self.api_status_label.setText("API code saved successfully!")
        else:
            self.api_status_label.setText("Please enter an API code.")

    def load_api_code(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                api_code = config.get('api_code', '')
                self.api_input.setText(api_code)
                if api_code:
                    self.api_status_label.setText("API code loaded from config.")
                else:
                    self.api_status_label.setText("No API code found in config.")
        else:
            self.api_status_label.setText("No config file found.")