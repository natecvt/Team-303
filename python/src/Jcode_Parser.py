import json
def print_event(dct):
    if 'event_type' in dct:
        return str(dct['event_type'])
    return dct

with open('/home/kenne/Team-303/python/src/msg.json', 'r') as file:
    data = json.load(file, object_hook=print_event)

def main():
    print(data)

    pass










if __name__ == "__main__":

    main()