from PyQt5.QtWidgets import (QApplication, QCheckBox, QDialog, QGridLayout,
                             QGroupBox, QHBoxLayout, QLabel, QPushButton,
                             QStyleFactory, QVBoxLayout, QListWidget, QListWidgetItem,
                             QAbstractItemView, QRadioButton, QProgressDialog,
                             QMainWindow, QWidget, QSlider, QLCDNumber, QMessageBox)
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
from PyQt5.QtCore import Qt, QSize, QThreadPool, QTimer
import utils.config
import darkdetect
from utils.utils import WINDOWS, MAC


# Preferences window
class Preferences(QMainWindow):
    """
    Preferences window
    """
    def __init__(self, parent, status_queue):
        """
        Initialize preferences window.

        It allows to:

        * enable or disable process discovery analysis
        * select the number of runs after which event log is generated
        * select analysis type (either decision points or most frequent routine)

        :param status_queue: queue to send messages to main GUI
        """
        super(Preferences, self).__init__(parent,
                                          flags=Qt.Window |
                                          Qt.WindowTitleHint |
                                          Qt.CustomizeWindowHint |
                                          Qt.WindowCloseButtonHint |
                                          Qt.WindowMinimizeButtonHint
                                          )

        self.status_queue = status_queue
        self.setWindowTitle(" ")
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
        font = QFont(monospaceFont, fontSize, QFont.Normal)

        self.decisionGroupBox = QGroupBox("Analysis type")

        self.process_discovery_cb = QCheckBox(
            "Enable Process Discovery \nanalysis on event log")
        self.process_discovery_cb.setToolTip("If enabled, process discovery analysis is performed automatically\n"
                                             "after selecting event log file, otherwise only event log is generated")
        self.process_discovery_cb.tag = "process_discovery_cb"
        self.process_discovery_cb.stateChanged.connect(self.handle_cb)
        perform_process_discovery = utils.config.MyConfig.get_instance().perform_process_discovery
        self.process_discovery_cb.setChecked(perform_process_discovery)
        self.decisionGroupBox.setEnabled(perform_process_discovery)

        self.mfr = QRadioButton("Most frequent routine")
        self.mfr.clicked.connect(self.handle_radio)
        self.mfr.setChecked(utils.config.MyConfig.get_instance().enable_most_frequent_routine_analysis)
        self.mfr.setToolTip("Create SW Robot based on most frequent routine in the event log")

        self.decision = QRadioButton("Decision points")
        self.decision.clicked.connect(self.handle_radio)
        self.decision.setChecked(utils.config.MyConfig.get_instance().enable_decision_point_analysis)
        self.decision.setToolTip("Create SW Robot based on user decisions")

        self.decisionRPA = QRadioButton("Decision points in UiPath")
        self.decisionRPA.clicked.connect(self.handle_radio)
        self.decisionRPA.setChecked(utils.config.MyConfig.get_instance().enable_decision_point_RPA_analysis)
        self.decisionRPA.setToolTip("Create SW Robot that asks for user decisions in UiPath script")

        slider_minimum = 1 if utils.config.MyConfig.get_instance().enable_most_frequent_routine_analysis else 2
        slider_maximum = 30

        self.lcd = QLCDNumber(self)
        self.lcd.setMinimumHeight(45)

        self.sld = QSlider(Qt.Horizontal, self)
        self.sld.setMinimum(slider_minimum)
        self.sld.setMaximum(slider_maximum)
        self.sld.setValue(utils.config.MyConfig.get_instance().totalNumberOfRunGuiXes)
        self.sld.valueChanged.connect(self.handle_slider)

        label_minimum = QLabel(str(1), alignment=Qt.AlignLeft, font=font)
        label_maximum = QLabel(str(slider_maximum), alignment=Qt.AlignRight, font=font)

        self.slider_label = QLabel(
            "Number of runs after which \nevent is generated:")
        self.slider_label.setToolTip(
            "When the selected number of runs is reached, all CSV logs collected are merged into one \nand a XES file "
            "is automatically generated, to be used for process mining techniques")
        self.handle_slider()

        confirmButton = QPushButton("OK")
        confirmButton.setCheckable(True)
        confirmButton.setChecked(False)
        confirmButton.clicked.connect(self.handleButton)
        if darkdetect.isDark():
            confirmButton.setStyleSheet(
                'QPushButton {background-color: #656565;}')

        processDiscoveryGroupBox = QGroupBox("Process Discovery")
        vbox = QVBoxLayout()
        vbox.addWidget(self.process_discovery_cb)
        processDiscoveryGroupBox.setLayout(vbox)

        vbox = QVBoxLayout()
        vbox.addWidget(self.mfr)
        vbox.addWidget(self.decision)
        # vbox.addWidget(self.decisionRPA)
        self.decisionGroupBox.setLayout(vbox)

        xesGroupBox = QGroupBox()
        vbox = QVBoxLayout()
        vbox.addWidget(self.slider_label)
        vbox.addWidget(self.lcd)
        vbox.addSpacing(10)
        vbox.addWidget(self.sld)
        hbox = QHBoxLayout()
        hbox.addWidget(label_minimum, Qt.AlignLeft)
        hbox.addWidget(label_maximum, Qt.AlignRight)
        vbox.addLayout(hbox)
        xesGroupBox.setLayout(vbox)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(processDiscoveryGroupBox)
        mainLayout.addWidget(self.decisionGroupBox)
        mainLayout.addWidget(xesGroupBox)
        mainLayout.addWidget(confirmButton)

        wid = QWidget(self)
        self.setCentralWidget(wid)
        wid.setLayout(mainLayout)
        wid.setGeometry(300, 300, 250, 150)
        wid.show()

    def handle_slider(self):
        value = self.sld.value()
        self.lcd.display(value)
        utils.config.MyConfig.get_instance().totalNumberOfRunGuiXes = value

    def handle_cb(self):
        perform = self.process_discovery_cb.isChecked()
        self.decisionGroupBox.setEnabled(perform)
        utils.config.MyConfig.get_instance().perform_process_discovery = perform
        if perform:
            self.status_queue.put("[GUI] Process discovery enabled")
        else:
            self.status_queue.put("[GUI] Process discovery disabled")

    def handle_radio(self):
        mfr_checked = self.mfr.isChecked()
        decision_checked = self.decision.isChecked()
        decisionRPA_checked = self.decisionRPA.isChecked()

        utils.config.MyConfig.get_instance().enable_most_frequent_routine_analysis = mfr_checked
        utils.config.MyConfig.get_instance().enable_decision_point_analysis = decision_checked
        utils.config.MyConfig.get_instance().enable_decision_point_RPA_analysis = decisionRPA_checked

        # update lcd value, if decision there should be at least 2 traces
        if mfr_checked:
            self.sld.setMinimum(1)
            self.sld.setValue(1)
        else:
            self.sld.setMinimum(2)

        msg = "[GUI] "
        if mfr_checked:
            msg += "Most frequent routine analysis enabled"
        elif decision_checked:
            msg += "Decision point analysis enabled"
        elif decisionRPA_checked:
            msg += "Decision point analysis in RPA script enabled"
        self.status_queue.put(msg)

    def handleButton(self):
        self.close()
