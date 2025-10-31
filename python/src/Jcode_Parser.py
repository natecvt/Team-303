import json
<<<<<<< HEAD
from datetime import datetime
=======
import os # For accessing environment variables, such as USER


>>>>>>> 3813ca9628b34c40e758f308d6f158657f4b6c0b
array = ["PRINT_COMPLETE", "ERROR"]

def print_event(status):
    if 'event_type' in status:
        event_type = status['event_type']
        return event_type
    else:
        return "Error: event_type not found"

def printer_number(status):
    if 'event_type' in status:
        printer_id = status['printer']['id']
        print(f"Printer {printer_id}")
        return printer_id
    else:
        return "Error: not a valid event"


def printer_status(current_status):
    if current_status == "PRINT_COMPLETE":
        print("The 3D print job has completed successfully.")
    elif current_status == "ERROR":
        print("An error has occurred during the 3D printing process.") 
    else:
        print("Unknown event type.") 
    return
    

def main():
<<<<<<< HEAD
    with open('/home/kenne/Team-303/python/src/msg.json', 'r') as file:
        if file.readable():
            status = json.load(file)
        else:
            print("Error: File not readable")
            log = json.dumps(status, indent=4)
            current_time = datetime.now().strftime("%Y%m%d_%H%M")
            with open(f'log{current_time}.txt', 'w') as log_file:
                log_file.write(log)
            return  
        
    print_id = printer_number(status)
    event_status = print_event(status)
    printer_status(event_status)
=======
    with open(f'{os.getenv("HOME")}/Team-303/msgs/msg.json', 'r') as file:
        status = json.load(file, object_hook=print_event)

    printer_status(status)
>>>>>>> 3813ca9628b34c40e758f308d6f158657f4b6c0b

if __name__ == "__main__":
    main()