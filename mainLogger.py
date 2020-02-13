# https://docs.microsoft.com/en-us/WINDOWS/win32/api/
from sys import exit
from time import sleep
from threading import Thread
from utils import GUI
from utils import consumerServer
from utils.utils import WINDOWS,MAC,LINUX
from modules import systemEvents
from modules import officeEvents
from modules import clipboardEvents

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
    try:  # create the threads as daemons so they are closed when main ends

        # ************
        # main logging server
        # ************
        consumerServer.createLogFile()
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
            consumerServer.LOG_CHROME = True

        if browserFirefox:
            consumerServer.LOG_FIREFOX = True

        while 1:  # keep main active
            sleep(1)

    except (KeyboardInterrupt, SystemExit):
        print("Closing threads and exiting...")
        exit(0)


if __name__ == "__main__":
    #  launch gui
    GUI.buildGUI()
