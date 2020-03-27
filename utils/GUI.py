# ****************************** #
# GUI
# Build native user interface and start main logger
# ****************************** #

import sys

sys.path.append('../')  # this way main file is visible from this file
from PyQt5.QtCore import Qt, QSize, QDir, QTimer
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (QApplication, QCheckBox, QDialog, QGridLayout,
                             QGroupBox, QHBoxLayout, QLabel, QPushButton,
                             QStyleFactory, QVBoxLayout, QListWidget, QListWidgetItem,
                             QAbstractItemView, QFileDialog, QRadioButton, QProgressDialog,
                             QMainWindow, QWidget, QSlider, QLCDNumber, QDialogButtonBox,
                             QFormLayout, QLineEdit)
import darkdetect
from multiprocessing import Process
import pandas
from utils.utils import *
import mainLogger
import utils.config
import utils.generateRPAScript
import utils.xesConverter
import utils.process_mining
import utils.utils

# Preferences window
class Preferences(QMainWindow):
    def __init__(self, parent=None):
        super(Preferences, self).__init__(parent,
                                          flags=Qt.Window |
                                                Qt.WindowTitleHint |
                                                Qt.CustomizeWindowHint |
                                                Qt.WindowCloseButtonHint |
                                                Qt.WindowMinimizeButtonHint
                                          )

        self.setWindowTitle("")
        if WINDOWS:
            self.resize(360, 320)

        slider_minimum = 1
        slider_maximum = 50

        self.lcd = QLCDNumber(self)
        self.lcd.setMinimumHeight(45)

        self.sld = QSlider(Qt.Horizontal, self)
        self.sld.setMinimum(slider_minimum)
        self.sld.setMaximum(slider_maximum)
        self.sld.setValue(utils.config.MyConfig.get_instance().totalNumberOfRunGuiXes)
        self.sld.valueChanged.connect(self.handle_slider)

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
        label_minimum = QLabel(str(slider_minimum), alignment=Qt.AlignLeft, font=font)
        label_maximum = QLabel(str(slider_maximum), alignment=Qt.AlignRight, font=font)

        self.slider_label = QLabel(alignment=Qt.AlignCenter)
        self.slider_label.setToolTip(
            "When the selected number of runs is reached, all CSV logs collected are merged into one \nand a XES file "
            "is automatically generated, to be used for process mining techniques")
        self.handle_slider()

        confirmButton = QPushButton("OK")
        confirmButton.setCheckable(True)
        confirmButton.setChecked(False)
        confirmButton.clicked.connect(self.handleButton)

        hbox = QHBoxLayout()
        hbox.addWidget(label_minimum, Qt.AlignLeft)
        hbox.addWidget(label_maximum, Qt.AlignRight)
        vbox = QVBoxLayout()
        vbox.addWidget(self.slider_label)
        vbox.addWidget(self.lcd)
        vbox.addSpacing(10)
        vbox.addWidget(self.sld)
        vbox.addLayout(hbox)
        vbox.addWidget(confirmButton)

        wid = QWidget(self)
        self.setCentralWidget(wid)
        wid.setLayout(vbox)
        wid.setGeometry(300, 300, 250, 150)
        wid.show()

    def handle_slider(self):
        value = self.sld.value()
        self.lcd.display(value)
        msg = "Number of runs after which \nXES file is generated:"
        self.slider_label.setText(msg)
        utils.config.MyConfig.get_instance().totalNumberOfRunGuiXes = value

    def handleButton(self):
        self.close()


class MainApplication(QMainWindow, QDialog):
    def __init__(self, parent=None):
        super(MainApplication, self).__init__(parent)
        self.originalPalette = QApplication.palette()
        self.setWindowTitle("ComputerLogger")
        self.setAppIcon()
        self.setStyle()

        menu = self.menuBar().addMenu('File')
        action = menu.addAction('Preferences...')
        action.triggered.connect(self.handlePreferences)
        mergeAction = menu.addAction('Merge and analyze multiple CSV...')
        mergeAction.triggered.connect(self.handleMerge)
        self.preferencesDialog = Preferences(self)

        # create layouts
        self.createSystemLoggerGroupBox()
        self.createOfficeLoggerGroupBox()
        self.createBrowserLoggerGroupBox()
        self.createTopLayout()
        self.createStartButton()
        self.createBottomLayout()
        self.createStatusLayout()

        self.platformCheck()

        #  Variables
        self.running = False
        self.mainProcess = None
        self.officeFilename = None
        self.runCount = 0
        self.csv_to_join = list()

        # Boolean variables that save the state of each checkbox
        self.systemLoggerFilesFolder = self.systemLoggerFilesFolderCB.isChecked()
        self.systemLoggerPrograms = self.systemLoggerProgramsCB.isChecked()
        self.systemLoggerClipboard = self.systemLoggerClipboardCB.isChecked()
        self.systemLoggerHotkeys = self.systemLoggerHotkeysCB.isChecked()
        self.systemLoggerUSB = self.systemLoggerHotkeysCB.isChecked()
        self.systemLoggerEvents = self.systemLoggerEventsCB.isChecked()
        self.officeExcel = self.officeExcelCB.isChecked()
        self.officeWord = self.officeWordCB.isChecked()
        self.officePowerpoint = self.officePowerpointCB.isChecked()
        self.officeOutlook = self.officeOutlookCB.isChecked()
        self.browserChrome = self.browserChromeCB.isChecked()
        self.browserFirefox = self.browserFirefoxCB.isChecked()
        self.browserEdge = self.browserEdgeCB.isChecked()
        self.browserOpera = self.browserOperaCB.isChecked()

        mainLayout = QGridLayout()
        mainLayout.addLayout(self.topLayout, 0, 0, 1, 2)
        # start from cell (1,0) and expand in 2 rows but remain in 1 column
        mainLayout.addWidget(self.systemGroupBox, 1, 0, 2, 1)
        mainLayout.addWidget(self.officeGroupBox, 1, 1)
        # mainLayout.addWidget(self.browserGroupBox, 2, 0) # bottom left
        mainLayout.addWidget(self.browserGroupBox, 2, 1)
        mainLayout.addLayout(self.bottomLayout, 3, 0, 1, 2)
        mainLayout.addLayout(self.statusLayout, 4, 0, 1, 2)
        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(2, 1)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)

        wid = QWidget(self)
        self.setCentralWidget(wid)
        wid.setLayout(mainLayout)
        # self.setLayout(mainLayout)

    def createSystemLoggerGroupBox(self):
        self.systemGroupBox = QGroupBox("System logger")

        self.systemLoggerFilesFolderCB = QCheckBox("Files/Folders")
        self.systemLoggerFilesFolderCB.tag = "systemLoggerFilesFolder"
        self.systemLoggerFilesFolderCB.stateChanged.connect(
            self.handleCheckBox)
        self.systemLoggerFilesFolderCB.setToolTip("Log edits on files and folder like create, modify, delete and more")

        self.systemLoggerClipboardCB = QCheckBox("Clipboard")
        self.systemLoggerClipboardCB.tag = "systemLoggerClipboard"
        self.systemLoggerClipboardCB.stateChanged.connect(self.handleCheckBox)
        self.systemLoggerClipboardCB.setToolTip("Log clipboard copy")

        self.systemLoggerProgramsCB = QCheckBox("Programs")
        self.systemLoggerProgramsCB.tag = "systemLoggerPrograms"
        self.systemLoggerProgramsCB.stateChanged.connect(self.handleCheckBox)
        self.systemLoggerProgramsCB.setToolTip("Log opening and closing of programs")

        self.systemLoggerHotkeysCB = QCheckBox("Hotkeys")
        self.systemLoggerHotkeysCB.tag = "systemLoggerHotkeys"
        self.systemLoggerHotkeysCB.stateChanged.connect(self.handleCheckBox)
        self.systemLoggerHotkeysCB.setToolTip("Log system-wide hotkeys")

        self.systemLoggerUSBCB = QCheckBox("USB Drives")
        self.systemLoggerUSBCB.tag = "systemLoggerUSB"
        self.systemLoggerUSBCB.stateChanged.connect(self.handleCheckBox)
        self.systemLoggerUSBCB.setToolTip("Log insertion and removal of usb drives")

        self.systemLoggerEventsCB = QCheckBox("Events")
        self.systemLoggerEventsCB.tag = "systemLoggerEvents"
        self.systemLoggerEventsCB.stateChanged.connect(self.handleCheckBox)
        self.systemLoggerEventsCB.setToolTip("Log edits on files and folder")

        layout = QVBoxLayout()
        layout.addWidget(self.systemLoggerFilesFolderCB)
        layout.addWidget(self.systemLoggerProgramsCB)
        layout.addWidget(self.systemLoggerClipboardCB)
        layout.addWidget(self.systemLoggerHotkeysCB)
        layout.addWidget(self.systemLoggerUSBCB)
        # layout.addWidget(self.systemLoggerEventsCB)

        self.systemGroupBox.setLayout(layout)

    def createOfficeLoggerGroupBox(self):

        self.officeGroupBox = QGroupBox("Office logger")
        self.officeGroupBox.setToolTip(
            "Log all activities in Office applications \nlike opening, closing, editing documents and more")

        hboxExcel = QHBoxLayout()
        self.officeExcelCB = QCheckBox("Excel")
        self.officeExcelCB.tag = "officeExcel"
        self.officeExcelCB.stateChanged.connect(self.handleCheckBox)
        self.officeExcelNewRB = QRadioButton("New File")
        self.officeExcelNewRB.setChecked(True)
        self.officeExcelNewRB.setAutoExclusive(True)
        self.officeExcelOpenRB = QRadioButton("Open File")
        self.officeExcelOpenRB.setAutoExclusive(True)
        hboxExcel.addWidget(self.officeExcelCB)
        hboxExcel.addWidget(self.officeExcelNewRB)
        hboxExcel.addWidget(self.officeExcelOpenRB)

        hboxWord = QHBoxLayout()
        self.officeWordCB = QCheckBox("Word")
        self.officeWordCB.tag = "officeWord"
        self.officeWordCB.stateChanged.connect(self.handleCheckBox)
        self.officeWordNewRB = QRadioButton("New File")
        self.officeWordNewRB.setChecked(True)
        self.officeWordOpenRB = QRadioButton("Open File")
        hboxWord.addWidget(self.officeWordCB)
        hboxWord.addWidget(self.officeWordNewRB)
        hboxWord.addWidget(self.officeWordOpenRB)

        hboxPowerpoint = QHBoxLayout()
        self.officePowerpointCB = QCheckBox("PowerPoint")
        self.officePowerpointCB.tag = "officePowerpoint"
        self.officePowerpointCB.stateChanged.connect(self.handleCheckBox)
        self.officePowerpointNewRB = QRadioButton("New File")
        self.officePowerpointNewRB.setChecked(True)
        self.officePowerpointOpenRB = QRadioButton("Open File")
        hboxPowerpoint.addWidget(self.officePowerpointCB)
        hboxPowerpoint.addWidget(self.officePowerpointNewRB)
        hboxPowerpoint.addWidget(self.officePowerpointOpenRB)

        self.officeOutlookCB = QCheckBox("Outlook")
        self.officeOutlookCB.tag = "officeOutlook"
        self.officeOutlookCB.stateChanged.connect(self.handleCheckBox)

        layout = QVBoxLayout()
        layout.addWidget(self.officeExcelCB)
        layout.addWidget(self.officeWordCB)
        layout.addWidget(self.officePowerpointCB)
        # if hbox is added to layout the user can select an existing file to open when starting office logging
        # layout.addLayout(hboxExcel)
        # layout.addLayout(hboxWord)
        # layout.addLayout(hboxPowerpoint)
        # layout.addWidget(self.officeOutlookCB)

        self.officeGroupBox.setLayout(layout)

    def createBrowserLoggerGroupBox(self):
        self.browserGroupBox = QGroupBox("Browser logger")
        self.browserGroupBox.setToolTip(
            "Log all browser events in the window (like opening, closing tabs, printing, etc) \nand in the page (like clicking, zooming, pasting, etc)")

        self.browserChromeCB = QCheckBox("Google Chrome")
        self.browserChromeCB.tag = "browserChrome"
        self.browserChromeCB.stateChanged.connect(self.handleCheckBox)

        self.browserFirefoxCB = QCheckBox("Mozilla Firefox")
        self.browserFirefoxCB.tag = "browserFirefox"
        self.browserFirefoxCB.stateChanged.connect(self.handleCheckBox)

        self.browserEdgeCB = QCheckBox("Microsoft Edge")
        self.browserEdgeCB.tag = "browserEdge"
        self.browserEdgeCB.stateChanged.connect(self.handleCheckBox)

        self.browserOperaCB = QCheckBox("Opera")
        self.browserOperaCB.tag = "browserOpera"
        self.browserOperaCB.stateChanged.connect(self.handleCheckBox)

        layout = QVBoxLayout()
        layout.addWidget(self.browserChromeCB)
        layout.addWidget(self.browserFirefoxCB)
        layout.addWidget(self.browserEdgeCB)
        layout.addWidget(self.browserOperaCB)

        self.browserGroupBox.setLayout(layout)

    def createStartButton(self):
        self.runButton = QPushButton("Start logger")
        self.runButton.setCheckable(True)
        self.runButton.setChecked(False)
        self.runButton.clicked.connect(self.onButtonClick)
        self.runButton.toggled.connect(self.systemGroupBox.setDisabled)
        self.runButton.toggled.connect(self.browserGroupBox.setDisabled)
        self.runButton.toggled.connect(self.checkButton.setDisabled)
        # if WINDOWS:
        self.runButton.toggled.connect(self.officeGroupBox.setDisabled)

    def createTopLayout(self):
        self.topLayout = QHBoxLayout()
        self.topLayout.addWidget(QLabel("Select modules to activate"))

        self.topLayout.addStretch(1)
        self.checkButton = QPushButton("Enable all")
        self.checkButton.setCheckable(True)
        self.checkButton.setChecked(False)
        self.checkButton.setFlat(True)
        self.allCBChecked = False
        self.checkButton.toggled.connect(self.setCheckboxChecked)

        self.topLayout.addWidget(self.checkButton)

    def createBottomLayout(self):
        self.bottomLayout = QHBoxLayout()
        self.bottomLayout.addStretch(1)
        self.bottomLayout.addWidget(self.runButton)
        self.bottomLayout.addStretch(1)

    def createStatusLayout(self):
        if WINDOWS:
            monospaceFont = 'Lucida Console'
            fontSize = 8
        elif MAC:
            monospaceFont = 'Monaco'
            fontSize = 11
        else:
            monospaceFont = 'monospace'
            fontSize = 11

        self.statusLayout = QVBoxLayout()

        self.statusListWidget = QListWidget()
        self.statusListWidget.setFont(QFont(monospaceFont, fontSize, QFont.Normal))
        self.statusListWidget.setSelectionMode(QAbstractItemView.NoSelection)

        self.statusLayout.addWidget(self.statusListWidget)

    def createProgressDialog(self, title, message, timeout):
        flags = Qt.WindowTitleHint | Qt.Dialog | Qt.WindowMaximizeButtonHint | Qt.CustomizeWindowHint
        self.progress_dialog = QProgressDialog(message, None, 0, 0, self, flags)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setWindowTitle(title)
        if WINDOWS:
            self.progress_dialog.resize(470, 100)
        else:
            self.progress_dialog.resize(260, 100)
        self.progress_dialog.show()
        self.timer = QTimer(self)
        self.timer.start(timeout)
        self.timer.timeout.connect(self.cancelProgressDialog)

    def cancelProgressDialog(self):
        self.progress_dialog.done(0)
        self.timer.stop()
        self.timer.deleteLater()

    # display native GUI for each OS
    def setStyle(self):
        if WINDOWS:
            QApplication.setStyle(QStyleFactory.create('windowsvista'))
        elif MAC:
            QApplication.setStyle(QStyleFactory.create('macintosh'))
        else:
            QApplication.setStyle(QStyleFactory.create('Fusion'))

        # remove question mark and expand button, show minimize and close button
        self.setWindowFlags(
            Qt.Window |
            Qt.WindowTitleHint |
            Qt.CustomizeWindowHint |
            Qt.WindowCloseButtonHint |
            Qt.WindowMinimizeButtonHint
        )

    def setAppIcon(self):
        # set app icon with support to dark mode
        app_icon = QIcon()
        if darkdetect.isDark():
            app_icon.addFile('utils/icons/icon-16-dark.png', QSize(16, 16))
            app_icon.addFile('utils/icons/icon-32-dark.png', QSize(32, 32))
            app_icon.addFile('utils/icons/icon-48-dark.png', QSize(48, 48))
            app_icon.addFile('utils/icons/icon-128-dark.png', QSize(128, 128))
        else:
            app_icon.addFile('utils/icons/icon-16.png', QSize(16, 16))
            app_icon.addFile('utils/icons/icon-32.png', QSize(32, 32))
            app_icon.addFile('utils/icons/icon-48.png', QSize(48, 48))
            app_icon.addFile('utils/icons/icon-128.png', QSize(128, 128))
        self.setWindowIcon(app_icon)

    # set appropriate values based on platform
    def platformCheck(self):

        if WINDOWS:
            # window size
            self.resize(640, 600)
            # margins
            self.topLayout.setContentsMargins(0, 0, 0, 20)
            self.bottomLayout.setContentsMargins(0, 20, 0, 20)

            # disable checkbox if corresponding program is not installed in system
            if not OFFICE:
                self.officeGroupBox.setEnabled(False)
                self.officeExcelCB.setChecked(False)
                self.officeWordCB.setChecked(False)
                self.officePowerpointCB.setChecked(False)
                self.officeOutlookCB.setChecked(False)
                self.officeExcel = False
                self.officeWord = False
                self.officePowerpoint = False
                self.officeOutlook = False

            self.statusListWidget.setStyleSheet("QListWidget{background: #F0F0F0;}")

        elif MAC or LINUX:

            if not OFFICE:
                self.officeExcelCB.setChecked(False)
                self.officeExcel = False

            # program logger is not supported on mac
            # self.systemLoggerFilesFolderCB.setChecked(False)
            # self.systemLoggerFilesFolderCB.setDisabled(True)

            self.systemLoggerHotkeysCB.setChecked(False)
            self.systemLoggerHotkeysCB.setDisabled(True)
            self.systemLoggerUSBCB.setChecked(False)
            self.systemLoggerUSBCB.setDisabled(True)
            self.systemLoggerEventsCB.setChecked(False)
            self.systemLoggerEventsCB.setDisabled(True)

            self.officeWordCB.setDisabled(True)
            self.officePowerpointCB.setDisabled(True)
            self.officeOutlookCB.setDisabled(True)

            # window size
            self.resize(360, 420)

            # margins
            self.topLayout.setContentsMargins(0, 0, 0, 10)
            self.bottomLayout.setContentsMargins(0, 0, 0, 0)

            # if darkdetect.isLight():
            #     self.statusListWidget.setStyleSheet("QListWidget{background: #ECECEC;}")
            # else:
            #     self.statusListWidget.setStyleSheet("QListWidget{background: #3A3B3B;}")
            self.statusListWidget.setStyleSheet("QListWidget{background: #ECECEC;}")

        if not CHROME:
            self.browserChromeCB.setEnabled(False)
            self.browserChromeCB.setChecked(False)
            self.browserChrome = False

        if not FIREFOX:
            self.browserFirefoxCB.setEnabled(False)
            self.browserFirefoxCB.setChecked(False)
            self.browserFirefox = False

        if not EDGE:
            self.browserEdgeCB.setEnabled(False)
            self.browserEdgeCB.setChecked(False)
            self.browserEdge = False

        if not OPERA:
            self.browserOperaCB.setEnabled(False)
            self.browserOperaCB.setChecked(False)
            self.browserOpera = False

        self.compatibilityCheckMessage()

    def compatibilityCheckMessage(self):
        self.statusListWidget.clear()
        if MAC:
            self.statusListWidget.addItem(QListWidgetItem("- Office module not available on MacOS"))
        if WINDOWS and not OFFICE:
            self.statusListWidget.addItem(QListWidgetItem("- Office not installed"))
        if not CHROME:
            self.statusListWidget.addItem(QListWidgetItem("- Chrome not installed"))
        if not FIREFOX:
            self.statusListWidget.addItem(QListWidgetItem("- Firefox not installed"))
        if not EDGE:
            self.statusListWidget.addItem(QListWidgetItem("- Edge (chromium) not installed"))
        if not OPERA:
            self.statusListWidget.addItem(QListWidgetItem("- Opera not installed"))

    # triggered by "enable all" button on top of the UI
    # in some cases the checkbox should be enabled only if the program is installed in the system
    def setCheckboxChecked(self):

        if not self.allCBChecked:
            self.allCBChecked = True
            self.checkButton.setText('Disable all')
            self.checkButton.update()
        else:
            self.allCBChecked = False
            self.checkButton.setText('Enable all')
            self.checkButton.update()

        # System checkboxes
        self.systemLoggerClipboardCB.setChecked(self.allCBChecked)
        self.systemLoggerProgramsCB.setChecked(self.allCBChecked)
        self.officeExcelCB.setChecked(self.allCBChecked)
        self.systemLoggerFilesFolderCB.setChecked(self.allCBChecked)

        if WINDOWS:
            self.systemLoggerHotkeysCB.setChecked(self.allCBChecked)
            self.systemLoggerUSBCB.setChecked(self.allCBChecked)
            self.systemLoggerEventsCB.setChecked(self.allCBChecked)

        # office checkboxes
        if WINDOWS and OFFICE:
            self.officeWordCB.setChecked(self.allCBChecked)
            self.officePowerpointCB.setChecked(self.allCBChecked)
            self.officeOutlookCB.setChecked(self.allCBChecked)

        # browser checkboxes
        if CHROME:
            self.browserChromeCB.setChecked(self.allCBChecked)
        if FIREFOX:
            self.browserFirefoxCB.setChecked(self.allCBChecked)
        if EDGE:
            self.browserEdgeCB.setChecked(self.allCBChecked)
        if OPERA:
            self.browserOperaCB.setChecked(self.allCBChecked)

        # Create a dialog to select a file and return its path
        # Used if the user wants to select an existing file for logging excel
        # (not implemented in gui)
    @staticmethod
    def getFilenameDialog(customDialog=True, title="Open", hiddenItems=False, isFolder=False, forOpen=True,
                          directory='',
                          filter_format=''):

        options = QFileDialog.Options()
        if customDialog:
            options |= QFileDialog.DontUseNativeDialog
            options |= QFileDialog.DontUseCustomDirectoryIcons

        dialog = QFileDialog()
        dialog.setOptions(options)
        dialog.setWindowTitle(title)

        if hiddenItems:
            dialog.setFilter(dialog.filter() | QDir.Hidden)

        # Files or folders
        if isFolder:
            dialog.setFileMode(QFileDialog.DirectoryOnly)
        else:
            # dialog.setFileMode(QFileDialog.AnyFile)
            dialog.setFileMode(QFileDialog.ExistingFiles)

        # Opening or saving
        if forOpen:
            dialog.setAcceptMode(QFileDialog.AcceptOpen)
        else:
            dialog.setAcceptMode(QFileDialog.AcceptSave)

        # Set format
        if filter_format != '' and isFolder is False:
            # dialog.setDefaultSuffix(filter_format)
            dialog.setNameFilters([filter_format])

        # starting directory
        if directory != '':
            dialog.setDirectory(str(directory))
        else:
            dialog.setDirectory(DESKTOP)

        if dialog.exec_() == QDialog.Accepted:
            path = dialog.selectedFiles()  # returns a list
            return path
        else:
            return []

    def handlePreferences(self):
        self.preferencesDialog.show()

    def handleMerge(self):
        csv_to_merge = self.getFilenameDialog(customDialog=False,
                                              title='Select CSV to merge',
                                              filter_format="CSV log files (*.csv)")
        if csv_to_merge:
            self.handleProcessMining(sorted(csv_to_merge))
        else:
            print("[GUI] Select multiple csv to join")

    # detect what modules should be run based on selected checkboxes in UI
    def handleCheckBox(self):
        tag = self.sender().tag
        checked = self.sender().isChecked()
        if (tag == "systemLoggerFilesFolder"):
            self.systemLoggerFilesFolder = checked
        elif (tag == "systemLoggerPrograms"):
            self.systemLoggerPrograms = checked
        elif (tag == "systemLoggerClipboard"):
            self.systemLoggerClipboard = checked
        elif (tag == "systemLoggerHotkeys"):
            self.systemLoggerHotkeys = checked
        elif (tag == "systemLoggerUSB"):
            self.systemLoggerUSB = checked
        elif (tag == "systemLoggerEvents"):
            self.systemLoggerEvents = checked
        elif (tag == "officeExcel"):
            self.officeExcel = checked
        elif (tag == "officeWord"):
            self.officeWord = checked
        elif (tag == "officePowerpoint"):
            self.officePowerpoint = checked
        elif (tag == "officeOutlook"):
            self.officeOutlook = checked
        elif (tag == "browserChrome"):
            self.browserChrome = checked
        elif (tag == "browserFirefox"):
            self.browserFirefox = checked
        elif (tag == "browserEdge"):
            self.browserEdge = checked
        elif (tag == "browserOpera"):
            self.browserOpera = checked

    def handleRPA(self, log_filepath):
        # generate RPA actions from log file just saved.
        rpa = utils.generateRPAScript.RPAScript(log_filepath)
        rpa_success = rpa.run()
        msg = f"- RPA generated in /RPA/{getFilename(log_filepath)}"
        self.statusListWidget.addItem(QListWidgetItem(msg))

    def handleProcessMining(self, log_filepath: list):
        try:
            # check if library is installed
            import pm4py
            # create class, combine all csv into one
            pm = utils.process_mining.ProcessMining(log_filepath)

            # create high level DFG model based on all logs
            pm.highLevelDFG()

            # calculate high level bpmn and petri net based on dfg
            pm.createGraphs()

            # open BPMN
            utils.utils.open_file(
                os.path.join(pm.discovery_path,
                             f'{utils.utils.getFilename(log_filepath[-1]).strip("_combined")}_BPMN.pdf')
            )

            # ask if some fields should be changed before generating RPA script
            # build choices dialog, passing low level most frequent case to analyze
            choicesDialog = utils.choicesDialog.ChoicesDialog(pm.mostFrequentCase)
            # when OK button is pressed
            if choicesDialog.exec_() in [0, 1]:
                mostFrequentCase = choicesDialog.df

                # create RPA based on most frequent path
                rpa = utils.generateRPAScript.RPAScript(log_filepath[-1])
                rpa.generateRPAMostFrequentPath(mostFrequentCase)

                pm.createGraphs(mostFrequentCase)

        except ImportError:
            print(
                "[GUI] Can't apply process mining techniques because 'pm4py' module is not installed."
                "See https://github.com/marco2012/ComputerLogger#PM4PY")
            # reset counter and list
            self.runCount = 0
            self.csv_to_join.clear()
            return False

    # Generate xes file from multiple csv, each csv corresponds to a trace
    def handleRunCount(self, log_filepath):

        if utils.utils.CSVEmpty(log_filepath):
            print(f"[GUI] CSV log {os.path.basename(log_filepath)} emtpy, skipping")
            return False
        else:
            # contains paths of csv to join
            self.csv_to_join.append(log_filepath)

        self.runCount += 1

        totalRunCount = utils.config.MyConfig.get_instance().totalNumberOfRunGuiXes
        print(f"[GUI] Run count = {self.runCount}, Total = {totalRunCount}")
        self.statusListWidget.addItem(QListWidgetItem(f"- Run {self.runCount} of {totalRunCount}"))

        # after each run append generated csv log to list, when totalNumberOfRun is reached, xes file will be created
        # from these csv
        if self.runCount >= totalRunCount and self.csv_to_join:

            self.handleProcessMining(self.csv_to_join)

            # reset counter and list
            self.runCount = 0
            self.csv_to_join.clear()

    # Called when start button is clicked by user
    def onButtonClick(self):

        # start button clicked
        if not self.running:
            # set gui parameters
            self.running = True

            print("[GUI] Loading threads, please wait...")

            # start main process with the options selected in gui. It handles all other methods main method is
            # started as a process so it can be terminated once the button is clicked all the methods in the main
            # process are started as daemon threads so they are closed automatically when the main process is closed
            self.mainProcess = Process(target=mainLogger.startLogger, args=(
                self.systemLoggerFilesFolder,
                self.systemLoggerPrograms,
                self.systemLoggerClipboard,
                self.systemLoggerHotkeys,
                self.systemLoggerUSB,
                self.systemLoggerEvents,
                self.officeFilename,
                self.officeExcel,
                self.officeWord,
                self.officePowerpoint,
                self.officeOutlook,
                self.browserChrome,
                self.browserFirefox,
                self.browserEdge,
                self.browserOpera,
            ))

            self.mainProcess.start()

            self.createProgressDialog("Starting...", "Starting server...", 1500)

            self.statusListWidget.clear()
            self.compatibilityCheckMessage()

            self.runButton.setText('Stop logger')
            self.runButton.update()

            self.statusListWidget.addItem(QListWidgetItem("- Logging server running, recording logs..."))

        # stop button clicked
        else:
            # set gui parameters
            self.running = False

            self.createProgressDialog("Stopping...", "Stopping server...", 1500)

            self.runButton.setText('Start logger')
            self.runButton.update()

            self.compatibilityCheckMessage()
            self.statusListWidget.addItem(QListWidgetItem(f"- Logger stopped."))

            # stop main process, automatically closing all daemon threads in main process
            self.mainProcess.terminate()

            log_filepath = utils.config.MyConfig.get_instance().log_filepath
            msg = f"[GUI] Log saved as {os.path.basename(log_filepath)}"
            print(msg)
            self.statusListWidget.addItem(QListWidgetItem(f"- {msg.strip('[GUI] ')}"))

            # once log file is created, RPA actions are automatically generated for each category
            # self.handleRPA(log_filepath)
            # generate xes file from combined csv
            self.handleRunCount(log_filepath)

            # kill node server when closing python server, otherwise port remains occupied
            if MAC and self.officeExcel:
                os.system("pkill -f node")

            print("[GUI] Logger stopped")


def buildGUI():
    app = QApplication(sys.argv)
    mainApplication = MainApplication()
    mainApplication.show()
    sys.exit(app.exec_())
