from config import config
import gcode_gen as gg
import math as m
import numpy as np
import csv
import yaml
import json

try:
    import linuxcnc_interface as li
    import apriltag_python.apriltag_locator as al
    import apriltag_python.camera_intrinsics as ci
    HAS_AP = True
except:
    print("Apriltag Library not found, using manual procedure\n")
    HAS_AP = False

X_MAX = config["axis_x_max"]
Y_MAX = config["axis_y_max"]
Z_MAX = config["axis_z_max"]

T_CAMERA = config["camera_global_transform"]

CAMERA_T = config["camera_transform_coeffs"]
CAMERA_FOV_X = config["camera_fov_length"]
CAMERA_FOV_Y = config["camera_fov_height"]

NX = int(np.ceil(X_MAX / CAMERA_FOV_X))
NY = int(np.ceil(Y_MAX / CAMERA_FOV_Y))

DS_IDS: dict = config["ds_cols_tag_ids"]
DS_COLS = len(DS_IDS)

PR_IDS: dict = config["printer_tag_ids"]
PR_NUM = len(PR_IDS)

def precomp_grid_search() -> np.ndarray:
    dx = CAMERA_FOV_X * 0.8
    dy = CAMERA_FOV_Y * 0.8

    xs = np.array(range(NX)) * dx
    ys = np.array(range(NY)) * dy

    x, y = np.meshgrid(xs, ys)
    coords = np.stack((x, y), axis=2)
    return coords

ds_cols_coords = {"ds_cols_coords": []}
def write_ds_coords(xfound, yfound, col):
    pos = {col: {"x": xfound, "y": yfound}}
    ds_cols_coords["ds_cols_coords"].append(pos)

    if len(ds_cols_coords["ds_cols_coords"]) == DS_COLS:
        with open("ref_files/config.yaml", "r") as file:
            config_r = yaml.load(file, yaml.FullLoader)
            config_r["ds_cols_coords"] = ds_cols_coords["ds_cols_coords"]

        with open("ref_files/config.yaml", "w") as file:
            yaml.dump(config_r, file)

        ds_cols_coords["ds_cols_coords"] = []
        

pr_num_coords = {"pr_num_coords": []}
def write_pr_coords(xfound, yfound, num):
    pos = {num: {"x": xfound, "y": yfound}}
    pr_num_coords["pr_num_coords"].append(pos)

    print(pr_num_coords)

    if len(pr_num_coords["pr_num_coords"]) == DS_COLS:
        with open("ref_files/config.yaml", "r") as file:
            config_r = yaml.load(file, yaml.FullLoader)
            config_r["pr_num_coords"] = pr_num_coords["pr_num_coords"]

        with open("ref_files/config.yaml", "w") as file:
            yaml.dump(config_r, file)

        pr_num_coords["pr_num_coords"] = []


def write_cs_coords(xfound, yfound):
    with open("ref_files/config.yaml", "r") as file:
        config_r = yaml.load(file, yaml.FullLoader)
        config_r["cs_coords"] = {"x": xfound, "y": yfound}

    with open("ref_files/config.yaml", "w") as file:
        yaml.dump(config_r, file)

def find_tags_loop(params, cap, detector):
    xfound = 0.0
    yfound = 0.0

    coords = precomp_grid_search()
    
    for i in range(NY):
        for j in range(NX):
            [x,y] = coords[i,j,:]

            move = gg.generate_code({"x": x, "y": y}, 0, True)

            if(li.ok_for_mdi()):
                li.send_mdi_line(move)

            else:
                print("Error")
                return

            img = al.capture_image(cap)
            dets = al.detect_apriltags(img, detector, params=params)
            t = al.get_pose(dets)

            xfound = x + T_CAMERA["x"] + t[0]
            yfound = y + T_CAMERA["y"] + t[1]

            if (dets[0].id in DS_IDS.keys()):
                write_ds_coords(xfound, yfound, DS_IDS.get(dets[0].id))

            if (dets[0].id in PR_IDS.keys()):
                write_pr_coords(xfound, yfound, PR_IDS.get(dets[0].id))

            if dets[0].id == 0:
                write_cs_coords(xfound, yfound)



def main():
    write_ds_coords(0.1, 0.1, 1)
    write_ds_coords(0.1, 0.1, 2)
    write_ds_coords(0.1, 0.1, 3)
    write_ds_coords(0.1, 0.1, 4)
    write_ds_coords(0.1, 0.1, 5)
    write_ds_coords(0.1, 0.1, 6)
    write_ds_coords(0.1, 0.1, 7)
    
    write_cs_coords(0.3, 0.2)
    write_cs_coords(0.5, 0.4)


if __name__ == "__main__":
    main()
