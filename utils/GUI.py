
from tkinter import *
from tkinter import messagebox
from platform import system
from sys import path
path.append('../') #this way main file is visible from this file
import mainLogger
from multiprocessing import Process

class LoggerGUI(Frame):
    def __init__(self, parent):
        
        # gui inizialization
        Frame.__init__(self, parent)
        self.parent = parent
        self.parent.title('SystemLogger')
        self.parent.geometry('300x450')

        # process inizialization
        self.running = False
        self.mainProcess = None

        #define checkbox variable
        self.systemLoggerFilesFolder = BooleanVar()
        self.systemLoggerFilesFolder.set(True)
        self.systemLoggerPrograms = BooleanVar()
        self.systemLoggerPrograms.set(True)
        self.officeExcel = BooleanVar()
        self.officeExcel.set(False)
        self.officeWord = BooleanVar()
        self.officeWord.set(False)
        self.officePowerpoint = BooleanVar()
        self.officePowerpoint.set(False)
        self.officeAccess = BooleanVar()
        self.officeAccess.set(False)
        self.browserChrome = BooleanVar()
        self.browserChrome.set(False)
        self.browserFirefox = BooleanVar()
        self.browserFirefox.set(False)

        menu = Menu(self.parent)
        self.parent.config(menu=menu)
        fileMenu = Menu(menu)
        fileMenu.add_command(label="About", command=self.aboutMenu)
        menu.add_cascade(label="File", menu=fileMenu)

        Label(parent, text="Select modules to activate",font=("Arial", 14), pady=10).pack()

        systemFrame = LabelFrame(parent, text = "System logger", padx=20, pady=10)
        systemFrame.pack()
        Checkbutton(systemFrame, text="Files/Folders", variable=self.systemLoggerFilesFolder).pack(anchor="w")
        Checkbutton(systemFrame, text="Programs", variable=self.systemLoggerPrograms).pack(anchor="w")

        officeFrame = LabelFrame(parent, text = "Office logger", padx=25, pady=10)
        officeFrame.pack()
        officeExcelCB = Checkbutton(officeFrame, text="Excel", variable=self.officeExcel)
        officeExcelCB.pack(anchor="w")
        officeWordCB = Checkbutton(officeFrame, text="Word", variable=self.officeWord)
        officeWordCB.pack(anchor="w")
        officePowerpointCB = Checkbutton(officeFrame, text="PowerPoint", variable=self.officePowerpoint)
        officePowerpointCB.pack(anchor="w")
        officeAccessCB = Checkbutton(officeFrame, text="Access", variable=self.officeAccess)
        officeAccessCB.pack(anchor="w")
        
        if system() == "Darwin" or system() == "Linux": #disable unsupported components
            self.officeWord.set(False)
            officeWordCB.config(state=DISABLED)
            self.officePowerpoint.set(False)
            officePowerpointCB.config(state=DISABLED)
            self.officeAccess.set(False)
            officeAccessCB.config(state=DISABLED)
            Label(parent, text="Office logger is not available on MacOS", font=("Arial", 12), fg="gray" ).pack()

        browserFrame = LabelFrame(parent, text = "Browser logger", padx=15, pady=10)
        browserFrame.pack()
        Checkbutton(browserFrame, text="Google Chrome", variable=self.browserChrome).pack(anchor="w")
        Checkbutton(browserFrame, text="Mozilla Firefox", variable=self.browserFirefox).pack(anchor="w")

        Label(parent, text="").pack()

        self.runButton = Button(parent, text='Start logger', command=self.onclick, padx=5, pady=5)
        self.runButton.pack()

        self.statusLabel = Label(parent, text="",font=("Courier", 12), fg="green", pady=5)
        self.statusLabel.pack()

    def onclick(self):
        
        if not self.running: #start button clicked
            # set gui parameters
            self.running = True
            self.statusLabel.config(text='Logger running...')
            self.runButton.config(text='Stop logger')
            
            #start main process with the options selected in gui. It handles all other methods
            #main method is started as a process so it can be terminated once the button is clicked
            #all the methods in the main process are started as daemon threads so they are closed automatically when the main process is closed
            self.mainProcess=Process(target=mainLogger.startLogger,args=[
                self.systemLoggerFilesFolder.get(),
                self.systemLoggerPrograms.get(),
                self.officeExcel.get(),
                self.officeWord.get(),
                self.officePowerpoint.get(),
                self.officeAccess.get(),
                self.browserChrome.get(),
                self.browserFirefox.get()
            ])
            self.mainProcess.start()
            print("Logger started, selected threads activated...")

        else: # stop button clicked
            # set gui parameters
            self.running = False
            self.statusLabel.config(text='')
            self.runButton.config(text='Start logger')
            
            #stop main process, automatically closing all daemon threads in main process
            self.mainProcess.terminate()
            print("Main process terminated, daemon threads closed, wainting for new input...")
    
    def aboutMenu(self):
        messagebox.showinfo("About", "Master's Thesis")

def buildGUI():
    #Older versions of Tk doesn't work with macOS dark mode
    if (system() == "Darwin" and TkVersion < 8.6):
        print ("You're running an old version of python. Please download the latest version from http://python.org") 
        return -1
    root = Tk()
    LoggerGUI(root)
    root.mainloop() 
