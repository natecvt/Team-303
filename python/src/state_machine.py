from statemachine import StateMachine, State, exceptions
from storage_tracker import ds, cs
from json_msg_parser import printer_id
from config import config
class ManipulatorSM(StateMachine):
    # Define states
    Empty = State(initial=True)
    Full = State()
    Clean = State()
    
    grab = Empty.to(Full, on="placeholder")
    release = Full.to(Empty, on="placeholder")
    clean = Empty.to(Clean, on="placeholder") | Clean.to(Empty, on="placeholder")

    def require_manipulator(*allowed_states):
        if manipulator.current_state not in allowed_states:
            allowed = [s.id for s in allowed_states]
            raise RuntimeError(
                f"Manipulator must be {allowed} but is '{manipulator.current_state.id}'"
            )
        
    def placeholder(self):
        print(self.configuration)
        pass
    
    def plate_grab(self) -> bool:
        # if clamp not open
        #   open clamp
        # open door gcode
        # rotate -15° gcode
        # do plate grab moves
        # close door
        pass
    
    def plate_release(self, ds) -> bool:
        dp_loc_idx = [0,0]
        # if clamp open
        # why?
        dp_loc_idx = ds.detect_first_free()
        
        # find dps position
        # do plate release moves
        # move out
        pass

class PositionSM(StateMachine):
    # Define states
    Home = State(initial=True)
    Printer = State()
    DirtyS = State()
    CleanS = State()

    go_printer = Home.to(Printer, cond="placeholder") | CleanS.to(Printer, cond="placeholder")
    go_home = Printer.to(Home, cond="placeholder") | DirtyS.to(Home, cond="placeholder") | CleanS.to(Home, cond="placeholder")
    go_dirty = Printer.to(DirtyS, cond="placeholder")
    go_clean = DirtyS.to(CleanS, cond="placeholder")

    def require_position(self, *allowed_states):
        if self.current_state not in allowed_states:
            allowed = [s.id for s in allowed_states]
            raise RuntimeError(
                f"Position must be {allowed} but is '{position.current_state.id}'"
            )
        
    def placeholder(self):
        print(self.configuration)
        pass

    def home_to_printer(self, m: ManipulatorSM, printer_id: int) -> bool:
        printer_location = [0,0]
        if ds.is_full():
            return False
        if m.require_manipulator(~m.Empty):
            return False
        # if manipulator is not 90 degrees:
        # return false
        if position.require_position(~position.Home):
            return False
        if printer_id == None:
            return False
        printer_location = config["printer_locations"].index(printer_id)
    
manipulator = ManipulatorSM()
position = PositionSM()

def main():
    manipulator.activate_initial_state()

    manipulator.grab()
    try:
        manipulator.clean()
    except exceptions.TransitionNotAllowed:
        print("Wrong transition queued, expected")

    manipulator.release()
    manipulator.clean()
    manipulator.Empty
    home_to_printer(manipulator.empty, printer_id)

if __name__ == "__main__":
    main()