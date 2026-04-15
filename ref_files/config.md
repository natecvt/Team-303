# Config
This file contains the definitions for many of the values contained in `config.yaml`.

## MQTT
All MQTT-related values for the system:
- `mqtt_broker_ip`: ip for the broker, should be local
- `mqtt_complete_topic`: topic that swap complete messages will be sent on
- `mqtt_acknowledge_topic`: topic that ack messages will be sent on
- `mqtt_error_topic`: topic that error messages will be sent on
- `mqtt_received_topic`: topic that print complete messages will be received on
- `mqtt_storage_topic`: topic that storage messages will be received on
- `mqtt_heartbeat_topic`: topic that heartbeats will be sent on
- `mqtt_keepalive`: keepalive duration (s)
- `heartbeat_duration`: duration for heartbeat delay (s)

## Printers
Printer-related values for the system:
- `printer_coords`: coords of each printer, formatted as such:
  - `1: x: XX.xx, y: YY.yy`
- `printer_plate_z`: assuming printers are at the same `z`, amount Manipulator (M) moves forward to grab plate
- `door_z`: amount M moves forward to engage with door handle
- `door_into_y`: amount M moves up into door handle
- `door_close_x_offset`: amount to move in X to compensate for door backlash
- `door_radius`: radius of XZ radial move that is performed when opening/closing door
- `door_open_delta`: change in position when opening door
  - `x`: x-change, should be negative for open
  - `y`: y-change, should be zero
  - `z`: z-change, should be negative for open
- `door_close_delta`: change in position when closing door
  - `x`: should be equal to `door_close_x_offset + door_open_delta['x']`
  - `y`: should be zero
  - `z`: should be equal to `3 - door_open_delta['z']`, where 3 is an amount to push forward to guarantee door closes
- `door_to_plate_delta`: change in position to center the manipulator on the plate, from door location

