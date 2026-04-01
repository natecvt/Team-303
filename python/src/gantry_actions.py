from os import getenv
import yaml
import gcode_gen
from state_machine import position, manipulator
from config import config

def read_printer_coords(path: str, printer_number: int) -> dict:
    if not isinstance(printer_number, int) or printer_number < 1 or printer_number > 12:
        raise ValueError("Invalid printer number")
    
    with open(path, 'r') as file:
        lines = file.readlines()
        line = lines[printer_number - 1]
        coords = line.strip().split(',')
        
        return {"x": float(coords[0]), "y": float(coords[1])}
    
def gcode_generic_move(x: float, y: float, feed_rate=1500) -> str:
    code = gcode_gen.generate_code({'x': x, 'y': y, 'f': feed_rate}, 1, True)

    return code

def gcode_move_to_printer(printer_number: int, feed_rate=1500) -> str:
    coords = read_printer_coords(f'{getenv("HOME")}/Team-303/ref_files/printer_centers.csv', printer_number)
    code = ""

    code += gcode_gen.generate_code({'x': coords['x'], 'f': feed_rate}, 1, True)
    code += gcode_gen.generate_code({'y': coords['y']}, 1, True)
    code += gcode_gen.generate_code({}, 1, False)
    position.go_printer()
    return code

def gcode_move_to_home(feed_rate=1500) ->str:
    code = ""
    code += gcode_gen.generate_code({'x': 0.0, 'f': feed_rate}, 1, True)
    code += gcode_gen.generate_code({'y': 0.0}, 1, True)
    code += gcode_gen.generate_code({}, 1, False)
    position.go_home()
    return code

def gcode_grab_plate(z_dist: float, feed_rate=1500) -> str:
    code = ""
    code += gcode_gen.generate_code({'x': config['clean_x'], 'f': feed_rate}, 1, True)
    code += gcode_gen.generate_code({'y': config['clean_y']}, 1, True)
    code += gcode_gen.generate_code({}, 1, False)
    return code

def gcode_grab_plate(z_dist: float, feed_rate=1500) -> str:
    code = ""
    code += gcode_gen.generate_code({}, 92, True)
    code += gcode_gen.generate_code({'s': config['angle_0']}, 3, False)
    code += gcode_gen.generate_code({'z': z_dist, 'f': feed_rate}, 1, True)
    # add grab plate g/mcode commands here
    code += gcode_gen.generate_code({'a': config['clamp']}, 1, True)
    code += gcode_gen.generate_code({'z': 0.0}, 1, True)
    code += gcode_gen.generate_code({'s': config['angle_90']}, 3, False)
    # add fold up commands here
    code += gcode_gen.generate_code({}, 1, False)
    manipulator.grab()
    return code

def gcode_release_plate(z_dist: float, feed_rate=1500) -> str:
    code = ""
    code += gcode_gen.generate_code({'z': 0.0, 'f': feed_rate}, 1, True)
    code += gcode_gen.generate_code({'z': z_dist}, 1, True)
    # add fold down commands here
    code += gcode_gen.generate_code({'s': config['angle_15']}, 4, False)
    # add release plate g/mcode commands here
    code += gcode_gen.generate_code({'a': config['unclamp']}, 1, True)
    code += gcode_gen.generate_code({'z': 0.0}, 1, True)
    code += gcode_gen.generate_code({}, 1, False)
    manipulator.release()
    return code

def gcode_open_door(radius: float, feed_rate=900) -> str:
    code = ""
    code = gcode_gen.generate_code({'s':config['angle_90']}, 1, False)
    code = gcode_gen.generate_code({'x':config['handle_x'], 'y':config['handle_y'], 'f': feed_rate}, 1, True)
    code = gcode_gen.generate_code({'z':config['handle_z']}, 1, True)
    code = gcode_gen.generate_code({'x':config['door_open_x'], 'y':config['door_open_y'], 'r':config['door_radius']}, 2, True)
    code = gcode_gen.generate_code({'z': 0,}, 1, True)
    return code

def gcode_close_door(radius:float, feed_rate=900) -> str:
    code = ""
    code = gcode_gen.generate_code({'s':config['angle_90']}, 1, False)
    code = gcode_gen.generate_code({'x':config['door_open_x'], 'y':config['door_open_y'], 'f': feed_rate}, 1, True)
    code = gcode_gen.generate_code({'z':config['handle_z']}, 1, True)
    code = gcode_gen.generate_code({'x':config['handle_x'], 'y':config['handle_y'], 'r':config['door_radius']}, 3, True)
    code = gcode_gen.generate_code({'z': 0,}, 1, True)
    return code

def main():
    path = f'{getenv("HOME")}/Team-303/ref_files/printer_centers.csv'
    printer_num = int(input("Enter printer number: "))
    coords = read_printer_coords(path, printer_num)
    if coords:
        print(f"Printer {printer_num} coordinates: {coords}")
    else:
        print(f"Printer number {printer_num} not found.")

    print(f"Position:    {position.current_state.id}")
    print(f"Manipulator: {manipulator.current_state.id}")

    code = gcode_move_to_printer(printer_num)
    print(f"G-code to move to printer {printer_num} generated.")
    print(code)

    code = gcode_move_to_home()
    print("G-code to move to home position generated.")
    print(code)
    
    code = gcode_release_plate(20.10)
    print("G-code to release plate")
    print(code)

    print(f"Position:    {position.current_state.id}")
    print(f"Manipulator: {manipulator.current_state.id}")

if __name__ == "__main__":
    print("Testing printer coordinate retrieval:")
    main()