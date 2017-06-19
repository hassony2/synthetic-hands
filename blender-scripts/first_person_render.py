import bpy
from bpy_extras.object_utils import world_to_camera_view
from importlib import reload
import numpy as np
import sys

sys.path.insert(
    0, "/home/local2/yhasson/first-person-action-recognition/blender-scripts")

from settings import params
from utils import blender
from utils import filesys

# Insure modules are reloaded in blender
reload(blender)
reload(filesys)

render = True

scene = bpy.context.scene
cam = bpy.context.scene.camera
armature = bpy.data.objects["Armature"]

folders = params["folders"]
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


blender.set_cycle_nodes(scene, background_img,
                        segm=True, segm_folder=segm_folder,
                        segm_mats=['Material.003', 'mia_material_x2SG'],
                        depth_folder=depth_folder)

if render:
    # Render frames
    frame_beg = scene.frame_start
    frame_end = scene.frame_end
    # camera_names = ['Headcam', 'Chestcam']
    camera_names = ['Headcam']
    for camera_name in camera_names:
        for frame_nb in range(frame_beg, frame_end + 1):
            scene.frame_set(frame_nb)
            cam = bpy.context.scene.objects[camera_name]
            bpy.context.scene.camera = cam
            # Render
            scene.render.filepath = rgb_folder + \
                'render-' + camera_name + str(frame_nb)
            scene.render.image_settings.file_format = 'PNG'
            bpy.ops.render.render(write_still=True)

            # Save coordinates
            side = "Right"
            coords_2d = np.empty((bone_nb, 2))
            coords_3d = np.empty((bone_nb, 3))
            position = 0

            # Save 2D coordinates
            finger_names = []
            for finger in fingers:
                for bone_idx in bone_idxs:
                    finger_tip_name = "mixamorig:{side}Hand{finger}{bone_idx}".format(side=side,
                                                                                      finger=finger,
                                                                                      bone_idx=bone_idx)
                    finger_names.append(finger_tip_name)

            coords_2d, coords_3d = blender.coordinates(
                scene, cam, armature, finger_names)
            annot_file_2d = coord_2d_folder + \
                camera_name + str(frame_nb) + "_2d.txt"
            annot_file_3d = coord_3d_folder + \
                camera_name + str(frame_nb) + "_3d.txt"
            np.savetxt(annot_file_2d, coords_2d)
            np.savetxt(annot_file_3d, coords_3d)
            print("processed frame ", frame_nb)
            # REMOVE ME
            break
            # REMOVE ME
