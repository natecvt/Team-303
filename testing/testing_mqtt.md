# MQTT Testing

## Dependencies

Install eclipse-mosquitto:

- On Linux: `sudo apt install mosquitto mosquitto-clients`

## Testing

The following steps can be used to test the `mqtt_receive.py` program:

1. Make sure you are in the top-level Team-303 directory. Activate virtual environment with `source .venv/bin/activate`
2. Run the program with `python3 python/mqtt_receive.py` and make sure the connection code indicates success.
3. Run the command-line publisher with `mosquitto_pub -t "test/topic" -V mqttv5 -f msgs/msg.json`. This should publish the specified file's contents once. This file's contents should appear on the terminal.
