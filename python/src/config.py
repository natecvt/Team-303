import yaml

CONF_PATH = "ref_files/config.yaml"

file = open(CONF_PATH, "r")
config = yaml.safe_load(file)
file.close()
del file

def get_param(param: str):
    return config[param]

