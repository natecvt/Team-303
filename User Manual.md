# User Manual
## Intro
This document is an overview of how to use the software provided in this repo. This includes setup, dealing with errors, calibration, and others.

## First Time Setup
This does not cover the installation of the linuxCNC-compatible distro. A link to that has been provided in README.

### SSH
1. Password and Hostname will have already been provided.
2. Run `ssh -i<pubkey_name.id> username@hostname` in a console, give affirmative responses to all prompts, and type the password when prompted.
3. A shell session should be open on the Raspberry Pi.

### Setting Up App as a System Service (Minimal Intervention)

1. Download software: open a terminal and run `git clone --recurse-submodules https://github.com/natecvt/Team-303`.
2. Navigate to the Team-303 folder with `cd`. Run `python -m venv .venv` then `source .venv/bin/activate` then `pip install -r requirements.txt`.
3. Registering it as a systemd service: run `sudo bash scripts/bind_new_service.sh`. Do not reboot until the all other steps in FTS are complete.
4. Confirm the service is registered with `sudo systemctl status start_software`

### Calibration

1. Run the script with `sudo bash calibrate.sh`. This will start a calibration procedure that should be followed. 2 people are best for this.
2. After the previous step is complete, open the `config.yaml` file to confirm values were written as expected.
3. Add the following properties manually to the config (press Ctrl+S to save):
    - `heartbeat_duration`: duration to send heartbeats (s), should be shorter than timeout setting 
    - `mqtt_broker_ip`: local ip of broker
    - `mqtt_complete_topic`: topic for app to send SWAP_COMPLETE messages on
    - `mqtt_acknowledge_topic`: 
    - `mqtt_heartbeat_topic`:
    - `mqtt_error_topic`: 
    - `mqtt_keepalive`: mqtt keepalive duration in seconds
    - `mqtt_storage_topic`: topic for app to receive STORAGE_RESET messages on
    - `mqtt_received_topic`: topic for app to receive PRINT_COMPLETE messages on

### Raspberry Pi Connect

1. Run `sudo menu-config`.
2. Use the arrow keys and the ENTER key to navigate `3 Interface Options->I2 RPi Connect` and select `<Yes>`.
3. Press the `<Ok>` option and press the right arrow twice then ENTER to exit.
4. Run `rpi-connect on` then `rpi-connect signin`, copy or ctrl+click the provided link.
5. Make an account at the link then give a name when prompted.
6. Navigate to the Devices panel and click 'Connect Via' if the named device is online. This will open a window with the desktop. A shell akin to SSH can also be opened with this method.
