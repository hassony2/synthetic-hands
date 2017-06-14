import bpy
from bpy_extras.object_utils import world_to_camera_view
import numpy as np
import sys

root = "/home/local2/yhasson/first-person-action-recognition/"
sys.path.insert(0, root + "blender-scripts/")

from utils import filesys



scene = bpy.context.scene
cam = bpy.context.scene.camera
armature = bpy.data.objects["Armature"]

data_folder = root + "data/"
export_folder = data_folder + "blender-renders/"
image_folder = export_folder + 'Images/'
annot_folder = export_folder + 'Annots/'

filesys.create_dir(image_folder)
filesys.create_dir(annot_folder)



bone_nb = 20
fingers = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
bone_idxs = ['1', '2', '3', '4']

image_name =  "pexels-photo-table-wood.jpeg"
# Load background image
background_folder= data_folder + "/blender-assets/backgrounds/"
background_path = background_folder + image_name
background_img = bpy.data.images.load(background_path)

scene.world.use_nodes = True
world = scene.world
node_tree = bpy.data.worlds[world.name].node_tree

# Create or retrive environment texture node
env_node = node_tree.nodes.get("Environment Texture")
if env_node is None:
    env_node = node_tree.nodes.new(type="ShaderNodeTexEnvironment")
    back_node = node_tree.nodes["Background"]

    # Move new node
    env_node.location.x = back_node.location.x - 300
    env_node.location.y = back_node.location.y

    # Link to background node
    env_col_out = env_node.outputs['Color']
    back_col_in = back_node.inputs['Color']
    node_tree.links.new(env_col_out, back_col_in)

# Set image
env_node.image = background_img

# Render frames
frame_beg = scene.frame_start
frame_end = scene.frame_end
camera_names = ['Headcam', 'Chestcam']

for camera_name in camera_names:
    for frame_nb in range(frame_beg, frame_end + 1):
        scene.frame_set(frame_nb)
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
        annot_file_2d = annot_folder + camera_name + str(frame_nb) + "_2d.txt"
        annot_file_3d = annot_folder + camera_name + str(frame_nb) + "_3d.txt"
        np.savetxt(annot_file_2d, coords_2d)
        np.savetxt(annot_file_3d, coords_3d)
        print("processed frame ", frame_nb)
