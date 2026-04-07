from statemachine import StateMachine, State, exceptions
from config import config
import linuxcnc_interface as li
import gantry_actions as ga
from storage_tracker import cs, ds

class ManipulatorSM(StateMachine):
    # Define states
    Empty = State(initial=True)
    Full = State()
    
    grab = Empty.to(Full, cond="plate_grab")
    release = Full.to(Empty, cond="plate_release")

    def require_manipulator(self, allowed_states) -> bool:
        if (allowed_states not in self.configuration):
            return False
        
        return True
        
    def placeholder(self):
        print(self.configuration)
        pass
    
    def plate_grab(self, p) -> bool:

        at_clean = p.require_position(p.CleanS)
        at_printer = p.require_position(p.Printer)

        if not (at_clean or at_printer):
            return False
        
        if (at_clean and at_printer):
            print("Invalid state")
            return False

        if li.ok_for_mdi():
            if at_clean:
                move = ga.gcode_grab_plate_cs(True)
            if at_printer:
                move = ga.gcode_open_door(True)
                move.extend(ga.gcode_grab_plate_printer(True))
                move.extend(ga.gcode_close_door(True))
                
            if not (li.multiline_mdi_loop(move)):
                return False
            
        return True
    
    def plate_release(self, p) -> bool:
        at_dirty = p.require_position(p.DirtyS)
        at_printer = p.require_position(p.Printer)

        if not (at_dirty or at_printer):
            return False
        
        if (at_dirty and at_printer):
            print("Invalid state")
            return False

        if li.ok_for_mdi():

            if at_dirty:
                move = ga.gcode_release_plate_ds(True)
            if at_printer:
                move = ga.gcode_open_door(True)
                move.extend(ga.gcode_release_plate_printer(True))
                move.extend(ga.gcode_close_door(True))
                
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

    def require_position(self, *allowed_states) -> bool:
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
        
        if not (li.check_z_is_zero()):
            return False
        
        if li.ok_for_mdi():
            coords: dict = ga.read_printer_coords(number)

            if coords['x'] == None:
                return False
            
            move = ga.gcode_move_to_printer(coords, True)

            if li.multiline_mdi_loop(move):
                return True

        return False

    def clean_to_printer(self, m: ManipulatorSM, number: int) -> bool:
        if not (m.require_manipulator(ManipulatorSM.Clean)):
            return False
        
        if not (li.check_spindle(ga.MAN_ANGLE_P90)):
            return False
        
        if not (li.check_z_is_zero()):
            return False
        
        if li.ok_for_mdi():
            coords: dict = ga.read_printer_coords(number)

            if coords['x'] == None:
                return False
            
            move = ga.gcode_move_to_printer(coords, True)

            if li.multiline_mdi_loop(move):
                return True

        return False
    
    def printer_to_home(self, m: ManipulatorSM) -> bool:
        if not (m.require_manipulator(ManipulatorSM.Empty)):
            return False
        
        if not (li.check_spindle(ga.MAN_ANGLE_P90)):
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
        
        if not (li.check_spindle(ga.MAN_ANGLE_P90)):
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
        
        if not (li.check_spindle(ga.MAN_ANGLE_P90)):
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
        
        if not (li.check_spindle(ga.MAN_ANGLE_P90)):
            return False
        
        if not (li.check_z_is_zero()):
            return False

        if li.ok_for_mdi():
            move = ga.gcode_move_to_ds(r, c, True)

            if li.multiline_mdi_loop(move):
                return True
            
        return False
    
    def dirty_to_clean(self, m: ManipulatorSM):
        if (cs.is_empty()):
            return False
        
        if not (m.require_manipulator(ManipulatorSM.Empty)):
            return False
        
        if not (li.check_spindle(ga.MAN_ANGLE_P90)):
            return False
        
        if not (li.check_z_is_zero()):
            return False
        
        if li.ok_for_mdi():
            move = ga.gcode_move_to_cs(True)

            if li.multiline_mdi_loop(move):
                return True
            
        return False
        


m = ManipulatorSM()
p = PositionSM()

def main():
    m.activate_initial_state()

    p.send("go_printer")

    if p.Printer.is_active:
        print("transition success")
    

if __name__ == "__main__":
    main()