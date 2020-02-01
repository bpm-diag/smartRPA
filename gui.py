
from tkinter import *
from sys import platform #detect running os

def checkPlatform():
    if platform == "win32" or platform == "win64":
        pass
    elif platform == "darwin" or platform == "linux" or platform == "linux2":
        pass

def runButtonClicked():
    global window
    print("button clicked")
    Label(window, text="Logger running...", fg="green", pady=5).pack()

def buildUI():
    #Older versions of Tk doesn't work with macOS dark mode
    if (platform == "darwin" and TkVersion < 8.6):
        print ("You're running an old version of python. Please download the latest version from http://python.org") 
        return -1
    
    window = Tk()
    window.title("SystemLogger")
    window.geometry('300x200')
    
    Label(window, text="Select modules to activate", pady=5).pack()
    
    sysLoggerCheck = BooleanVar()
    sysLoggerCheck.set(True)
    Checkbutton(window, text='System logger', font=("Arial", 11), var=sysLoggerCheck, pady=5).pack()
    
    officeLoggerCheck = BooleanVar()
    officeLoggerCheck.set(True)
    officeLoggerCheckButton=Checkbutton(window, text='Office logger', font=("Arial", 11), var=officeLoggerCheck, pady=5)
    officeLoggerCheckButton.pack()
    if platform == "darwin" or platform == "linux" or platform == "linux2":
        officeLoggerCheck.set(False)
        officeLoggerCheckButton.config(state=DISABLED)
        Label(window, text="Office logger is not available on MacOS", font=("Arial", 12)).pack()

    browserLoggerCheck = BooleanVar()
    browserLoggerCheck.set(True)
    Checkbutton(window, text='Browser logger', font=("Arial", 11), var=browserLoggerCheck, pady=5).pack()
    
    Button( window, text="Run logger", command=runButtonClicked, pady=5 ).pack()

    window.mainloop()

buildUI()