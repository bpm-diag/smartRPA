# ****************************** #
# Main logger
# Handles all the threads of the application
# ****************************** #

import os
import sys
import time
from threading import Thread
from multiprocessing import Process
from utils.utils import WINDOWS, MAC, LINUX
import utils.GUI
import utils.config
import utils.consumerServer
import utils.utils
from modules import systemEvents, mouseEvents
from modules import officeEvents
from modules import clipboardEvents


#  this method is called by GUI when the user presses "start logger" button
def startLogger(systemLoggerFilesFolder,
                systemLoggerPrograms,
                systemLoggerClipboard,
                systemLoggerHotkeys,
                systemLoggerUSB,
                systemLoggerEvents,
                officeFilename,
                officeExcel,
                officeWord,
                officePowerpoint,
                officeOutlook,
                browserChrome,
                browserFirefox,
                browserEdge,
                browserOpera,
                status_queue,
                LOG_FILEPATH
                ):
    try:
        # create the threads as daemons so they are closed when main ends

        # ************
        # main logging server
        # ************
        log_filepath = utils.utils.createLogFile()
        # return log file to GUI so it can be processed
        LOG_FILEPATH.put(log_filepath)

        t0 = Thread(target=utils.consumerServer.runServer)
        t0.daemon = True
        t0.start()

        utils.consumerServer.log_filepath = log_filepath

        # ************
        # system logger
        # ************

        if systemLoggerClipboard:
            # log copy event
            t8 = Process(target=clipboardEvents.logClipboard)
            t8.daemon = True
            t8.start()
            # only way to log paste event is to detect ctrl + v, but it should be started as process instead of thread
            # otherwise some events are lost
            if WINDOWS:
                t9 = Process(target=systemEvents.logPasteHotkey)
                t9.daemon = True
                t9.start()

        if systemLoggerFilesFolder:

            if WINDOWS:
                t1 = Process(target=systemEvents.watchFolder)
                t1.daemon = True
                t1.start()

                t2 = Process(target=systemEvents.watchRecentsFilesWin)
                t2.daemon = True
                t2.start()

                # t3 = Thread(target=systemEvents.detectSelectionWindowsExplorer)
                # t3.daemon = True
                # t3.start()

                # t4 = Thread(target=systemEvents.printerLogger)
                # t4.daemon = True
                # t4.start()

            elif MAC:
                t5 = Thread(target=systemEvents.watchFolderMac)
                t5.daemon = True
                t5.start()

        if systemLoggerPrograms:
            if WINDOWS:
                t6 = Process(target=systemEvents.logProcessesWin)
                t6.daemon = True
                t6.start()
            elif MAC:
                t7 = Process(target=systemEvents.logProcessesMac)
                t7.daemon = True
                t7.start()

        if systemLoggerHotkeys and WINDOWS:
            t10 = Process(target=systemEvents.logHotkeys)
            t10.daemon = True
            t10.start()

        if systemLoggerUSB and WINDOWS:
            t11 = Process(target=systemEvents.logUSBDrives)
            t11.daemon = True
            t11.start()

        if systemLoggerEvents:
            pass

        # ************
        # office logger
        # ************

        if officeExcel:
            if WINDOWS:
                t12 = Process(target=officeEvents.excelEvents)
                t12.daemon = True
                t12.start()

                # t14 = Thread(target=mouseEvents.logMouse)
                # t14.daemon = True
                # t14.start()

            if MAC:
                t13 = Thread(target=officeEvents.excelEventsMacServer)
                t13.daemon = True
                t13.start()

        if officeWord and WINDOWS:
            t14 = Thread(target=officeEvents.wordEvents)
            t14.daemon = True
            t14.start()

        if officePowerpoint and WINDOWS:
            t15 = Thread(target=officeEvents.powerpointEvents)
            t15.daemon = True
            t15.start()

        if officeOutlook and WINDOWS:
            t16 = Thread(target=officeEvents.outlookEvents)
            t16.daemon = True
            t16.start()

        # ************
        # browser logger
        # ************

        if browserChrome:
            utils.consumerServer.log_chrome = True

        if browserFirefox:
            utils.consumerServer.log_firefox = True

        if browserEdge:
            utils.consumerServer.log_edge = True

        if browserOpera:
            utils.consumerServer.log_opera = True

        status_queue.put(f"[mainLogger] Logging started")

        if browserChrome or browserFirefox or browserEdge or browserOpera:
            status_queue.put(f"[mainLogger] Remember to click on extension icon to enable browser logging")

        # keep main active
        while 1:
            time.sleep(1)

    except (KeyboardInterrupt, SystemExit):
        print("Closing threads and exiting...")
        sys.exit(0)


if __name__ == "__main__":
    #  launch gui
    utils.GUI.buildGUI()
