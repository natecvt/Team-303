from threading import Thread, Lock
import yaml
import time

import mqtt_manager as mqr

def create_message_thread() -> Thread:
    return Thread(target=mqr.mqttc.loop_forever)

def create_main_loop_thread(main_loop) -> Thread | None:
    if callable(main_loop):
        return Thread(target=test_loop)
    
    return None

def start_threads(mt: Thread, lt: Thread):
    mt.start()
    lt.start()

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

    start_threads(mt, lt)

    time.sleep(10.0)
    mqr.recieved_q.join()

    print("finished all")

if __name__ == "__main__":
    main()
