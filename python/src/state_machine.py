from statemachine import StateMachine, State, exceptions, graph
from config import config
import linuxcnc_interface as li
import gantry_actions as ga
from storage_tracker import cs, ds

class ManipulatorSM(StateMachine):
    # Define states
    Empty = State(initial=True)
    Full = State()
    
    Empty.to(Full, cond="etf")
    Full.to(Empty, cond="fte")

    grab = (Empty.to.itself(internal=True, on="plate_grab"))
    release = (Full.to.itself(internal=True, on="plate_release"))

    def require_manipulator(self, allowed_states) -> bool:
        if (allowed_states in self.configuration):
            return True
        
        return False
    
    etf = False
    fte = False
        
    def placeholder(self):
        print(self.configuration)
        pass
    
    def plate_grab(self, p) -> bool:
        at_clean = p.require_position(p.CleanS)
        at_printer = p.require_position(p.Printer)

        if not (at_clean or at_printer):
            self.etf = False
            return self.etf
        
        if (at_clean and at_printer):
            print("Invalid state")
            self.etf = False
            return self.etf

        if li.ok_for_mdi():
            if at_clean:
                move = ga.gcode_grab_plate_cs(True)
                cs.remove_one()
            if at_printer:
                move = ga.gcode_open_door(True)
                move.extend(ga.gcode_grab_plate_printer(True))
                move.extend(ga.gcode_close_door(True, False))
                
            if (li.multiline_mdi_loop(move)):
                self.etf = True
                self.fte = False
                return self.etf
            
        self.etf = False
        return self.etf
    
    def plate_release(self, p) -> bool:
        at_dirty = p.require_position(p.DirtyS)
        at_printer = p.require_position(p.Printer)

        if not (at_dirty or at_printer):
            self.fte = False
            return self.fte
        
        if (at_dirty and at_printer):
            print("Invalid state")
            self.fte = False
            return self.fte

        if li.ok_for_mdi():

            if at_dirty:
                move = ga.gcode_release_plate_ds(True)
            if at_printer:
                move = ga.gcode_open_door(True)
                move.extend(ga.gcode_release_plate_printer(True))
                move.extend(ga.gcode_close_door(True, False))
                
            if (li.multiline_mdi_loop(move)):
                self.fte = True
                self.etf = False
                return self.fte
        
        self.fte = False
        return self.fte

        
class PositionSM(StateMachine):
    # Define states
    Home = State(initial=True)
    Error = State()
    Printer = State()
    DirtyS = State()
    CleanS = State()

    Home.to(Printer, cond="htp")
    CleanS.to(Printer, cond="ctp")
    DirtyS.to(CleanS, cond="dtc")
    DirtyS.to(Home, cond="dth")
    Printer.to(Home, cond="pth")
    CleanS.to(Home, cond="cth")
    Printer.to(DirtyS, cond="ptd")

    # Error
    Home.to(Error, cond="err", on="")
    Printer.to(Error, cond="err")
    DirtyS.to(Error, cond="err")
    CleanS.to(Error, cond="err")
    Error.to(Home, cond="eth")

    home_printer = Home.to.itself(internal=True, on="home_to_printer") 
    clean_printer = CleanS.to.itself(internal=True, on="clean_to_printer")
    clean_home = CleanS.to.itself(internal=True, on="clean_to_home")
    printer_home = Printer.to.itself(internal=True, on="printer_to_home")
    dirty_home = DirtyS.to.itself(internal=True, on="dirty_to_home")
    dirty_clean = DirtyS.to.itself(internal=True, on="dirty_to_clean")
    printer_dirty = Printer.to.itself(internal=True, on="printer_to_dirty")
                
    htp = False
    ctp = False
    pth = False
    cth = False
    dth = False
    ptd = False
    dtc = False
    err = False
    eth = False

    def require_position(self, allowed_states) -> bool:
        if (self.configuration.__contains__(allowed_states)):
            return True
        
        return False
        
    def placeholder(self):
        print(self.configuration)
        pass

    def error(self):
        if li.home_all_axes():
            err = False
            eth = True

    def home_to_printer(self, m: ManipulatorSM, number: int):
        if not (m.require_manipulator(ManipulatorSM.Empty)):
            self.htp = False
            return self.htp

        if ds.is_full():
            print("DS Full, can't do anything")
            self.htp = False
            return self.htp

        if not li.set_state_active():
            return False
        
        if not (li.check_z_is_zero()):
            self.htp = False
            return self.htp
        
        if li.ok_for_mdi():
            coords: dict = ga.read_printer_coords(number)

            if coords['x'] == None:
                self.htp = False
                return self.htp
            
            move = ga.gcode_move_to_printer(coords, True)

            if li.multiline_mdi_loop(move):
                self.htp = True

                self.pth = False
                self.ctp = False
                self.cth = False
                self.dth = False
                self.ptd = False
                self.dtc = False
                self.eth = False

                return self.htp

        self.htp = False
        return self.htp

    def clean_to_printer(self, m: ManipulatorSM, number: int) -> bool:
        if not (m.require_manipulator(ManipulatorSM.Full)):
            self.ctp = False
            return self.ctp
        
        if not (li.check_spindle(ga.MAN_ANGLE_P90)):
            self.ctp = False
            return self.ctp
        
        if not (li.check_z_is_zero()):
            self.ctp = False
            return self.ctp
        
        if li.ok_for_mdi():
            coords: dict = ga.read_printer_coords(number)

            if coords['x'] == None:
                self.ctp = False
                return self.ctp
            
            move = ga.gcode_move_to_printer(coords, True)

            if li.multiline_mdi_loop(move):
                self.ctp = True

                self.pth = False
                self.htp = False
                self.cth = False
                self.dth = False
                self.ptd = False
                self.dtc = False
                self.eth = False

                return self.ctp

        self.ctp = False
        return self.ctp

    def printer_to_home(self, m: ManipulatorSM) -> bool:
        if not (m.require_manipulator(ManipulatorSM.Empty)):
            self.pth = False
            return self.pth
        
        if not (li.check_spindle(ga.MAN_ANGLE_P90)):
            self.pth = False
            return self.pth
        
        if not (li.check_z_is_zero()):
            self.pth = False
            return self.pth
        
        li.c.mode(li.linuxcnc.MODE_MANUAL)
        li.c.wait_complete()

        if li.home_all_axes():
            self.pth = True
            li.set_state_resting()

            if (self.pth):
                self.htp = False
                self.ctp = False
                self.cth = False
                self.dth = False
                self.ptd = False
                self.dtc = False
                self.eth = False
            
            return self.pth
        
        self.pth = False
        return self.pth

    def dirty_to_home(self, m: ManipulatorSM) -> bool:
        if not (m.require_manipulator(ManipulatorSM.Empty)):
            self.dth = False
            return self.dth
        
        if not (li.check_spindle(ga.MAN_ANGLE_P90)):
            self.dth = False
            return self.dth
        
        if not (li.check_z_is_zero()):
            self.dth = False
            return self.dth
        
        li.c.mode(li.linuxcnc.MODE_MANUAL)
        li.c.wait_complete()

        if li.home_all_axes():
            self.dth = True
            li.set_state_resting()

            if (self.dth):
                self.htp = False
                self.ctp = False
                self.cth = False
                self.pth = False
                self.ptd = False
                self.dtc = False
                self.eth = False

            return self.dth
        
        self.dth = False
        return self.dth

    def clean_to_home(self, m: ManipulatorSM) -> bool:
        if not (m.require_manipulator(ManipulatorSM.Empty)):
            self.cth = False
            return self.cth
        
        if not (li.check_spindle(ga.MAN_ANGLE_P90)):
            self.cth = False
            return self.cth
        
        if not (li.check_z_is_zero()):
            self.cth = False
            return self.cth
        
        li.c.mode(li.linuxcnc.MODE_MANUAL)
        li.c.wait_complete()

        if li.home_all_axes():
            self.cth = True
            li.set_state_resting()

            if (self.cth):
                self.htp = False
                self.ctp = False
                self.dth = False
                self.pth = False
                self.ptd = False
                self.dtc = False
                self.eth = False

            return self.cth
        
        self.cth = False
        return self.cth

    def printer_to_dirty(self, m: ManipulatorSM) -> bool:
        if (ds.is_full()):
            self.ptd = False
            return self.ptd
        
        [r, c] = ds.detect_first_free()

        if not (m.require_manipulator(ManipulatorSM.Full)):
            self.ptd = False
            return self.ptd
        
        if not (li.check_spindle(ga.MAN_ANGLE_P90)):
            self.ptd = False
            return self.ptd
        
        if not (li.check_z_is_zero()):
            self.ptd = False
            return self.ptd

        if li.ok_for_mdi():
            move = ga.gcode_move_to_ds(r, c, True)

            if li.multiline_mdi_loop(move):
                ds.add_one(r, c)
                self.ptd = True

                self.pth = False
                self.htp = False
                self.cth = False
                self.dth = False
                self.ctp = False
                self.dtc = False
                self.eth = False

                return self.ptd
            
        self.ptd = False
        return self.ptd
    
    def dirty_to_clean(self, m: ManipulatorSM):
        if (cs.is_empty()):
            self.dtc = False
            return self.dtc
        
        if not (m.require_manipulator(ManipulatorSM.Empty)):
            self.dtc = False
            return self.dtc
        
        if not (li.check_spindle(ga.MAN_ANGLE_P90)):
            self.dtc = False
            return self.dtc
        
        if not (li.check_z_is_zero()):
            self.dtc = False
            return self.dtc
        
        if li.ok_for_mdi():
            move = ga.gcode_move_to_cs(True)

            if li.multiline_mdi_loop(move):
                self.dtc = True

                self.pth = False
                self.htp = False
                self.cth = False
                self.dth = False
                self.ptd = False
                self.ctp = False
                self.eth = False

                return self.dtc
            
        self.dtc = False
        return self.dtc


m = ManipulatorSM()
p = PositionSM()

ERROR_MASK = 0b11110111

def check_transition(state, is_man: bool) -> int:
    if state.is_active:
        return 0
    
    return 0b00010000 + (0b00100000 << is_man)

def main():

    p._graph().write_png("home/natec/Team-303/docs/posgraph.png")

    pass

    if (not li.open_linuxcnc()):
        print("Linuxcnc failed to initialize properly")
        exit(1)
    
    if (li.home_all_axes()):
        li.send_mdi_line("G92.1")

    err_flag = 0
    num = 2

    p.activate_initial_state()
    m.activate_initial_state()

    p.send("home_printer", m=m, number=num)
    err_flag |= check_transition(p.Printer, False)
    if (err_flag & (1 << 4)): print(bin(err_flag))

    m.send("grab", p=p)
    err_flag |= check_transition(m.Full, True)
    if (err_flag & (1 << 4)): print(bin(err_flag))

    print("DS Storage: " + str(ds.get_storage()))

    p.send("printer_dirty", m=m)
    err_flag |= check_transition(p.DirtyS, False)
    if (err_flag & (1 << 4)): print(err_flag)

    m.send("release", p=p)
    err_flag |= check_transition(m.Empty, True)
    if (err_flag & (1 << 4)): print(err_flag)

    print("DS Storage: " + str(ds.get_storage()))

    p.send("dirty_clean", m=m)
    err_flag |= check_transition(p.CleanS, False)
    if (err_flag & (1 << 4)): print(err_flag)

    print("CS Storage: " + str(cs.get_amount()))

    m.send("grab", p=p)
    err_flag |= check_transition(m.Full, True)
    if (err_flag & (1 << 4)): print(err_flag)

    print("CS Storage: " + str(cs.get_amount()))

    p.send("clean_printer", m=m, number=num)
    err_flag |= check_transition(p.Printer, False)
    if (err_flag & (1 << 4)): print(err_flag)

    m.send("release", p=p)
    err_flag |= check_transition(m.Empty, True)
    if (err_flag & (1 << 4)): print(err_flag)

    p.send("printer_home", m=m, number=num)
    err_flag |= check_transition(p.Printer, False)
    if (err_flag & (1 << 4)): print(bin(err_flag))
    

if __name__ == "__main__":
    main()