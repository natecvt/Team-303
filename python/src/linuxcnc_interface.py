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
LCNC_HOME_TIMEOUT: int = config.get_param("linuxcnc_homing_timeout")

s: linuxcnc.stat
c: linuxcnc.command

def create_s_and_c():
    s = linuxcnc.stat()
    c = linuxcnc.command()

def open_linuxcnc() -> subprocess.Popen | None:
    lcnc_process = subprocess.Popen(["linuxcnc", LCNC_PATH])

    time.sleep(10.0) # sleep for a minute to give linuxcnc ample time to start

    try:
        s.poll() # get current values
    except (linuxcnc.error, detai):
        print("error", detail)
        return None

    for x in dir(s):
        if not x.startswith("_"):
            print("LinucCNC Status: \n\n")
            print(x, getattr(s,x))

    return lcnc_process

def home_all_axes() -> bool:
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
    if (c.wait_complete(LCNC_HOME_TIMEOUT) == -1):
        print("Homing timed out in 2 minutes")

        #TODO: check stat for more specific errors

        return False

    s.poll()
    if all(s.joint[i]['homed'] for i in range(s.axes)):
        print("All axes successfully homed")
    else:
        print("Homing sequence complete, but some axes might not be homed. Check INI configuration")
    
    return True

def ok_for_mdi():
    return not s.estop and s.enabled and (s.homed.count(1) == s.joints) and (s.interp_state == linuxcnc.INTERP_IDLE)

if (ok_for_mdi()):
	print("Entered MDI-Safe Mode")
	sys.exit(0)
