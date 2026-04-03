from types import MappingProxyType

gcode_template = {
    0 : ["G00 Xx Yy Zz Uu Vv", (1, 2, 3, 4, 5)], # rapid positioning
    1 : ["G01 Xx Yy Zz Uu Vv Ff", (1, 2, 3, 4, 5, 6)], # fed move
    2 : ["G02 Xx Yy Zz Rr Ff", (2, 3, 4, 5)], # clockwise arc
    3 : ["G03 Xx Yy Zz Rr Ff", (2, 3, 4, 5)], # counterclockwise arc
    4 : ["G04 Pp", (1,)], # dwell

    17 : ["G17", (0,)], # set to xy interp
    18 : ["G18", (0,)], # set to xz interp
    19 : ["G19", (0,)], # set to zy interp

    20 : ["G20", (0,)], # set units to inches
    21 : ["G21", (0,)], # set units to mm

    54 : ["G54 Xx Yy Zz", (1, 2, 3)], # work coordinate system 1

    61 : ["G61", (0,)], # exact stop check
    611 : ["G61.1", (0,)], # continuous path mode

    90 : ["G90", (0,)], # absolute programming
    91 : ["G91", (0,)], # incremental programming
    92 : ["G92 Xx Yy Zz", (1, 2, 3)], # set position
    921 : ["G92.1", (0,)], # reset G92 position to actual zero
    93 : ["G93", (0,)], # inverse time feed rate
    94 : ["G94", (0,)], # units per minute feed rate
    95 : ["G95", (0,)], # units per revolution feed rate
}
gcode_template = MappingProxyType(gcode_template) # make immutable

mcode_template = {
    0 : ["M00", (0,)], # pause
    1 : ["M01", (0,)], # optional pause
    2 : ["M02", (0,)], # end of program
    3 : ["M03 Ss", (1,)], # spindle on clockwise
    4 : ["M04 Ss", (1,)], # spindle on counterclockwise
    5 : ["M05", (0,)], # spindle stop

    61 : ["M61 Qq", (1,)], # tool change with tool number Q
    66 : ["M66 Pp Ll Qq", (2, 3)], # wait for input

    100 : ["M100 Pp Qq Rr", (1, 2, 3)], # user-defined actuator command placeholder
    101 : ["M101 Pp Qq Rr", (1, 2, 3)], # user-defined actuator command placeholder
}
mcode_template = MappingProxyType(mcode_template) # make immutable

# G-code / M-code generation function
def generate_code(command_args: dict, command_type: int, is_gcode = True) -> str:
    if is_gcode:
        template_dict = gcode_template
    else:
        template_dict = mcode_template

    if command_type not in template_dict:
        raise ValueError("Invalid command type")
    
    if not isinstance(command_args, dict):
        raise TypeError("Command_args must be a dictionary")

    if len(command_args) == 0:
        return template_dict[command_type][0]

    template = str(template_dict[command_type][0])
    possible_nargs = (template_dict[command_type][1])
    nargs = len(command_args)

    if possible_nargs.count(nargs) == 0:
        raise ValueError("Invalid number of arguments for command type")
    else:
        code = template
        for i in command_args:
            code = code.replace(i, f"{command_args[i]:.1f}")
    for i in code:
        if i.islower():
            unused = str(code[code.index(i)-2:code.index(i)+1])
            code = code.replace(unused, "")

    return code

def main():
    c1_args = {'u': 10.0, 'z': 5.4}
    print(generate_code(c1_args, 0))
    c2_args = {'x': 10.0, 'y': 23.4}
    print(generate_code({'u': 1.0}, 1, True))
    c3_args = {}
    print(generate_code(c3_args, 2, False))

    full_gcode = ""
    full_gcode += generate_code(c1_args, 0, True)
    full_gcode += generate_code(c2_args, 1, True)
    full_gcode += generate_code(c3_args, 2, False)
    print("Full G-code:")
    print(full_gcode)

    pass

if __name__ == "__main__":
    print("Testing G-code generation:")
    main()

