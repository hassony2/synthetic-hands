import os
import cv2


def create_dir(path):
    """
    Creates dir if absent
    """
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.mkdir(directory)


def read_depth(path):
    """
    Reads depth from exr file

    :rtype: numpy.ndarray
    """
    depth3channels = cv2.imread(path, flags=3)
    depth = depth3channels[:, :, 0]
    return depth
