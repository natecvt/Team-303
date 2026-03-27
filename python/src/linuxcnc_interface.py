import subprocess
import sys
import time

try:
    import linuxcnc
except:
    print("linuxcnc not found, assuming this is for tests\n")


lcnc_process = subprocess.Popen(["linuxcnc", "linuxCNC/team303_machine.ini"])

time.sleep(10.0) # sleep for a minute to give linuxcnc ample time to start

try:
    s = linuxcnc.stat() # create a connection to the status channel
    c = linuxcnc.command() 
    s.poll() # get current values
except (linuxcnc.error, detai):
    print("error", detail)
    sys.exit(1)

for x in dir(s):
    if not x.startswith("_"):
        print("LinucCNC Status: \n\n")
        print(x, getattr(s,x))

def ok_for_mdi():
    s.poll()
    return not s.estop and s.enabled and (s.homed.count(1) == s.joints) and (s.interp_state == linuxcnc.INTERP_IDLE)

if (ok_for_mdi()):
	print("Entered MDI-Safe Mode")
	sys.exit(0)
