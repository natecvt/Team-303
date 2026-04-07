from datetime import datetime
import time
import json

SEVERITY = {
    0: "NOTICE",
    1: "WARNING",
    2: "ERROR"
}


class Error:
    contents = {
        "event_type": "ERROR",
        "error_code": int,
        "timestamp": str,
        "source": str,
        "at": {
            "statep": str,
            "statem": str,
            "location": dict
        },

        "message": str,
        "severity": str
    }

    def __init__(self):
        pass

    def __str__(self):
        return json.dumps(self.contents, indent=4)
    
    def error_message(err_flag: int) -> str:
        msg_lookup = {1 : "Wrong printer number\n",
                    2 : "LinuxCNC in bad state\n",
                    3 : "Dirty storage full\n",
                    4 : "Clean storage full\n",
                    5 : "Returned early, see following messages:\n\t",
                    6 : "Position State Machine failed transition\n",
                    7 : "Manipulator State Machine failed transition\n",
                    8 : ""}

        msg = ""
        for i in range(err_flag.bit_length()):
            if err_flag & (1 << i):
                msg += msg_lookup[i]

        return msg

    def fill_data(self, 
                  severity=contents["severity"],
                  error_code=contents["error_code"],
                  source=contents["source"],
                  location=contents["at"]["location"],
                  statep=contents["at"]["statep"], 
                  statem=contents["at"]["statem"],
                  message=contents["message"]):
        
        self.contents["timestamp"] = str(datetime.now().time())
        self.contents["severity"] = severity
        self.contents["error_code"] = error_code
        self.contents["source"] = source
        self.contents["at"]["location"] = location
        self.contents["at"]["statep"] = statep
        self.contents["at"]["statem"] = statem
        self.contents["message"] = message

class SwapComplete:
    contents = {
        "event_type": "SWAP_COMPLETE",
        "timestamp": str,
        "printer": {
            "id": int
        },

        "operation": {
            "status": "SUCCESS",
            "duration_s": int,
        },

        "gantry": {
            "statep": str,
            "statem": str,
            "location": dict
        }
    }

    __creation_time: int

    def __init__(self):
        self.update_time()
        pass

    def __str__(self):
        return json.dumps(self.contents, indent=4)
    
    def update_time(self):
        t = datetime.now()
        self.__creation_time = t.second + t.minute * 60

    def fill_data(self, 
                  id=contents["printer"]["id"], 
                  location=contents["gantry"]["location"],
                  statep=contents["gantry"]["statep"], 
                  statem=contents["gantry"]["statem"]):
        
        t = datetime.now()

        self.contents["timestamp"] = str(t.time())
        self.contents["printer"]["id"] = id
        self.contents["operation"]["duration_s"] = t.second + t.minute * 60 - self.__creation_time
        self.contents["gantry"]["location"] = location
        self.contents["gantry"]["statep"] = statep
        self.contents["gantry"]["statem"] = statem

def main():
    sc = SwapComplete()

    time.sleep(110.0)

    sc.fill_data(2, {"x": 234.4, "y": 64.6}, "Home", "Empty")

    print(sc)

if __name__ == "__main__":
    main()