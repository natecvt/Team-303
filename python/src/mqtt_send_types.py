from datetime import datetime
import time
import json

SEVERITY = {
    0: "NOTICE",
    1: "WARNING",
    2: "ERROR"
}

STATUS = {
    0: "NORMAL",
    1: "ERROR",
    2: "STORAGE_RESET"
}

class Message:
    contents: dict

    def __str__(self):
        return json.dumps(self.contents, indent=4)


class Error(Message):
    contents = {
        "event_type": "ERROR",
        "error_code": 0,
        "timestamp": "",
        "source": "",
        "at": {
            "statep": "",
            "statem": "",
            "location": {}
        },

        "message": "",
        "severity": ""
    }
    
    def error_message(self, err_flag: int) -> str:
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
                msg += msg_lookup[i+1]

        return msg

    def fill_data(self, 
                  severity=contents["severity"],
                  error_code=contents["error_code"],
                  source=contents["source"],
                  location=contents["at"]["location"],
                  statep=contents["at"]["statep"], 
                  statem=contents["at"]["statem"],
                  message=contents["message"]):
        
        self.contents["timestamp"] = datetime.now().time().isoformat()
        self.contents["severity"] = severity
        self.contents["error_code"] = error_code
        self.contents["source"] = source
        self.contents["at"]["location"] = location
        self.contents["at"]["statep"] = statep
        self.contents["at"]["statem"] = statem
        self.contents["message"] = message

class SwapComplete(Message):
    contents = {
        "event_type": "SWAP_COMPLETE",
        "timestamp": "",
        "printer": {
            "id": 0
        },

        "operation": {
            "status": "SUCCESS",
            "duration_s": 0,
        },

        "gantry": {
            "statep": "",
            "statem": "",
            "location": {}
        }
    }

    __creation_time: int

    def __init__(self):
        self.update_time()
    
    def update_time(self):
        t = datetime.now()
        self.__creation_time = t.second + t.minute * 60

    def fill_data(self, 
                  id=contents["printer"]["id"], 
                  location=contents["gantry"]["location"],
                  statep=contents["gantry"]["statep"], 
                  statem=contents["gantry"]["statem"]):
        
        t = datetime.now()

        self.contents["timestamp"] = t.isoformat()
        self.contents["printer"]["id"] = id
        self.contents["operation"]["duration_s"] = t.second + t.minute * 60 - self.__creation_time
        self.contents["gantry"]["location"] = location
        self.contents["gantry"]["statep"] = statep
        self.contents["gantry"]["statem"] = statem

class HeartBeat(Message):
    contents = {
        "event_type": "HEARTBEAT",
        "status": "",
        "timestamp": "",
    }

    def __init__(self):
        pass

    def fill_data(self,
                  status=contents["status"]):
        
        self.contents["status"] = status
        self.contents["timestamp"] = datetime.now().isoformat()

class Acknowledgement(Message):
    contents = {
        "event_type": "ACKNOWLEDGEMENT",
        "status": "",
        "message": "",
        "timestamp": ""
    }

    def fill_data(self,
                  status=contents["status"],
                  message=contents["message"]):
        
        self.contents["status"] = status
        self.contents["message"] = message
        self.contents["timestamp"] = datetime.now().isoformat()

def main():
    sc = SwapComplete()

    time.sleep(10.0)

    sc.fill_data(2, {"x": 234.4, "y": 64.6}, "Home", "Empty")

    print(sc)

if __name__ == "__main__":
    main()