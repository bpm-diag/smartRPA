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

# this method is called by GUI when the user presses "start logger" button
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
    # modules.GUI.GUI.buildGUI()
    from modules.RPA.uipath import UIPathXAML
    import pandas
    csv_path = "/Users/marco/Desktop/RPA/smartRPA/RPA/2020-09-10_11-06-33/event_log/2020-09-10_11-06-33_combined.csv"
    df = pandas.read_csv(csv_path, encoding='utf-8-sig') \
        .rename(columns={'event_type': 'concept:name', 'timestamp': 'time:timestamp', 'user': 'org:resource'}) \
        .dropna(subset=["time:timestamp"]) \
        .fillna('') \
        .sort_values(by='time:timestamp')
    uipath = UIPathXAML(csv_path, Queue(), df)
    uipath.generateUiPathRPA(decision=True)

