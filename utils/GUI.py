from PyQt5.QtCore import QDateTime, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox,
                             QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel,
                             QPushButton, QSizePolicy, QSpacerItem,
                             QStyleFactory, QTabWidget, QVBoxLayout, QWidget)
from multiprocessing import Process
import mainLogger
from platform import system
import sys
sys.path.append('../')  # this way main file is visible from this file


class WidgetGallery(QDialog):
    def __init__(self, parent=None):
        super(WidgetGallery, self).__init__(parent)
        self.originalPalette = QApplication.palette()
        self.setWindowTitle("ComputerLogger")
        self.setStyle()

        # create layouts
        self.createSystemLoggerGroupBox()
        self.createOfficeLoggerGroupBox()
        self.createBrowserLoggerGroupBox()
        self.createStartButton()
        self.createTopLayout()
        self.createBottomLayout()
        self.createStatusLayout()

        self.platformCheck()

        # Variables
        self.running = False
        self.mainProcess = None
        # Boolean variables that save the state of each checkbox
        self.systemLoggerFilesFolder = self.systemLoggerFilesFolderCB.isChecked()
        self.systemLoggerPrograms = self.systemLoggerPrograms.isChecked()
        self.systemLoggerClipboard = self.systemLoggerClipboard.isChecked()
        self.officeExcel = self.officeExcel.isChecked()
        self.officeWord = self.officeWord.isChecked()
        self.officePowerpoint = self.officePowerpoint.isChecked()
        self.officeAccess = self.officeAccess.isChecked()
        self.browserChrome = self.browserChrome.isChecked()
        self.browserFirefox = self.browserFirefox.isChecked()

        mainLayout = QGridLayout()
        mainLayout.addLayout(self.topLayout, 0, 0, 1, 2)
        mainLayout.addWidget(self.topLeftGroupBox, 1, 0)
        mainLayout.addWidget(self.topRightGroupBox, 1, 1)
        mainLayout.addWidget(self.bottomLeftTabWidget, 2, 0)
        # mainLayout.addWidget(self.bottomRightGroupBox, 2, 1)
        mainLayout.addLayout(self.bottomLayout, 3, 0, 1, 2)
        mainLayout.addLayout(self.statusLayout, 4, 0, 1, 2)
        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(2, 1)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)
        self.setLayout(mainLayout)

    def createSystemLoggerGroupBox(self):
        self.topLeftGroupBox = QGroupBox("System logger")

        self.systemLoggerFilesFolderCB = QCheckBox("Files/Folders")
        self.systemLoggerFilesFolderCB.setChecked(True)
        self.systemLoggerFilesFolderCB.tag = "systemLoggerFilesFolder"
        self.systemLoggerFilesFolderCB.stateChanged.connect(
            self.handleCheckBox)

        self.systemLoggerProgramsCB = QCheckBox("Programs")
        self.systemLoggerProgramsCB.setChecked(True)
        self.systemLoggerProgramsCB.tag = "systemLoggerPrograms"
        self.systemLoggerProgramsCB.stateChanged.connect(self.handleCheckBox)

        self.systemLoggerClipboardCB = QCheckBox("Clipboard")
        self.systemLoggerClipboardCB.setChecked(True)
        self.systemLoggerClipboardCB.tag = "systemLoggerClipboard"
        self.systemLoggerClipboardCB.stateChanged.connect(self.handleCheckBox)

        layout = QVBoxLayout()
        layout.addWidget(self.systemLoggerFilesFolderCB)
        layout.addWidget(self.systemLoggerProgramsCB)
        layout.addWidget(self.systemLoggerClipboardCB)
        layout.addStretch(1)

        self.topLeftGroupBox.setLayout(layout)

    def createOfficeLoggerGroupBox(self):

        self.topRightGroupBox = QGroupBox("Office logger")

        self.officeExcelCB = QCheckBox("Excel")
        self.officeExcelCB.setChecked(False)
        self.officeExcelCB.tag = "officeExcel"
        self.officeExcelCB.stateChanged.connect(self.handleCheckBox)

        self.officeWordCB = QCheckBox("Word")
        self.officeWordCB.setChecked(False)
        self.officeWordCB.tag = "officeWord"
        self.officeWordCB.stateChanged.connect(self.handleCheckBox)

        self.officePowerpointCB = QCheckBox("PowerPoint")
        self.officePowerpointCB.setChecked(False)
        self.officePowerpointCB.tag = "officePowerpoint"
        self.officePowerpointCB.stateChanged.connect(self.handleCheckBox)

        self.officeAccessCB = QCheckBox("Access")
        self.officeAccessCB.setChecked(False)
        self.officeAccessCB.tag = "officeAccess"
        self.officeAccessCB.stateChanged.connect(self.handleCheckBox)

        layout = QVBoxLayout()
        layout.addWidget(self.officeExcelCB)
        layout.addWidget(self.officeWordCB)
        layout.addWidget(self.officePowerpointCB)
        layout.addWidget(self.officeAccessCB)
        layout.addStretch(1)

        self.topRightGroupBox.setLayout(layout)

    def createBrowserLoggerGroupBox(self):
        self.bottomLeftTabWidget = QGroupBox("Browser logger")

        self.browserChromeCB = QCheckBox("Google Chrome")
        self.browserChromeCB.setChecked(True)
        self.browserChromeCB.tag = "browserChrome"
        self.browserChromeCB.stateChanged.connect(self.handleCheckBox)

        self.browserFirefoxCB = QCheckBox("Mozilla Firefox")
        self.browserFirefoxCB.setChecked(True)
        self.browserFirefoxCB.tag = "browserFirefox"
        self.browserFirefoxCB.stateChanged.connect(self.handleCheckBox)

        layout = QVBoxLayout()
        layout.addWidget(self.browserChromeCB)
        layout.addWidget(self.browserFirefoxCB)
        layout.addStretch(1)

        self.bottomLeftTabWidget.setLayout(layout)

    def createStartButton(self):
        self.runButton = QPushButton("Start logger")
        self.runButton.setCheckable(True)
        self.runButton.setChecked(False)
        self.runButton.clicked.connect(self.onButtonClick)

    def createTopLayout(self):
        self.topLayout = QVBoxLayout()
        self.topLayout.addWidget(QLabel("Select modules to activate"))
        verticalSpacer = QSpacerItem(
            20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.topLayout.addItem(verticalSpacer)

    def createBottomLayout(self):
        self.bottomLayout = QHBoxLayout()
        self.bottomLayout.addStretch(1)
        self.bottomLayout.addWidget(self.runButton)
        self.bottomLayout.addStretch(1)

    def createStatusLayout(self):
        if system() == 'Windows':
            MONOSPACE_FONT = 'Lucida Console'
        elif system() == 'Darwin':
            MONOSPACE_FONT = 'Monaco'
        else:
            MONOSPACE_FONT = 'monospace'
        self.statusLayout = QHBoxLayout()
        self.statusLabel = QLabel("")
        font = QFont(MONOSPACE_FONT, 12, QFont.Normal)
        font.setFamily("Courier")
        # font.setItalic(True)
        self.statusLabel.setFont(font)
        self.statusLayout.addStretch(1)
        self.statusLayout.addWidget(self.statusLabel)
        self.statusLayout.addStretch(1)

    def setStyle(self):
        if (system() == "Windows"):
            QApplication.setStyle(QStyleFactory.create('windowsvista'))
        elif (system() == "Darwin"):
            QApplication.setStyle(QStyleFactory.create('macintosh'))
        else:
            QApplication.setStyle(QStyleFactory.create('Fusion'))

    def platformCheck(self):
        # Office logging is not available on macos
        if system() == "Windows":
            pass
        if system() == "Darwin":
            self.topRightGroupBox.setEnabled(False)

            self.systemLoggerProgramsCB.setChecked(False)
            self.systemLoggerProgramsCB.setDisabled(True)

    def handleCheckBox(self, state):
        tag = self.sender().tag
        checked = self.sender().isChecked()
        if (tag == "systemLoggerFilesFolder"):
            self.systemLoggerFilesFolder = checked
        elif (tag == "systemLoggerPrograms"):
            self.systemLoggerPrograms = checked
        elif (tag == "systemLoggerClipboard"):
            self.systemLoggerClipboard = checked
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

    def onButtonClick(self):
        if not self.running:  # start button clicked

            # set gui parameters
            self.running = True

            self.statusLabel.setText('Logger running...')
            self.statusLabel.setStyleSheet('color: green')
            self.statusLabel.update()

            self.runButton.setText('Stop logger')
            self.runButton.update()

            # start main process with the options selected in gui. It handles all other methods
            # main method is started as a process so it can be terminated once the button is clicked
            # all the methods in the main process are started as daemon threads so they are closed automatically when the main process is closed
            self.mainProcess = Process(target=mainLogger.startLogger, args=[
                self.systemLoggerFilesFolder,
                self.systemLoggerPrograms,
                self.systemLoggerClipboard,
                self.officeExcel,
                self.officeWord,
                self.officePowerpoint,
                self.officeAccess,
                self.browserChrome,
                self.browserFirefox
            ])
            self.mainProcess.start()

            print("Logger started, selected threads activated...")

        else:  # stop button clicked

            # set gui parameters
            self.running = False

            self.statusLabel.setText("Logger stopped")
            self.statusLabel.setStyleSheet('color: black')
            self.statusLabel.update()

            self.runButton.setText('Start logger')
            self.runButton.update()

            # stop main process, automatically closing all daemon threads in main process
            self.mainProcess.terminate()

            print(
                "Main process terminated, daemon threads closed, wainting for new input...")


def buildGUI():
    app = QApplication(sys.argv)
    d = QDialog(None, Qt.WindowSystemMenuHint | Qt.WindowTitleHint)
    # setWindowFlags(windowFlags() & ~Qt::WindowContextHelpButtonHint)
    gallery = WidgetGallery()
    gallery.resize(350, 350)
    gallery.show()
    sys.exit(app.exec_())
