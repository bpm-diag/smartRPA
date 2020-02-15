import sys
sys.path.append('../')  # this way main file is visible from this file
from PyQt5.QtCore import Qt, QSize, QDir
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (QApplication, QCheckBox, QDialog, QGridLayout,
                             QGroupBox, QHBoxLayout, QLabel, QPushButton,
                             QStyleFactory, QVBoxLayout, QListWidget, QListWidgetItem,
                             QAbstractItemView, QFileDialog)
import darkdetect
from multiprocessing import Process
from utils.utils import *
import mainLogger

# Debugging
# Test the UI without starting main every time
DISABLE_MAIN = False
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
        self.officeFilename = None
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
        self.browserEdge = self.browserEdgeCB.isChecked()

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
        # layout.addWidget(self.officeAccessCB)
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

        self.browserEdgeCB = QCheckBox("Microsoft Edge")
        self.browserEdgeCB.tag = "browserEdge"
        self.browserEdgeCB.stateChanged.connect(self.handleCheckBox)

        layout = QVBoxLayout()
        layout.addWidget(self.browserChromeCB)
        layout.addWidget(self.browserFirefoxCB)
        layout.addWidget(self.browserEdgeCB)
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

        self.statusListWidget = QListWidget()
        self.statusListWidget.setFont(QFont(monospaceFont, fontSize, QFont.Normal))
        self.statusListWidget.setSelectionMode(QAbstractItemView.NoSelection)

        if SHOW_STATUS_TEXTEDIT:
            self.statusLayout.addWidget(self.statusListWidget)

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
            self.resize(600, 560)
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

            self.statusListWidget.setStyleSheet("QListWidget{background: #F0F0F0;}")

        elif MAC or LINUX:
            # office is not supported on mac
            self.officeGroupBox.setEnabled(False)

            # program logger is not supported on mac
            self.systemLoggerProgramsCB.setChecked(False)
            self.systemLoggerProgramsCB.setDisabled(True)

            self.browserEdgeCB.setDisabled(True)

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
            self.browserChromeCB.setChecked(False)
            self.browserFirefox = False

        self.compatibilityCheckMessage()

    def compatibilityCheckMessage(self):
        self.statusListWidget.clear()
        if MAC:
            self.statusListWidget.addItem(QListWidgetItem("- Office, Edge modules not available on MacOS"))
        if WINDOWS and not OFFICE:
            self.statusListWidget.addItem(QListWidgetItem("- Office disabled because not installed"))
        if WINDOWS and not EDGE:
            self.statusListWidget.addItem(QListWidgetItem("- Edge disabled because not installed"))
        if not CHROME:
            self.statusListWidget.addItem(QListWidgetItem("- Chrome disabled because not installed"))
        if not FIREFOX:
            self.statusListWidget.addItem(QListWidgetItem("- Firefox disabled because not installed"))


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
        if EDGE:
            self.browserEdgeCB.setChecked(self.allCBChecked)

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
        elif (tag == "browserEdge"):
            self.browserEdge = checked

    # Create a dialog to select a file and return its path
    def getFilenameDialog(self, customDialog=True, title="Open",hiddenItems=False, isFolder=False, forOpen=True, directory='',
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
            dialog.setFileMode(QFileDialog.AnyFile)

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
            path = dialog.selectedFiles()[0]  # returns a list
            return path
        else:
            return ''

    # Called when start button is clicked by user
    def onButtonClick(self):

        # start button clicked
        if not self.running:
            # set gui parameters
            self.running = True

            # self.statusListWidget.clear()
            self.compatibilityCheckMessage()
            self.statusListWidget.addItem(QListWidgetItem("- Logging server running, recording logs..."))

            self.runButton.setText('Stop logger')
            self.runButton.update()

            # start main process with the options selected in gui. It handles all other methods main method is
            # started as a process so it can be terminated once the button is clicked all the methods in the main
            # process are started as daemon threads so they are closed automatically when the main process is closed
            self.mainProcess = Process(target=mainLogger.startLogger, args=(
                self.systemLoggerFilesFolder,
                self.systemLoggerPrograms,
                self.systemLoggerClipboard,
                self.systemLoggerHotkeys,
                self.systemLoggerEvents,
                self.officeFilename,
                self.officeExcel,
                self.officeWord,
                self.officePowerpoint,
                self.officeAccess,
                self.browserChrome,
                self.browserFirefox,
                self.browserEdge,
            ))

            if not DISABLE_MAIN:
                self.mainProcess.start()

            print("[GUI] Logger started")

        # stop button clicked
        else:
            # set gui parameters
            self.running = False

            self.compatibilityCheckMessage()
            self.statusListWidget.addItem(QListWidgetItem(f"- Logger stopped."))

            self.runButton.setText('Start logger')
            self.runButton.update()

            # stop main process, automatically closing all daemon threads in main process
            if not DISABLE_MAIN:
                self.mainProcess.terminate()

            print("[GUI] Main process terminated, daemon threads closed, wainting for new input...")


def buildGUI():
    app = QApplication(sys.argv)
    gallery = WidgetGallery()
    gallery.show()
    sys.exit(app.exec_())
