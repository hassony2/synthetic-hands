import cv2
import matplotlib.pyplot as plt
import numpy as np

from settings import params
from utils import filesys
from utils import reading

folders = params["folders"]
rgb_folder = folders["rgb"]
depth_folder = folders["depth"]
coord_2d_folder = folders["coord_2d"]
coord_3d_folder = folders["coord_3d"]
segm_folder = folders["segm"]

# Display segmentation
img_name = 'remy-0-0124.exr'
segm_path = segm_folder + img_name
print(segm_path)
segm = cv2.imread(segm_path, flags=0)
print(segm.shape)
print(np.max(segm), np.min(segm))
plt.imshow(segm)
plt.show()

# Display depth
depth_path = depth_folder + img_name
depth = reading.read_depth(depth_path)
im_range = 1
readable_depth = np.clip(depth, 0.8, im_range)
plt.imshow(readable_depth/im_range)
plt.show()


