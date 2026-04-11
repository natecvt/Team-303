import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
import paho.mqtt.publish as pub
from mqtt_send_types import Message, Error, SwapComplete, HeartBeat, Acknowledgement
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
TOPIC_A: str = config["mqtt_acknowledge_topic"]
TOPIC_E: str = config["mqtt_error_topic"]
TOPIC_C: str = config["mqtt_complete_topic"]
TOPIC_H: str = config["mqtt_heartbeat_topic"]
MQTT_IP: str = config["mqtt_broker_ip"]

e_msg = Error()
sc_msg = SwapComplete()
hb_msg = HeartBeat()
ak_msg = Acknowledgement()

recieved_q = queue.Queue()
heartbeat_q = queue.Queue()

mqttc = mqtt.Client(CallbackAPIVersion.VERSION2)

def on_connect(client, userdata, flags, rc, properties):
    print("Connected with result code " + str(rc))
    client.subscribe(TOPIC_C)

def on_message(client, userdata, msg):
    print("Received message")
    recieved_q.put(msg.payload)

mqttc.on_connect = on_connect
mqttc.on_message = on_message

def connect(host, port=1883, ka=60):
    errc = mqttc.connect(host, port, ka)
    if errc != 0:
        print(f"Connection failed with error code: {errc}")
        return False
    return True

# can be done on the worker thread, since this does not require a loop_forever() call
def publish_message(msg: Message, topic: str,  host=MQTT_IP, port=1883, ka=60):
    pub.single(topic, payload=str(msg), hostname=host, port=port, keepalive=ka)

def main():
    mqttc.connect(MQTT_IP)

if __name__ == "__main__":
    main()


