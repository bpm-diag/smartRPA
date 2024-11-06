import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QPixmap
import numpy as np
import os
import utils.config
from multiprocessing import Process, Queue

sys.path.append('../') # So main file is visible from this file

######
# Should be integrated in GUI file as it currently produces an error:
#     "WARNING: QApplication was not created in the main() thread."
######

def getResponse(json_str=""):
    """
    Takes a dict object containing the key-values of the recorded user action.
    Displays a UI to the user for feedback on the relevancy of the previous action.

    :param json_str: Dictionary containing event key-values
    :return: Response TRUE, FALSE, NONE
    :rtype: bool or None
    """
    # Only activate if the global setting is put to true
    if utils.config.read_config("supervisionFeature", bool):
        # Queue for inter-process communication
        response_queue = Queue()

        # Start the application in a separate process
        process = Process(target=start_app, args=(json_str, response_queue))
        process.start()

        # Wait for a response from the GUI application
        response = response_queue.get()  # This will block until a response is received
        process.join()  # Ensure the process has finished

        return response  # Return the user's feedback
    return None  # Return None if the feature is disabled


def handle_button_click(selected_option, window):
    global response_sp_feature
    response_sp_feature = selected_option
    window.close()

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPixmap
import sys

def start_app(json_str, response_queue):
    """
    Displays a feedback window based on json_str and sends the result to the response_queue.
    :param json_str: Dictionary containing event key-values
    :param response_queue: Queue to send the user's feedback back to the main process
    """
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QWidget()
    window.setWindowTitle("Feedback on Action Logged")
    window.resize(500, 300)
    # Set the position of the window to the top-left corner
    window.move(100, 100)  # Position at (0, 0) to open in the top-left
    window.setWindowFlags(window.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

    # Create a layout to arrange widgets
    layout = QtWidgets.QVBoxLayout(window)

    # Create a label to display the key-value dictionary
    kv_dict_label = QtWidgets.QLabel(window)
    kv_dict_label.setText("Key-Value Dictionary:")
    kv_dict_label.setAlignment(QtCore.Qt.AlignLeft)

    # Create a formatted string to display the key-value dictionary
    kv_dict_string = "\n".join(f"{key}: {value}" for key, value in json_str.items())
    kv_dict_label.setWordWrap(True)
    kv_dict_label.setText(kv_dict_string)
    layout.addWidget(kv_dict_label)

    # Display screenshot if available
    screenshot_label = QtWidgets.QLabel(window)
    if "screenshot" in json_str and json_str.get("screenshot") != "":
        window.resize(800, 500)
        pixmap = QPixmap(json_str.get("screenshot"))
        pix = pixmap.scaled(500, 450, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.FastTransformation)
        screenshot_label.setPixmap(pix)
        screenshot_label.setAlignment(QtCore.Qt.AlignCenter)
    layout.addWidget(screenshot_label)

    # Internal handler for the feedback buttons
    def handle_button_click(response):
        response_queue.put(response)  # Send response back to the main process
        window.close()

    # Feedback buttons
    yes_button = QtWidgets.QPushButton("Yes")
    yes_button.clicked.connect(lambda: handle_button_click(True))

    no_button = QtWidgets.QPushButton("No")
    no_button.clicked.connect(lambda: handle_button_click(False))

    close_button = QtWidgets.QPushButton("Close")
    close_button.clicked.connect(lambda: handle_button_click(None))

    layout.addWidget(yes_button)
    layout.addWidget(no_button)
    layout.addWidget(close_button)

    window.setLayout(layout)
    window.show()
    app.exec_()
