

gcode_template = {
   0 : ["G0 Xx Yy Zz\n", (1, 2, 3, 4)],
   1 : ["G1 Xx Yy Zz Ff\n", (1, 2, 3, 4)],
   2 : ["G2 Xx Yy Zz Rr\n", (2, 3)],
   3 : ["G3 Xx Yy Zz Rr\n", (2, 3)],
   4 : ["G4 Pp\n", (1)],
   5 : ["G54 Xx Yy Zz\n", (1, 2, 3, 4)],
   6 : ["M00\n", (0)],
}

printer_loc = [
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
    12 : {"x": 75.0,  "y": 50.0},
]


def generate_gcode(command_args, command_type):
    if command_type not in gcode_template:
        raise ValueError("Invalid command type")
    
    if not isinstance(command_args, dict):
        raise TypeError("command_args must be a dictionary")

    template = str(gcode_template[command_type][0])
    possible_nargs = tuple(gcode_template[command_type][1])
    nargs = len(command_args)

    if possible_nargs.count(nargs) == 0:
        raise ValueError("Invalid number of arguments for command type")
    
    else:
        gcode = template
        for i in command_args:
            gcode = gcode.replace(command_args[i], f"{i:.1f}")

        return gcode


def printers(printer_number):
    if not isinstance(printer_number, int):
        raise ValueError("Invalid printer number")
    else:
        printer_location = str(printer_loc[printer_number])
        return printer_location


def main():

    while(1):
        printer_num = int(input("Enter printer number: "))
        new_location = printers(printer_num)
        print("New location:",  new_location)
        print(generate_gcode(new_location, 1))
pass

if __name__ == "__main__":
    home = {"x": 0.0, "y": 0.0, "z": 0.0}
    print(generate_gcode(home, 5))
    print("Starting location:", home)
    #print("Testing G-code generation:")
    main()