import bpy
from importlib import reload
import os
import random
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

actions = ['PlayGuitar', 'PickupObject']
spots = ['Spot1', 'Spot2', 'Spot3']
spot_values = list(range(0, 1001, 200))

# Clear camera constraints
for const in cam.constraints:
    cam.constraints.remove(const)


for folder in params['folders'].values():
    filesys.create_dir(folder)

# Get background images
bg_folder = folders["background"]
bg_names = [bg_folder + filen for filen in os.listdir(bg_folder)]

depth_folder = folders['depth']
segm_folder = folders['segm']

# Render
rgb_folder = folders['rgb']

render_nbs = 1000

fileprefix = "remy-"
for render_nb in range(render_nbs):
    # Camera follows hand
    finger = random.choice(fingers)
    bone_idx = random.choice(bone_idxs)
    bone_name = 'mixamorig_RightHand{finger}{idx}'.format(finger=finger,
                                                          idx=bone_idx)
    const = blender.follow_bone(arm, bone_name=bone_name, track_axis='z',
                                track_axis_neg=True, up_axis='y')

    # Randomly pick background
    bg_name = random.choice(bg_names)
    bg_img = bpy.data.images.load(bg_name)

    # TODO find a way to adapt the filename to handle >9999
    filename = fileprefix + "{idx}-".format(idx=render_nb)
    blender.set_cycle_nodes(scene, background_img=bg_img, filename=filename,
                            segm=True, segm_folder=segm_folder,
                            segm_mats=["Bodymat"],
                            depth_folder=depth_folder)

    # Randomly pick action
    action_name = random.choice(actions)
    action = bpy.data.actions[action_name]
    arm.animation_data.action = action

    # Randomly change light emission of spots
    for spot_name in spots:
        spot = bpy.data.lamps[spot_name]
        spot_value = random.choice(spot_values)
        spot.node_tree.nodes["Emission"].inputs[1].default_value = spot_value

    file_template = fileprefix
    blender.render_frames(scene, cam, arm,
                          params['folders'],
                          bone_names,
                          file_template=file_template,
                          rendering_idx=render_nb)
    break
