import gcode_gen as gg
from config import config

GRIP_AXIS: str = config["gripper_axis"]
GRIP_UP: float = config["gripper_up"]
GRIP_DOWN: float = config["gripper_down"]

MAN_ANGLE_P00 = config["manipulator_angle_0"]
MAN_ANGLE_P90 = config["manipulator_angle_90"]
MAN_ANGLE_N12 = config["manipulator_angle_n12"]

CS_AXIS: str = config["clean_plate_axis"]
CS_DIST: float = config["clean_plate_distance"]
CS_COORDS: dict = config["cs_coords"]
CS_GRAB_Z: float = config["cs_grab_z"]

DS_COORDS: dict = config['ds_coords']
DS_DX: float = config['ds_dx']
DS_DY: float = config['ds_dy']
DS_RELEASE_Z: float = config['ds_release_z']
DS_RELEASE_DY: float = config['ds_release_dy']

DOOR_Z: float = config["door_z"]
DOOR_Y_ENG: float = config["door_into_y"]
DOOR_CLOSE_X_OFFSET: float = config["door_close_x_offset"]
DOOR_RADIUS: float = config["door_radius"]
DOOR_OPEN_DEL: dict = config["door_open_delta"]
DOOR_CLOSE_DEL: dict = config["door_close_delta"]

# should be the point under the door where a y-move would engage the peg
PRINTERS = config["printer_coords"]
# distance from printer zero to point where plate grabbing is possible
# note this is much different since manipulator will be angled differently
DOOR_PLATE_DEL: dict = config["door_to_plate_delta"]
PRINTER_GRAB_Z: float = config["printer_plate_z"]


def read_printer_coords(printer_number: int) -> dict:
    if not isinstance(printer_number, int) or printer_number not in PRINTERS.keys():
        return {"x": None, "y": None}
    
    return PRINTERS.get(printer_number)

# does this only for the x and y, z should always have global zero
def set_zero(z_is_zero: bool, feed_rate=1500) -> list[str]:
    code = []

    if not z_is_zero:
        code.append(gg.generate_code({'z': 0.0, 'f': feed_rate}, 1))

    code.append(gg.generate_code({'x': 0.0, 'y': 0.0}, 92))

    return code

def reset_zero() -> list[str]:
    code = []

    code.append(gg.generate_code({}, 921))
    return code
    
def gcode_generic_move(x: float, y: float, z_is_zero: bool, feed_rate=1500) -> list[str]:
    code = []
    
    code.extend(reset_zero())
    code.append(gg.generate_code({}, 90))

    if not z_is_zero:
        code.append(gg.generate_code({'z': 0.0, 'f': feed_rate}, 1))

    code.append(gg.generate_code({'x': x, 'y': y, 'f': feed_rate}, 1))

    return code

# global move, sets zero to end location 
def gcode_move_to_printer(printer_number: int, z_is_zero: bool, feed_rate=1500) -> list[str]:
    coords = read_printer_coords(printer_number)
    code = []

    code.extend(reset_zero())
    code.append(gg.generate_code({}, 90))

    # set z zero before doing global moves
    if not z_is_zero:
        code.append(gg.generate_code({'z': 0.0, 'f': feed_rate}, 1))

    code.append(gg.generate_code({'s': MAN_ANGLE_P90}, 3, False))
    code.extend(gcode_generic_move(coords['x'], coords['y'], True, feed_rate))
    
    code.extend(set_zero(True, feed_rate))

    return code

def gcode_move_to_home(z_is_zero: bool, feed_rate=1500) -> list[str]:
    code = []

    code.append(gg.generate_code({}, 90))

    if not z_is_zero:
        code.append(gg.generate_code({'z': 0.0, 'f': feed_rate}, 1))

    code.append(gg.generate_code({'x': 0.0, 'y': 0.0, 'f': feed_rate}, 1))

    # G92 would be redundant here
    
    return code

def gcode_move_to_cs(z_is_zero: bool, feed_rate=1500) -> list[str]:
    code = []

    code.extend(reset_zero())
    code.append(gg.generate_code({}, 90))

    if not z_is_zero:
        code.append(gg.generate_code({'z': 0.0, 'f': feed_rate}, 1))

    code.extend(gcode_generic_move(CS_COORDS['x'], CS_COORDS['y'], True, feed_rate))
    code.extend(set_zero(True, feed_rate))

    return code

def gcode_move_to_ds(row: int, col: int, z_is_zero: bool, feed_rate=1500) -> list[str]:
    code = []

    code.extend(reset_zero())
    code.append(gg.generate_code({}, 90))

    if not z_is_zero:
        code.append(gg.generate_code({'z': 0.0, 'f': feed_rate}, 1))

    code.extend(gcode_generic_move(DS_COORDS['x'], DS_COORDS['y'], True, feed_rate))
    
    # set the zero to the top left slot
    code.extend(set_zero(True, feed_rate))

    # DY should be negative, since zero is set to top left corner slot
    [x, y] = [DS_DX * col, DS_DY * row]
    code.append(gg.generate_code({'x': x, 'y': y, 'f': feed_rate}, 1))

    return code

def gcode_grab_plate_printer(z_is_zero: bool, z_dist=PRINTER_GRAB_Z,  feed_rate=750) -> list[str]:
    code = []

    # make sure z is zero before moving servo
    if not z_is_zero: 
        code.append(gg.generate_code({'z': 0.0, 'f': feed_rate}, 1))
    
    code.append(gg.generate_code({}, 91))
    code.append(gg.generate_code({'x': DOOR_PLATE_DEL['x'], 'y': DOOR_PLATE_DEL['y'], 'f': feed_rate}, 1))
    code.append(gg.generate_code({GRIP_AXIS: GRIP_UP, 'f': feed_rate}, 1))

    code.append(gg.generate_code({'s': MAN_ANGLE_N12}, 3, False))
    code.append(gg.generate_code({'z': z_dist, 'f': feed_rate}, 1))

    code.append(gg.generate_code({GRIP_AXIS: GRIP_DOWN,  'f': feed_rate / 10.0}, 1))

    code.append(gg.generate_code({}, 90))

    code.append(gg.generate_code({'s': MAN_ANGLE_P00}, 3, False))
    code.append(gg.generate_code({'z': 0.0, 'f': feed_rate}, 1))
    code.append(gg.generate_code({'s': MAN_ANGLE_P90}, 3, False))
    
    return code

def gcode_release_plate_printer(z_is_zero: bool, z_dist=PRINTER_GRAB_Z, feed_rate=750) -> list[str]:
    code = []

    # make sure z is zero before moving servo
    if not z_is_zero: 
        code.append(gg.generate_code({'z': 0.0, 'f': feed_rate}, 1))
    
    code.append(gg.generate_code({'x': DOOR_PLATE_DEL['x'], 'y': DOOR_PLATE_DEL['y'], 'f': feed_rate}, 1))
    code.append(gg.generate_code({'s': MAN_ANGLE_P00}, 3, False))
    code.append(gg.generate_code({'z': 3.0 * z_dist / 4.0, 'f': feed_rate}, 1))
    code.append(gg.generate_code({'s': MAN_ANGLE_N12}, 3, False))
    code.append(gg.generate_code({'z': z_dist, 'f': feed_rate}, 1))
    
    code.append(gg.generate_code({}, 91))
    code.append(gg.generate_code({GRIP_AXIS: GRIP_UP}, 1))
    code.append(gg.generate_code({}, 90))

    code.append(gg.generate_code({'z': 0.0}, 1))
    code.append(gg.generate_code({'s': MAN_ANGLE_P90}, 3, False))

    code.append(gg.generate_code({}, 91))
    code.append(gg.generate_code({GRIP_AXIS: GRIP_DOWN}, 1))
    code.append(gg.generate_code({}, 90))

    # return to home
    code.extend(gcode_move_to_home(True, feed_rate))

    return code    

def gcode_open_door(z_is_zero: bool, feed_rate=900) -> list[str]:
    code = []

    #G92 has already set zero to right location
    #M03 has already set servo to right angle
    #G90 should be active on entry

    # send to currently set zero, if not already there
    code.extend(gcode_move_to_home(z_is_zero, feed_rate))

    # move peg under handle
    code.append(gg.generate_code({'z': DOOR_Z, 'f': feed_rate}, 1))
    code.append(gg.generate_code({}, 91))
    # move up to engage peg
    code.append(gg.generate_code({'y': DOOR_Y_ENG, 'f': feed_rate}, 1))
    # set xz planar circlular interp
    code.append(gg.generate_code({}, 18))
    # radial move
    code.append(gg.generate_code({'x': DOOR_OPEN_DEL["x"], 
                                  'z': DOOR_OPEN_DEL["z"],
                                  'r': DOOR_RADIUS,
                                  'f': feed_rate}, 3))
    # lower to disengage
    code.append(gg.generate_code({'x': DOOR_CLOSE_X_OFFSET, 'f': feed_rate}, 1))
    code.append(gg.generate_code({'y': -DOOR_Y_ENG, 'f': feed_rate}, 1))
    code.append(gg.generate_code({}, 90))
    # move back
    code.append(gg.generate_code({'z': 0.0, 'f': feed_rate}, 1))
    code.extend(gcode_move_to_home(True, feed_rate))
    
    return code

def gcode_close_door(z_is_zero: bool, is_second: bool, feed_rate=900) -> list[str]:
    code = []

    #G92 has already set zero to right location
    #M03 has already set servo to right angle
    #G90 should be active on entry

    # make sure z is zero before moving servo
    if not z_is_zero: 
        code.append(gg.generate_code({'z': 0.0, 'f': feed_rate}, 1))

    # start z below handle
    code.append(gg.generate_code({'x': DOOR_OPEN_DEL['x'] + DOOR_CLOSE_X_OFFSET, 'y': 0.0, 'f': feed_rate}, 1))
    code.append(gg.generate_code({'z': DOOR_Z + DOOR_OPEN_DEL["z"], 'f': feed_rate}, 1))

    code.append(gg.generate_code({}, 91))

    code.append(gg.generate_code({'y': DOOR_Y_ENG, 'f': feed_rate}, 1))
    code.append(gg.generate_code({}, 18))
    code.append(gg.generate_code({'x': DOOR_CLOSE_DEL["x"],
                                  'z': DOOR_CLOSE_DEL["z"],
                                  'r': DOOR_RADIUS,
                                  'f': feed_rate}, 2))
    code.append(gg.generate_code({'y': -DOOR_Y_ENG, 'f': feed_rate}, 1))

    code.append(gg.generate_code({}, 90))
    
    code.append(gg.generate_code({'z': 0.0, 'f': feed_rate}, 1))

    # final coords (G92 relative)
    # x = 0.0
    # y = 0.0
    # z = 0.0

    # two printer door opens and closes per cycle
    if (is_second):
        # finished printer actions for cycle
        code.extend(reset_zero())
    
    return code

def gcode_release_plate_ds(z_is_zero: bool, z_dist=DS_RELEASE_Z, y_dist=DS_RELEASE_DY, feed_rate=750) -> list[str]:
    code = []

    # make sure z is zero before moving servo
    if not z_is_zero: 
        code.append(gg.generate_code({'z': 0.0, 'f': feed_rate}, 1))

    code.append(gg.generate_code({'s': MAN_ANGLE_P00}, 3, False))
    code.append(gg.generate_code({'z': z_dist, 'f': feed_rate}, 1))
    code.append(gg.generate_code({}, 91))
    code.append(gg.generate_code({'s': MAN_ANGLE_N12}, 3, False))
    code.append(gg.generate_code({'y': y_dist, 'f': feed_rate}, 1))
    code.append(gg.generate_code({GRIP_AXIS: GRIP_UP, 'f': feed_rate}, 1))
    code.append(gg.generate_code({}, 90))
    code.append(gg.generate_code({'z': 0.0, 'f': feed_rate}, 1))
    code.append(gg.generate_code({'s': MAN_ANGLE_P90}, 3, False))

    code.append(gg.generate_code({}, 91))
    code.append(gg.generate_code({GRIP_AXIS: GRIP_DOWN, 'f': feed_rate}, 1))
    code.append(gg.generate_code({}, 90))

    # finished dirty plate actions for cycle
    code.extend(reset_zero())

    return code

def gcode_grab_plate_cs(z_is_zero: bool, z_dist=CS_GRAB_Z, feed_rate=750) -> list[str]:
    code = []

    # make sure z is zero before moving servo
    if not z_is_zero: 
        code.append(gg.generate_code({'z': 0.0, 'f': feed_rate}, 1))

    code.append(gg.generate_code({}, 91))
    code.append(gg.generate_code({GRIP_AXIS: GRIP_UP, CS_AXIS: CS_DIST, 'f': feed_rate}, 1))
    code.append(gg.generate_code({}, 90))
    code.append(gg.generate_code({'s': MAN_ANGLE_P00}, 3, False))
    code.append(gg.generate_code({'z': z_dist, 'f': feed_rate}, 1))
    code.append(gg.generate_code({}, 91))
    code.append(gg.generate_code({GRIP_AXIS: GRIP_DOWN}, 1))
    code.append(gg.generate_code({}, 90))
    code.append(gg.generate_code({'z': 0.0, 'f': feed_rate}, 1))
    code.append(gg.generate_code({'s': MAN_ANGLE_P90}, 3, False))

    # finished dirty plate actions for cycle
    code.extend(reset_zero())

    return code

def main():
    print(set_zero(False))
    print(reset_zero())
    print()
    print(gcode_move_to_printer(1, False))
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