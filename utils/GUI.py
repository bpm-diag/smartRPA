import sys
sys.path.append('../')  # this way main file is visible from this file
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QTextCursor
from PyQt5.QtWidgets import (QApplication, QCheckBox, QDialog, QGridLayout,
                             QGroupBox, QHBoxLayout, QLabel, QPushButton,
                             QStyleFactory, QVBoxLayout, QListWidget, QListWidgetItem, QAbstractItemView)
import darkdetect
from multiprocessing import Process
from utils.utils import *
import mainLogger

# Test GUI without starting main server, must be set to False to start main
UI_DEBUG = False

# Shows text area below start button with log information about the execution of the program
SHOW_STATUS_TEXTEDIT = True


class WidgetGallery(QDialog):
    def __init__(self, parent=None):
        super(WidgetGallery, self).__init__(parent)
        self.originalPalette = QApplication.palette()
        self.setWindowTitle("ComputerLogger")
        self.setAppIcon()
        self.setStyle()

        # create layouts
        self.createSystemLoggerGroupBox()
        self.createOfficeLoggerGroupBox()
        self.createBrowserLoggerGroupBox()
        self.createTopLayout()
        self.createStartButton()
        self.createBottomLayout()
        self.createStatusLayout()

        self.platformCheck()

        # Variables
        self.running = False
        self.mainProcess = None
        # Boolean variables that save the state of each checkbox
        self.systemLoggerFilesFolder = self.systemLoggerFilesFolderCB.isChecked()
        self.systemLoggerPrograms = self.systemLoggerProgramsCB.isChecked()
        self.systemLoggerClipboard = self.systemLoggerClipboardCB.isChecked()
        self.systemLoggerHotkeys = self.systemLoggerHotkeysCB.isChecked()
        self.systemLoggerEvents = self.systemLoggerEventsCB.isChecked()
        self.officeExcel = self.officeExcelCB.isChecked()
        self.officeWord = self.officeWordCB.isChecked()
        self.officePowerpoint = self.officePowerpointCB.isChecked()
        self.officeAccess = self.officeAccessCB.isChecked()
        self.browserChrome = self.browserChromeCB.isChecked()
        self.browserFirefox = self.browserFirefoxCB.isChecked()

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
        self.setLayout(mainLayout)

    def createSystemLoggerGroupBox(self):
        self.systemGroupBox = QGroupBox("System logger")

        self.systemLoggerFilesFolderCB = QCheckBox("Files/Folders")
        self.systemLoggerFilesFolderCB.tag = "systemLoggerFilesFolder"
        self.systemLoggerFilesFolderCB.stateChanged.connect(
            self.handleCheckBox)
        self.systemLoggerFilesFolderCB.setToolTip("Log edits on files and folder like create, modify, delete and more")

        self.systemLoggerProgramsCB = QCheckBox("Programs")
        self.systemLoggerProgramsCB.tag = "systemLoggerPrograms"
        self.systemLoggerProgramsCB.stateChanged.connect(self.handleCheckBox)
        self.systemLoggerProgramsCB.setToolTip("Log opening and closing of programs")

        self.systemLoggerClipboardCB = QCheckBox("Clipboard")
        self.systemLoggerClipboardCB.tag = "systemLoggerClipboard"
        self.systemLoggerClipboardCB.stateChanged.connect(self.handleCheckBox)
        self.systemLoggerClipboardCB.setToolTip("Log clipboard copy")

        self.systemLoggerHotkeysCB = QCheckBox("Hotkeys")
        self.systemLoggerHotkeysCB.tag = "systemLoggerHotkeys"
        self.systemLoggerHotkeysCB.stateChanged.connect(self.handleCheckBox)
        self.systemLoggerHotkeysCB.setToolTip("Log system-wide hotkeys")

        self.systemLoggerEventsCB = QCheckBox("Events")
        self.systemLoggerEventsCB.tag = "systemLoggerEvents"
        self.systemLoggerEventsCB.stateChanged.connect(self.handleCheckBox)
        self.systemLoggerEventsCB.setToolTip("Log edits on files and folder")

        layout = QVBoxLayout()
        layout.addWidget(self.systemLoggerFilesFolderCB)
        layout.addWidget(self.systemLoggerProgramsCB)
        layout.addWidget(self.systemLoggerClipboardCB)
        layout.addWidget(self.systemLoggerHotkeysCB)
        layout.addWidget(self.systemLoggerEventsCB)

        self.systemGroupBox.setLayout(layout)

    def createOfficeLoggerGroupBox(self):
        self.officeGroupBox = QGroupBox("Office logger")
        self.officeGroupBox.setToolTip("Log all activities in Office applications \nlike opening, closing, editing documents and more")

        self.officeExcelCB = QCheckBox("Excel")
        self.officeExcelCB.tag = "officeExcel"
        self.officeExcelCB.stateChanged.connect(self.handleCheckBox)

        self.officeWordCB = QCheckBox("Word")
        self.officeWordCB.tag = "officeWord"
        self.officeWordCB.stateChanged.connect(self.handleCheckBox)

        self.officePowerpointCB = QCheckBox("PowerPoint")
        self.officePowerpointCB.tag = "officePowerpoint"
        self.officePowerpointCB.stateChanged.connect(self.handleCheckBox)

        self.officeAccessCB = QCheckBox("Access")
        self.officeAccessCB.tag = "officeAccess"
        self.officeAccessCB.stateChanged.connect(self.handleCheckBox)

        layout = QVBoxLayout()
        layout.addWidget(self.officeExcelCB)
        layout.addWidget(self.officeWordCB)
        layout.addWidget(self.officePowerpointCB)
        layout.addWidget(self.officeAccessCB)
        layout.addStretch(1)

        self.officeGroupBox.setLayout(layout)

    def createBrowserLoggerGroupBox(self):
        self.browserGroupBox = QGroupBox("Browser logger")
        self.browserGroupBox.setToolTip("Log all browser events in the window (like opening, closing tabs, printing, etc) \nand in the page (like clicking, zooming, pasting, etc)")

        self.browserChromeCB = QCheckBox("Google Chrome")
        self.browserChromeCB.tag = "browserChrome"
        self.browserChromeCB.stateChanged.connect(self.handleCheckBox)

        self.browserFirefoxCB = QCheckBox("Mozilla Firefox")
        self.browserFirefoxCB.tag = "browserFirefox"
        self.browserFirefoxCB.stateChanged.connect(self.handleCheckBox)

        layout = QVBoxLayout()
        layout.addWidget(self.browserChromeCB)
        layout.addWidget(self.browserFirefoxCB)
        layout.addStretch(1)

        self.browserGroupBox.setLayout(layout)

    def createStartButton(self):
        self.runButton = QPushButton("Start logger")
        self.runButton.setCheckable(True)
        self.runButton.setChecked(False)
        self.runButton.clicked.connect(self.onButtonClick)
        self.runButton.toggled.connect(self.systemGroupBox.setDisabled)
        self.runButton.toggled.connect(self.browserGroupBox.setDisabled)
        self.runButton.toggled.connect(self.checkButton.setDisabled)
        if WINDOWS:
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

        # self.statusLabel = QLabel("")

        font = QFont(monospaceFont, fontSize, QFont.Normal)

        # self.statusLabel.setFont(font)

        # self.statusLayout.addStretch(1)
        # self.statusLayout.addWidget(self.statusLabel)
        # self.statusLayout.addStretch(1)

        self.statusTextEdit = QListWidget()
        self.statusTextEdit.setFont(font)
        self.statusTextEdit.setSelectionMode(QAbstractItemView.NoSelection)

        if SHOW_STATUS_TEXTEDIT:
            self.statusLayout.addWidget(self.statusTextEdit)


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
            self.resize(520, 480)
            # margins
            self.topLayout.setContentsMargins(0, 0, 0, 20)
            self.bottomLayout.setContentsMargins(0, 20, 0, 20)
            # disable checkbox if corresponding program is not installed in system
            if not OFFICE:
                self.officeGroupBox.setEnabled(False)
                self.officeExcelCB.setChecked(False)
                self.officeWordCB.setChecked(False)
                self.officePowerpointCB.setChecked(False)
                self.officeAccessCB.setChecked(False)
                self.officeExcel = False
                self.officeWord = False
                self.officePowerpoint = False
                self.officeAccess = False

        elif MAC or LINUX:
            # office is not supported on mac
            self.officeGroupBox.setEnabled(False)

            # program logger is not supported on mac
            self.systemLoggerProgramsCB.setChecked(False)
            self.systemLoggerProgramsCB.setDisabled(True)

            # window size
            self.resize(360, 420)

            # margins
            self.topLayout.setContentsMargins(0, 0, 0, 10)
            self.bottomLayout.setContentsMargins(0, 0, 0, 0)

        if not CHROME:
            self.browserChromeCB.setEnabled(False)
            self.browserChromeCB.setChecked(False)
            self.browserChrome = False

        if not FIREFOX:
            self.browserFirefoxCB.setEnabled(False)
            self.browserChromeCB.setChecked(False)
            self.browserFirefox = False

        self.compatibilityCheckMessage()

    def compatibilityCheckMessage(self):
        if MAC:
            self.statusTextEdit.addItem(QListWidgetItem("- Office module not available on MacOS"))
        if (WINDOWS and not OFFICE) or not CHROME or not FIREFOX:
            self.statusTextEdit.addItem(QListWidgetItem("- Some modules disabled, programs not installed"))

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
        self.systemLoggerFilesFolderCB.setChecked(self.allCBChecked)
        self.systemLoggerProgramsCB.setChecked(self.allCBChecked)
        self.systemLoggerClipboardCB.setChecked(self.allCBChecked)
        self.systemLoggerHotkeysCB.setChecked(self.allCBChecked)
        self.systemLoggerEventsCB.setChecked(self.allCBChecked)

        # office checkboxes
        if WINDOWS and OFFICE:
            self.officeExcelCB.setChecked(self.allCBChecked)
            self.officeWordCB.setChecked(self.allCBChecked)
            self.officePowerpointCB.setChecked(self.allCBChecked)
            self.officeAccessCB.setChecked(self.allCBChecked)

        # browser checkboxes
        if CHROME:
            self.browserChromeCB.setChecked(self.allCBChecked)
        if FIREFOX:
            self.browserFirefoxCB.setChecked(self.allCBChecked)

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
        elif (tag == "systemLoggerEvents"):
            self.systemLoggerEvents = checked
        elif (tag == "officeExcel"):
            self.officeExcel = checked
        elif (tag == "officeWord"):
            self.officeWord = checked
        elif (tag == "officePowerpoint"):
            self.officePowerpoint = checked
        elif (tag == "officeAccess"):
            self.officeAccess = checked
        elif (tag == "browserChrome"):
            self.browserChrome = checked
        elif (tag == "browserFirefox"):
            self.browserFirefox = checked

    # Called when start button is clicked by user
    def onButtonClick(self):

        if not self.running:  # start button clicked

            # set gui parameters
            self.running = True

            # self.statusLabel.setText('Logger running')
            # self.statusLabel.setStyleSheet('color: green')
            # self.statusLabel.update()
            # item.setFont(self.font)
            self.statusTextEdit.clear()
            self.compatibilityCheckMessage()
            # self.statusTextEdit.addItem(QListWidgetItem("- Activating selected modules in threads"))
            self.statusTextEdit.addItem(QListWidgetItem("- Logging server running, recording logs..."))

            self.runButton.setText('Stop logger')
            self.runButton.update()

            # start main process with the options selected in gui. It handles all other methods
            # main method is started as a process so it can be terminated once the button is clicked
            # all the methods in the main process are started as daemon threads so they are closed automatically when the main process is closed
            self.mainProcess = Process(target=mainLogger.startLogger, args=(
                self.systemLoggerFilesFolder,
                self.systemLoggerPrograms,
                self.systemLoggerClipboard,
                self.systemLoggerHotkeys,
                self.systemLoggerEvents,
                self.officeExcel,
                self.officeWord,
                self.officePowerpoint,
                self.officeAccess,
                self.browserChrome,
                self.browserFirefox
            ))

            if not UI_DEBUG:
                self.mainProcess.start()

            print("Logger started, selected threads activated...")

        else:  # stop button clicked

            # set gui parameters
            self.running = False

            # self.statusLabel.setText("Logger stopped")
            # self.statusLabel.setStyleSheet('color: gray')
            # self.statusLabel.update()
            # self.statusTextEdit.appendPlainText("- Logger stopped")
            # self.statusTextEdit.appendPlainText("- Threads stopped")
            # self.statusTextEdit.update()
            self.statusTextEdit.addItem(QListWidgetItem(f"- Logger stopped."))

            self.runButton.setText('Start logger')
            self.runButton.update()

            # stop main process, automatically closing all daemon threads in main process
            if not UI_DEBUG:
                self.mainProcess.terminate()

            print(
                "Main process terminated, daemon threads closed, wainting for new input...")


def buildGUI():
    app = QApplication(sys.argv)
    gallery = WidgetGallery()
    gallery.show()
    sys.exit(app.exec_())
