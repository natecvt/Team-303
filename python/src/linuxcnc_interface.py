import subprocess
import sys
import time
import config

try:
    import linuxcnc
except:
    print("linuxcnc not found, don't run this on other machines\n")
    sys.exit(1)

LCNC_PATH: str = config.get_param("linuxcnc_folder")
LCNC_MOTION_TIMEOUT: int = config.get_param("linuxcnc_timeout")

s: linuxcnc.stat = None
c: linuxcnc.command = None

def open_linuxcnc() -> subprocess.Popen | None:
    s = linuxcnc.stat()
    c = linuxcnc.command()

    if (s == None or c == None):
        print("Stat and Command channels not initialized")
        return None

    lcnc_process = subprocess.Popen(["linuxcnc", LCNC_PATH])

    time.sleep(10.0) # sleep for a minute to give linuxcnc ample time to start

    try:
        s.poll() # get current values
    except (linuxcnc.error, detail):
        print("error", detail)
        return None

    for x in dir(s):
        if not x.startswith("_"):
            print("LinucCNC Status: \n\n")
            print(x, getattr(s,x))

    return lcnc_process

def home_all_axes() -> bool:
    if (s == None or c == None):
        print("Stat and Command channels not initialized")
        return False

    s.poll()

    if (s.estop):
        print("EStop released, starting machine...")
    else:
        print("Releasing EStop...")
        c.state(linuxcnc.STATE_ESTOP_RESET)
        c.wait_complete()

    s.poll()

    if not s.machine_is_on:
        print("Turning machine power on...")
        c.state(linuxcnc.STATE_ON)
        c.wait_complete()
        s.poll()
    else:
        print("Machine is already powered on. Proceeding...")

    print("Homing...")
    c.home(-1) # home all axes by INI configuration
    rc = c.wait_complete(LCNC_MOTION_TIMEOUT)
    if (rc == -1 or rc == linuxcnc.RCS_ERROR):
        print("Homing timed out in 2 minutes")

        #TODO: check stat for more specific errors

        return False

    s.poll()
    if all(s.joint[i]['homed'] for i in range(s.axes)):
        print("All axes successfully homed")
    else:
        print("Homing sequence complete, but some axes might not be homed. Check INI configuration")
    
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

    if (not (s.interp_state == linuxcnc.INTERP_IDLE) or not (s.interp_state == linuxcnc.INTERP_WAITING)):
        print("Interpreter in odd state for no motion, checking further")
        if (s.interpreter_errcode == linuxcnc.INTERP_ERROR):
            print("Interpreter in err state, handling")

            #TODO: handle this error

    return True


def send_mdi_line(code: str) -> bool:
    if ok_for_mdi(): # polls inside function

        #TODO: detect whether move would exceed axes
        c.mdi(code) # send mdi commands
        c.wait_complete(LCNC_MOTION_TIMEOUT)

    else:
        return False
    
    if handle_not_ok():
        return True
    
    print("Unhandled error caught")
    return False


def main():

    

    pass

if __name__ == "__main__":
    main()