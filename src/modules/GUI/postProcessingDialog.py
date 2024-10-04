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

import google.generativeai as genai

from utils.utils import WINDOWS, MAC

import utils.LLMtagger

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
        self.config_file = 'src/utils/LLM_gemini_config.json'
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

        # Add Process File button
        self.process_file_button = QPushButton("Process File")
        self.process_file_button.clicked.connect(self.LLM_data_tagging)
        main_layout.addWidget(self.process_file_button)

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
                genai.configure(api_key=api_code)
                if api_code:
                    self.api_status_label.setText("API code loaded from config.")
                else:
                    self.api_status_label.setText("No API code found in config.")
        else:
            self.api_status_label.setText("No config file found.")

    def LLM_data_tagging(self):

        # Get the selected file path from the UI
        csvFilePath = self.file_path_label.text()
        directory_path = os.path.dirname(csvFilePath)
        filename = os.path.basename(csvFilePath)
        filename_without_extension = os.path.splitext(filename)[0]
        tags_json_file_path = directory_path + '/' + filename_without_extension + '_tagged.json'

        jsonUiLog = utils.LLMtagger.csv_to_json(csvFilePath)
        jsonUiLog = utils.LLMtagger.remove_keys(jsonUiLog, ["Supervised Action Tag", "screenshot"])

        semanticUiLog = ""
        try:
            semanticUiLog = utils.LLMtagger.combine_header_and_data(jsonUiLog)
        except Exception as e:
            self.status_queue.put(f"An error occurred: {str(e)}")

        # ToDo: Implement API Code validity check 
        self.load_api_code()
        model = utils.LLMtagger.startModel() 

        self.status_queue.put(f"[LLM] Promting UI Log")

        promt = f"Given the following Json file with the semantic header and multiple rows that contain the features/attributes of user actions: Tag each element with a short description of what the user did. Keep the tag to 5-10 words. Base your answer on the key values and the semantic header information. Provide a response in json key value format. Do not add any other information to the response. \n {semanticUiLog}"
        response = model.generate_content(promt,
                                        #https://ai.google.dev/gemini-api/docs/text-generation?lang=python#configure
                                            generation_config=genai.types.GenerationConfig(
                                            candidate_count=1,
                                            #max_output_tokens=20,
                                            temperature=0.0,
                                            ),
                                        )
        print(response.usage_metadata)

        # print(response.text)
        extracted_json = utils.LLMtagger.extract_json_from_text(response.text)

        # Write the generated tags into the tags file
        with open(tags_json_file_path, 'w') as outfile:
            json.dump(extracted_json, outfile, indent=2)
        
        self.status_queue.put(f"[LLM] Tagging Process Complete")
        # Checking type of object
        # returned by json.dumps


    def postprocessing():
        tagged_ui_log = utils.LLMtagger.read_json_file("data/tagged_Ui_log.json")
        generated_tags = utils.LLMtagger.read_json_file("data/tags.json")

        data = utils.LLMtagger.combine_elements(tagged_ui_log,generated_tags)
        print(data)