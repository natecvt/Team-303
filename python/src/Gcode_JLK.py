from gcode_gen import gcode_template, mcode_template, generate_code

printer_loc = {
    0 : {"x": 0.0,   "y": 0.0},
    1 : {"x": 1.1,   "y": 0.1},
    2 : {"x": 100.0, "y": 0.0},
    3 : {"x": 0.0,   "y": 100.0},
    4 : {"x": 100.0, "y": 100.0},
    5 : {"x": 0.0,   "y": 50.0}, 
    6 : {"x": 100.0, "y": 50.0},
    7 : {"x": 0.0,   "y": 75.0},
    8 : {"x": 100.0, "y": 75.0},
    9 : {"x": 50.0,  "y": 0.0},
    10 : {"x": 50.0,  "y": 100.0},
    11 : {"x": 50.0,  "y": 50.0},  
    12 : {"x": 75.0,  "y": 50.0}
}


def printers(printer_number):
    if not isinstance(printer_number, int) or not (0 <= printer_number <= 12):
        raise ValueError("Invalid printer number")
    else:
        return printer_loc[printer_number]


def main():
    home = {"x": 0.0, "y": 0.0, "z": 0.0}
    print(generate_code(home, 1, True))
    print("Starting location:", home)

    while(1):
        printer_num = int(input("Enter printer number: "))
        new_location = printers(printer_num)
        print("New location:",  new_location)
        print(generate_code(new_location, 1, True))
pass

if __name__ == "__main__":
    print("Testing G-code generation:")
    main()