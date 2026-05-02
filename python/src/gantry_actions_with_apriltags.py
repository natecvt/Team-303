import gcode_gen as gg
from config import config
import apriltag_python.apriltag_locator as al


def read_printer_coords(printer_number: int) -> dict:
    if not isinstance(printer_number, int) or printer_number not in config["printer_coords"].keys():
        return {"x": None, "y": None}
    
    return config["printer_coords"].get(printer_number)

# does this only for the x and y, z should always have global zero
def set_zero(z_is_zero: bool, feed_rate=config["feed_rate"]) -> list[str]:
    code = []

    if not z_is_zero:
        code.append(gg.generate_code({'z': 0.0, 'f': feed_rate}, 1))

    code.append(gg.generate_code({'x': 0.0, 'y': 0.0}, 92))

    return code

def reset_zero() -> list[str]:
    code = []

    code.append(gg.generate_code({}, 921))
    return code
    
def gcode_generic_move(x: float, y: float, z_is_zero: bool, feed_rate=config["feed_rate"]) -> list[str]:
    code = []
    
    code.extend(reset_zero())
    code.append(gg.generate_code({}, 90))

    if not z_is_zero:
        code.append(gg.generate_code({'z': 0.0, 'f': feed_rate}, 1))

    code.append(gg.generate_code({'x': x, 'y': y, 'f': feed_rate}, 1))

    return code

# global move, sets zero to end location 
def gcode_move_to_printer(coords: dict, z_is_zero: bool, feed_rate=config["feed_rate"]) -> list[str]:

    code = []

    code.extend(reset_zero())
    code.append(gg.generate_code({}, 90))

    # set z zero before doing global moves
    if not z_is_zero:
        code.append(gg.generate_code({'z': 0.0, 'f': feed_rate}, 1))

    code.append(gg.generate_code({'s': config["manipulator_angle_90"]}, 3, False))
    code.extend(gcode_generic_move(coords['x'], coords['y'], True, feed_rate))
    
    code.extend(set_zero(True, feed_rate))

    return code

def gcode_move_to_home(z_is_zero: bool, feed_rate=config["feed_rate"]) -> list[str]:
    code = []

    code.append(gg.generate_code({}, 90))

    if not z_is_zero:
        code.append(gg.generate_code({'z': 0.0, 'f': feed_rate}, 1))

    code.append(gg.generate_code({'x': 0.0, 'y': 0.0, 'f': feed_rate}, 1))

    return code

def gcode_move_to_cs(z_is_zero: bool, feed_rate=config["feed_rate"]) -> list[str]:
    code = []

    code.extend(reset_zero())
    code.append(gg.generate_code({}, 90))

    if not z_is_zero:
        code.append(gg.generate_code({'z': 0.0, 'f': feed_rate}, 1))

    code.extend(gcode_generic_move(config["cs_coords"]['x'], config["cs_coords"]['y'], True, feed_rate))
    code.extend(set_zero(True, feed_rate))

    return code

def gcode_move_to_ds(row: int, col: int, z_is_zero: bool, feed_rate=config["feed_rate"]) -> list[str]:
    code = []

    code.extend(reset_zero())
    code.append(gg.generate_code({}, 90))

    if not z_is_zero:
        code.append(gg.generate_code({'z': 0.0, 'f': feed_rate}, 1))

    code.extend(gcode_generic_move(config["ds_coords"]['x'], config["ds_coords"]['y'], True, feed_rate))
    
    code.extend(set_zero(True, feed_rate))

    [x, y] = [config["ds_dx"] * col, config["ds_dy"] * row]
    code.append(gg.generate_code({'x': x, 'y': y, 'f': feed_rate}, 1))

    return code

def gcode_grab_plate_printer(z_is_zero: bool, z_dist=config["printer_plate_z"],  feed_rate=config["feed_rate"]) -> list[str]:
    code = []

    if not z_is_zero: 
        code.append(gg.generate_code({'z': 0.0, 'f': feed_rate}, 1))
    
    code.append(gg.generate_code({}, 91))
    code.append(gg.generate_code({'x': config["door_to_plate_delta"]['x'], 'y': config["door_to_plate_delta"]['y'], 'f': feed_rate}, 1))
    code.append(gg.generate_code({config["gripper_axis"]: config["gripper_up"], 'f': feed_rate}, 1))

    code.append(gg.generate_code({'s': config["manipulator_angle_n12"]}, 3, False))
    code.append(gg.generate_code({'z': z_dist, 'f': feed_rate}, 1))

    code.append(gg.generate_code({config["gripper_axis"]: config["gripper_down"],  'f': feed_rate / 10.0}, 1))

    code.append(gg.generate_code({}, 90))

    code.append(gg.generate_code({'s': config["manipulator_angle_0"]}, 3, False))
    code.append(gg.generate_code({'z': 0.0, 'f': feed_rate}, 1))
    code.append(gg.generate_code({'s': config["manipulator_angle_90"]}, 3, False))
    
    return code

def gcode_release_plate_printer(z_is_zero: bool, z_dist=config["printer_plate_z"], feed_rate=config["feed_rate"]) -> list[str]:
    code = []

    if not z_is_zero: 
        code.append(gg.generate_code({'z': 0.0, 'f': feed_rate}, 1))
    
    code.append(gg.generate_code({}, 90))
    code.append(gg.generate_code({'x': config["door_to_plate_delta"]['x'], 'y': config["door_to_plate_delta"]['y'], 'f': feed_rate}, 1))
    code.append(gg.generate_code({'s': config["manipulator_angle_0"]}, 3, False))
    code.append(gg.generate_code({'z': 3.0 * z_dist / 4.0, 'f': feed_rate}, 1))
    code.append(gg.generate_code({'s': config["manipulator_angle_n12"]}, 3, False))
    code.append(gg.generate_code({'z': z_dist, 'f': feed_rate}, 1))
    
    code.append(gg.generate_code({}, 91))
    code.append(gg.generate_code({config["gripper_axis"]: config["gripper_up"]}, 1))
    code.append(gg.generate_code({}, 90))

    code.append(gg.generate_code({'z': 0.0}, 1))
    code.append(gg.generate_code({'s': config["manipulator_angle_90"]}, 3, False))

    code.append(gg.generate_code({}, 91))
    code.append(gg.generate_code({config["gripper_axis"]: config["gripper_down"]}, 1))
    code.append(gg.generate_code({}, 90))

    code.extend(gcode_move_to_home(True, feed_rate))

    return code    

def gcode_open_door(z_is_zero: bool, feed_rate=config["feed_rate"]) -> list[str]:
    code = []

    code.extend(gcode_move_to_home(z_is_zero, feed_rate))

    code.append(gg.generate_code({'z': config["door_z"], 'f': feed_rate}, 1))
    code.append(gg.generate_code({}, 91))
    code.append(gg.generate_code({'y': config["door_into_y"], 'f': feed_rate}, 1))
    code.append(gg.generate_code({}, 18))
    code.append(gg.generate_code({'x': config["door_open_delta"]["x"], 
                                  'z': config["door_open_delta"]["z"],
                                  'r': config["door_radius"],
                                  'f': feed_rate}, 3))
    code.append(gg.generate_code({'x': config["door_close_x_offset"], 'f': feed_rate}, 1))
    code.append(gg.generate_code({'y': -config["door_into_y"], 'f': feed_rate}, 1))
    code.append(gg.generate_code({}, 90))
    code.append(gg.generate_code({'z': 0.0, 'f': feed_rate}, 1))
    code.extend(gcode_move_to_home(True, feed_rate))
    
    return code

def gcode_close_door(z_is_zero: bool, is_second: bool, feed_rate=config["feed_rate"]) -> list[str]:
    code = []

    if not z_is_zero: 
        code.append(gg.generate_code({'z': 0.0, 'f': feed_rate}, 1))

    code.append(gg.generate_code({'x': config["door_open_delta"]['x'] + config["door_close_x_offset"], 'y': 0.0, 'f': feed_rate}, 1))
    code.append(gg.generate_code({'z': config["door_z"] + config["door_open_delta"]["z"], 'f': feed_rate}, 1))

    code.append(gg.generate_code({}, 91))

    code.append(gg.generate_code({'y': config["door_into_y"], 'f': feed_rate}, 1))
    code.append(gg.generate_code({}, 18))
    code.append(gg.generate_code({'x': config["door_close_delta"]["x"],
                                  'z': config["door_close_delta"]["z"],
                                  'r': config["door_radius"],
                                  'f': feed_rate}, 2))
    code.append(gg.generate_code({'y': -config["door_into_y"], 'f': feed_rate}, 1))

    code.append(gg.generate_code({}, 90))
    
    code.append(gg.generate_code({'x': 0.0, 'z': 0.0, 'f': feed_rate}, 1))

    if (is_second):
        code.extend(reset_zero())
    
    return code

def gcode_release_plate_ds(z_is_zero: bool, z_dist=config["ds_release_z"], y_dist=config["ds_release_dy"], feed_rate=config["feed_rate"]) -> list[str]:
    code = []

    if not z_is_zero: 
        code.append(gg.generate_code({'z': 0.0, 'f': feed_rate}, 1))

    code.append(gg.generate_code({'s': config["manipulator_angle_0"]}, 3, False))
    code.append(gg.generate_code({'z': z_dist, 'f': feed_rate}, 1))
    code.append(gg.generate_code({}, 91))
    code.append(gg.generate_code({'s': config["manipulator_angle_n12"]}, 3, False))
    code.append(gg.generate_code({'y': y_dist, 'f': feed_rate}, 1))
    code.append(gg.generate_code({config["gripper_axis"]: config["gripper_up"], 'f': feed_rate}, 1))
    code.append(gg.generate_code({}, 90))
    code.append(gg.generate_code({'z': 0.0, 'f': feed_rate}, 1))
    code.append(gg.generate_code({'s': config["manipulator_angle_90"]}, 3, False))

    code.append(gg.generate_code({}, 91))
    code.append(gg.generate_code({config["gripper_axis"]: config["gripper_down"], 'f': feed_rate}, 1))
    code.append(gg.generate_code({}, 90))

    code.extend(reset_zero())

    return code

def gcode_grab_plate_cs(z_is_zero: bool, z_dist=config["cs_grab_z"], feed_rate=config["feed_rate"]) -> list[str]:
    code = []

    if not z_is_zero: 
        code.append(gg.generate_code({'z': 0.0, 'f': feed_rate}, 1))

    code.append(gg.generate_code({}, 91))
    code.append(gg.generate_code({config["gripper_axis"]: config["gripper_up"], config["clean_plate_axis"]: config["clean_plate_distance"], 'f': feed_rate}, 1))
    code.append(gg.generate_code({}, 90))
    code.append(gg.generate_code({'s': config["manipulator_angle_n12"]}, 3, False))
    code.append(gg.generate_code({'z': z_dist, 'f': feed_rate}, 1))
    code.append(gg.generate_code({'s': config["manipulator_angle_0"]}, 3, False))
    code.append(gg.generate_code({}, 91))
    code.append(gg.generate_code({"y": config["cs_grab_y"], config["gripper_axis"]: config["gripper_down"]}, 1))
    code.append(gg.generate_code({}, 90))
    code.append(gg.generate_code({'z': 0.0, 'f': feed_rate}, 1))
    code.append(gg.generate_code({'s': config["manipulator_angle_90"]}, 3, False))

    code.extend(reset_zero())

    return code

def main():
    print(set_zero(False))
    print(reset_zero())
    print()
    print(gcode_move_to_printer(read_printer_coords(1), False))
    print(gcode_open_door(False))
    print(gcode_close_door(True, True))
    print(gcode_grab_plate_printer(True))
    print(gcode_release_plate_printer(True))
    print()
    print(gcode_move_to_cs(True))
    print(gcode_grab_plate_cs(False))
    print()
    print(gcode_move_to_ds(2, 3, False))
    print(gcode_release_plate_ds(False))


if __name__ == "__main__":
    main()