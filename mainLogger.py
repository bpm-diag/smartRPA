# ****************************** #
# Main logger
# Handles all the threads of the application
# ****************************** #

import multiprocessing
from sys import exit
import errno
import os
from csv import writer
from time import sleep
from datetime import datetime
from threading import Thread
from utils import GUI
from utils import consumerServer
from utils.consumerServer import HEADER
from utils.utils import WINDOWS,MAC,LINUX
from modules import systemEvents
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

        # ************
        # main logging server
        # ************
        createLogFile()
        t0 = Thread(target=consumerServer.runServer)
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
            consumerServer.LOG_CHROME = True

        if browserFirefox:
            consumerServer.LOG_FIREFOX = True

        if browserEdge:
            consumerServer.LOG_EDGE = True

        if browserOpera:
            consumerServer.LOG_OPERA = True

        print(f"[mainLogger] Chrome={browserChrome}, Firefox={browserFirefox}, Edge={browserEdge}, Opera={browserOpera}")
        # print(f"[mainLogger] Excel={officeExcel}, Word={officeWord}, Powerpoint={officePowerpoint}, Outlook={officeOutlook}")
        print(f"[mainLogger] Selected threads activated, logging to {consumerServer.filename}")

        # keep main active
        while 1:
            sleep(1)

    except (KeyboardInterrupt, SystemExit):
        print("Closing threads and exiting...")
        exit(0)


# used by main, creates new log file with the current timestamp in /logs directory at the root of the project.
def createLogFile():
    current_directory = os.getcwd()
    # logs are saved in logs/ direcgory
    logs_directory = os.path.join(current_directory, 'logs/')
    # use current timestamp as filename
    filenameWithTimestamp = logs_directory + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.csv'
    # filename to use in current session until the 'stop' button is pressed. must be set here because the filename
    # uses the current timestamp and it must remain the same during the whole session
    consumerServer.filename = filenameWithTimestamp
    if not os.path.exists(logs_directory):
        try:
            os.makedirs(logs_directory)
            print(f"Created directory {logs_directory}")
        except OSError as exc:  # Guard against race condition
            print(f"Could not create directory {logs_directory}")
            if exc.errno != errno.EEXIST:
                raise

    # create HEADER
    with open(consumerServer.filename, 'a', newline='') as out_file:
        f = writer(out_file)
        f.writerow(HEADER)


if __name__ == "__main__":
    #  launch gui
    GUI.buildGUI()
