from os import getenv
import yaml
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

def reset_zero() -> list[str]:
    code = []

    code.append(gg.generate_code({}, 92.1))
    
def gcode_generic_move(x: float, y: float, z_is_zero: bool, feed_rate=1500) -> list[str]:
    code = []
    
    code.append(gg.generate_code({}, 90))

    if not z_is_zero:
        code.append(gg.generate_code({'z': 0.0, 'f': feed_rate}, 1))

    code.append(gg.generate_code({'x': x, 'y': y, 'f': feed_rate}, 1))
    return code

def gcode_move_to_printer(printer_number: int, z_is_zero: bool, feed_rate=1500) -> list[str]:
    coords = read_printer_coords(printer_number)
    code = []

    # set z zero before doing global moves
    if not z_is_zero:
        code.append(gg.generate_code({'z': 0.0, 'f': feed_rate}, 1))

    code.append(gg.generate_code({'s': MAN_ANGLE_P90}, 3, False))
    code.append(gg.generate_code({'x': coords['x'], 'y': coords['y'], 'f': feed_rate}, 1))

    return code

def gcode_move_to_home(z_is_zero: bool, feed_rate=1500) -> list[str]:
    code = []

    if not z_is_zero:
        code.append(gg.generate_code({'z': 0.0, 'f': feed_rate}, 1))

    code.append(gg.generate_code({'x': 0.0, 'y': 0.0, 'f': feed_rate}, 1))
    return code

# can apply to grabbing from cs or printer
def gcode_grab_plate(z_dist: float, z_is_zero: bool, feed_rate=1500) -> list[str]:
    code = []

    # make sure z is zero before moving servo
    if not z_is_zero: 
        code.append(gg.generate_code({'z': 0.0, 'f': feed_rate}, 1))

    code.append(gg.generate_code({'s': MAN_ANGLE_N12}, 3, False))
    code.append(gg.generate_code({'z': z_dist, 'f': feed_rate}, 1))
    # G91 for relative moves on U or V axes
    code.append(gg.generate_code({}, 91))
    code.append(gg.generate_code({GRIP_AXIS: GRIP_DOWN}, 1))
    code.append(gg.generate_code({}, 90))

    code.append(gg.generate_code({'z': 0.0}, 1))
    code.append(gg.generate_code({'s': MAN_ANGLE_P90}, 3, False))
    # add up commands here
    return code

# can apply to releasing to ds or printer
def gcode_release_plate(z_dist: float, z_is_zero: bool, feed_rate=1500) -> list[str]:
    code = []

    # make sure z is zero before moving servo
    if not z_is_zero: 
        code.append(gg.generate_code({'z': 0.0, 'f': feed_rate}, 1))

    code.append(gg.generate_code({'s': MAN_ANGLE_N12}, 4, False))
    code.append(gg.generate_code({'z': z_dist}, 1))
    
    # relative moves for U or V axes
    code.append(gg.generate_code({}, 91))
    code.append(gg.generate_code({GRIP_AXIS: GRIP_UP}, 1))
    code.append(gg.generate_code({}, 90))

    code.append(gg.generate_code({'z': 0.0}, 1))
    return code

def gcode_open_door(z_is_zero: bool, feed_rate=900) -> list[str]:
    code = []

    #G92 has already set zero to right location
    #M03 has already set servo to right angle
    #G90 should be active on entry

    # send to currently set zero
    code.extend(gcode_move_to_home(z_is_zero))

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
    code.append(gg.generate_code({'y': -DOOR_Y_ENG, 'f': feed_rate}, 1))
    code.append(gg.generate_code({}, 90))
    # move back
    code.append(gg.generate_code({'z': 0.0, 'f': feed_rate}, 1))

    # final coords (G92 relative)
    # x = DOOR_OPEN_DEL["x"]
    # y = 0.0
    # z = 0.0
    
    return code

def gcode_close_door(z_is_zero: bool, feed_rate=900) -> list[str]:
    code = []

    #G92 has already set zero to right location
    #M03 has already set servo to right angle
    #G90 should be active on entry

    # send to currently set zero
    code.extend(gcode_move_to_home(z_is_zero))

    # start z below handle
    code.append(gg.generate_code({'x': DOOR_OPEN_DEL['x'], 'f': feed_rate}, 1))
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
    
    return code

def clean_plate_prime(feed_rate=1500) -> list[str]:
    code = []

    code.append(gg.generate_code({}, 91))
    code.append(gg.generate_code({CS_AXIS: CS_DIST, 'f': feed_rate}))
    code.append(gg.generate_code({}, 90))

    return code

def main():
    print(gcode_open_door(False))
    print("\n")
    print(gcode_close_door(True))


if __name__ == "__main__":
    main()