import bpy
import configparser
from importlib import reload
import sys

absolute_root = '/home/local2/yhasson/first-person-action-recognition/'
sys.path.insert(0, absolute_root + 'blender-scripts/')

from utils import blender
from utils import filesys

config = configparser.ConfigParser()
config.read(absolute_root + 'config.ini')

# Insure modules are reloaded in blender
reload(blender)
reload(filesys)

render = True

scene = bpy.context.scene
cam = bpy.context.scene.camera
arm = bpy.data.objects["Armature"]

folders = config["folders"]
data_folder = folders["data"]
rgb_folder = folders["rgb"]
depth_folder = folders["depth"]
coord_2d_folder = folders["coord_2d"]
coord_3d_folder = folders["coord_2d"]
segm_folder = folders["segm"]

# Create folders if absent
filesys.create_dir(coord_2d_folder)
filesys.create_dir(coord_3d_folder)
filesys.create_dir(depth_folder)
filesys.create_dir(segm_folder)

bone_nb = 20
fingers = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
bone_idxs = ['1', '2', '3', '4']

# Load background image
image_name = "uci-ego-seq1-951.jpg"
background_folder = folders["background"]
background_path = background_folder + image_name
background_img = bpy.data.images.load(background_path)

bone_names = [
    "mixamorig:RightHand{0}{1}".format(finger, idx)
    for finger in fingers for idx in bone_idxs
]
if render:
    # Render frames
    frame_beg = scene.frame_start
    frame_end = scene.frame_end
    # camera_names = ['Headcam', 'Chestcam']
    camera_names = ['Headcam']
    for camera_name in camera_names:
        filename = "regina-pick-up-cup-{cam}".format(cam=camera_name.lower())
        blender.set_cycle_nodes(
            scene,
            background_img,
            filename=filename,
            segm=True,
            segm_folder=segm_folder,
            segm_mats=['Material.003', 'mia_material_x2SG'],
            depth_folder=depth_folder)

        file_template = filename + "{0:04d}"
        blender.render_frames(
            scene,
            cam,
            arm,
            folders,
            hand_side,
            bone_names,
            file_template=file_template)
