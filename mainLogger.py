# ****************************** #
# Main logger
# Handles all the threads of the application
# ****************************** #

import os
import sys
import time
from threading import Thread
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
                ):
    try:
        # create the threads as daemons so they are closed when main ends

        # set main directory in config
        config = utils.config.MyConfig.get_instance()
        config.main_directory = os.getcwd()

        # ************
        # main logging server
        # ************
        utils.utils.createLogFile()
        t0 = Thread(target=utils.consumerServer.runServer)
        t0.daemon = True
        t0.start()

        # ************
        # system logger
        # ************

        if systemLoggerFilesFolder:

            if WINDOWS:
                t1 = Thread(target=systemEvents.watchFolder)
                t1.daemon = True
                t1.start()

                t2 = Thread(target=systemEvents.watchRecentsFilesWin)
                t2.daemon = True
                t2.start()

                t9 = Thread(target=systemEvents.detectSelectionWindowsExplorer)
                t9.daemon = True
                t9.start()

                t14 = Thread(target=systemEvents.printerLogger)
                t14.daemon = True
                t14.start()

            elif MAC:
                t15 = Thread(target=systemEvents.watchFolderMac)
                t15.daemon = True
                t15.start()

        if systemLoggerPrograms:
            if WINDOWS:
                t3 = Thread(target=systemEvents.logProcessesWin)
                t3.daemon = True
                t3.start()
            elif MAC:
                t12 = Thread(target=systemEvents.logProcessesMac)
                t12.daemon = True
                t12.start()

        if systemLoggerClipboard:
            t4 = Thread(target=clipboardEvents.logClipboard)
            t4.daemon = True
            t4.start()

        if systemLoggerHotkeys and WINDOWS:
            t10 = Thread(target=systemEvents.logHotkeys)
            t10.daemon = True
            t10.start()

        if systemLoggerUSB and WINDOWS:
            t11 = Thread(target=systemEvents.logUSBDrives)
            t11.daemon = True
            t11.start()

        if systemLoggerEvents:
            pass

        # ************
        # office logger
        # ************

        if officeExcel and WINDOWS:
            t5 = Thread(target=officeEvents.excelEvents)
            t5.daemon = True
            t5.start()

            # t14 = Thread(target=mouseEvents.logMouse)
            # t14.daemon = True
            # t14.start()

        if officeExcel and MAC:
            t13 = Thread(target=officeEvents.excelEventsMacServer)
            t13.daemon = True
            t13.start()

        if officeWord and WINDOWS:
            t6 = Thread(target=officeEvents.wordEvents)
            t6.daemon = True
            t6.start()

        if officePowerpoint and WINDOWS:
            t7 = Thread(target=officeEvents.powerpointEvents)
            t7.daemon = True
            t7.start()

        if officeOutlook and WINDOWS:
            t8 = Thread(target=officeEvents.outlookEvents)
            t8.daemon = True
            t8.start()

        # ************
        # browser logger
        # ************

        if browserChrome:
            config.log_chrome = True

        if browserFirefox:
            config.log_firefox = True

        if browserEdge:
            config.log_edge = True

        if browserOpera:
            config.log_opera = True

        # print(f"[mainLogger] Chrome={browserChrome}, Firefox={browserFirefox}, Edge={browserEdge}, Opera={browserOpera}")
        # print(f"[mainLogger] Excel={officeExcel}, Word={officeWord}, Powerpoint={officePowerpoint}, Outlook={officeOutlook}")
        print(f"[mainLogger] Selected threads activated, logging to {utils.config.MyConfig.get_instance().log_filepath}")

        # keep main active
        while 1:
            time.sleep(1)  # important: use sleep(1) and not pass

    except (KeyboardInterrupt, SystemExit):
        print("Closing threads and exiting...")
        sys.exit(0)


if __name__ == "__main__":
    #  launch gui
    utils.GUI.buildGUI()
