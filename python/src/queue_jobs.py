from threading import Thread, Lock
from config import config
import time

import mqtt_manager as mqr

HEARTBEAT_DT = config["heartbeat_duration"]

def create_message_thread() -> Thread:
    return Thread(target=mqr.mqttc.loop_forever, name="messager")

def create_main_loop_thread(main_loop) -> Thread:
    if callable(main_loop):
        return Thread(target=main_loop, name="worker")
    
    return Thread()

def create_heartbeat_thread(heartbeat_loop) -> Thread:
    if callable(heartbeat_loop):
        return Thread(target=heartbeat_loop, name="heartbeat")
    
    return Thread()

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

def heartbeat_loop():
    while True:
        time.sleep(HEARTBEAT_DT)

        if not mqr.heartbeat_q.empty():
            mqr.hb_msg.fill_data(status=mqr.heartbeat_q.get())
            mqr.heartbeat_q.task_done()

        mqr.publish_message(mqr.hb_msg, mqr.TOPIC_H)

def main():
    mqr.connect("localhost")

    mt = create_message_thread()
    lt = create_main_loop_thread(test_loop)

    if not (mt == None or lt == None):
        start_threads([mt, lt])

if __name__ == "__main__":
    main()
