import cv2


def read_depth(path):
    """
    Reads depth from exr file

    :rtype: numpy.ndarray
    """
    depth3channels = cv2.imread(path, flags=3)
    depth = depth3channels[:, :, 0]
    return depth

