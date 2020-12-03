# ****************************** #
# Main logger
# Handles all the threads of the application
# ****************************** #

import os
import sys
import time
from threading import Thread
from multiprocessing import Process, Queue
import utils.utils
import modules.GUI.GUI
import utils.config
import modules.consumerServer
import utils.utils
from modules.events import systemEvents, officeEvents, clipboardEvents


def startLogger(systemLoggerFilesFolder,
                systemLoggerPrograms,
                systemLoggerClipboard,
                systemLoggerHotkeys,
                systemLoggerUSB,
                systemLoggerEvents,
                excelFilepath,
                officeExcel,
                officeWord,
                officePowerpoint,
                officeOutlook,
                browserChrome,
                browserFirefox,
                browserEdge,
                browserOpera,
                status_queue,
                LOG_FILEPATH,
                processesPID
                ):
    """
    Main function where program starts.
    This method is called by the GUI when the user presses "start logger" button.
    All the values are passed by the GUI module

    :param systemLoggerFilesFolder: true if files/folder checkbox is checked in GUI
    :param systemLoggerPrograms: true if programs checkbox is checked in GUI
    :param systemLoggerClipboard: true if clipboard checkbox is checked in GUI
    :param systemLoggerHotkeys: true if hotkeys checkbox is checked in GUI
    :param systemLoggerUSB: true if usb checkbox is checked in GUI
    :param systemLoggerEvents: deprecated
    :param excelFilepath: contains path of excel file, default is None
    :param officeExcel: true if excel checkbox is checked in GUI
    :param officeWord: true if word checkbox is checked in GUI
    :param officePowerpoint: true if powerpoint checkbox is checked in GUI
    :param officeOutlook: true if outlook checkbox is checked in GUI
    :param browserChrome: true if chrome checkbox is checked in GUI
    :param browserFirefox: true if firefox checkbox is checked in GUI
    :param browserEdge: true if edge checkbox is checked in GUI
    :param browserOpera: true if opera checkbox is checked in GUI
    :param status_queue: Queue to print messages on GUI
    :param LOG_FILEPATH: path of the event log file
    :param processesPID: PID of started processes, used to kill them when logger is stopped
    """

    try:
        # create the threads as daemons so they are closed when main ends

        # ************
        # main logging server
        # ************
        log_filepath = utils.utils.createLogFile()
        # return log file to GUI so it can be processed
        LOG_FILEPATH.put(log_filepath)

        t0 = Thread(target=modules.consumerServer.runServer, args=[status_queue])
        t0.daemon = True
        t0.start()

        modules.consumerServer.log_filepath = log_filepath

        # ************
        # system logger
        # ************

        if systemLoggerClipboard:
            # log copy event
            t8 = Thread(target=clipboardEvents.logClipboard)
            t8.daemon = True
            t8.start()

            # only way to log paste event is to detect ctrl + v, but it should be started as process instead of thread
            # otherwise some events are lost
            if utils.utils.WINDOWS:
                t9 = Process(target=systemEvents.logPasteHotkey)
                # t9.daemon = True
                t9.start()
                processesPID.put(t9.pid)

        if systemLoggerFilesFolder:

            if utils.utils.WINDOWS:
                t1 = Thread(target=systemEvents.watchFolder)
                t1.daemon = True
                t1.start()

                t2 = Process(target=systemEvents.watchRecentsFilesWin)
                # t2.daemon = True
                t2.start()
                processesPID.put(t2.pid)

                # t3 = Thread(target=systemEvents.detectSelectionWindowsExplorer)
                # t3.daemon = True
                # t3.start()

                # t4 = Thread(target=systemEvents.printerLogger)
                # t4.daemon = True
                # t4.start()

            elif utils.utils.MAC:
                t5 = Thread(target=systemEvents.watchFolderMac)
                t5.daemon = True
                t5.start()

        if systemLoggerPrograms:
            if utils.utils.WINDOWS:
                t6 = Thread(target=systemEvents.logProcessesWin)
                t6.daemon = True
                t6.start()
            elif utils.utils.MAC:
                t7 = Thread(target=systemEvents.logProcessesMac)
                t7.daemon = True
                t7.start()

        if systemLoggerHotkeys and utils.utils.WINDOWS:
            t10 = Process(target=systemEvents.logHotkeys)
            t10.start()
            processesPID.put(t10.pid)

        if systemLoggerUSB and utils.utils.WINDOWS:
            t11 = Thread(target=systemEvents.logUSBDrives)
            t11.daemon = True
            t11.start()

        if systemLoggerEvents:
            pass

        # ************
        # office logger
        # ************

        if officeExcel:
            status_queue.put(f"[mainLogger] Loading Excel...")

            if utils.utils.WINDOWS:
                t12 = Process(target=officeEvents.excelEvents, args=(status_queue, excelFilepath,))
                t12.start()
                processesPID.put(t12.pid)

                # t14 = Thread(target=mouseEvents.logMouse)
                # t14.daemon = True
                # t14.start()

            if utils.utils.MAC:
                if utils.utils.isPortInUse(3000):
                    os.system("pkill -f node")
                t13 = Thread(target=officeEvents.excelEventsMacServer, args=[status_queue, excelFilepath])
                t13.daemon = True
                t13.start()

        if officeWord and utils.utils.WINDOWS:
            t14 = Process(target=officeEvents.wordEvents)
            t14.start()
            processesPID.put(t14.pid)
            status_queue.put(f"[mainLogger] Loading Word...")

        if officePowerpoint and utils.utils.WINDOWS:
            t15 = Process(target=officeEvents.powerpointEvents)
            t15.start()
            processesPID.put(t15.pid)
            status_queue.put(f"[mainLogger] Loading PowerPoint...")

        if officeOutlook and utils.utils.WINDOWS:
            t16 = Process(target=officeEvents.outlookEvents)
            t16.start()
            processesPID.put(t16.pid)

        # ************
        # browser logger
        # ************

        if browserChrome:
            modules.consumerServer.log_chrome = True

        if browserFirefox:
            modules.consumerServer.log_firefox = True

        if browserEdge:
            modules.consumerServer.log_edge = True

        if browserOpera:
            modules.consumerServer.log_opera = True

        # status_queue.put(f"[mainLogger] Logging started")

        if browserChrome or browserFirefox or browserEdge or browserOpera:
            status_queue.put(f"[mainLogger] Remember to click on extension icon to enable browser logging")

        # keep main active
        while 1:
            time.sleep(1)

    except (KeyboardInterrupt, SystemExit):
        print("Closing threads and exiting...")
        sys.exit(0)


if __name__ == "__main__":
    # launch GUI
    modules.GUI.GUI.buildGUI()
