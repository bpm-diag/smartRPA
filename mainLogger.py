# https://docs.microsoft.com/en-us/windows/win32/api/
from sys import exit
from time import sleep
from platform import system
from threading import Thread
from datetime import datetime
import csv
import os
import errno

from utils import GUI
from modules import systemEvents
from modules import officeEvents
from utils import consumerServer

# creates new log file with the current timestamp in /logs directory at the root of the project.
# creates /logs if it does not exist
def createLogFile():
    current_directory = os.getcwd()
    logs_directory = os.path.join(current_directory, 'logs/')
    filename = logs_directory + datetime.now().strftime("%Y%m%d_%H%M%S") + '.csv' #use current timestamp as filename
    consumerServer.filename = filename  # filename to use in current session until the 'stop' button is pressed. must be set here because the ilename uses the current timestamp and it must remain the same during the whole session
    #if not os.path.exists(os.path.dirname(filename)):
    if not os.path.exists(logs_directory):
        try:
            os.makedirs(logs_directory)
            print(f"created directory {logs_directory}")
        except OSError as exc:  # Guard against race condition
            print(f"could not create directory {logs_directory}")
            if exc.errno != errno.EEXIST:
                raise
    # create header
    with open(filename, 'a') as out_file:
        f = csv.writer(out_file)
        f.writerow(["datetime", "user", "category", "application", "event_type", "event_src_path", "event_dest_path"])  # header


#  this method is called by GUI when the user presses "start logger" button
def startLogger(systemLoggerFilesFolder,
                systemLoggerPrograms,
                officeExcel,
                officeWord,
                officePowerpoint,
                officeAccess,
                browserChrome,
                browserFirefox):

    windows = (system() == "windows")

    try:  # create the threads as daemon so they are closed when main ends

        # start writer server
        createLogFile()
        t0 = Thread(target=consumerServer.runServer)
        t0.daemon = True
        t0.start()

        if systemLoggerFilesFolder:
            t1 = Thread(target=systemEvents.watchFolder)
            t1.daemon = True
            t1.start()

            if windows:
                t2 = Thread(target=systemEvents.watchRecentsFolderWin)
                t2.daemon = True
                t2.start()
                # t4=Thread(target=printerLogger)
                # t4.daemon = True
                # t4.start()

        if systemLoggerPrograms and windows:
            t3 = Thread(target=systemEvents.logProcessesWin)
            t3.daemon = True
            t3.start()

        if officeExcel and windows:
            t5 = Thread(target=officeEvents.excelEvents)
            t5.daemon = True
            t5.start()

        if officeWord and windows:
            t6 = Thread(target=officeEvents.wordEvents)
            t6.daemon = True
            t6.start()

        if officePowerpoint and windows:
            t7 = Thread(target=officeEvents.powerpointEvents)
            t7.daemon = True
            t7.start()

        if officeAccess and windows:
            print("Office not implemented yet.")

        if browserChrome:
            print("Browser not implemented yet.")

        if browserFirefox:
            print("Browser not implemented yet.")

        while 1:  # keep main active
            sleep(1)

    except (KeyboardInterrupt, SystemExit):
        print("Closing threads and exiting...")
        exit(0)


if __name__ == "__main__":
    #  launch gui
    GUI.buildGUI()
