import bpy
from bpy_extras.object_utils import world_to_camera_view
import numpy as np
import sys

root = "/home/local2/yhasson/first-person-action-recognition/"
sys.path.insert(0, root + "blender-scripts/")

from utils import filesys

render = True

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

# Load background image
image_name = "pexels-photo-table-wood.jpeg"
background_folder = data_folder + "/blender-assets/backgrounds/"
background_path = background_folder + image_name
background_img = bpy.data.images.load(background_path)

# Set cycles params
scene.render.engine = 'CYCLES'
scene.cycles.film_transparent = True

# Get node tree
scene.use_nodes = True
node_tree = scene.node_tree

# Remove existing nodes
for n in node_tree.nodes:
    node_tree.nodes.remove(n)

# Create nodes
inp_node = node_tree.nodes.new(type="CompositorNodeImage")
inp_node.image = background_img

scale_node = node_tree.nodes.new(type="CompositorNodeScale")
scale_node.space = "RENDER_SIZE"
scale_node.frame_method = "FIT"
node_tree.links.new(inp_node.outputs[0], scale_node.inputs[0])

render_node = node_tree.nodes.new(type="CompositorNodeRLayers")

alpha_node = node_tree.nodes.new(type="CompositorNodeAlphaOver")
node_tree.links.new(scale_node.outputs[0], alpha_node.inputs[1])
node_tree.links.new(render_node.outputs[0], alpha_node.inputs[2])

comp_node = node_tree.nodes.new(type="CompositorNodeComposite")
node_tree.links.new(alpha_node.outputs[0], comp_node.inputs[0])

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
