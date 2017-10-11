import argparse
import configparser
import os
import random
import sys

import bpy
from importlib import reload

root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, root)

from utils import blender
from utils import filesys

# Insure modules are reloaded in blender
reload(blender)
reload(filesys)

# Parse arguments
parser = argparse.ArgumentParser()
_, all_args = parser.parse_known_args()
script_args = all_args[all_args.index('--') + 1:]

parser.add_argument(
    '--person',
    type=str,
    default='malcolm',
    help='Name of the character (used to name files')
parser.add_argument(
    '--trimmed',
    action='store_true',
    help='whether to add the "_trimmed" suffix to file names')
parser.add_argument(
    '--background_folder',
    type=str,
    help='Path to folder containing the backgrounds')
parser.add_argument(
    '--render_nb', type=int, default=10, help='Number of frames to render')
parser.add_argument(
    '--lsun', action='store_true', help="Using gül's LSUN dataset")
parser.add_argument(
    '--focal_min', type=int, default=15, help='Min camera focal length')
parser.add_argument(
    '--focal_max', type=int, default=25, help='Max camera focal length')
args, _ = parser.parse_known_args(script_args)

# Read config parser
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(root), 'config.ini'))
render = True

arm = bpy.data.objects['Armature']
scene = bpy.context.scene

folders = config['folders']

# Hand bone name variables
fingers = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
bone_idxs = ['1', '2', '3', '4']
bone_names = [
    'mixamorig_RightHand{0}{1}'.format(finger, idx)
    for finger in fingers for idx in bone_idxs
]

actions = [
    'PlayGuitar', 'PickupObject', 'SittingThumbsUp', 'BangFist', 'Count',
    'Piano', 'Beckoning'
]
spots = ['Spot1', 'Spot2', 'Spot3']
spot_values = list(range(0, 1001, 200))
camera_names = ['Camera', 'Camera2']

for folder in folders.values():
    filesys.create_dir(folder)

if args.lsun:
    train_list_path = os.path.join(args.background_folder, 'train_img.txt')
    bg_names = [
        os.path.join(args.background_folder, line.strip())
        for line in open(train_list_path)
    ]
else:
    bg_names = [
        os.path.join(args.background_folder, file_name)
        for file_name in os.listdir(args.background_folder)
    ]

depth_folder = folders['depth']
segm_folder = folders['segm']

# Render
rgb_folder = folders['rgb']

trimmed_suffix = '-trimmed'
fileprefix = args.person + (trimmed_suffix if args.trimmed else '')
print('fileprefix : {}'.format(fileprefix))

if render:
    for render_idx in range(args.render_nb):
        # Set camera
        camera_name = random.choice(camera_names)
        cam = bpy.data.objects[camera_name]

        # Randomly set focal length between bounds
        cam.lens = random.randint(args.focal_min, args.focal_max)
        # Clear camera constraints
        for const in cam.constraints:
            cam.constraints.remove(const)
        # Camera follows hand
        finger = random.choice(fingers)
        bone_idx = random.choice(bone_idxs)
        bone_name = 'mixamorig_RightHand{finger}{idx}'.format(
            finger=finger, idx=bone_idx)
        const = blender.follow_bone(
            arm,
            camera_name,
            bone_name=bone_name,
            track_axis='z',
            track_axis_neg=True,
            up_axis='y')

        # Randomly pick background
        bg_name = random.choice(bg_names)
        bg_img = bpy.data.images.load(bg_name)

        filename = fileprefix + '{idx}-'.format(idx=render_idx)
        blender.set_cycle_nodes(
            scene,
            background_img=bg_img,
            filename=filename,
            segm=True,
            segm_folder=segm_folder,
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
            spot.node_tree.nodes['Emission'].inputs[
                1].default_value = spot_value

            file_template = fileprefix
        blender.render_frames(
            scene,
            cam,
            arm,
            folders,
            bone_names,
            file_template=file_template,
            rendering_idx=render_idx)
