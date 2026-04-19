import yaml

CONF_PATH = "ref_files/config.yaml"

file = open(CONF_PATH, "r")

config = yaml.safe_load(file)

file.close()
del file

def update_config_file(config):
    with open(CONF_PATH, "w") as file:
        yaml.safe_dump(config, file)

        
