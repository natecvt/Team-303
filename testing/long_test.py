import paho.mqtt.publish as pub
import time
import random
import yaml
import json

# timings in seconds
MIN_INTERVAL = 0.0
MAX_INTERVAL = 3600.0

with open("ref_files/config.yaml") as file: 
    config = yaml.safe_load(file)

TOPIC_R: str = config["mqtt_received_topic"]
TOPIC_A: str = config["mqtt_acknowledge_topic"]
TOPIC_E: str = config["mqtt_error_topic"]
TOPIC_C: str = config["mqtt_complete_topic"]
TOPIC_H: str = config["mqtt_heartbeat_topic"]
MQTT_IP: str = config["mqtt_broker_ip"]

with open("msgs/print_complete.json") as file: 
    msg = str(json.load(file))

while True:

    r = random.random() # normalized random value
    sleep_interval = (MAX_INTERVAL - MIN_INTERVAL) * r + MIN_INTERVAL
    print(f"sleeping {sleep_interval}s")

    time.sleep(sleep_interval)

    pub.single(topic=TOPIC_C, payload=msg, hostname=MQTT_IP)



