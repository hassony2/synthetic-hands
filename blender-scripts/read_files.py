import cv2
import matplotlib.pyplot as plt
import numpy as np


from utils import filesys

im_path = '/home/local2/yhasson/first-person-action-recognition/data/blender-renders/Annots/Image0081.exr'
# Read depth
depth = filesys.read_depth(im_path)
im_range = 1
readable_depth = np.clip(depth, 0.8, im_range)
plt.imshow(readable_depth/im_range)
plt.show()


