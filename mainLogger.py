# https://docs.microsoft.com/en-us/windows/win32/api/
from sys import exit
from time import sleep
from threading import Thread
import gui
import systemEvents
import officeEvents

# this method is called when the user presses "start logger" button in gui, and stores the user's preferences as to what to launch
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
            pass

        if browserChrome:
            pass

        if browserFirefox:
            pass
    
        while 1: #keep main active
            sleep(1)
    
    except (KeyboardInterrupt, SystemExit):
        print("Closing threads...")
        exit(0)

def stopLogger():
    print("Closing threads...")
    exit(0)

if __name__ == "__main__":
    
    # launch gui
    gui.buildGUI()


