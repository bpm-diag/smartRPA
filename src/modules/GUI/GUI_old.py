# ****************************** #
# Old GUI
# Old user interface built with Tkinter. Does not scale well on windows, does not provide native UI
# ****************************** #

from multiprocessing import Process
import main
from tkinter import *
from tkinter import messagebox
from platform import system
from sys import path
import utils

path.append('../')  # this way main file is visible from this file


class LoggerGUI(Frame):
    def __init__(self, parent, geometry):

        # GUI inizialization
        Frame.__init__(self, parent)
        self.parent = parent
        self.TG_BLUE = '#1A222C'
        self.parent.title('MainLogger')
        self.parent.geometry(geometry)
        self.parent.configure(background=self.TG_BLUE)

        # process inizialization
        self.running = False
        self.mainProcess = None

        # define checkbox variable
        self.systemLoggerFilesFolder = BooleanVar()
        self.systemLoggerFilesFolder.set(True)
        self.systemLoggerPrograms = BooleanVar()
        self.systemLoggerPrograms.set(False)
        self.systemLoggerClipboard = BooleanVar()
        self.systemLoggerClipboard.set(True)
        self.officeExcel = BooleanVar()
        self.officeExcel.set(True)
        self.officeWord = BooleanVar()
        self.officeWord.set(False)
        self.officePowerpoint = BooleanVar()
        self.officePowerpoint.set(False)
        self.officeAccess = BooleanVar()
        self.officeAccess.set(False)
        self.browserChrome = BooleanVar()
        self.browserChrome.set(True)
        self.browserFirefox = BooleanVar()
        self.browserFirefox.set(True)

        menu = Menu(self.parent)
        self.parent.config(menu=menu)
        fileMenu = Menu(menu)
        fileMenu.add_command(label="About", command=self.aboutMenu)
        menu.add_cascade(label="File", menu=fileMenu)

        Label(parent, text="MainLogger", font=("Courier", 20), foreground="white", pady=20, background=self.TG_BLUE).pack()

        Label(parent, text="Select modules to activate", font=("Arial", 14), pady=5, background=self.TG_BLUE,
              foreground='white').pack()

        systemFrame = LabelFrame(parent, text="System logger", padx=20, pady=10, background=self.TG_BLUE,
                                 foreground='white')
        systemFrame.pack()
        Checkbutton(systemFrame, text="Files/Folders", variable=self.systemLoggerFilesFolder, background=self.TG_BLUE,
                    foreground='white', selectcolor=self.TG_BLUE).pack(anchor="w")
        Checkbutton(systemFrame, text="Programs", variable=self.systemLoggerPrograms, background=self.TG_BLUE,
                    foreground='white', selectcolor=self.TG_BLUE).pack(anchor="w")
        Checkbutton(systemFrame, text="Clipboard", variable=self.systemLoggerClipboard, background=self.TG_BLUE,
                    foreground='white', selectcolor=self.TG_BLUE).pack(anchor="w")

        #Checkbutton(systemFrame, variable=self.systemLoggerClipboard, onvalue=True, offvalue=False, text="Old Testament", bg=self.TG_BLUE, fg='white', activebackground=self.TG_BLUE, activeforeground='white',selectcolor=self.TG_BLUE).pack(anchor="w")

        officeFrame = LabelFrame(parent, text="Office logger", padx=25, pady=10, background=self.TG_BLUE,
                                 foreground='white')
        officeFrame.pack()
        officeExcelCB = Checkbutton(officeFrame, text="Excel", variable=self.officeExcel, background=self.TG_BLUE,
                                    foreground='white', selectcolor=self.TG_BLUE)
        officeExcelCB.pack(anchor="w")
        officeWordCB = Checkbutton(officeFrame, text="Word", variable=self.officeWord, background=self.TG_BLUE,
                                   foreground='white', selectcolor=self.TG_BLUE)
        officeWordCB.pack(anchor="w")
        officePowerpointCB = Checkbutton(officeFrame, text="PowerPoint", variable=self.officePowerpoint,
                                         background=self.TG_BLUE, foreground='white', selectcolor=self.TG_BLUE)
        officePowerpointCB.pack(anchor="w")
        officeAccessCB = Checkbutton(officeFrame, text="Access", variable=self.officeAccess, background=self.TG_BLUE,
                                     foreground='white', selectcolor=self.TG_BLUE)
        officeAccessCB.pack(anchor="w")

        if system() == "Darwin" or system() == "Linux":  # disable unsupported components
            self.officeWord.set(False)
            officeWordCB.config(state=DISABLED)
            self.officePowerpoint.set(False)
            officePowerpointCB.config(state=DISABLED)
            self.officeAccess.set(False)
            officeAccessCB.config(state=DISABLED)
            Label(parent, text="Office logger is not available on MacOS", font=("Arial", 12), fg="gray",
                  background=self.TG_BLUE, foreground='white').pack()

        browserFrame = LabelFrame(parent, text="Browser logger", padx=15, pady=10, background=self.TG_BLUE,
                                  foreground='white')
        browserFrame.pack()
        Checkbutton(browserFrame, text="Google Chrome", variable=self.browserChrome, background=self.TG_BLUE,
                    foreground='white', selectcolor=self.TG_BLUE).pack(anchor="w")
        Checkbutton(browserFrame, text="Mozilla Firefox", variable=self.browserFirefox, background=self.TG_BLUE,
                    foreground='white', selectcolor=self.TG_BLUE).pack(anchor="w")

        Label(parent, text="", background=self.TG_BLUE,
              foreground='white').pack()

        self.runButton = Button(
            parent, text='Start logger', command=self.onclick, padx=5, pady=5)
        self.runButton.pack()

        self.statusLabel = Label(parent, text="", font=(
            "Courier", 12), fg="green", pady=5, background=self.TG_BLUE)
        self.statusLabel.pack()

    def onclick(self):

        if not self.running:  # start button clicked
            # set GUI parameters
            self.running = True
            self.statusLabel.config(text='Logger running...')
            self.runButton.config(text='Stop logger')

            # start main process with the options selected in GUI. It handles all other methods
            # main method is started as a process so it can be terminated once the button is clicked
            # all the methods in the main process are started as daemon threads so they are closed automatically when the main process is closed
            self.mainProcess = Process(target=main.startLogger, args=[
                self.systemLoggerFilesFolder.get(),
                self.systemLoggerPrograms.get(),
                self.systemLoggerClipboard.get(),
                self.officeExcel.get(),
                self.officeWord.get(),
                self.officePowerpoint.get(),
                self.officeAccess.get(),
                self.browserChrome.get(),
                self.browserFirefox.get()
            ])
            self.mainProcess.start()
            print("Logger started, selected threads activated...")

        else:  # stop button clicked
            # set GUI parameters
            self.running = False
            self.statusLabel.config(text='')
            self.runButton.config(text='Start logger')

            # stop main process, automatically closing all daemon threads in main process
            self.mainProcess.terminate()
            print(
                "Main process terminated, daemon threads closed, wainting for new input...")

    def aboutMenu(self):
        messagebox.showinfo("About", "Master's Thesis")


def buildGUI():
    
    geometry = '300x530'

    # Older versions of Tk doesn't work with macOS dark mode
    if (system() == "Darwin" and TkVersion < 8.6):
        print("You're running an old version of python. Please download the latest version from http://python.org")
        return -1
    # Fix blurry UI on windows
    if (utils.utils.WINDOWS):
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        geometry = '600x900'
    
    root = Tk()
    LoggerGUI(root, geometry)
    root.mainloop()
