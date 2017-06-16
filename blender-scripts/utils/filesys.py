import os


def create_dir(path):
    """
    Creates dir if absent
    """
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)


