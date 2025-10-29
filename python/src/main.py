

gcode_template = {
    0 : ["G0 Xx Yy Zz Ff\n", (1, 2, 3, 4)],
    1 : ["G1 Xx Yy Zz\n", (1, 2, 3)],
    2 : ["G2 Xx Yy Zz Rr\n", (2, 3)],
    3 : ["G3 Xx Yy Zz Rr\n", (2, 3)],
    4 : ["G4 Pp\n", (1)],
}

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





def main():
    c1_args = {10.0: 'x', 20.5: 'y', 5.4: 'z', 1500: 'f'}
    print(generate_gcode(c1_args, 0))
    c2_args = {15: 'x', 25.3: 'y'}
    print(generate_gcode(c2_args, 1))
    c3_args = {30.0: 'x', 40.0: 'y', 5.0: 'r'}
    print(generate_gcode(c3_args, 2))

    full_gcode = ""
    full_gcode += generate_gcode(c1_args, 0)
    full_gcode += generate_gcode(c2_args, 1)
    full_gcode += generate_gcode(c3_args, 2)
    print("Full G-code:")
    print(full_gcode)

    pass

if __name__ == "__main__":
    print("Testing G-code generation:")
    main()

