import os


def create_dir(path):
    """
    Creates dir if absent
    """
    # Extract folder name if filepath is given
    if '.' in os.path.basename(path):
        directory = os.path.dirname(path)
    else:
        directory = path
    if not os.path.exists(directory):
        os.makedirs(directory)
