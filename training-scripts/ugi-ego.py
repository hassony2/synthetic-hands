import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np

uci_ego_folder = '/home/local2/yhasson/datasets/UCI-EGO/'
seq_folder = uci_ego_folder + 'Seq4/'

depth_im = seq_folder + 'fr1_z.png'
img = mpimg.imread(depth_im)
print(img)
print(np.max(img))
print(np.min(img))
img = np.clip(img, 0, 0.02)
plt.imshow(img)
plt.imshow(img)
plt.show()

