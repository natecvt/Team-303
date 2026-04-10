import json
import os # For accessing environment variables, such as USER
import datetime
from datetime import datetime

EVENT_PC = "PRINT_COMPLETE"
EVENT_E = "ERROR"
EVENT_SC = "SWAP_COMPLETE"
EVENT_SR = "STORAGE_RESET"

def get_event(msg: str) -> str:
    obj = json.loads(str)

    if "event_type" in obj.keys():
        return obj["event_type"]
    
    return None

def storage_reset_get_amount(msg: str) -> int | None:
    obj = json.loads(str)

    if "plate_amount" in obj.keys():
        return obj["plate_amount"]
    
    return None

def storage_reset_get_time(msg: str) -> str | None:
    obj = json.loads(str)

    if "timestamp" in obj.keys():
        return obj["timestamp"]
    
    return None

def printer_get_number(msg: str) -> int|None:
    obj = json.loads(str)

    if "printer" in obj.keys():
        return obj["printer_id"]
    
    return None

# file should be open before this
def write_str_as_json(file, contents: str):
    if not file.writable():
        print("Invalid file for writing")
    
    json.dump(contents, file, indent=4)

def main():
        with open(f'{os.getenv("HOME")}/Team-303/msgs/msg.json', 'r') as file:
            if file.readable():
                status = json.load(file)
                print("File read successfully")
            else:
                print("Error: File not readable")
                log = json.dumps(status, indent=4)
                current_time = datetime.now().strftime("%Y%m%d_%H%M")
                with open(f'log{current_time}.txt', 'w') as log_file:
                    log_file.write(log)
                return

if __name__ == "__main__":
    main()