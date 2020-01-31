# https://docs.microsoft.com/en-us/windows/win32/api/
from sys import exit
from threading import Thread
from systemEvents import *
from officeEvents import *

if __name__ == "__main__":
    
    print("Logger started...")
    
    try:
        #create the threads
        t1=Thread(target=watchFolder)
        t2=Thread(target=logProcessesWin)
        t3=Thread(target=watchRecentsFolder)
        #t4=Thread(target=printerLogger)
        
        #daemon threads are closed when main ends
        t1.daemon = True
        t2.daemon = True
        t3.daemon = True  
        #t4.daemon = True  
        
        #launch the threads
        t1.start()
        t2.start()
        t3.start()
        #t4.start()
        
        while 1: #keep main active
            sleep(1)
   
    except (KeyboardInterrupt, SystemExit):
        print("Closing threads...")
        exit(0)

