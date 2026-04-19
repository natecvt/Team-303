import linuxcnc_interface as li
from config import config, update_config_file

def main():
    print("----------------------------")
    print("Calibration Protocol Started")
    print("----------------------------\n")

    block = 0

    while True:

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
                    print("Make Sure a Plate is in this Printer, then:")
                    print(f"1. Jog the System to the Printer, open the door, then Jog Z to ~{config['printer_plate_z']}mm")
                    print("2. Jog the System so the Peg is Centered with the Fork")
                    print("   and the Manipulator Touches the Bottom of the Plate")
                    print(f"   If Z={config['printer_plate_z']}mm is Insufficient, Move the Printer")
                    print("3. Press ENTER when Position is Correct ...")
                    print("4. (On only 1 Plate) Mark a Reference Point on the Plate with a Marker")
                    print("   This can be Any Point Where the Fork is in Contact\n")
                    input("")

                    coords = li.get_coords()
                    xy = {"x": coords['x'] - config["door_to_plate_delta"]["x"],
                          "y": coords['y'] - config["door_to_plate_delta"]["y"]}
                    
                    config["printer_coords"][i] = xy
                    print(f"Position Value for Printer {i} Written")
                    print( "-------------------------------------\n")

                print("Jog System Away and Close All Doors")
                input("Press ENTER when done")

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

                li.send_mdi_line(f"G01 V{config['clean_plate_distance']} F1000")

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

                update_config_file(config)
                block += 1
                continue
                    
            case _:
                if not li.home_all_axes():
                    print("Homing Failed, Retry")
                    exit(1)

                print("Finished Calibration")
                break

if __name__ == "__main__":
    main()