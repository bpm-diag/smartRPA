import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QPixmap
import numpy as np
import os
import utils.config

sys.path.append('../') # So main file is visible from this file

######
# Should be integrated in GUI file as it currently produces an error:
#     "WARNING: QApplication was not created in the main() thread."
######

def getResponse(json_str=""):
    """
    Takes a dict object containing the key-values of the recorded user action.
    Displays a UI to the user for feedback on the relevancy of the previous action.

    :param json_str: String containing a dictonary with event key-values
    :return: Response TRUE, FALSE, NONE
    :rtype: bool
    """
    # Only activate if the global setting is put to true
    if utils.config.read_config("supervisionFeature",bool):
        global response_sp_feature
        response_sp_feature = False
        app = QtWidgets.QApplication(sys.argv)
        window = QtWidgets.QWidget()
        window.setWindowTitle("Feedback on Action Logged")
        window.resize(500, 300)

        # Create a layout to arrange widgets
        layout = QtWidgets.QVBoxLayout(window)

        # Create a label to display the key-value dictionary
        kv_dict_label = QtWidgets.QLabel(window)
        kv_dict_label.setText("Key-Value Dictionary:")
        kv_dict_label.setAlignment(QtCore.Qt.AlignLeft)

        # Create a formatted string to display the key-value dictionary
        kv_dict_string = ""
        for key, value in json_str.items():
            kv_dict_string += f"{key}: {value}\n"

        kv_dict_label.setWordWrap(True)
        kv_dict_label.setText(kv_dict_string)
        layout.addWidget(kv_dict_label)

        screenshot_label = QtWidgets.QLabel(window)
        # Display screenshot if available
        if "screenshot" in json_str and json_str.get("screenshot") != "":
            window.resize(800, 500)
            # Read the screenshot image: https://stackoverflow.com/questions/71935118/how-to-putting-image-in-the-label-on-pyqt
            pixmap = QPixmap(json_str.get("screenshot"))
            pix = pixmap.scaled(500, 450, QtCore.Qt.AspectRatioMode.KeepAspectRatio,QtCore.Qt.TransformationMode.FastTransformation)
            screenshot_label.setPixmap(pix)
            screenshot_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            # Enhancement: Make the screenshot_label clickable so that the image can be opened from clicking on it in the GUI
            

        layout.addWidget(screenshot_label)

        # Create buttons to provide feedback
        yes_button = QtWidgets.QPushButton(window, text="Yes")
        yes_button.clicked.connect(lambda: handle_button_click(True, window))

        no_button = QtWidgets.QPushButton(window, text="No")
        no_button.clicked.connect(lambda: handle_button_click(False, window))

        close_button = QtWidgets.QPushButton(window, text="Close")
        close_button.clicked.connect(lambda: handle_button_click(None, window))

        layout.addWidget(yes_button)
        layout.addWidget(no_button)
        layout.addWidget(close_button)

        window.show()
        app.exec_()
        return response_sp_feature
    return None


def handle_button_click(selected_option, window):
    global response_sp_feature
    response_sp_feature = selected_option
    window.close()