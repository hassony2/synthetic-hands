import cv2
import matplotlib.pyplot as plt
import numpy as np


from utils import filesys

render_folder = '/home/local2/yhasson/first-person-action-recognition/data/blender-renders/'
annot_folder = render_folder + 'Annots/'
segm_folder = annot_folder + 'hand-segm/'
depth_folder = annot_folder + 'depth/'

# Display segmentation
img_name = 'Image0001.exr'
segm_path = segm_folder + img_name
print(segm_path)
segm = cv2.imread(segm_path, flags=0)
print(segm.shape)
print(np.max(segm), np.min(segm))
plt.imshow(segm)
plt.show()

# Display depth
depth_path = depth_folder + img_name
depth = filesys.read_depth(depth_path)
im_range = 1
readable_depth = np.clip(depth, 0.8, im_range)
plt.imshow(readable_depth/im_range)
plt.show()


