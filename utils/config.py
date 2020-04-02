# ****************************** #
# Config
# Global config class used to store values in memory like current filename
# ****************************** #

import os
from nativeconfig import PreferredConfig, StringOption, BooleanOption, IntOption


class MyConfig(PreferredConfig):
    REGISTRY_PATH = r'Software\ComputerLogger'
    JSON_PATH = os.path.expanduser('~/.config/ComputerLogger/config')

    # directory of main file. Used when creating logs or rpa files to know where to save them
    main_directory = StringOption('main_directory', default=os.getcwd())

    # path of the current log file being written. It must be saved here because I need this reference when main
    # terminates to generate RPA log and to write messages to GUI
    # filepath is like /Users/marco/Desktop/ComputerLogger/logs/2020-02-25_23-21-57.csv
    log_filepath = StringOption('log_filepath')

    # used by server to check which browser should be logged
    log_chrome = BooleanOption('log_chrome', default=False)
    log_firefox = BooleanOption('log_firefox', default=False)
    log_edge = BooleanOption('log_edge', default=False)
    log_opera = BooleanOption('log_opera', default=False)

    # When totalNumberOfRunGuiXes of runs is reached (set by user in preferences), all CSV logs collected are merged
    # into one and a XES file is automatically generated, to be used for process mining techniques
    totalNumberOfRunGuiXes = IntOption('totalNumberOfRunGuiXes', default=1)

    perform_process_discovery = BooleanOption('perform_process_discovery', default=True)
