
gcode_template = {
    0 : ["G00 Xx Yy Zz Ff\n", (1, 2, 3, 4)],
    1 : ["G01 Xx Yy Zz\n", (1, 2, 3)],
    2 : ["G02 Xx Yy Zz Rr\n", (2, 3)],
    3 : ["G03 Xx Yy Zz Rr\n", (2, 3)],
    4 : ["G04 Pp\n", (1)],
}

mcode_template = {
    0 : ["M00\n", (0)],
    1 : ["M01\n", (0)],
    2 : ["M02\n", (0)],
    3 : ["M03 Ss\n", (1)],
    4 : ["M05\n", (0)],
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





def main():
    c1_args = {'x': 10.0, 'y': 23.4, 'z': 5.4}
    print(generate_code(c1_args, 0, True))
    c2_args = {'x': 10.0, 'y': 23.4}
    print(generate_code(c2_args, 1, True))
    c3_args = {'x': 3.2, 'y': 5.3, 'r': 5.0}
    print(generate_code(c3_args, 2, True))

    full_gcode = ""
    full_gcode += generate_code(c1_args, 0, True)
    full_gcode += generate_code(c2_args, 1, True)
    full_gcode += generate_code(c3_args, 2, True)
    print("Full G-code:")
    print(full_gcode)

    pass

if __name__ == "__main__":
    print("Testing G-code generation:")
    main()

