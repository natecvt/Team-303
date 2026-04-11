echo "main.py should be running in a different terminal"

mosquitto_sub -t "test/complete" -V mqttv5 -h localhost
mosquitto_sub -t "test/heartbeat" -V mqttv5 -h localhost
mosquitto_sub -t "test/error" -V mqttv5 -h localhost
mosquitto_sub -t "test/ack" -V mqttv5 -h localhost