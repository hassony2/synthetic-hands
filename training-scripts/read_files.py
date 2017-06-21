import cv2
import configparser
import matplotlib.pyplot as plt
import numpy as np
import os

from visualize import reading

config = configparser.ConfigParser()
config.read('../config.ini')
folders = config['folders']

rgb_folder = folders["rgb"]
depth_folder = folders["depth"]
coord_2d_folder = folders["coord_2d"]
coord_3d_folder = folders["coord_3d"]
segm_folder = folders["segm"]

png_names = os.listdir(rgb_folder)
img_prefixes = [name.split('.')[0] for name in png_names]

for prefix in img_prefixes:
    reading.visualize_sample(prefix, folders)
    plt.show()

