import cv2
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np


def read_depth(path):
    """
    Reads depth from exr file

    :rtype: numpy.ndarray
    """
    depth3channels = cv2.imread(path, flags=3)
    depth = depth3channels[:, :, 0]
    return depth


def visualize_sample(prefix, folders):
    rgb_folder = folders['rgb']
    depthpng_folder = folders["depthpng"]
    depth_folder = folders["depth"]
    coord_2d_folder = folders["coord_2d"]
    coord_3d_folder = folders["coord_3d"]
    segm_folder = folders["segm"]

    png_name = prefix + ".png"
    exr_name = prefix + ".exr"
    txt_name = prefix + ".txt"
    fig, axes = plt.subplots(2, 2)

    # Plot Rgb
    img = mpimg.imread(rgb_folder + png_name)
    axes[0, 0].imshow(img)
    axes[0, 0].axis('off')

    # Plot depth
    depth = read_depth(depth_folder + exr_name)
    readable_depth = np.clip(depth, 0.8, 1)
    axes[0, 1].imshow(readable_depth)
    axes[0, 1].axis('off')

    # Plot segmentation
    segm = cv2.imread(segm_folder + exr_name, flags=0)
    axes[1, 0].imshow(segm)
    axes[1, 0].axis('off')

    # Plot keypoints
    coord2d = np.loadtxt(coord_2d_folder + txt_name)
    axes[1, 1].imshow(img)
    # TODO fix the 540 - y in coord
    axes[1, 1].scatter(coord2d[:, 0], img.shape[0] - coord2d[:, 1], c='r')
    axes[1, 1].axis('off')






