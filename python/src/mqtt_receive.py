import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc, properties):
    print("Connected with result code "+str(rc))
    client.subscribe("test/topic")

def on_message(client, userdata, msg):
    print(msg.topic+":\n\n"+str(msg.payload))


def main():
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message

    errc = mqttc.connect("localhost", 1883, 60)
    if errc != 0:
        print("Connection failed with error code "+str(errc))
        return
    
    mqttc.loop_forever()

if __name__ == "__main__":
    main()


