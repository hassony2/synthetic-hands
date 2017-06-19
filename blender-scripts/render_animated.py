import bpy
from importlib import reload
import numpy as np
import os
import sys

sys.path.insert(
    0, '/home/local2/yhasson/first-person-action-recognition/blender-scripts')

from settings import params
from utils import blender
from utils import filesys

# Insure modules are reloaded in blender
reload(blender)
reload(filesys)

arm = bpy.data.objects['Armature']
camera_name = 'Camera'
cam = bpy.data.objects[camera_name]
scene = bpy.context.scene

folders = params['folders']

# Hand bone name variables
fingers = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
bone_idxs = ['1', '2', '3', '4']
bone_names = ["mixamorig_RightHand{0}{1}".format(finger, idx)
              for finger in fingers
              for idx in bone_idxs]

# Clear camera constraints
for const in cam.constraints:
    cam.constraints.remove(const)

# Camera follows hand
bone_name = 'mixamorig_RightHandIndex4'
const = blender.follow_bone(arm, bone_name=bone_name, track_axis='z',
                                 track_axis_neg=True, up_axis='y')

for folder in params['folders'].values():
    filesys.create_dir(folder)

# Get background images
bg_folder = folders["background"]
bg_names = [bg_folder + filen for filen in os.listdir(bg_folder)]
bg_img = bpy.data.images.load(bg_names[0])

depth_folder = folders['depth']
segm_folder = folders['segm']
filename = "remy-pick-up-ntg-anim-{cam}".format(cam=camera_name.lower())

blender.set_cycle_nodes(scene, background_img=bg_img, filename=filename,
                        segm=True, segm_folder=segm_folder,
                        segm_mats=["Bodymat"],
                        depth_folder=depth_folder)

# Render
rgb_folder = folders['rgb']
file_template = filename + "{0:04d}"

blender.render_frames(scene, cam, arm,
                      params['folders'],
                      bone_names,
                      file_template=file_template)
