# Could be made nicer for future work, e.g. Displaying the JSON in nice format
import tkinter as tk
import json
import utils.config

import sys
from PyQt5 import QtWidgets, QtGui, QtCore
import numpy as np
import cv2

def getResponse(json_str=""):
    global response_sp_feature
    response_sp_feature = False
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QWidget()
    window.setWindowTitle("Feedback on Action Logged")
    window.resize(600, 400)

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

    # Display screenshot if available

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

def handle_button_click(selected_option, window):
    global response_sp_feature
    response_sp_feature = selected_option
    window.close()

# def getResponse(jsonSTR=""):
#     """
#     Opens a tkinter GUI requesting feedback on the action logged

#     :param jsonSTR: Descriptive string of all user action attributes
#     :return: Boolean on "is the display action necessary?"
#     :rtype: bool
#     """

#     def yes_clicked():
#         global response_sp_feature
#         response_sp_feature = True
#         root.destroy()

#     def no_clicked():
#         global response_sp_feature
#         response_sp_feature = False
#         root.destroy()

#     def close_clicked():
#         global response_sp_feature
#         response_sp_feature = None
#         root.destroy()

#     # Only activate if the global setting is put to true
#     if utils.config.MyConfig.get_instance().supervisionFeature:
#         root = tk.Tk()
        
#         # Create a label to display the formatted JSON data
#         label = tk.Label(root, text=jsonSTR, justify=tk.LEFT)
#         label.pack(fill="both", expand=True, padx=10, pady=10)

#         # Create a button to close the window
#         button = tk.Button(root, text="Close", command=close_clicked)
#         button.pack()

#         label = tk.Label(root, text="Is the displayed action necessary?")
#         label.pack()

#         yes_button = tk.Button(root, text="Yes", command=yes_clicked)
#         yes_button.pack()

#         no_button = tk.Button(root, text="No", command=no_clicked)
#         no_button.pack()

#         root.mainloop()
#         return response_sp_feature

#     return None