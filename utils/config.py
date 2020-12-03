# ****************************** #
# Config
# Global config class used to store values
# ****************************** #

import os
from nativeconfig import PreferredConfig, StringOption, BooleanOption, IntOption
from datetime import datetime


class MyConfig(PreferredConfig):
    """
    Configuration class, used to store preferences.

    Preferences include:

    * total number of runs before executing process mining analysis
    * control process discovery, if disabled csv is generated but process discovery techniques are not applied
    * enable most frequent routine analysis (deprecated)
    * enable decision points analysis
    """
    REGISTRY_PATH = r'Software\ComputerLogger'
    JSON_PATH = os.path.expanduser('~/.config/ComputerLogger/config')

    # When totalNumberOfRunGuiXes of runs is reached (set by user in preferences), all CSV logs collected are merged
    # into one and a XES file is automatically generated, to be used for process mining techniques
    totalNumberOfRunGuiXes = IntOption('totalNumberOfRunGuiXes', default=1)

    # Option in settings to control process discovery, if disabled, csv is generated but process discovery techniques
    # are not applied
    perform_process_discovery = BooleanOption('perform_process_discovery', default=True)

    enable_most_frequent_routine_analysis = BooleanOption('enable_most_frequent_routine_analysis', default=False)
    enable_decision_point_analysis = BooleanOption('enable_decision_point_analysis', default=True)
    enable_decision_point_RPA_analysis = BooleanOption('enable_decision_point_RPA_analysis', default=False)
