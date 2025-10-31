import json
from datetime import datetime
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

if __name__ == "__main__":

    main()