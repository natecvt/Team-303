from statemachine import StateMachine, State, exceptions
from config import config
import linuxcnc_interface as li
import gantry_actions as ga
from storage_tracker import cs, ds

class ManipulatorSM(StateMachine):
    # Define states
    Empty = State(initial=True)
    Full = State()
    Clean = State()
    
    grab = Empty.to(Full, cond="plate_grab")
    release = Full.to(Empty, cond="plate_release")
    clean = Empty.to(Clean, cond="clean_grab") | Clean.to(Empty, cond="clean_release")

    def require_manipulator(self, allowed_states):
        if (allowed_states not in self.configuration):
            return False
        
        return True
        
    def placeholder(self):
        print(self.configuration)
        pass
    
    def plate_grab(self, p) -> bool:
        if not (p.require_position(p.Printer)):
            return False

        if li.ok_for_mdi():
            move = ga.gcode_open_door(False)
            if not (li.multiline_mdi_loop(move)):
                return False
            
        if li.ok_for_mdi():
            move = ga.gcode_grab_plate_printer(False)
            if not (li.multiline_mdi_loop(move)):
                return False
            
        if li.ok_for_mdi():
            move = ga.gcode_close_door(False)
            if not (li.multiline_mdi_loop(move)):
                return False
            
        return True
    
    def plate_release(self, p) -> bool:
        if not (p.require_position(p.DirtyS)):
            return False

        if li.ok_for_mdi():
            move = ga.gcode_release_plate_ds(False)
            if not (li.multiline_mdi_loop(move)):
                return False
        
        return True

    def clean_grab(self, p) -> bool:
        if not (p.require_position(p.DirtyS)):
            return False
        
        if li.ok_for_mdi():
            move = ga.gcode_grab_plate_cs(False)
            if not (li.multiline_mdi_loop(move)):
                return False
        
        return True


    def clean_release(self, p) -> bool:
        if not (p.require_position(p.Printer)):
            return False
        
        if li.ok_for_mdi():
            move = ga.gcode_release_plate_printer(False)
            if not (li.multiline_mdi_loop(move)):
                return False
        
        return True

        
class PositionSM(StateMachine):
    # Define states
    Home = State(initial=True)
    Printer = State()
    DirtyS = State()
    CleanS = State()

    go_printer = Home.to(Printer, cond="home_to_printer") | CleanS.to(Printer, cond="clean_to_printer")
    go_home = Printer.to(Home, cond="printer_to_home") | DirtyS.to(Home, cond="dirty_to_home") | CleanS.to(Home, cond="clean_to_home")
    go_dirty = Printer.to(DirtyS, cond="printer_to_dirty")
    go_clean = DirtyS.to(CleanS, cond="dirty_to_clean")

    def require_position(self, *allowed_states):
        if (allowed_states not in self.configuration):
            return False
        
        return True
        
    def placeholder(self):
        print(self.configuration)
        pass

    def home_to_printer(self, m: ManipulatorSM, number: int):

        if not (m.require_manipulator(ManipulatorSM.Empty)):
            return False

        if ds.is_full():
            print("DS Full, can't do anything")
            return False

        if not li.set_state_active():
            return False
        
        if not (m.require_manipulator(ManipulatorSM.Clean)):
            return False
        
        if not (li.check_spindle(config["angle_90"])):
            return False
        
        if not (li.check_z_is_zero()):
            return False
        
        if li.ok_for_mdi():

            move = ga.gcode_move_to_printer(number, True)

            if li.multiline_mdi_loop(move):
                return True

        return False

    def clean_to_printer(self, m: ManipulatorSM, number: int) -> bool:
        if not (m.require_manipulator(ManipulatorSM.Clean)):
            return False
        
        if not (li.check_spindle(config["angle_90"])):
            return False
        
        if not (li.check_z_is_zero()):
            return False
        
        if li.ok_for_mdi():

            move = ga.gcode_move_to_printer(number, True)

            if li.multiline_mdi_loop(move):
                return True

        return False
    
    def printer_to_home(self, m: ManipulatorSM) -> bool:
        if not (m.require_manipulator(ManipulatorSM.Empty)):
            return False
        
        if not (li.check_spindle(config["angle_90"])):
            return False
        
        if not (li.check_z_is_zero()):
            return False
        
        li.c.mode(li.linuxcnc.MODE_MANUAL)
        li.c.wait_complete()

        if li.home_all_axes():
            return li.set_state_resting()
        
        return False

    def dirty_to_home(self, m: ManipulatorSM) -> bool:
        if not (m.require_manipulator(ManipulatorSM.Empty)):
            return False
        
        if not (li.check_spindle(config["angle_90"])):
            return False
        
        if not (li.check_z_is_zero()):
            return False
        
        li.c.mode(li.linuxcnc.MODE_MANUAL)
        li.c.wait_complete()

        if li.home_all_axes():
            return li.set_state_resting()
        
        return False

    def clean_to_home(self, m: ManipulatorSM) -> bool:
        if not (m.require_manipulator(ManipulatorSM.Empty)):
            return False
        
        if not (li.check_spindle(config["angle_90"])):
            return False
        
        if not (li.check_z_is_zero()):
            return False
        
        li.c.mode(li.linuxcnc.MODE_MANUAL)
        li.c.wait_complete()

        if li.home_all_axes():
            return li.set_state_resting()
        
        return False

    def printer_to_dirty(self, m: ManipulatorSM) -> bool:
        if (ds.is_full()):
            return False
        
        [r, c] = ds.detect_first_free()

        if not (m.require_manipulator(ManipulatorSM.Full)):
            return False

        if li.ok_for_mdi():
            move = ga.gcode_move_to_ds(r, c, False)

            if li.multiline_mdi_loop(move):
                return True
            
        return False
    
    def dirty_to_clean(self, m: ManipulatorSM):
        if (cs.is_empty()):
            return False
        
        if not (m.require_manipulator(ManipulatorSM.Empty)):
            return False
        
        [x, y] = cs.get_origin()

        if li.ok_for_mdi():
            move = ga.gcode_generic_move(x, y)

            if li.multiline_mdi_loop(move):
                return True
            
        return False
        


m = ManipulatorSM()
p = PositionSM()

def main():
    m.activate_initial_state()

    m.grab()
    try:
        m.clean()
    except exceptions.TransitionNotAllowed:
        print("Wrong transition queued, expected")

    m.release()
    m.clean()
    

if __name__ == "__main__":
    main()