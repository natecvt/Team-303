import subprocess
import sys
import time
from config import config
import gantry_actions as ga

try:
    import linuxcnc
except:
    print("linuxcnc not found, don't run this on other machines\n")
    sys.exit(1)

ZERO_TOLERANCE: float = 1.0 # mm

lcnc_process = subprocess.Popen(["linuxcnc", config["linuxcnc_folder"]])
time.sleep(10.0) # sleep for a bit to give linuxcnc ample time to start

s = linuxcnc.stat()
c = linuxcnc.command()
e = linuxcnc.error_channel()

c.teleop_enable(False)
c.wait_complete()

s.poll()

ini = linuxcnc.ini(s.ini_filename)

def open_linuxcnc() -> bool:

    if (s == None or c == None):
        print("Stat or Command channels not initialized")
        return False

    try:
        s.poll() # get current values
    except linuxcnc.error:
        print("error", linuxcnc.error)
        return False

    for x in dir(s):
        if not x.startswith("_"):
            print("LinucCNC Status: \n\n")
            print(x, getattr(s,x))

    return True

def set_state_resting() -> bool:

    c.abort()
    c.wait_complete()

    c.mode(linuxcnc.MODE_MANUAL)
    c.wait_complete()

    c.state(linuxcnc.STATE_OFF)
    c.wait_complete()

    time.sleep(2.0)

    s.poll()
    if s.task_state == linuxcnc.STATE_OFF:
        print("Resting Until Next Job")
        return True
    
    return False

def set_state_active() -> bool:

    c.state(linuxcnc.STATE_ON)
    c.wait_complete()

    c.mode(linuxcnc.MODE_MANUAL)
    c.wait_complete()

    s.poll()
    if s.task_state == linuxcnc.STATE_ON:
        print("Returning to Active")
        return home_all_axes()
    
    return False

def home_all_axes() -> bool:

    if (s == None or c == None):
        print("Stat or Command channels not initialized")
        return False
    
    print("Setting Manual Mode for Homing")
    c.mode(linuxcnc.MODE_MANUAL)
    c.wait_complete()

    c.teleop_enable(0)
    c.wait_complete()

    s.poll()
    print("Releasing EStop")
    c.state(linuxcnc.STATE_ESTOP_RESET)
    c.wait_complete()

    s.poll()
    print("Turning machine power on...")
    c.state(linuxcnc.STATE_ON)
    c.wait_complete()

    s.poll()
    print("Homing...")
    c.unhome(-1)
    c.wait_complete()
    s.poll()
    c.home(-1) # home all axes by INI configuration

    count = 0
    while (not all(s.joint[i]['homed'] for i in range(s.axis_mask.bit_count()))) and count < config["linuxcnc_timeout"] * 10:
        s.poll()
        time.sleep(0.1)
        count += 1

    if (count >= config["linuxcnc_timeout"] * 10):
        print(f"Homing timed out in {config["linuxcnc_timeout"]/60} minutes")

        #TODO: check stat for more specific errors

        return False

    print("All axes successfully homed")
    
    return True

def ok_for_mdi() -> bool:
    s.poll()
    return not s.estop and s.enabled and (s.homed.count(1) == s.joints) and (s.interp_state == linuxcnc.INTERP_IDLE)

def handle_errors() -> bool:
    err = e.poll()
    s.poll()
    if not err and not s.estop:
        return True
    
    rc = False

    c.abort()

    #kind, text = err
    #print(f"Error: {text}")

    # handling e-stop
    if (s.estop):
        print("EStop triggered, waiting until further action")
        while s.estop:
            s.poll()
            time.sleep(1.0)
        print("EStop unpressed, returning home")
        return False
    
    # handling not enabled (power off)
    if not (s.enabled):
        rc = False
        c.state(linuxcnc.STATE_ON)
        c.wait_complete()
        rc = True

    # handling not homed, z should home first
    if not all(s.joint[i]['homed'] for i in range(s.axis_mask.bit_count())):
        rc = False
        if home_all_axes():
            rc = True

    # handling wrong mode
    if not (s.task_mode == linuxcnc.MODE_MDI):
        rc = False
        c.mode(linuxcnc.MODE_MDI)
        c.wait_complete()
        rc = True

    # handling interpreter errors
    if (s.interpreter_errcode == 1):
        rc = False
        c.reset_interpreter()
        c.wait_complete()
        rc = True
    

    return rc

# send single-line MDI command
# return codes listed below:
# 0: no errors, normal
# 1: error in state retry currently impossible
# 2: errors handled, retry possible
def send_mdi_line(code: str) -> int:
    rc = 0

    if ok_for_mdi(): # polls inside function
        c.mode(linuxcnc.MODE_MDI)
        c.wait_complete()
        c.mdi(code) # send mdi commands
        crc = c.wait_complete(config["linuxcnc_timeout"])
        if (crc == -1 or crc == linuxcnc.RCS_ERROR):
            rc = 1
            print("MDI line failed" + code)
    else:
        print("State not ok for MDI commands")
        rc = 1
    
    if not handle_errors():
        rc = 1
    
    return rc

def multiline_mdi_loop(codes: list[str]) -> bool:
    for code in codes:
        rc = send_mdi_line(code)
        if (rc == 0):
            continue

        if (rc == 1):
            c.abort()
            home_all_axes()
            return False

    return True

def manual_on_error():
    print("Relinquishing automatic control until ESTOP pressed and released")
    s.poll()
    c.mode(linuxcnc.MODE_MANUAL)
    c.wait_complete()
    while not (s.estop):
        print("Please jog the system out of harm's way, then press ESTOP and release")
        time.sleep(10.0)
        s.poll()

    while s.estop:
        print("Please release ESTOP")
        time.sleep(10.0)
        s.poll()



def check_spindle(speed: float) -> bool:
    s.poll()
    if (s.spindle[0]["enabled"] and s.spindle[0]["speed"] == speed):
        return True
    
    return False

# important for doing spindle commands
def check_z_is_zero() -> bool:
    s.poll()
    if (s.actual_position[2] <= ZERO_TOLERANCE):
        return True
    
    return False

def get_coords() -> dict:
    s.poll()
    axes = s.actual_position
    return {"x": axes[0], "y": axes[1], "z": axes[2], config["clean_plate_axis"]: axes[3], config["gripper_axis"]: axes[4]}

def main():
    if (not open_linuxcnc()):
        print("Linuxcnc failed to initialize properly")
        exit(1)
    
    send_mdi_line("G92.1") # should fail
    set_state_resting()
    set_state_active()
    send_mdi_line("G90")
    send_mdi_line("G01 X100.0 F1000")
    print("Sample MDI sucessful")

    check_spindle(100.0)

    print("Successful Test")


if __name__ == "__main__":
    main()