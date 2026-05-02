import yaml
import copy

CONF_PATH = "ref_files/config.yaml"

file = open(CONF_PATH, "r")

config: dict = yaml.safe_load(file)

file.close()
del file

def update_config_file(config):
    with open(CONF_PATH, "w") as file:
        yaml.safe_dump(config, file)

def update_config_variable():
    with open(CONF_PATH, "r") as file:
        nconfig: dict = yaml.safe_load(file)
        if not (nconfig == config):
            print("WARNING: Modifying Config during Runtime can Cause Errors")
            config = copy.deepcopy(nconfig)

        
