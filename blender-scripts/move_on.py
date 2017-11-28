import bpy
import configparser
from importlib import reload
import sys

absolute_root = '/sequoia/data1/yhasson/code/first-person-action-recognition/'
sys.path.insert(0, absolute_root + 'blender-scripts/')

from utils import blender
from utils import filesys
from utils import randomutils

config = configparser.ConfigParser()
config.read(absolute_root + 'config.ini')

# Insure modules are reloaded in blender
reload(blender)
reload(filesys)
reload(randomutils)

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
bone = arm.pose.bones['mixamorig_RightHand']
randomutils.move_on_sphere(cam, arm, bone)
