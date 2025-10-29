import json
array = ["PRINT_COMPLETE", "ERROR"]

def print_event(dct):
    if 'event_type' in dct:
        return str(dct['event_type'])
    return dct

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
        status = json.load(file, object_hook=print_event)

    printer_status(status)

if __name__ == "__main__":

    main()