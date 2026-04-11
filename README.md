# Team-303 - 3D Print Farm Automation
All programming related to the team 303 robotics and modelling will go here - even MATLAB. This repository includes the main python application, linuxCNC configuration, testing and design documentation, and MQTT message examples used during testing.

## External Connection - MQTT
Message Queuing Telemetry Transport (MQTT) is used to send and receive messages between an external application and the Raspberry Pi 5 that hosts this application. Examples of these messages are in the `msgs` folder, and there are 3 types:
- `print_complete` (Received): client software sends this message to our application to initiate a bed swap
- `storage_reset` (Received): client software sends this message to tell program if storage has been manually reset
- `swap_complete` (Sent): send this to the client once a swap is completed
- `acknowledgement` (Sent): sent to client upon receiving a message
- `error` (Sent): send this to the client if a swap encounters an error, under the following conditions:
  - Full plate storage full
  - LinuxCNC encounters and error
  - State changes fail
  - Others
- `heartbeat` (Sent): signal sent at a set rate
 
Each message is a json-encoded string that can be parsed for data. 

## Multithreading
Three threads are used in this system: the main control and handling thread `worker`, the hearbeat signal thread `heartbeat`, and the MQTT message handler `messager`. The `worker` thread targets the `main_loop()`, which is used to parse the message, complete the bed swap, and checks for errors. The `messager` thread targets the `loop_forever()` function, used on the MQTT client to check for messages. A `Queue` object is used to share messages between threads. If a message is received, it is added to the queue. If a message is processed by the `worker` thread, it is removed. If an error occurs, it is re-added to the end of the queue for later processing. The heartbeat publishes status periodically, taking state information from a different queue.
 
## Control - LinuxCNC
LinuxCNC is used to control the motion of the system, as realtime capabilities are required for precise control on the Raspberry Pi. The compatible distro was installed to an SD card from [here](https://linuxcnc.org/downloads/). The [Byte2Bot](https://byte2bot.com/products/parallel-port-raspberry-pi-hat) 5-Axis CNC breakout and Parallel Port Hat are used to interface to hardware. The pins are mapped similar to the image with a few differences:

<img width="480" height="261" alt="image" src="https://github.com/user-attachments/assets/a7e8fa0e-9a14-447d-929d-33568ed57404" />

The VFD output PWM pin (P1) outputs an analog voltage from 0-10V, which is used with a analog-to-PWM converter board to control a positional servo. In software this is mapped to the spindle speed, and spindle commands control the angle of the servo. `M03 S100` is mapped to the servo vertical direction, and `M03 S895` is mapped to the servo horizontal.

The LinuxCNC python module is used to interface with the program in software. This manages `stat`, `command`, and `error` channels to control the system. Commands are sent through the MDI interface, and `stat` is used to check the result of each successive command. Commands are generated using the data in the `gcode_gen.py` file, compiled into more comprehensive actions in `gantry_actions.py`.

## Config
The `ref_files` folder contains a `config.yaml` file that is used to set all of the configurable items in the program. This includes coordinates, motion parameters, MQTT parameters, and other things. See [[config.md]] to see the details of this.

## State Machines
Two state machines are used to ensure the system is in the right external configuration: `PositionSM` and `ManipulatorSM`. Each implements methods to control the position and manipulator state and ensure each other are in the right state before continuing an action. The following graph shows the construction of these state machines, generated with `pydot`:

<img width="843" height="243" alt="image" src="https://github.com/user-attachments/assets/dc7eaf3f-a16d-4b53-b54c-6ee641146ba4" />
<img width="374" height="187" alt="image" src="https://github.com/user-attachments/assets/5574a823-d33b-4fca-8857-f5f8996f8fde" />



