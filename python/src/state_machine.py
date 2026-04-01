from statemachine import StateMachine, State, exceptions

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

    def clean_grab():
        position.require_position(position.CleanS)
        manipulator.require_manipulator(manipulator.Empty)
        if CleanDispenser.is_empty:
            raise RuntimeError("Clean dispenser is empty")
        manipulator_clamp = False
        manipulator_degree = 0
        code = gcode_grab_clean()
        manipulator_degree = 90


    def clean_release():
        position.require_position(position.Printer)
        manipulator.require_manipulator(manipulator.Clean)
        if manipulator_degree == 90:
            code = gcode_open_door()
        manipulator_degree = -15
        code = gcode_move_printer()
        manipulator_clamp = False
        code = gcode_out_printer()
        manipulator_degree = 90
        code = gcode_close_door()

        
class PositionSM(StateMachine):
    # Define states
    Home = State(initial=True)
    Printer = State()
    DirtyS = State()
    CleanS = State()

    go_printer = Home.to(Printer, on="placeholder") | CleanS.to(Printer, on="placeholder")
    go_home = Printer.to(Home, on="placeholder") | DirtyS.to(Home, on="placeholder")
    go_dirty = Printer.to(DirtyS, on="placeholder")
    go_clean = DirtyS.to(CleanS, on="placeholder")

    def require_position(self, *allowed_states):
        if self.current_state not in allowed_states:
            allowed = [s.id for s in allowed_states]
            raise RuntimeError(
                f"Position must be {allowed} but is '{position.current_state.id}'"
            )
        
    def placeholder(self):
        print(self.configuration)
        pass

manipulator = ManipulatorSM()
position = PositionSM()

def dirty_home():
    if manipulator.Empty and manipulator_degree == 90:
        # code = gcode_move_to_home()
    else:
        raise RuntimeError("error fix it bub")

def dirty_clean():
    manipulator.require_manipulator(manipulator.Empty)
    # code = gcode_move_to_clean()

    

def main():
    manipulator.activate_initial_state()

    manipulator.grab()
    try:
        manipulator.clean()
    except exceptions.TransitionNotAllowed:
        print("Wrong transition queued, expected")

    manipulator.release()
    manipulator.clean()

if __name__ == "__main__":
    main()