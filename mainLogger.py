# https://docs.microsoft.com/en-us/windows/win32/api/
from sys import exit
from time import sleep
from threading import Thread
from multiprocessing import Process
import modules.GUI as GUI
import modules.systemEvents as systemEvents
import modules.officeEvents as officeEvents

# this method is called by GUI when the user presses "start logger" button
def startLogger(systemLoggerFilesFolder,
                systemLoggerPrograms,
                officeExcel,
                officeWord,
                officePowerpoint,
                officeAccess,
                browserChrome,
                browserFirefox):
    
    print("Logger started...")
    
    try: #create the threads as daemon so they are closed when main ends
        
        if systemLoggerFilesFolder:
            
            t1=Thread(target=systemEvents.watchFolder)
            t1.daemon = True
            t1.start()
            
            t2=Thread(target=systemEvents.watchRecentsFolderWin)
            t2.daemon = True
            t2.start()
            #t4=Thread(target=printerLogger)
            #t4.daemon = True
            #t4.start()

        if systemLoggerPrograms:
            t3=Thread(target=systemEvents.logProcessesWin)
            t3.daemon = True
            t3.start()
        
        if officeExcel:
            t5=Thread(target=officeEvents.excelEvents)
            t5.daemon = True
            t5.start()

        if officeWord:
            t6=Thread(target=officeEvents.wordEvents)
            t6.daemon = True
            t6.start()

        if officePowerpoint:
            t7=Thread(target=officeEvents.powerpointEvents)
            t7.daemon = True
            t7.start()

        if officeAccess:
            print("Office not implemented yet.")

        if browserChrome:
            print("Browser not implemented yet.")

        if browserFirefox:
            print("Browser not implemented yet.")
    
        while 1: #keep main active
            sleep(1)
    
    except (KeyboardInterrupt, SystemExit):
        print("Closing threads...")
        exit(0)

if __name__ == "__main__":
    
    # launch gui
    GUI.buildGUI()


