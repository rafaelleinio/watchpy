import cv2
import numpy as np


def xy_calc(xy):
    return (xy[0], 600 - xy[1])  # invert y ax


def crop_image(image, x, y, offset):
    return np.array([np.array(
        line[x - offset: x + offset - 1]
        ) for line in image[y - offset: y + offset - 1]])


def open_image(image_path):
    return cv2.imread(image_path, 1)


def resize_image(image, scaling_factor):
    return cv2.resize(
        image, None,
        fx=scaling_factor,
        fy=scaling_factor,
        interpolation=cv2.INTER_AREA)


def save_image(image_path, image):
    cv2.imwrite(image_path, image)


def get_frame(i_frame):
    return open_image('tmp/frames/' + str(i_frame) + '.jpg')
