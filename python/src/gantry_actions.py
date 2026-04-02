from os import getenv
import yaml
import gcode_gen
from config import config

def read_printer_coords(printer_number: int) -> dict:
    if not isinstance(printer_number, int) or printer_number not in config["printer_coords"].keys():
        return {"x": None, "y": None}
    
    return config["printer_coords"].get(printer_number)
    
    
def gcode_generic_move(x: float, y: float, feed_rate=1500) -> list[str]:
    code = [gcode_gen.generate_code({'x': x, 'y': y, 'f': feed_rate}, 1, True)]
    return code

def gcode_move_to_printer(printer_number: int, feed_rate=1500) -> list[str]:
    coords = read_printer_coords(printer_number)
    code = []
    code.append(gcode_gen.generate_code({'x': coords['x'], 'f': feed_rate}, 1, True))
    code.append(gcode_gen.generate_code({'y': coords['y']}, 1, True))
    code.append(gcode_gen.generate_code({}, 1, False))
    return code

def gcode_move_to_home(feed_rate=1500) -> list[str]:
    code = []
    code.append(gcode_gen.generate_code({'x': 0.0, 'f': feed_rate}, 1, True))
    code.append(gcode_gen.generate_code({'y': 0.0}, 1, True))
    code.append(gcode_gen.generate_code({}, 1, False))
    return code

def gcode_grab_plate(z_dist: float, feed_rate=1500) -> list[str]:
    code = []
    code.append(gcode_gen.generate_code({}, 92, True))
    code.append(gcode_gen.generate_code({'s': config['angle_0']}, 3, False))
    code.append(gcode_gen.generate_code({'z': z_dist, 'f': feed_rate}, 1, True))
    # add plate g/mcode commands here
    code.append(gcode_gen.generate_code({'a': config['clamp']}, 1, True))
    code.append(gcode_gen.generate_code({'z': 0.0}, 1, True))
    code.append(gcode_gen.generate_code({'s': config['angle_90']}, 3, False))
    # add up commands here
    code.append(gcode_gen.generate_code({}, 1, False))
    return code

def gcode_release_plate(z_dist: float, feed_rate=1500) -> list[str]:
    code = []
    code.append(gcode_gen.generate_code({'z': 0.0, 'f': feed_rate}, 1, True))
    code.append(gcode_gen.generate_code({'z': z_dist}, 1, True))
    # add down commands here
    code.append(gcode_gen.generate_code({'s': config['angle_15']}, 4, False))
    # add ease plate g/mcode commands here
    code.append(gcode_gen.generate_code({'a': config['unclamp']}, 1, True))
    code.append(gcode_gen.generate_code({'z': 0.0}, 1, True))
    code.append(gcode_gen.generate_code({}, 1, False))
    return code

def gcode_open_door(radius: float, feed_rate=900) -> list[str]:
    code = []
    code.append(gcode_gen.generate_code({'s':config['angle_90']}, 1, False))
    code.append(gcode_gen.generate_code({'x':config['handle_x'], 'y':config['handle_y'], 'f': feed_rate}, 1, True))
    code.append(gcode_gen.generate_code({'z':config['handle_z']}, 1, True))
    code.append(gcode_gen.generate_code({'x':config['door_open_x'], 'y':config['door_open_y'], 'r':config['door_radius']}, 2, True))
    code.append(gcode_gen.generate_code({'z': 0,}, 1, True))
    return code

def gcode_close_door(radius:float, feed_rate=900) -> list[str]:
    code = []
    code.append(gcode_gen.generate_code({'s':config['angle_90']}, 1, False))
    code.append(gcode_gen.generate_code({'x':config['door_open_x'], 'y':config['door_open_y'], 'f': feed_rate}, 1, True))
    code.append(gcode_gen.generate_code({'z':config['handle_z']}, 1, True))
    code.append(gcode_gen.generate_code({'x':config['handle_x'], 'y':config['handle_y'], 'r':config['door_radius']}, 3, True))
    code.append(gcode_gen.generate_code({'z': 0,}, 1, True))
    return code

def main():
    print(read_printer_coords(11))

if __name__ == "__main__":
    main()