import yaml

CONF_PATH = "ref_files/config.yaml"

file = open(CONF_PATH, "r")

config = yaml.safe_load(file)

file.close()
del file

def update_config(config):
    with open(CONF_PATH, "r") as file:
        newconfig = yaml.safe_load(file)

        if not (config == newconfig):
            print("Updated config values")
            config = newconfig

        
