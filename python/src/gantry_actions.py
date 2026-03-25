from os import getenv
import yaml
import gcode_gen

def read_printer_coords(path: str, printer_number: int) -> dict:
    if not isinstance(printer_number, int) or printer_number < 1 or printer_number > 12:
        raise ValueError("Invalid printer number")
    
    with open(path, 'r') as file:
        lines = file.readlines()
        line = lines[printer_number - 1]
        coords = line.strip().split(',')
        
        return {"x": float(coords[0]), "y": float(coords[1])}

def gcode_move_to_printer(printer_number: int, feed_rate=1500) -> str:
    coords = read_printer_coords(f'{getenv("HOME")}/Team-303/ref_files/printer_centers.csv', printer_number)
    code = ""

    code += gcode_gen.generate_code({'x': coords['x'], 'f': feed_rate}, 1, True)
    code += gcode_gen.generate_code({'y': coords['y'], 'f': feed_rate}, 1, True)
    code += gcode_gen.generate_code({}, 1, False)
    return code

def gcode_move_to_home(feed_rate=1500) -> str:
    code = ""
    code += gcode_gen.generate_code({'x': 0.0, 'f': feed_rate}, 1, True)
    code += gcode_gen.generate_code({'y': 0.0, 'f': feed_rate}, 1, True)
    code += gcode_gen.generate_code({}, 1, False)
    return code

def gcode_grab_plate(z_dist: float, feed_rate=1500) -> str:
    code = ""
    code += gcode_gen.generate_code({'z': z_dist, 'f': feed_rate}, 1, True)
    # add grab plate g/mcode commands here
    code += gcode_gen.generate_code({'z': 0.0, 'f': feed_rate}, 1, True)
    # add fold up commands here
    code += gcode_gen.generate_code({}, 1, False)
    return code

def gcode_release_plate(z_dist: float, feed_rate=1500) -> str:
    code = ""
    code += gcode_gen.generate_code({'z': 0.0, 'f': feed_rate}, 1, True)
    code += gcode_gen.generate_code({'z': z_dist, 'f': feed_rate}, 1, True)
    # add fold down commands here
    # add release plate g/mcode commands here
    code += gcode_gen.generate_code({'z': 0.0, 'f': feed_rate}, 1, True)
    code += gcode_gen.generate_code({}, 1, False)
    return code


def main():
    path = f'{getenv("HOME")}/Team-303/ref_files/printer_centers.csv'
    printer_num = int(input("Enter printer number: "))
    coords = read_printer_coords(path, printer_num)
    if coords:
        print(f"Printer {printer_num} coordinates: {coords}")
    else:
        print(f"Printer number {printer_num} not found.")

    code = gcode_move_to_printer(printer_num)
    print(f"G-code to move to printer {printer_num} generated.")
    print(code)

    code = gcode_move_to_home()
    print("G-code to move to home position generated.")
    print(code)

if __name__ == "__main__":
    print("Testing printer coordinate retrieval:")
    main()