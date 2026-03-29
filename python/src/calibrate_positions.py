from config import config
import gcode_gen as gg
import math as m
import numpy as np

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

T_CAMERA = config["transform_to_camera"]

CAMERA_T = config["camera_transform_coeffs"]
CAMERA_FOV_X = config["camera_fov_length"]
CAMERA_FOV_Y = config["camera_fov_height"]

NX = int(np.ceil(X_MAX / CAMERA_FOV_X))
NY = int(np.ceil(Y_MAX / CAMERA_FOV_Y))

DS_IDS: dict = config["ds_cols_tag_ids"]
DS_COLS = DS_IDS.__len__()

PR_IDS: dict = config["printer_tag_ids"]
PR_NUM = PR_IDS.__len__()



def precomp_grid_search() -> np.ndarray:
    dx = CAMERA_FOV_X * 0.8
    dy = CAMERA_FOV_Y * 0.8

    xs = np.array(range(NX)) * dx
    ys = np.array(range(NY)) * dy

    x, y = np.meshgrid(xs, ys)
    coords = np.stack((x, y), axis=2)
    return coords

def write_ds_coords(xfound, yfound, col):
    pass

def write_pr_coords(xfound, yfound, num):
    pass

def write_cs_coords(xfound, yfound):
    pass

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
    if HAS_AP:
        params = al.load_config("python/src/apriltag_python/config.yaml")
        [cap, detector] = al.init_capture_apriltags(params)

        if (not li.open_linuxcnc()):
            print("Linuxcnc failed to initialize properly")
            exit(1)
        
        if (not li.home_all_axes()):
            exit(2)
    
    precomp_grid_search()
    
        

if __name__ == "__main__":
    main()
