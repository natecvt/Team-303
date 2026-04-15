from state_machine import m, p
import linuxcnc_interface as li
from config import config
from storage_tracker import ds, cs
import queue_jobs as qj
import mqtt_manager as mq
import mqtt_send_types as mt
import json_msg_parser as js
import gantry_actions as ga

FLOW_CS_EMPTY = True
FLOW_CS_OK = False

ERROR_MASK = 0b11110111

def check_transition(state, is_man: bool) -> int:
    if state.is_active:
        return 0
    
    return 0b00010000 + (0b00100000 << is_man)

def main_loop():

    # bits determine code, in format 0b00000000
    # First 4 bits (initial code): 
    # 1 CRITICAL printer number does not exist
    # 2 CRITICAL not initial liCNC movement capability 
    # 3 CRITICAL dirty storage full
    # 4 ACCEPTABLE clean storage empty
    #
    # Last 4 bits (result code): 
    # 5 CRITICAL return early? set if 1-3 are not zero (can still do something if clean)
    # 6 CRITICAL posSM failed transition
    # 7 CRITICAL manSM failed transition
    # 8 
    err_flag: int = 0

    mq.heartbeat_q.put(mt.STATUS[0])

    m.activate_initial_state()
    p.activate_initial_state()

    while True:
        if (err_flag & ERROR_MASK) > 0:
            print(f"Errors Code: {bin(err_flag)}")

            p.err = True

            mq.heartbeat_q.put(mt.STATUS[1])
            mq.recieved_q.task_done()
            mq.recieved_q.put(msg) # append earlier message to end of list for retry
            mq.e_msg.fill_data(mt.SEVERITY[2],
                                err_flag,
                                "",
                                li.get_coords(),
                                str(p.configuration),
                                str(m.configuration),
                                mq.e_msg.error_message(err_flag)
                                )
            mq.publish_message(mq.e_msg, mq.TOPIC_E)

            li.time.sleep(10.0)

        err_flag = 0

        # get storage reset messages first, guarantees best accounting
        if not (mq.storage_q.empty()):
            print("Storage reset message received")
            msg = mq.storage_q.get()
            mq.ak_msg.fill_data(message="Storage Reset Prompt Received",
                                status=mt.STATUS[2])
            mq.publish_message(mq.ak_msg, mq.TOPIC_A)

            amount = js.storage_reset_get_amount(msg)
            if (amount == None):
                print("Bad message format")
            cs.reset(amount)
            ds.reset()
            mq.storage_q.task_done()
            # do not continue here, could be a message in the other queue

        if (mq.recieved_q.empty()):
            print("Queue empty")
            li.time.sleep(10.0)
            continue

        # get message and parse for printer
        msg = mq.recieved_q.get()
        print(msg)

        if (js.get_event(msg) == None):
            print("Bad message")
            continue

        # get event and publish ack
        if (js.get_event(msg) == js.EVENT_PC):

            mq.ak_msg.fill_data(message=f"Print Complete Received ID {js.printer_get_number(msg)}",
                                status=mt.STATUS[0])
            mq.publish_message(mq.ak_msg, mq.TOPIC_A)

        num = js.printer_get_number(msg)

        if num == None:
            print("Invalid Message")
            continue

        mq.sc_msg.update_time() # for calculating delta T

        # initial errors
        err_flag |= (not (num in ga.PRINTERS.keys())) << 0
        err_flag |= (not li.ok_for_mdi()) << 1
        err_flag |= (ds.is_full()) << 2
        err_flag |= (cs.is_empty()) << 3

        if err_flag & 0b0111 > 0:
            err_flag |= (1 << 4) # set return early bit if errors 0-2 happen
            continue

        if (err_flag & (1 << 4)):
           print(f"Initial Errors Code: {bin(err_flag)}")
           continue 
        
        flow = err_flag & (1 << 3)
        print("Error state nominal")
        print(f"Processing plate replacement from printer {num}")

        if flow == FLOW_CS_OK:
            p.send("home_printer", m=m, number=num)
            err_flag |= check_transition(p.Printer, False)
            if (err_flag & (1 << 4)): continue

            m.send("grab", p=p)
            err_flag |= check_transition(m.Full, True)
            if (err_flag & (1 << 4)): continue

            p.send("printer_dirty", m=m)
            err_flag |= check_transition(p.DirtyS, False)
            if (err_flag & (1 << 4)): continue

            m.send("release", p=p)
            err_flag |= check_transition(m.Empty, True)
            if (err_flag & (1 << 4)): continue

            p.send("dirty_clean", m=m)
            err_flag |= check_transition(p.CleanS, False)
            if (err_flag & (1 << 4)): continue

            m.send("grab", p=p)
            err_flag |= check_transition(m.Full, True)
            if (err_flag & (1 << 4)): continue

            p.send("clean_printer", m=m, number=num)
            err_flag |= check_transition(p.Printer, False)
            if (err_flag & (1 << 4)): continue

            m.send("release", p=p)
            err_flag |= check_transition(m.Empty, True)
            if (err_flag & (1 << 4)): continue

            p.send("printer_home", m=m, number=num)
            err_flag |= check_transition(p.Home, False)
            if (err_flag & (1 << 4)): continue
        
        else:
            print("Clean storage empty, proceeding without plate replacement")

            p.send("home_printer", m=m, number=num)
            err_flag |= check_transition(p.Printer, False)
            if (err_flag & (1 << 4)): continue

            m.send("grab", p=p)
            err_flag |= check_transition(m.Full, True)
            if (err_flag & (1 << 4)): continue

            p.send("printer_dirty", m=m)
            err_flag |= check_transition(p.DirtyS, False)
            if (err_flag & (1 << 4)): continue

            m.send("release", p=p)
            err_flag |= check_transition(m.Empty, True)
            if (err_flag & (1 << 4)): continue

            p.send("dirty_home", m=m, number=num)
            err_flag |= check_transition(p.Home, False)
            if (err_flag & (1 << 4)): continue
        
        print("Swap Complete, moving to next item in queue")
        mq.sc_msg.fill_data(num,
                            mt.SC_STATUS[flow],
                            li.get_coords(), 
                            str(p.configuration), 
                            str(m.configuration)
                            )
        mq.publish_message(mq.sc_msg, mq.TOPIC_C)

        mq.recieved_q.task_done()

def main():
    # linuxCNC
    if not (li.open_linuxcnc()):
        print("LinuxCNC not opened correctly")
        exit(1)
    
    if not (li.home_all_axes()):
        print("Homing failed")
        exit(1)

    #li.set_state_resting()

    # mqtt
    ip = config["mqtt_broker_ip"]
    print(f"MQTT IP Address: {ip}")
    port = 1883
    if not mq.connect(host=ip, port=port):
        print("MQTT connection failed")
        exit(2)

    # seperate worker and mqtt threads
    mt = qj.create_message_thread()
    lt = qj.create_main_loop_thread(main_loop)
    ht = qj.create_heartbeat_thread(qj.heartbeat_loop)

    if (lt.name == "worker"):
        print("Starting threads...")
        qj.start_threads([mt, lt, ht])
    else:
        print("Threads not created correctly")
        exit(3)

    print("Initialization Done")


if __name__ == "__main__":
    main()