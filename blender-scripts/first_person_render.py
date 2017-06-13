import bpy
from bpy_extras.object_utils import world_to_camera_view
import numpy as np
import os

scene = bpy.context.scene
cam = bpy.context.scene.camera
armature = bpy.data.objects["Armature"]

export_folder = '/home/local2/yhasson/blender-assets/Renders/'
image_folder = export_folder + 'Images/'
annot_folder = export_folder + 'Annots/'

# Create folders if they do not exist
def create_if_missing_dir(folder_path):
    directory = os.path.dirname(folder_path)
    if not os.path.exists(directory):
        os.mkdir(directory)

create_if_missing_dir(image_folder)
create_if_missing_dir(annot_folder)

frame_nb = 10
scene.frame_set(frame_nb)

camera_names = ['Headcam', 'Chestcam']

bone_nb = 20
fingers = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
bone_idxs = ['1', '2', '3', '4']

for camera_name in camera_names:
    cam = bpy.context.scene.objects[camera_name]
    bpy.context.scene.camera = cam
    # Render
    scene.render.filepath = image_folder + \
        'render-' + camera_name + str(frame_nb)
    scene.render.image_settings.file_format = 'PNG'
    bpy.ops.render.render(write_still=True)

    # Save coordinates
    side = "Right"
    coords_2d = np.empty((bone_nb, 2))
    coords_3d = np.empty((bone_nb, 3))
    position = 0
    for finger in fingers:
        for bone_idx in bone_idxs:
            finger_tip_name = "mixamorig:{side}Hand{finger}{bone_idx}".format(side=side,
                                                                              finger=finger,
                                                                              bone_idx=bone_idx)
            finger_bone = armature.pose.bones[finger_tip_name]
            coord_3d = armature.matrix_world * finger_bone.tail
            coord_2d = list(world_to_camera_view(scene, cam, coord_3d))
            coords_3d[position] = list(coord_3d)
            render_scale = scene.render.resolution_percentage / 100
            x_render = int(scene.render.resolution_x * render_scale)
            y_render = int(scene.render.resolution_y * render_scale)
            coords_2d[position] = [coord_2d[0] *
                                   x_render, coord_2d[1] * y_render]
            position += 1
    annot_file_2d = annot_folder + camera_name + "2d_" +str(frame_nb) + ".txt"
    annot_file_3d = annot_folder + camera_name + "3d_" + str(frame_nb) + ".txt"
    np.savetxt(annot_file_2d, coords_2d)
    np.savetxt(annot_file_3d, coords_3d)
    print(coords_2d)
    print(coords_3d)
    print(position)
