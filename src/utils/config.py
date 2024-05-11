# ****************************** #
# Config
# Global config class used to store values
# ****************************** #

import configparser
import os
from typing import cast

# ---- Default Values ----
#capture_sceenshot= False,
# REGISTRY_PATH  = r'Software\ComputerLogger',
# JSON_PATH  = os.path.expanduser('~/.config/ComputerLogger/config'),
# totalNumberOfRunGuiXes  = 1,  # When total number of runs is reached, CSV logs are merged into XES file
# capture_screenshots  = False,  # Control screenshot feature
# supervisionFeature  = False,  # Control supervision feature
# perform_process_discovery  = True,  # Control process discovery
# enable_most_frequent_routine_analysis  = False,  # Enable most frequent routine analysis
# enable_decision_point_analysis  = True,  # Enable decision points analysis
# enable_decision_point_RPA_analysis  = False  # Enable decision point RPA analysis
#
#

default_config = """
[SmartRPA]
capture_sceenshot= false,
REGISTRY_PATH  = r'Software\\ComputerLogger',
JSON_PATH  = os.path.expanduser('~/.config/ComputerLogger/config'),
totalNumberOfRunGuiXes  = 1
capture_screenshots  = false
supervisionFeature  = false
perform_process_discovery  = true
enable_most_frequent_routine_analysis  = false
enable_decision_point_analysis  = true
enable_decision_point_RPA_analysis  = false
"""


def set_config_default():
    config = configparser.ConfigParser()
    config.read_string(default_config)
    if not os.path.exists("src/utils/config.ini"):
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        
def read_config(config_var_key, type: type, config_area="SmartRPA"):
    config = configparser.ConfigParser()
    config.read('src/utils/config.ini')
    if type == bool:
        return config.getboolean(config_area,config_var_key)
    elif type == float:
        return float(config[config_area][config_var_key])
    elif type == int:
        return int(config[config_area][config_var_key])
    else: # Type = Str > Just return what is there, no parsing necessary
        # If further data types are necessary, just add them :)
        # https://www.w3schools.com/python/python_datatypes.asp
        return str(config[config_area][config_var_key])

def write_config(config_var_key: str, config_var_val, config_area: str="SmartRPA"):
    # Update a configuration value
    config = configparser.ConfigParser()
    config.read('src/utils/config.ini')
    config_var_key = str(config_var_key)
    config_var_val = str(config_var_val)
    config.set(config_area, config_var_key, config_var_val)
    with open('src/utils/config.ini', 'w') as f:
        config.write(f)