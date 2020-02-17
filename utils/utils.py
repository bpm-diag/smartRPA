from getpass import getuser
from os.path import expanduser
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
    from inspect import getmembers

HOME_FOLDER = expanduser("~")
DESKTOP = HOME_FOLDER + "/Desktop"
USER = getuser()

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
    EDGE = isInstalledWin('edge')
    OPERA = isInstalledWin('opera')
elif MAC:
    OFFICE = False
    CHROME = isInstalledMac('chrome')
    FIREFOX = isInstalledMac('firefox')
    EDGE = isInstalledMac('edge')
    OPERA = isInstalledMac('opera')
else:
    OFFICE = False
    CHROME = True
    FIREFOX = True
    EDGE = False
    OPERA = False

#  return current timestamp in the format '2020-02-12 17:11:14:465'
def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")[:-3]

# Print members of given COM object
def print_members(obj, obj_name="placeholder_name"):
    try:
        fields = list(obj._prop_map_get_.keys())
    except AttributeError:
        print("Object has no attribute '_prop_map_get_'")
        print("Check if the initial COM object was created with"
              "'win32com.client.gencache.EnsureDispatch()'")
        raise
    methods = [m[0] for m in getmembers(obj) if (not m[0].startswith("_") and "clsid" not in m[0].lower())]

    if len(fields) + len(methods) > 0:
        print("Members of '{}' ({}):".format(obj_name, obj))
    else:
        raise ValueError("Object has no members to print")

    print("\tFields:")
    if fields:
        for field in fields:
            print(f"\t\t{field}")
    else:
        print("\t\tObject has no fields to print")

    print("\tMethods:")
    if methods:
        for method in methods:
            print(f"\t\t{method}")
    else:
        print("\t\tObject has no methods to print")

