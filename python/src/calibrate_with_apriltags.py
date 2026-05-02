import linuxcnc_interface as li
import gcode_gen as gg
from config import config, update_config_file, update_config_variable
import apriltag_python.apriltag_locator as al

def main():
    print("----------------------------")
    print("Calibration Protocol Started")
    print("----------------------------\n")

    if not (al.load_config("apriltag_python/config.yaml")):
        exit(1)
    
    if not (al.init_capture_apriltags()):
        exit(1)

    li.set_state_active()
    if not li.home_all_axes():
        print("Homing Failed, Retry")
        exit(1)
        
    print("Homing Complete, Please Manually Locate Printers")
    
    print("Setting Servo to Correct Angle")
    li.send_mdi_line("G92 X0 Y0 Z0 U0 V0")
    li.send_mdi_line("G90")

    li.send_mdi_line(f"G01 Z0 U{config['gripper_down']} F3000")
    li.send_mdi_line(f"G01 Z0 U{config['gripper_down']} F3000")

    block = 0

    while True:

        update_config_variable()

        match block:
            case 0:
                print("Skip Calibration for Printers?")
                if (input("y/n: ") == 'y'):
                    print("Skipping Printers")
                    block += 2
                    continue

                print("How Many Printers are You Calibrating?")

                try:
                    n :int = int(input("Number of Printers: "))
                except:
                    print("Wrong data entered, try again")
                    continue
                block += 1
                continue

            case 1:
                print("Calibrating Printer Positions")
                print("-----------------------------\n")

                li.set_state_active()
                if not li.home_all_axes():
                    print("Homing Failed, Retry")
                    exit(1)
                    
                print("Homing Complete, Please Manually Locate Printers")
                
                print("Setting Servo to Correct Angle")
                li.send_mdi_line(f"M03 S{config['manipulator_angle_n12']}")

                print("Lifting Clamp")
                li.send_mdi_line(f"G01 U{config['gripper_up']} F1000")

                li.c.mode(li.linuxcnc.MODE_MANUAL)
                li.c.wait_complete()
                
                for i in range(1, n + 1):
                    print(f"Skip Calibration for Printer {i}?")
                    print(f"If yes, this will only save calibration for {i} if previously calibrated")
                    if (input("y/n: ") == "y"):
                        continue

                    print(f"Position Calibration for Printer {i}")
                    print( "-----------------------------------\n")
                    print( "Make Sure the Marked Plate is in this Printer, then:")
                    print(f"1. Jog the System to the Printer, open the door, then Jog Z to ~{config['printer_plate_z']}mm")
                    print( "2. Jog the System so the Peg is Centered with the Fork")
                    print( "   and the Manipulator Touches the Bottom of the Plate")
                    print(f"   If Z={config['printer_plate_z']}mm is Insufficient, Move the Printer")
                    print( "3. Press ENTER when Position is Correct ...")
                    print( "4. (On only 1st Plate) Mark a Reference Point on the Plate with a Marker")
                    print( "   This can be Any Point Where the Fork is in Contact")
                    print( "   All Other Plates Should be Aligned with this Marking\n")
                    input("")

                    print("Auto-adjusting Manual Coordinate")
                    while True:
                        if not (al.capture_image()):
                            continue

                        tags = al.detect_apriltags()

                        if tags == None:
                            print("Could not Find Tag, Jog until Found")
                            continue

                        pose = al.get_pose(tags)

                        pose[0] -= config["camera_transform_coeffs"]["x"]
                        pose[1] -= config["camera_transform_coeffs"]["y"]

                        if (abs(pose[0] + pose[1]) > config["tolerance"]):
                            diffx = -pose[0]
                            diffy = -pose[1]

                            print(f"Adjustment: x{diffx}, y{diffy}")
                            li.send_mdi_line(f"G01 X{diffx} Y{diffy} F500")
                            continue

                        print("Plate Successfully Centered")

                        break

                    print("Simulating Plate Grab...")
                    li.send_mdi_line(f"G01 Z0 F3000")
                    li.send_mdi_line(f"G91")
                    li.send_mdi_line(f"G01 U{config['gripper_up']}")
                    li.send_mdi_line(f"G90")
                    li.send_mdi_line(f"G01 Z{config['printer_plate_z']}")
                    li.send_mdi_line(f"G91")
                    li.send_mdi_line(f"G01 U{config['gripper_down']}")
                    li.send_mdi_line(f"G90")
                    li.send_mdi_line(f"G01 Z0 F3000")

                    print("Was the plate grabbed correctly?")
                    if (input("y/n: ") == 'n'):
                        print("Retrying...")
                        i -= 1
                        continue

                    print("Simulating Plate Release...")
                    li.send_mdi_line(gg.generate_code({'s': config['manipulator_angle_0']}, 3, False))
                    li.send_mdi_line(gg.generate_code({'z': 3.0 * config['printer_plate_z'] / 4.0}, 1))
                    li.send_mdi_line(gg.generate_code({'s': config['manipulator_angle_n12']}, 3, False))
                    li.send_mdi_line(gg.generate_code({'z': config['printer_plate_z']}, 1))
                    
                    li.send_mdi_line(gg.generate_code({}, 91))
                    li.send_mdi_line(gg.generate_code({'u': config['gripper_up']}, 1))
                    li.send_mdi_line(gg.generate_code({}, 90))
                    li.send_mdi_line(gg.generate_code({'z': 0.0}, 1))
                    li.send_mdi_line(gg.generate_code({}, 91))
                    li.send_mdi_line(gg.generate_code({'u': config['gripper_down']}, 1))
                    li.send_mdi_line(gg.generate_code({}, 90))

                    print("Was the plate released correctly?")
                    if (input("y/n: ") == 'n'):
                        print("Retrying...")
                        i -= 1
                        continue

                    coords = li.get_coords()
                    xy = {"x": coords['x'] - config["door_to_plate_delta"]["x"],
                          "y": coords['y'] - config["door_to_plate_delta"]["y"]}
                    
                    config["printer_coords"][i] = xy
                    print(f"Position Value for Printer {i} Written")
                    print( "-------------------------------------\n")

                print("Grabbing Plate for DPS Calibration")
                li.send_mdi_line(f"G01 Z0 F3000")
                li.send_mdi_line(f"G91")
                li.send_mdi_line(f"G01 U{config['gripper_up']}")
                li.send_mdi_line(f"G90")
                li.send_mdi_line(f"G01 Z{config['printer_plate_z']}")
                li.send_mdi_line(f"G91")
                li.send_mdi_line(f"G01 U{config['gripper_down']}")
                li.send_mdi_line(f"G90")
                li.send_mdi_line(f"G01 Z0 F3000")
                li.send_mdi_line(f"M03 S{config['manipulator_angle_90']}")

                print("Jog System Away and Close All Doors")
                input("Press ENTER when done")

                if not li.home_all_axes():
                    print("Homing Failed, Retry")
                    exit(1)
                update_config_file(config)
                block += 1
                continue

            case 2:
                print("Skip Calibration for CPD?")
                if (input("y/n: ") == 'y'):
                    print("Skipping CPD Calibration")
                    block += 1
                    continue

                print("Calibrating Clean Plate Dispenser Position")
                print("------------------------------------------\n")

                if not li.home_all_axes():
                    print("Homing Failed, Retry")
                    exit(1)
                    
                print("Homing Complete, Please Manually Locate CPD")

                print("Setting Servo to Correct Angle")
                li.send_mdi_line(f"M03 S{config['manipulator_angle_n12']}")

                print("Place the Marked Plate in the CPD")
                print("Press ENTER when Plate is in CPD\n")
                input("")

                li.send_mdi_line(f"G01 V{config['clean_plate_distance']} F100")

                li.c.mode(li.linuxcnc.MODE_MANUAL)
                li.c.wait_complete()

                print("Please Jog the System to the CPD")
                print("Line up the Manipulator to the Marked Point on the Plate")

                print("Press ENTER when Position is Correct")
                input("")

                print("CPD Coordinates Written")
                coords = li.get_coords()
                config["cs_coords"] = {"x": coords["x"], "y": coords["y"]}
                config["cs_grab_z"] = coords["z"]

                if not li.home_all_axes():
                    print("Homing Failed, Retry")
                    exit(1)
                update_config_file(config)
                block += 1
                continue

            case 3:
                print("Skip Calibration for DPS?")
                if (input("y/n: ") == 'y'):
                    print("Skipping DPS Calibration")
                    block += 1
                    continue

                try:
                    r :int = int(input("Input Number of Rows: "))
                except:
                    print("Wrong data entered, try again")
                    continue

                try:
                    c :int = int(input("Input Number of Columns: "))
                except:
                    print("Wrong data entered, try again")
                    continue
                
                config["ds_rows"] = r
                config["ds_cols"] = c
                update_config_file(config)
                print("Written Rows and Columns")
                
                print(f"Calibrating DPS with {r} Rows and {c} Columns")
                print("-----------------------------------------")

                block += 1

            case 4:
                if not li.home_all_axes():
                    print("Homing Failed, Retry")
                    exit(1)
                    
                print("Homing Complete, Please Manually Locate DPS")

                print("Setting Servo to Correct Angle")
                li.send_mdi_line(f"M03 S{config['manipulator_angle_0']}")

                print("Place the Marked Plate in the Gripper, aligned with Previous Marking")
                print("Press ENTER when done")
                input("")

                print("Lowering Clamp")
                li.send_mdi_line(f"G01 U{config['gripper_down']} F100")

                li.c.mode(li.linuxcnc.MODE_MANUAL)
                li.c.wait_complete()

                print("Jog the System to the Upper Left Shelf Slot")
                print(f"Then Jog Z to {config['ds_release_z']}mm")
                print("Make Sure the Plate Lines up with the Marking")
                print("Press ENTER when done")
                input("")

                print("Releasing Plate")
                li.send_mdi_line("G91")
                li.send_mdi_line(f"G01 Y{config['ds_release_dy']} F1000")
                li.send_mdi_line(f"M03 S{config['manipulator_angle_n12']}")
                li.send_mdi_line(f"G01 U{config['gripper_up']} F100")
                li.send_mdi_line("G90")
                li.send_mdi_line(f"G01 Z0 F1000")

                print("Did the Plate Release Correctly?")
                if (input("y/n: ") == 'n'):
                    print("Try again, Try Lowering the System Some")
                    continue

                coords = li.get_coords()
                x0 = coords["x"]
                y0 = coords["y"]

                config["ds_coords"]["x"] = x0
                config["ds_coords"]["y"] = y0
                update_config_file(config)
                print("Written First DPS Coords")
                block += 1

            case 5:
                print("Setting Servo to Correct Angle")
                li.send_mdi_line(f"M03 S{config['manipulator_angle_0']}")

                print("Jog the System to the Lower Right Shelf Slot")
                print(f"Then Jog Z to {config['ds_release_z']}mm")
                print("Make Sure the Plate Lines up with the Marking")
                print("Press ENTER when done")
                input("")

                print("Setting Servo to Correct Angle")

                li.send_mdi_line("G91")
                li.send_mdi_line(f"G01 Y{config['ds_release_dy']} F1000")
                li.send_mdi_line(f"M03 S{config['manipulator_angle_n12']}")
                li.send_mdi_line(f"G01 U{config['gripper_up']} F100")
                li.send_mdi_line("G90")
                li.send_mdi_line(f"G01 Z0 F1000")

                print("Did the Plate Release Correctly?")
                if (input("y/n: ") == 'n'):
                    print("Try again, Try Lowering the System Some")
                    continue

                coords = li.get_coords()
                xc = coords["x"]
                yr = coords["y"]

                config["ds_dx"] = (xc - x0) / float(c-1)
                config["ds_dy"] = (yr - y0) / float(r-1) # should be negative
                update_config_file(config)
                print("Written DPS Coords and Offsets")
                block += 1

                    
            case _:
                if not li.home_all_axes():
                    print("Homing Failed, Retry")
                    exit(1)

                print("Finished Calibration")
                break

if __name__ == "__main__":
    main()