from platform import system
from datetime import datetime
import os

# asynchronous session.post requests to log server
from requests_futures.sessions import FuturesSession
session = FuturesSession()

#  boolean constants to detect current OS
WINDOWS = (system() == "Windows")
MAC = (system() == "Darwin")
LINUX = (system() == "Linux")

if WINDOWS:
    import winreg
def getInstalledProgramsWin(hive, flag):
    aReg = winreg.ConnectRegistry(None, hive)
    aKey = winreg.OpenKey(aReg, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                          0, winreg.KEY_READ | flag)
    count_subkey = winreg.QueryInfoKey(aKey)[0]
    software_list = []
    for i in range(count_subkey):
        software = {}
        try:
            asubkey_name = winreg.EnumKey(aKey, i)
            asubkey = winreg.OpenKey(aKey, asubkey_name)
            software['name'] = winreg.QueryValueEx(asubkey, "DisplayName")[0]
            try:
                software['version'] = winreg.QueryValueEx(asubkey, "DisplayVersion")[0]
            except EnvironmentError:
                software['version'] = 'undefined'
            try:
                software['publisher'] = winreg.QueryValueEx(asubkey, "Publisher")[0]
            except EnvironmentError:
                software['publisher'] = 'undefined'
            software_list.append(software)
        except EnvironmentError:
            continue
    return software_list

def isInstalledWin(programName):
    software_list = getInstalledProgramsWin(winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_32KEY) + \
                    getInstalledProgramsWin(winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_64KEY) + \
                    getInstalledProgramsWin(winreg.HKEY_CURRENT_USER, 0)
    return bool(list(filter(lambda program: programName in program['name'].lower(), software_list)))

def isInstalledMac(programName):
    output = os.popen("ls -1 /Applications").read().split('\n')
    return bool(list(filter(lambda program: programName in program.lower(), output)))

if WINDOWS:
    OFFICE = isInstalledWin('office')
    CHROME = isInstalledWin('chrome')
    FIREFOX = isInstalledWin('firefox')
elif MAC:
    OFFICE = False
    CHROME = isInstalledMac('chrome')
    FIREFOX = isInstalledMac('firefox')
else:
    OFFICE = False
    CHROME = True
    FIREFOX = True

#  return current timestamp in the format '2020-02-12 17:11:14:465'
def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")[:-3]
