import paho.mqtt.client as mqtt
import paho.mqtt.publish as pub
import json_msg_parser as jmp
from pathlib import Path
import queue
from config import config


try: 
    JOB_PATH = Path("jobs")
except: 
    print("Path not found")
    exit(1)

TOPIC_R: str = config["mqtt_received_topic"]
TOPIC_E: str = config["mqtt_error_topic"]
TOPIC_C: str = config["mqtt_complete_topic"]

MQTT_IP: str = config["mqtt_broker_ip"]

recieved_q = queue.Queue()
send_q = queue.Queue()

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

def on_connect(client, userdata, flags, rc, properties):
    print("Connected with result code " + str(rc))
    client.subscribe(TOPIC_R)

def on_message(client, userdata, msg):
    jobscount = sum(1 for entry in JOB_PATH.iterdir() if entry.is_file())
    with open(f"jobs/{jobscount}.json", "xt") as newjob:
        jmp.write_str_as_json(newjob, str(msg.payload))

    recieved_q.put(msg.payload)

def assign_callbacks(on_msg, on_con) -> bool:
    
    if (callable(on_msg) and callable(on_con)):
        mqttc.on_connect = on_con
        mqttc.on_message = on_msg
        return True
    
    return False

def connect(host, port=1883, ka=60):
    errc = mqttc.connect(host, port, ka)
    if errc != 0:
        print(f"Connection failed with error code: {errc}")
        return
    
def publish_error(msg, host: str, port=1883, ka=60):
    pub.single(TOPIC_E, payload=msg, hostname=host, port=port, keepalive=ka)
    pass

def publish_complete(msg, host: str, port=1883, ka=60):
    pub.single(TOPIC_C, payload=msg, hostname=host, port=port, keepalive=ka)
    pass

def main():
    if (assign_callbacks(on_message, on_connect)):
        connect("localhost")
        mqttc.loop_forever()
    
    exit(1)

if __name__ == "__main__":
    main()


