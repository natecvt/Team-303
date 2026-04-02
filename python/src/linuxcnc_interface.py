import subprocess
import sys
import time
from config import config

try:
    import linuxcnc
except:
    print("linuxcnc not found, don't run this on other machines\n")
    sys.exit(1)

LCNC_PATH: str = config["linuxcnc_folder"]
LCNC_MOTION_TIMEOUT: float = config["linuxcnc_timeout"]

lcnc_process = subprocess.Popen(["linuxcnc", LCNC_PATH])
time.sleep(10.0) # sleep for a minute to give linuxcnc ample time to start


s = linuxcnc.stat()
c = linuxcnc.command()

c.teleop_enable(False)
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

def home_all_axes() -> bool:
    if (s == None or c == None):
        print("Stat or Command channels not initialized")
        return False

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
    c.home(-1) # home all axes by INI configuration

    count = 0
    while not all(s.joint[i]['homed'] for i in range(s.axis_mask.bit_count())) and count < LCNC_MOTION_TIMEOUT * 10:
        s.poll()
        time.sleep(0.1)
        count += 1

    if (count >= LCNC_MOTION_TIMEOUT * 10):
        print(f"Homing timed out in {LCNC_MOTION_TIMEOUT/60} minutes")

        #TODO: check stat for more specific errors

        return False

    print("All axes successfully homed")
    
    return True

def ok_for_mdi() -> bool:
    s.poll()
    return not s.estop and s.enabled and (s.homed.count(1) == s.joints) and (s.interp_state == linuxcnc.INTERP_IDLE)

def handle_not_ok() -> bool:
    s.poll()

    if (s.estop):
        print("EStop triggered, waiting until further action")
        while True:
            if not s.estop:
                break
            s.poll()
            time.sleep(1.0)

        print("EStop unpressed, returning to regular operation")
    
    if (not s.enabled):
        print("Trajectory planner disabled, ")

        #TODO: handle this error

    if (not (s.interp_state == linuxcnc.INTERP_IDLE) and not (s.interp_state == linuxcnc.INTERP_WAITING)):
        print("Interpreter in odd state for no motion, checking further")
        if (s.interpreter_errcode == linuxcnc.INTERP_ERROR):
            print("Interpreter in err state, handling")

            #TODO: handle this error

    return True


def send_mdi_line(code: str) -> bool:
    if ok_for_mdi(): # polls inside function
        c.mode(linuxcnc.MODE_MDI)
        c.wait_complete()
        #TODO: detect whether move would exceed axes
        c.mdi(code) # send mdi commands
        rc = c.wait_complete(LCNC_MOTION_TIMEOUT)
        if (rc == -1 or rc == linuxcnc.RCS_ERROR):
            print("MDI code failed")
            return False

    else:
        return False
    
    if handle_not_ok():
        return True
    
    print("Unhandled error caught")
    return False


def main():
    if (not open_linuxcnc()):
        print("Linuxcnc failed to initialize properly")
        exit(1)
    
    if (home_all_axes()):
        send_mdi_line("G01 X00 Y00 F1500")
        print("Sample MDI sucessful")

if __name__ == "__main__":
    main()