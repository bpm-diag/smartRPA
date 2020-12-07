# ****************************** #
# GUI
# Build native user interface and start main logger
# ****************************** #
from PyQt5.QtCore import Qt, QSize, QThreadPool, QTimer
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
from PyQt5.QtWidgets import (QApplication, QCheckBox, QDialog, QGridLayout,
                             QGroupBox, QHBoxLayout, QLabel, QPushButton,
                             QStyleFactory, QVBoxLayout, QListWidget, QListWidgetItem,
                             QAbstractItemView, QRadioButton, QProgressDialog,
                             QMainWindow, QWidget, QSlider, QLCDNumber, QMessageBox)
from modules.GUI.GUIThread import Worker
import darkdetect
from multiprocessing import Process, Queue
import webbrowser
import time
from modules.GUI.filenameDialog import getFilenameDialog
from utils.utils import *
import main
import modules.GUI.PreferencesWindow
import utils.config
import modules.flowchart
import modules.decisionPoints
import modules.RPA.generateRPAScript
import modules.process_mining
import utils.utils
import traceback
import sys

sys.path.append('../')  # this way main file is visible from this file


# import utils.xesConverter


class MainApplication(QMainWindow, QDialog):
    """
    GUI
    """

    def __init__(self, parent=None):
        """
        Initialize GUI

        """

        super(MainApplication, self).__init__(parent)
        self.originalPalette = QApplication.palette()
        self.setWindowTitle("SmartRPA")
        self.setAppIcon()
        self.setStyle()

        self.threadpool = QThreadPool()

        # queue used to send messages to GUI
        self.status_queue = Queue()
        # queue used to get filepath of current log
        self.LOG_FILEPATH = Queue()
        # queue used to kill processes before closing main, when pressing stop
        self.processesPID = Queue()

        self.createMenu()

        # create layouts
        self.createSystemLoggerGroupBox()
        self.createOfficeLoggerGroupBox()
        self.createBrowserLoggerGroupBox()
        self.createTopLayout()
        self.createStartButton()
        self.createBottomLayout()
        self.createStatusLayout()

        self.platformCheck()

        # Variables
        self.running = False
        self.mainProcess = None
        self.officeFilepath = None
        self.runCount = 0
        self.csv_to_join = list()

        # In action logger version, set preferences statically here
        utils.config.MyConfig.get_instance().totalNumberOfRunGuiXes = 1
        utils.config.MyConfig.get_instance().perform_process_discovery = False

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

        updateUIThread = Thread(target=self.updateListWidget)
        updateUIThread.daemon = True
        updateUIThread.start()

    def createMenu(self):
        """
        Create file menu with preferences and options to merge multiple CSV event logs and to analyze one event log.
        """
        menu = self.menuBar()

        # In the action logger version of the tool, I don't need RPA analysis so I remove reference

        fileMenu = menu.addMenu('File')
        #preferencesAction = fileMenu.addAction('Preferences...')
        #preferencesAction.triggered.connect(self.handlePreferences)
        mergeAction = fileMenu.addAction('Merge multiple CSV...')
        mergeAction.triggered.connect(self.handleMerge)
        #runLogAction = fileMenu.addAction('RPA from log...')
        #runLogAction.triggered.connect(self.handleRunLogAction)
        # self.preferencesDialog = modules.GUI.PreferencesWindow.Preferences(
        #     self, self.status_queue)

        helpMenu = menu.addMenu('Help')
        about = helpMenu.addAction('About')
        about.triggered.connect(self.showAboutMessage)

    def createSystemLoggerGroupBox(self):
        """
        Create checkboxes to log operating systems events like opening a program, editing files/folders, logging clipboard, hotkeys or usb drives insertion
        """
        self.systemGroupBox = QGroupBox("System logger")

        self.systemLoggerFilesFolderCB = QCheckBox("Files/Folders")
        self.systemLoggerFilesFolderCB.tag = "systemLoggerFilesFolder"
        self.systemLoggerFilesFolderCB.stateChanged.connect(
            self.handleCheckBox)
        self.systemLoggerFilesFolderCB.setToolTip(
            "Log edits on files and folder like create, modify, delete and more")

        self.systemLoggerClipboardCB = QCheckBox("Clipboard")
        self.systemLoggerClipboardCB.tag = "systemLoggerClipboard"
        self.systemLoggerClipboardCB.stateChanged.connect(self.handleCheckBox)
        self.systemLoggerClipboardCB.setToolTip("Log clipboard copy")

        self.systemLoggerProgramsCB = QCheckBox("Programs")
        self.systemLoggerProgramsCB.tag = "systemLoggerPrograms"
        self.systemLoggerProgramsCB.stateChanged.connect(self.handleCheckBox)
        self.systemLoggerProgramsCB.setToolTip(
            "Log opening and closing of programs")

        self.systemLoggerHotkeysCB = QCheckBox("Hotkeys")
        self.systemLoggerHotkeysCB.tag = "systemLoggerHotkeys"
        self.systemLoggerHotkeysCB.stateChanged.connect(self.handleCheckBox)
        self.systemLoggerHotkeysCB.setToolTip("Log system-wide hotkeys")

        self.systemLoggerUSBCB = QCheckBox("USB Drives")
        self.systemLoggerUSBCB.tag = "systemLoggerUSB"
        self.systemLoggerUSBCB.stateChanged.connect(self.handleCheckBox)
        self.systemLoggerUSBCB.setToolTip(
            "Log insertion and removal of usb drives")

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
        """
        Create checkboxes to log microsoft office applications like excel, word, powerpoint
        """

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
        """
        Create checkboxes to log browser events in chrome, firefox, edge or opera
        """
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
        """
        create button to start and stop action logger
        """
        self.runButton = QPushButton("Start logger")
        if darkdetect.isDark():
            self.runButton.setStyleSheet(
                'QPushButton {background-color: #656565;}')
        self.runButton.setCheckable(True)
        self.runButton.setChecked(False)
        self.runButton.clicked.connect(self.onButtonClick)
        self.runButton.toggled.connect(self.systemGroupBox.setDisabled)
        self.runButton.toggled.connect(self.browserGroupBox.setDisabled)
        self.runButton.toggled.connect(self.checkButton.setDisabled)
        self.runButton.toggled.connect(self.officeGroupBox.setDisabled)

    def createTopLayout(self):
        """
        create top layout with buttons to enable all modules at once
        """
        self.topLayout = QHBoxLayout()
        self.topLayout.addWidget(QLabel("Select modules to activate"))

        self.topLayout.addStretch(1)
        self.checkButton = QPushButton("Enable all")
        if darkdetect.isDark():
            self.checkButton.setStyleSheet('QPushButton {color: white;}')
        self.checkButton.setCheckable(True)
        self.checkButton.setChecked(False)
        self.checkButton.setFlat(True)
        self.allCBChecked = False
        self.checkButton.toggled.connect(self.setCheckboxChecked)

        self.topLayout.addWidget(self.checkButton)

    def createBottomLayout(self):
        """
        create bottom layout that contains button to start logging
        """
        self.bottomLayout = QHBoxLayout()
        self.bottomLayout.addStretch(1)
        self.bottomLayout.addWidget(self.runButton)
        self.bottomLayout.addStretch(1)

    def createStatusLayout(self):
        """
        create status layout, the window below the start button where all logging appears
        """
        if WINDOWS:
            monospaceFont = 'Lucida Console'
            fontSize = 8
        elif MAC:
            monospaceFont = 'Courier'
            fontSize = 12
        else:
            monospaceFont = 'monospace'
            fontSize = 11

        self.statusLayout = QVBoxLayout()

        self.statusListWidget = QListWidget()
        self.statusListWidget.setFont(
            QFont(monospaceFont, fontSize, QFont.Normal))
        self.statusListWidget.setSelectionMode(QAbstractItemView.NoSelection)
        if WINDOWS:
            self.statusListWidget.setFixedHeight(200)
        else:
            self.statusListWidget.setFixedHeight(140)
        # self.statusListWidget.setMinimumWidth(self.statusListWidget.sizeHintForColumn(0))
        self.statusListWidget.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff)
        self.statusListWidget.setWordWrap(True)
        self.statusListWidget.setTextElideMode(Qt.ElideNone)

        # old school green font
        # if darkdetect.isDark():
        #     self.statusListWidget.setStyleSheet('QListWidget::item {color: #00FF33;}')

        self.statusLayout.addWidget(self.statusListWidget)
        self.statusListWidget.addItem(QListWidgetItem(
            "Ready to log, press Start button..."))
        if not utils.config.MyConfig.get_instance().perform_process_discovery:
            self.status_queue.put("[GUI] Process discovery disabled")

    def createProgressDialog(self, title, message, timeout=None):
        """
        Create progress dialog displayed when starting or stopping the action logger

        :param title: title of progress dialog
        :param message: message of progress dialog
        :param timeout: timeout after which progress dialog automatically disappears
        :return: progress dialog
        """
        flags = Qt.WindowTitleHint | Qt.Dialog | Qt.WindowMaximizeButtonHint | Qt.CustomizeWindowHint
        self.progress_dialog = QProgressDialog(
            message, None, 0, 0, self, flags)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setWindowTitle(title)
        if WINDOWS:
            self.progress_dialog.resize(470, 100)
        else:
            self.progress_dialog.resize(260, 100)

        if timeout:
            self.progress_dialog.show()
            self.timer = QTimer(self)
            self.timer.start(timeout)
            self.timer.timeout.connect(self.cancelProgressDialog)

        return self.progress_dialog

    def cancelProgressDialog(self):
        """
        manually dismiss progress dialog
        """
        self.progress_dialog.done(0)
        self.timer.stop()
        self.timer.deleteLater()

    def setStyle(self):
        """
        set native GUI style for each OS
        """
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
        """
        set app icon with support to dark mode
        """
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

    def platformCheck(self):
        """
        set appropriate values based on platform.\n
        disable checkboxes not available on macOS like word and powerpoint.
        """

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

            self.statusListWidget.setStyleSheet(
                "QListWidget{background: #F0F0F0;}")

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
            self.resize(400, 420)

            # margins
            self.topLayout.setContentsMargins(0, 0, 0, 10)
            self.bottomLayout.setContentsMargins(0, 0, 0, 0)

            if darkdetect.isDark():
                self.statusListWidget.setStyleSheet(
                    "QListWidget{background: #3A3B3B;}")
            else:
                self.statusListWidget.setStyleSheet(
                    "QListWidget{background: #ECECEC;}")

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

        # self.compatibilityCheckMessage()

    def compatibilityCheckMessage(self):
        """
        Display message if a program like office, firefox, chrome, edge, opera is not installed in the operating system.
        """
        self.statusListWidget.clear()
        if MAC:
            self.statusListWidget.addItem(QListWidgetItem(
                "- Office module not available on MacOS"))
        if WINDOWS and not OFFICE:
            self.statusListWidget.addItem(
                QListWidgetItem("- Office not installed"))
        if not CHROME:
            self.statusListWidget.addItem(
                QListWidgetItem("- Chrome not installed"))
        if not FIREFOX:
            self.statusListWidget.addItem(
                QListWidgetItem("- Firefox not installed"))
        if not EDGE:
            self.statusListWidget.addItem(
                QListWidgetItem("- Edge (chromium) not installed"))
        if not OPERA:
            self.statusListWidget.addItem(
                QListWidgetItem("- Opera not installed"))

    def setCheckboxChecked(self):
        """
        triggered by "enable all" button on top of the UI
        in some cases the checkbox should be enabled only if the program is installed in the system
        """

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
        # (not implemented in GUI)

    def updateListWidget(self):
        """
        Reads status queue and updates log window below start logger button in the GUI
        """
        while 1:
            if not self.status_queue.empty():
                item = self.status_queue.get()
                print(item)
                self.statusListWidget.addItem(QListWidgetItem(item))
            time.sleep(0.5)

    def handleCheckBox(self):
        """
        detect which modules should be run based on selected checkboxes in UI
        """
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

    def handlePreferences(self):
        self.preferencesDialog.show()

    def handleRunLogAction(self):
        """
        This method is called when the user wants to perform RPA analysis on an event log.

        It calls the handleMerge method with parameters (merged=False, title='Select CSV to run', multipleItems=False)
        """
        return self.handleMerge(merged=False, title='Select CSV to run', multipleItems=False)

    def handleMerge(self, merged=True, title='Select multiple CSV to merge', multipleItems=True):
        """
        This method is called when the user wants to merge multiple csv files
        or run an event log (in this case it is called by the handleRunLogAction() method).

        1. It displays a file dialog to select the event logs to process; this dialog returns a list of paths,
        each one representing the location of an event log.

        2. After the event logs have been selected, the method starts a worker thread to process them
        using the handleProcessMining() method. A new thread is necessary in order not to block the main UI.

        3. Once the thread completes, the choices() method is called.

        :param merged: boolean value indicating if the user wants to merge multiple files or to run a single event log
        :param title: title of the file dialog
        :param multipleItems: boolean value indicating the ability to select multiple items
        """
        self.statusListWidget.clear()
        csv_to_merge = getFilenameDialog(customDialog=False,
                                         title=title,
                                         multipleItems=multipleItems,
                                         filter_format="CSV log files (*.csv)")
        if csv_to_merge:
            if merged:
                self.status_queue.put("[GUI] Merging selected files...")
            else:
                self.status_queue.put("[GUI] Analyzing selected log...")
            # self.progress_dialogMFP = self.createProgressDialog("Working...", "Finding most frequent path...")

            # start PM as thread because it can take some time, I don't want to block the UI
            worker = Worker(self.handleProcessMining, sorted(csv_to_merge),
                            merged)  # Any other args, kwargs are passed to the run function
            worker.signals.result.connect(self.PMThreadComplete)
            self.threadpool.start(worker)
        else:
            self.status_queue.put("[GUI] No csv selected...")

    def handleProcessMining(self, log_filepath: list, merged=False, fromRunCount=False):
        """
        This method can either be called by handleMerge() (when the user wants to merge multiple CSV or run RPA from log)
        or by the GUI after the user presses the Stop logger button.

        1. It creates an instance of the Process Mining class, passing the selected event log files.
        2. Then it returns the instance of the class along with the selected file path.

        :param log_filepath: list of paths pointing to event logs selected in the file dialog
        :param merged: boolean indicating if the logs have been merged
        :param fromRunCount: indicates whether the method has been called by handleMerge() or by the GUI
        :return: process mining class instance, log_filepath
        """
        try:
            # check if library is installed
            import pm4py
            # create class, combine all csv into one
            # print(f"[PROCESS MINING] Finding most frequent path...")
            pm = modules.process_mining.ProcessMining(
                log_filepath, self.status_queue, merged)
            if fromRunCount:
                self.PMThreadComplete((pm, log_filepath))
            else:
                return pm, log_filepath
        except ImportError:
            print(
                "[GUI] Can't apply process mining techniques because 'pm4py' module is not installed."
                "See https://github.com/bpm-diag/smartRPA#1-pm4py")
            # reset counter and list
            self.runCount = 0
            self.csv_to_join.clear()
            return False
        except PermissionError as e:
            print(f"[GUI] Process mining analysis exited with error: {e}")
            print(
                f"[GUI] Maybe the file is opened in another program. Close it and try again.")
            self.status_queue.put(
                f"Unable to open the file. Maybe it is opened in another program.")
            return False
        except Exception as e:
            print(f"[GUI] Process mining analysis exited with error: {e}")
            traceback.print_exc()
            print(traceback.format_exc())
            return False

    def PMThreadComplete(self, result):
        """
        Once the working thread started by handleMerge() finishes processing, the result is returned in this method,
        which in turns calls the choices() method
        """
        if result:
            pm, log_filepath = result
            self.choices(pm, log_filepath)

    def handleRPA(self, log_filepath):
        rpa = modules.RPA.generateRPAScript.RPAScript(
            log_filepath, self.status_queue)
        rpa_success = rpa.run()
        msg = f"- RPA generated in /RPA/{getFilename(log_filepath)}"
        self.statusListWidget.addItem(QListWidgetItem(msg))

    def choices(self, pm, log_filepath):
        """
        This method is called once the worker thread started by handleMerge() completes.

        It is the core of the tool, responsible for performing all the analysis on the event log,
        from log processing to RPA SW robot generation.

        If process discovery is enabled in preferences:

        * high level flowchart is generated from process mining class
        * high level petri net is generated from process mining class
        * events are logged in status queue

        If decision points analysis is enabled and there are at least 2 traces in the event log

        * high level DFG is opened
        * decision points class is called, the resulting decision dataframe is stored
        * new flowchart is generated from decided dataframe
        * choices dialog class is called, taking as input decided dataframe
        * final flowchart with user edits is generated
        * python SW robot is generated from RPAScript path
        * Uipath project is generated from UIPathXAML class

        :param pm: instance of the Process Mining class
        :param log_filepath: path of the event log to analyze
        """
        # print(f"[DEBUG] PM enabled = {utils.config.MyConfig.get_instance().perform_process_discovery}")
        if utils.config.MyConfig.get_instance().perform_process_discovery:
            num_traces = len(
                pm.dataframe['case:concept:name'].drop_duplicates())
            pm.highLevelDFG()
            pm.highLevelPetriNet()
            self.status_queue.put(f"[PROCESS MINING] Generated diagrams")

            # most frequent routine
            if utils.config.MyConfig.get_instance().enable_most_frequent_routine_analysis:
                # create high level DFG model based on most frequent routine
                # pm.highLevelBPMN()
                modules.flowchart.Flowchart(
                    pm.mostFrequentCase).generateFlowchart(pm.bpmn_path)

                # open high level BPMN
                utils.utils.open_file(pm.bpmn_path)

                # ask if some fields should be changed before generating RPA script
                # build choices dialog, passing low level most frequent case to analyze
                choicesDialog = modules.GUI.choicesDialog.ChoicesDialog(
                    pm.mostFrequentCase)
                # when OK button is pressed
                if choicesDialog.exec_() in [0, 1]:
                    mostFrequentCase = choicesDialog.df

                    # create RPA based on most frequent path
                    rpa = modules.RPA.generateRPAScript.RPAScript(
                        log_filepath[-1], self.status_queue)
                    rpa.generatePythonRPA(mostFrequentCase)

                    # pm.highLevelBPMN(df=mostFrequentCase, name="BPMN_final")
                    modules.flowchart.Flowchart(mostFrequentCase).generateFlowchart(
                        pm.bpmn_path, name="BPMN_final")

                    # create UiPath RPA script passing dataframe with only the most frequent trace
                    UiPath = modules.RPA.uipath.UIPathXAML(
                        log_filepath[-1], self.status_queue, mostFrequentCase)
                    UiPath.generateUiPathRPA()

            # decision
            elif utils.config.MyConfig.get_instance().enable_decision_point_analysis:

                if num_traces >= 2:
                    # open high level DFG
                    utils.utils.open_file(pm.dfg_path)

                    # ask what to do if decisions could be made
                    d = modules.decisionPoints.DecisionPoints(
                        pm.dataframe, self.status_queue)
                    decided_dataframe = d.generateDecisionDataframe()

                    # pm.highLevelBPMN(df=decided_dataframe, decisionPoints=True)
                    modules.flowchart.Flowchart(
                        decided_dataframe).generateFlowchart(pm.bpmn_path)

                    # open high level BPMN
                    utils.utils.open_file(pm.bpmn_path)

                    # ask if some fields should be changed before generating RPA script
                    # build choices dialog, passing low level most frequent case to analyze
                    choicesDialog = modules.GUI.choicesDialog.ChoicesDialog(
                        decided_dataframe)
                    # when OK button is pressed
                    if choicesDialog.exec_() in [0, 1]:
                        decided_dataframe_with_choices = choicesDialog.df

                        # pm.highLevelBPMN(df=decided_dataframe_with_choices, name="BPMN_final", decisionPoints=True)
                        modules.flowchart.Flowchart(decided_dataframe_with_choices).generateFlowchart(
                            pm.bpmn_path, name="BPMN_final")

                        # create RPA
                        rpa = modules.RPA.generateRPAScript.RPAScript(
                            log_filepath[-1], self.status_queue)
                        rpa.generatePythonRPA(decided_dataframe_with_choices)

                        self.status_queue.put(
                            f"[PROCESS MINING] Generated diagrams")

                        # create UiPath RPA script passing dataframe with only the most frequent trace
                        UiPath = modules.RPA.uipath.UIPathXAML(log_filepath[-1], self.status_queue,
                                                               decided_dataframe_with_choices)
                        UiPath.generateUiPathRPA()
                else:
                    self.status_queue.put(f"[GUI] Could not perform decision points analysis, "
                                          f"at least 2 traces are needed in the event log\n")

            # decision point in RPA script at run time
            elif utils.config.MyConfig.get_instance().enable_decision_point_RPA_analysis:
                # at least 2 traces are needed to perform decision analysis
                if num_traces >= 2:
                    # create UiPath RPA script passing dataframe of entire process
                    UiPath = modules.RPA.uipath.UIPathXAML(
                        log_filepath[-1], self.status_queue, pm.dataframe)
                    UiPath.generateUiPathRPA(decision=True)
                else:
                    self.status_queue.put(f"[GUI] Could not perform decision points analysis, "
                                          f"at least 2 traces are needed in the event log\n")

        self.status_queue.put(f"[GUI] Done\n")


    def handleRunCount(self, log_filepath):
        """
        Merges multiple traces of execution together generating one event log.
        It depends on "number of runs after which event log is generated" setting in preferences.

        :param log_filepath: path of event log file
        """
        # print(f"[DEBUG] CSV path: {log_filepath}")
        if utils.utils.CSVEmpty(log_filepath):
            self.status_queue.put(
                f"[GUI] Log file {os.path.basename(log_filepath)} is empty, removing")
            os.remove(log_filepath)
            return False
        else:
            # contains paths of csv to join
            self.csv_to_join.append(log_filepath)
            self.status_queue.put(
                f"[GUI] Log saved as {os.path.basename(log_filepath)}")

            self.runCount += 1

        totalRunCount = utils.config.MyConfig.get_instance().totalNumberOfRunGuiXes
        if self.runCount == totalRunCount:
            self.status_queue.put(
                f"[GUI] Run {self.runCount} of {totalRunCount}")
        else:
            self.status_queue.put(
                f"[GUI] Run {self.runCount} of {totalRunCount}, waiting for next run...")

        # after each run append generated csv log to list, when totalNumberOfRun is reached, xes file will be created
        # from these csv
        if self.runCount >= totalRunCount and self.csv_to_join:
            self.handleProcessMining(self.csv_to_join, fromRunCount=True)

            # reset counter and list
            self.runCount = 0
            self.csv_to_join.clear()

    def showAboutMessage(self):
        """
        Show information about the tool under File menu
        """
        msgBox = QMessageBox()
        msgBox.setWindowTitle("About")
        msgBox.setText("SmartRPA allows to train RPA routines in order to automatically find the best way "
                       "to perform a specific user task.")
        websiteBtn = QPushButton('Website')
        websiteBtn.clicked.connect(lambda: webbrowser.open(
            'https://github.com/bpm-diag/smartRPA'))
        msgBox.addButton(websiteBtn, QMessageBox.AcceptRole)
        closeBtn = QPushButton('Close')
        if darkdetect.isDark():
            closeBtn.setStyleSheet('QPushButton {background-color: #656565;}')
        msgBox.addButton(closeBtn, QMessageBox.RejectRole)
        msgBox.exec_()

    def excelDialog(self):
        """
        Displays file dialog when excel is selected in order to choose a file to open
        """
        if self.officeExcel:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Excel spreadsheet")
            msgBox.setText(
                "Do you want to open an existing Excel spreadsheet or create a new one?")
            existing = QPushButton('Open existing spreadsheet')
            new = QPushButton('Create new spreadsheet')
            if darkdetect.isDark():
                existing.setStyleSheet(
                    'QPushButton {background-color: #656565;}')
                new.setStyleSheet('QPushButton {background-color: #656565;}')
            msgBox.addButton(existing, QMessageBox.YesRole)
            msgBox.addButton(new, QMessageBox.NoRole)
            ret = msgBox.exec_()
            if ret == 0:
                path = getFilenameDialog(customDialog=False,
                                         title='Select Excel spreadsheet to open',
                                         multipleItems=False,
                                         filter_format="Excel files (*.csv *.xlsx *xls *.xlsm)")
                self.officeFilepath = path[0] if path else None

    def onButtonClick(self):
        """
        Main method executed by the tool to start log capture when start button is clicked by user.

        If tool is starting:

        * set boolean variable 'running' to true
        * check which checkboxes are enabled in the GUI
        * if excel checkbox is selected, display dialog to select file to open (deprecated)
        * start progress dialog indicating loading
        * start main process, passing as parameters the boolean checkbox values

        If tool is stopping:

        * set boolean variable 'running' to false
        * kill active processes using their PID before closing main
        * terminate main
        * call handleRunCount() method to check counter and generate event log file

        """

        if not any([self.systemLoggerFilesFolder,
                    self.systemLoggerPrograms,
                    self.systemLoggerClipboard,
                    self.systemLoggerHotkeys,
                    self.systemLoggerUSB,
                    self.systemLoggerEvents,
                    self.officeFilepath,
                    self.officeExcel,
                    self.officeWord,
                    self.officePowerpoint,
                    self.officeOutlook,
                    self.browserChrome,
                    self.browserFirefox,
                    self.browserEdge,
                    self.browserOpera]):
            self.status_queue.put(
                "[GUI] Select at least one module to start logging")

        # start button clicked
        elif not self.running:
            # set GUI parameters
            self.running = True

            self.statusListWidget.clear()

            # ask if user want to create new spreadsheet or open existing one
            # self.excelDialog()

            self.status_queue.put("[GUI] Loading, please wait...")
            self.createProgressDialog("Loading...", "Loading...", 3000)

            # start main process with the options selected in GUI. It handles all other methods main method is
            # started as a process so it can be terminated once the button is clicked all the methods in the main
            # process are started as daemon threads so they are closed automatically when the main process is closed
            self.mainProcess = Process(target=main.startLogger, args=(
                self.systemLoggerFilesFolder,
                self.systemLoggerPrograms,
                self.systemLoggerClipboard,
                self.systemLoggerHotkeys,
                self.systemLoggerUSB,
                self.systemLoggerEvents,
                self.officeFilepath,
                self.officeExcel,
                self.officeWord,
                self.officePowerpoint,
                self.officeOutlook,
                self.browserChrome,
                self.browserFirefox,
                self.browserEdge,
                self.browserOpera,
                self.status_queue,
                self.LOG_FILEPATH,
                self.processesPID
            ))

            self.mainProcess.start()

            self.runButton.setText('Stop logger')
            self.runButton.update()

        # stop button clicked
        else:
            # set GUI parameters
            self.running = False

            # self.createProgressDialog("Stopping...", "Stopping server...", 1500)

            self.runButton.setText('Start logger')
            self.runButton.update()

            # kill active processes before closing main
            while not self.processesPID.empty():
                pid = self.processesPID.get()
                try:
                    os.kill(pid, -9)
                except PermissionError:
                    print(
                        f"[GUI] Could not kill process {pid}, trying another way")
                    if WINDOWS:
                        try:
                            import subprocess
                            subprocess.check_output(f"Taskkill /F /PID {pid}")
                            print(f"[GUI] Process {pid} killed")
                        except Exception:
                            print(f"[GUI] Could not kill process {pid}")
                            pass
            # stop main process, automatically closing all daemon threads in main process
            self.mainProcess.terminate()

            self.status_queue.put(f"[GUI] Logger stopped")

            # once log file is created, RPA actions are automatically generated for each category
            # log_filepath = utils.config.MyConfig.get_instance().log_filepath
            if not self.LOG_FILEPATH.empty():
                main_log_filepath = self.LOG_FILEPATH.get()
                if main_log_filepath and os.path.exists(main_log_filepath):
                    self.handleRunCount(main_log_filepath)
            else:
                self.status_queue.put(
                    f"[GUI] Could not locate log file.")

            # kill node server when closing python server, otherwise port remains busy
            if MAC and self.officeExcel:
                os.system("pkill -f node")


def buildGUI():
    """
    Main method to build the GUI
    """
    app = QApplication(sys.argv)

    # dark mode
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(15, 15, 15))
    palette.setColor(QPalette.AlternateBase, QColor(101, 101, 101))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.ToolTipBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Button, QColor(0, 0, 0))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Highlight, QColor(142, 45, 197).lighter())
    palette.setColor(QPalette.HighlightedText, Qt.black)
    if darkdetect.isDark():
        app.setPalette(palette)

    mainApplication = MainApplication()
    mainApplication.show()
    sys.exit(app.exec_())
