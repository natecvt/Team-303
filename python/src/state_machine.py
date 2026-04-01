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
    
    grab = Empty.to(Full, on="placeholder")
    release = Full.to(Empty, on="placeholder")
    clean = Empty.to(Clean, on="placeholder") | Clean.to(Empty, on="placeholder")

    def require_manipulator(self, allowed_states):
        if (allowed_states not in self.configuration):
            return False
        
        return True
        
    def placeholder(self):
        print(self.configuration)
        pass

class PositionSM(StateMachine):
    # Define states
    Home = State(initial=True)
    Printer = State()
    DirtyS = State()
    CleanS = State()

    go_printer = Home.to(Printer, on="placeholder") | CleanS.to(Printer, cond="clean_to_printer")
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

    def clean_to_printer(self, m: ManipulatorSM, number: int) -> bool:
        if not (m.require_manipulator(ManipulatorSM.Clean)):
            return False
        
        li.s.poll()
        if not (li.s.spindle.enabled and li.s.spindle.speed == config["angle_90"]):
            return False
        
        if li.ok_for_mdi():

            move = ga.gcode_move_to_printer(number)

            if li.send_mdi_line(move):
                return True

        return False
    
    def printer_to_home(self, m: ManipulatorSM) -> bool:
        if not (m.require_manipulator(ManipulatorSM.Empty)):
            return False
        
        li.s.poll()
        if not (li.s.spindle.enabled and li.s.spindle.speed == config["angle_90"]):
            return False
        
        if li.home_all_axes():
            return True
        
        return False

    def dirty_to_home(self, m: ManipulatorSM) -> bool:
        if not (m.require_manipulator(ManipulatorSM.Empty)):
            return False
        
        li.s.poll()
        if not (li.s.spindle.enabled and li.s.spindle.speed == config["angle_90"]):
            return False
        
        if li.home_all_axes():
            return True
        
        return False

    def clean_to_home(self, m: ManipulatorSM) -> bool:
        if not (m.require_manipulator(ManipulatorSM.Empty)):
            return False
        
        li.s.poll()
        if not (li.s.spindle.enabled and li.s.spindle.speed == config["angle_90"]):
            return False
        
        if li.home_all_axes():
            return True
        
        return False

    def printer_to_dirty(self, m: ManipulatorSM) -> bool:
        if (ds.is_full()):
            return False
        
        [x, y] = ds.coords_first_free()

        if li.ok_for_mdi():
            move = ga.gcode_generic_move(x, y)

            if li.send_mdi_line(move):
                return True
            
        return False
    
    def dirty_to_clean(self, m: ManipulatorSM):
        if (cs.is_empty()):
            return False
        
        [x, y] = cs.get_origin()

        if li.ok_for_mdi():
            move = ga.gcode_generic_move(x, y)

            if li.send_mdi_line(move):
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
    print(ManipulatorSM.Clean in m.configuration)

    print(m.require_manipulator(ManipulatorSM.Clean))

if __name__ == "__main__":
    main()