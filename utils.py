import os
import cv2
import numpy as np
import glob

def xy_calc(xy):
    return (xy[0], 600 - xy[1])  # invert y ax

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

def crop_image(image, x, y, offset):
    return np.array([np.array(
        line[x - offset: x + offset - 1]
        ) for line in image[y - offset: y + offset - 1]])

def crop_image_two_offsets(image, x, y, w, h):
    return np.array([np.array(
        line[x - w: x + w - 1]
        ) for line in image[y - h: y + h - 1]])

def open_image(image_path):
    return cv2.imread(image_path, 1)

def click_resize_image(image, scaling_factor):
    return cv2.resize(
        image, None,
        fx=scaling_factor,
        fy=scaling_factor,
        interpolation=cv2.INTER_AREA)

def resize_image(image, targ_x, targ_y):
    return cv2.resize(image, (targ_x, targ_y))

def save_image(image_path, image):
    cv2.imwrite(image_path, image)

def get_frame(i_frame):
    return open_image('tmp/frames/' + str(i_frame) + '.png')

def clean_tmp_folder():
    [rm_img for rm_img in map(os.remove, glob.glob('tmp/frames/*.png'))]

def clean_cars_folder():
    [rm_img for rm_img in map(os.remove, glob.glob('model/CAR/cars/*.png'))]

def get_car_positions():
    return [[int(s) for s in line.split()] for line in open('model/CAR/result.txt')]