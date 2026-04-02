import state_machine as sm
import linuxcnc_interface as li
from config import config
from storage_tracker import ds, cs
import queue_jobs as qj
import mqtt_manager as mq
import json_msg_parser as js
import gantry_actions as ga

def main_loop():
    while True:
        if (mq.recieved_q.all_tasks_done):
            li.time.sleep(10.0)
            print("queue empty")
            continue
        
        
        pass

def main():
    # linuxCNC
    if not (li.open_linuxcnc()):
        exit(1)
    
    if not (li.home_all_axes()):
        exit(1)

    if not (li.ok_for_mdi()):
        exit(1)

    # mqtt
    if not mq.assign_callbacks(on_msg=mq.on_message, on_con=mq.on_connect):
        exit(2)

    ip = config["mqtt_broker_ip"]
    print(ip)
    port = 1883
    if not mq.connect(host=ip, port=port):
        exit(2)

    # seperate worker and mqtt threads
    mt = qj.create_message_thread()
    lt = qj.create_main_loop_thread(main_loop)

    if (lt.name == "main"):
        print("starting threads...")
        qj.start_threads([mt, lt])
    else: 
        exit(3)

    print("main done")


if __name__ == "__main__":
    main()