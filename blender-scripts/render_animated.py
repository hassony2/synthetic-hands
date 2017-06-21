import bpy
import configparser
from importlib import reload
import os
import random
import sys

absolute_root = '/home/local2/yhasson/first-person-action-recognition/'
sys.path.insert(
    0, absolute_root + 'blender-scripts/')

from utils import blender
from utils import filesys

config = configparser.ConfigParser()
config.read(absolute_root + 'config.ini')
render = True

# Insure modules are reloaded in blender
reload(blender)
reload(filesys)

arm = bpy.data.objects['Armature']
scene = bpy.context.scene

folders = config['folders']

# Hand bone name variables
fingers = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
bone_idxs = ['1', '2', '3', '4']
bone_names = ['mixamorig_RightHand{0}{1}'.format(finger, idx)
              for finger in fingers
              for idx in bone_idxs]

actions = ['PlayGuitar', 'PickupObject', 'SittingThumbsUp',
           'BangFist', 'Count', 'Piano', 'Beckoning']
spots = ['Spot1', 'Spot2', 'Spot3']
spot_values = list(range(0, 1001, 200))
camera_names = ['Camera', 'Camera2']

for folder in folders.values():
    filesys.create_dir(folder)

# Get background images
bg_folder = folders['background']
bg_names = [bg_folder + filen for filen in os.listdir(bg_folder)]

depth_folder = folders['depth']
segm_folder = folders['segm']

# Render
rgb_folder = folders['rgb']

render_nbs = 10000

fileprefix = 'malcolm-'
if render:
    for render_nb in range(render_nbs):
        # Set camera
        camera_name = random.choice(camera_names)
        cam = bpy.data.objects[camera_name]
        # Clear camera constraints
        for const in cam.constraints:
            cam.constraints.remove(const)
        # Camera follows hand
        finger = random.choice(fingers)
        bone_idx = random.choice(bone_idxs)
        bone_name = 'mixamorig_RightHand{finger}{idx}'.format(finger=finger,
                                                              idx=bone_idx)
        const = blender.follow_bone(arm, camera_name, bone_name=bone_name, track_axis='z',
                                    track_axis_neg=True, up_axis='y')

        # Randomly pick background
        bg_name = random.choice(bg_names)
        bg_img = bpy.data.images.load(bg_name)

        filename = fileprefix + '{idx}-'.format(idx=render_nb)
        blender.set_cycle_nodes(scene, background_img=bg_img, filename=filename,
                                segm=True, segm_folder=segm_folder,
                                segm_mats=['Bodymat'],
                                depth_folder=depth_folder)

        # Randomly pick action
        action_name = random.choice(actions)
        action = bpy.data.actions[action_name]
        arm.animation_data.action = action

        # Randomly change light emission of spots
        for spot_name in spots:
            spot = bpy.data.lamps[spot_name]
            spot_value = random.choice(spot_values)
            spot.node_tree.nodes['Emission'].inputs[1].default_value = spot_value

        file_template = fileprefix
        blender.render_frames(scene, cam, arm,
                              folders,
                              bone_names,
                              file_template=file_template,
                              rendering_idx=render_nb)
