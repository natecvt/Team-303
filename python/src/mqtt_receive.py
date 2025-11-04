import paho.mqtt.client as mqtt

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

def on_connect(client, userdata, flags, rc, properties):
    print("Connected with result code "+str(rc))
    client.subscribe("test/topic")


def on_message(client, userdata, msg):
    print(msg.topic+":\n\n"+str(msg.payload))

mqttc.on_connect = on_connect
mqttc.on_message = on_message

def connect(host, port=1883, ka=60):
    errc = mqttc.connect(host, port, ka)
    if errc != 0:
        print(f"Connection failed with error code: {errc}")
        return

def main():
    
    connect("localhost")
    mqttc.loop_forever()

if __name__ == "__main__":
    main()


