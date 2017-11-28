import argparse
import os
import random
import sys

import bpy
from importlib import reload

import argutils  # Requires myana to be in PYTHONPATH

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
    '--root',
    type=str,
    default='data/blender-renders/debug',
    help='Path to dataset root folder')
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
    '--hands',
    action='store_true',
    help='Whether to randomly position camera on sphere around hand')
parser.add_argument(
    '--radius',
    type=float,
    default='0.5',
    help='Radius when camera is randomly positioned on sphere')
parser.add_argument(
    '--resolution',
    type=int,
    default=40,
    help=
    'Percentage for rendering resulution (the lower, the smaller the image)')
parser.add_argument(
    '--background_folder',
    type=str,
    help='Path to folder containing the backgrounds')
parser.add_argument(
    '--render_nb', type=int, default=10, help='Number of frames to render')
parser.add_argument(
    '--lsun', action='store_true', help='Using gül"s LSUN dataset')
parser.add_argument(
    '--focal_min', type=int, default=15, help='Min camera focal length')
parser.add_argument(
    '--focal_max', type=int, default=25, help='Max camera focal length')
parser.add_argument(
    '--no_render', action='store_true', help='Deactivate rendering')

args, _ = parser.parse_known_args(script_args)
argutils.print_args(args)

# Set appropriate folders for data creation
# Rendered data folderes
rgb_folder = os.path.join(args.root, 'rgb')
depth_folder = os.path.join(args.root, 'depth')
depthpng_folder = os.path.join(args.root, 'depthpng')

# Annotation data folders
coord_2d_folder = os.path.join(args.root, '2Dcoord')
coord_3d_folder = os.path.join(args.root, '3Dcoord')

segm_folder = os.path.join(args.root, 'segm')

folders = {
    'rgb': rgb_folder,
    'depth': depth_folder,
    'depthpng': depthpng_folder,
    'coord_2d': coord_2d_folder,
    'coord_3d': coord_3d_folder,
    'segm': segm_folder
}

arm = bpy.data.objects['Armature']
scene = bpy.context.scene
scene.render.resolution_percentage = args.resolution

# Hand bone name variables
hand_sides = ['right', 'left']
fingers = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
bone_idxs = ['1', '2', '3', '4']
right_bone_names = [
    'mixamorig_RightHand{0}{1}'.format(finger, idx)
    for finger in fingers for idx in bone_idxs
]
right_bone_names.append('mixamorig_RightHand')

left_bone_names = [
    'mixamorig_LeftHand{0}{1}'.format(finger, idx)
    for finger in fingers for idx in bone_idxs
]
left_bone_names.append('mixamorig_LeftHand')

actions = [
    'PlayGuitar', 'PickupObject', 'SittingThumbsUp', 'BangFist', 'Count',
    'Piano', 'Beckoning'
]
spots = ['Spot1', 'Spot2', 'Spot3']
spot_values = [0, 200, 400, 800, 1000]
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
trimmed_suffix = '-trimmed'
fileprefix = args.person + (trimmed_suffix if args.trimmed else '')
print('fileprefix : {}'.format(fileprefix))

for render_idx in range(args.render_nb):
    # Pick hand
    hand_side = random.choice(hand_sides)
    if hand_side == 'right':
        bone_names = right_bone_names
    if hand_side == 'left':
        bone_names = left_bone_names

    # Set camera
    if args.hands:
        camera_name = camera_names[0]
        obj_cam = bpy.data.objects[camera_name]
    else:
        camera_name = random.choice(camera_names)
        obj_cam = bpy.data.objects[camera_name]

    # Randomly set focal length between bounds
    cam_cam = bpy.data.cameras[obj_cam.name]
    cam_cam.lens = random.randint(args.focal_min, args.focal_max)

    # Clear camera constraints
    for const in obj_cam.constraints:
        obj_cam.constraints.remove(const)
    # Camera follows hand
    finger = random.choice(fingers)
    bone_idx = random.choice(bone_idxs)
    bone_name = 'mixamorig_{hand_side}Hand{finger}{idx}'.format(
        hand_side=hand_side.title(), finger=finger, idx=bone_idx)

    # Randomly pick background
    bg_name = random.choice(bg_names)
    bg_img = bpy.data.images.load(bg_name)

    filename = fileprefix + '{idx}-'.format(idx=render_idx)
    blender.set_cycle_nodes(
        scene,
        background_img=bg_img,
        filename=filename,
        segm=True,
        segm_folder=folders['segm'],
        segm_mats=['Bodymat'],
        depth_folder=folders['depth'])

    # Randomly pick action
    action_name = random.choice(actions)
    action = bpy.data.actions[action_name]
    arm.animation_data.action = action

    const = blender.follow_bone(
        arm,
        obj_cam.name,
        bone_name=bone_name,
        track_axis='z',
        track_axis_neg=True,
        up_axis='y')
    # Randomly change light emission of spots
    for spot_name in spots:
        spot = bpy.data.lamps[spot_name]
        spot_value = random.choice(spot_values)
        spot.node_tree.nodes['Emission'].inputs[1].default_value = spot_value

        file_template = fileprefix
    if args.no_render is False:
        blender.render_frames(
            scene,
            obj_cam,
            arm,
            folders,
            hand_side=hand_side,
            bone_names=bone_names,
            file_template=file_template,
            rendering_idx=render_idx,
            args=args)
