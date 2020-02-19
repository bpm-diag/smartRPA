# ****************************** #
# Utils
# Global utils used by the modules, provides information about current OS, installed applications and folders
# ****************************** #

from getpass import getuser
from os.path import expanduser
from datetime import datetime
import os

# asynchronous session.post requests to log server, used by multiple modules
from requests_futures.sessions import FuturesSession
session = FuturesSession()

#  boolean constants to detect current OS
from platform import system
WINDOWS = (system() == "Windows")
MAC = (system() == "Darwin")
LINUX = (system() == "Linux")

if WINDOWS:
    import winreg


HOME_FOLDER = expanduser("~")
DESKTOP = HOME_FOLDER + "/Desktop"
USER = getuser()


# return current timestamp in the format '2020-02-12 17:11:14:465'
# used by multiple modules
def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")[:-3]


# detect if program (both 32bit and 64bit) is installed checking windows registry
def isInstalledWin(programName):

    def _getInstalledProgramsWin(hive, flag):
        registry = winreg.ConnectRegistry(None, hive)
        registry_key = winreg.OpenKey(registry, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", 0, winreg.KEY_READ | flag)
        registry_subkeys_number = winreg.QueryInfoKey(registry_key)[0]
        software_list = []
        for i in range(registry_subkeys_number):
            try:
                asubkey_name = winreg.EnumKey(registry_key, i)
                subkey = winreg.OpenKey(registry_key, asubkey_name)
                software_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                software_list.append(software_name)
            except EnvironmentError:
                continue
        return software_list

    software_list = _getInstalledProgramsWin(winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_32KEY) + \
                    _getInstalledProgramsWin(winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_64KEY) + \
                    _getInstalledProgramsWin(winreg.HKEY_CURRENT_USER, 0)

    return bool(list(filter(lambda program: programName in program.lower(), software_list)))


# detect if program is installed in /Applications folder
def isInstalledMac(programName):
    output = os.popen("ls -1 /Applications").read().split('\n')
    return bool(list(filter(lambda program: programName in program.lower(), output)))


# needs testing
def isInstalledLinux(programName):
    return os.subprocess.call(f"dpkg -s {programName} > /dev/null 2>&1", shell=True) == 0


# set boolean variables for available programs, used by GUI to enable/disable checkboxes
if WINDOWS:
    OFFICE = isInstalledWin('office')
    CHROME = isInstalledWin('chrome')
    FIREFOX = isInstalledWin('firefox')
    EDGE = isInstalledWin('edge')
    OPERA = isInstalledWin('opera')
elif MAC:
    OFFICE = isInstalledMac('excel')
    CHROME = isInstalledMac('chrome')
    FIREFOX = isInstalledMac('firefox')
    EDGE = isInstalledMac('edge')
    OPERA = isInstalledMac('opera')
else:
    OFFICE = False
    CHROME = isInstalledLinux('chrome')
    FIREFOX = isInstalledLinux('firefox')
    EDGE = False
    OPERA = isInstalledLinux('opera')

