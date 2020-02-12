# https://docs.microsoft.com/en-us/WINDOWS/win32/api/
from sys import exit
from time import sleep
from platform import system
from threading import Thread
from datetime import datetime
import csv
import os
import errno

from utils import GUI
from utils import consumerServer
from modules import systemEvents
from modules import officeEvents
from modules import clipboardEvents

# creates new log file with the current timestamp in /logs directory at the root of the project.
# creates /logs if it does not exist


def createLogFile():
    current_directory = os.getcwd()
    # logs are saved in logs/ direcgory
    logs_directory = os.path.join(current_directory, 'logs/')
    filename = logs_directory + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + \
        '.csv'  # use current timestamp as filename
    consumerServer.filename = filename  # filename to use in current session until the 'stop' button is pressed. must be set here because the ilename uses the current timestamp and it must remain the same during the whole session
    # if not os.path.exists(os.path.dirname(filename)):
    if not os.path.exists(logs_directory):
        try:
            os.makedirs(logs_directory)
            print(f"Created directory {logs_directory}")
        except OSError as exc:  # Guard against race condition
            print(f"Could not create directory {logs_directory}")
            if exc.errno != errno.EEXIST:
                raise
    # create header
    with open(filename, 'a') as out_file:
        f = csv.writer(out_file)
        f.writerow(consumerServer.header)

#  this method is called by GUI when the user presses "start logger" button


def startLogger(systemLoggerFilesFolder,
                systemLoggerPrograms,
                systemLoggerClipboard,
                systemLoggerHotkeys,
                systemLoggerEvents,
                officeExcel,
                officeWord,
                officePowerpoint,
                officeAccess,
                browserChrome,
                browserFirefox):

    WINDOWS = (system() == "Windows")
    MAC = (system() == "Darwin")

    try:  # create the threads as daemons so they are closed when main ends

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
            t1 = Thread(target=systemEvents.watchFolder)
            t1.daemon = True
            t1.start()

            if WINDOWS:
                t2 = Thread(target=systemEvents.watchRecentsFolderWin)
                t2.daemon = True
                t2.start()
                # t4=Thread(target=printerLogger)
                # t4.daemon = True
                # t4.start()

        if systemLoggerPrograms:
            if WINDOWS:
                t3 = Thread(target=systemEvents.logProcessesWin)
                t3.daemon = True
                t3.start()

            if MAC:
                # TODO
                pass

        if systemLoggerClipboard:
            t4 = Thread(target=clipboardEvents.logClipboard)
            t4.daemon = True
            t4.start()

        if systemLoggerHotkeys:
            pass

        if systemLoggerEvents:
            pass

        # ************
        # office logger
        # ************

        if officeExcel and WINDOWS:
            t5 = Thread(target=officeEvents.excelEvents)
            t5.daemon = True
            t5.start()

        if officeWord and WINDOWS:
            t6 = Thread(target=officeEvents.wordEvents)
            t6.daemon = True
            t6.start()

        if officePowerpoint and WINDOWS:
            t7 = Thread(target=officeEvents.powerpointEvents)
            t7.daemon = True
            t7.start()

        if officeAccess and WINDOWS:
            print("Access not implemented yet.")

        # ************
        # browser logger
        # ************

        if browserChrome:
            consumerServer.log_chrome = True

        if browserFirefox:
            consumerServer.log_firefox = True

        while 1:  # keep main active
            sleep(1)

    except (KeyboardInterrupt, SystemExit):
        print("Closing threads and exiting...")
        exit(0)


if __name__ == "__main__":
    #  launch gui
    GUI.buildGUI()
