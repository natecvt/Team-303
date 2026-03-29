from threading import Thread, Lock
import yaml
import time

import mqtt_manager as mqr

def create_message_thread() -> Thread:
    return Thread(target=mqr.mqttc.loop_forever)

def create_main_loop_thread(main_loop) -> Thread | None:
    if callable(main_loop):
        return Thread(target=main_loop)
    
    return None

# number of threads should be 2, but can be any number within this function
def start_threads(threads: list[Thread]):
    for thread in threads:
        thread.start()

def test_loop():
    while True:
        q_item = mqr.recieved_q.get()
        print(f"Received:\n\n {str(q_item)}")
        time.sleep(5.0)
        mqr.recieved_q.task_done()

def main():
    if (mqr.assign_callbacks(mqr.on_message, mqr.on_connect)):
        mqr.connect("localhost")

    mt = create_message_thread()
    lt = create_main_loop_thread(test_loop)

    if not (mt == None or lt == None):
        start_threads([mt, lt])

if __name__ == "__main__":
    main()
