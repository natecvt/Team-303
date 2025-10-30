

gcode_template = {
   0 : ["G0 Xx Yy Zz\n", (1, 2, 3, 4)],
   1 : ["G1 Xx Yy Zz Ff\n", (1, 2, 3, 4)],
   2 : ["G2 Xx Yy Zz Rr\n", (2, 3)],
   3 : ["G3 Xx Yy Zz Rr\n", (2, 3)],
   4 : ["G4 Pp\n", (1)],
   5 : ["G54 Xx Yy Zz\n", (1, 2, 3, 4)],
   6 : ["M00\n", (0)],
}

mcode_template = {
    0 : ["M00\n", (0)],
    1 : ["M01\n", (0)],
    2 : ["M02\n", (0)],
    3 : ["M03 Ss\n", (1)],
    4 : ["M05\n", (0)],
}

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


def generate_code(command_args, command_type, is_gcode = True):
    if is_gcode:
        template_dict = gcode_template
    else:
        template_dict = mcode_template

    if command_type not in template_dict:
        raise ValueError("Invalid command type")
    
    if not isinstance(command_args, dict):
        raise TypeError("Command_args must be a dictionary")

    template = str(template_dict[command_type][0])
    possible_nargs = tuple(template_dict[command_type][1])
    nargs = len(command_args)

    if possible_nargs.count(nargs) == 0:
        raise ValueError("Invalid number of arguments for command type")
    
    else:
        code = template
        for i in command_args:
            code = code.replace(i, f"{command_args[i]:.1f}")

        return code


def printers(printer_number):
    if not isinstance(printer_number, int) or not (0 <= printer_number <= 12):
        raise ValueError("Invalid printer number")
    else:
        return printer_loc[printer_number]


def main():
    home = {"x": 0.0, "y": 0.0, "z": 0.0}
    print(generate_code(home, 5, True))
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