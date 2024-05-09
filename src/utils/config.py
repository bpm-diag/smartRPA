# ****************************** #
# Config
# Global config class used to store values
# ****************************** #

import os


class MyConfig:
    """
    Local configuration class, used to store preferences.

    Preferences include:

    * total number of runs before executing process mining analysis
    * control process discovery, if disabled csv is generated but process discovery techniques are not applied
    * enable most frequent routine analysis (deprecated)
    * enable decision points analysis
    """

    _instance = None

    def __init__(self):
        self.REGISTRY_PATH = r'Software\ComputerLogger'
        self.JSON_PATH = os.path.expanduser('~/.config/ComputerLogger/config')
        self.totalNumberOfRunGuiXes = 1  # When total number of runs is reached, CSV logs are merged into XES file
        self.capture_screenshots = False  # Control screenshot feature
        self.supervisionFeature = False  # Control supervision feature
        self.perform_process_discovery = True  # Control process discovery
        self.enable_most_frequent_routine_analysis = False  # Enable most frequent routine analysis
        self.enable_decision_point_analysis = True  # Enable decision points analysis
        self.enable_decision_point_RPA_analysis = False  # Enable decision point RPA analysis
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
