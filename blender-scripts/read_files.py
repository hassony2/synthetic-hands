import cv2
import matplotlib.pyplot as plt
import numpy as np


depth = cv2.imread('/home/local2/yhasson/first-person-action-recognition/data/blender-renders/Annots/Image0081.exr', flags=3)
print(depth)
print(type(depth))
print(np.max(depth))
print(np.min(depth))
print(np.unique(depth))
print(depth.shape)
im_range = 1
readable_depth = np.clip(depth, 0.8, im_range)
plt.imshow(readable_depth[:, :, 2]/im_range)
plt.show()


