import bpy
from bpy_extras.object_utils import world_to_camera_view
import numpy as np
import sys

sys.path.insert(
    0, "/home/local2/yhasson/first-person-action-recognition/blender-scripts")

from settings import params
from utils import filesys

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
inp_node.location = -400, 200

scale_node = node_tree.nodes.new(type="CompositorNodeScale")
scale_node.space = "RENDER_SIZE"
scale_node.frame_method = "CROP"
scale_node.location = -200, 200
node_tree.links.new(inp_node.outputs[0], scale_node.inputs[0])

render_node = node_tree.nodes.new(type="CompositorNodeRLayers")
render_node.location = -400, -200

alpha_node = node_tree.nodes.new(type="CompositorNodeAlphaOver")
alpha_node.location = 0, 200
node_tree.links.new(scale_node.outputs[0], alpha_node.inputs[1])
node_tree.links.new(render_node.outputs[0], alpha_node.inputs[2])

comp_node = node_tree.nodes.new(type="CompositorNodeComposite")
comp_node.location = 200, 200
node_tree.links.new(alpha_node.outputs[0], comp_node.inputs[0])

# Add depth
depth_node = node_tree.nodes.new('CompositorNodeOutputFile')
depth_node.format.file_format = 'OPEN_EXR'
depth_node.base_path = depth_folder
depth_node.location = 200, 0
node_tree.links.new(render_node.outputs['Z'], depth_node.inputs[0])

# Add segmentation
# Activate 'IndexMA' output for render layer
scene.render.layers['RenderLayer'].use_pass_material_index = True

# Set material index
body_mat = bpy.data.materials['Material.003']
body_mat.pass_index = 1
mug_mat = bpy.data.materials['mia_material_x2SG']
mug_mat.pass_index = 2

# Add material index renderint (<==> segmentation)
segm_node = node_tree.nodes.new('CompositorNodeOutputFile')
segm_node.format.file_format = 'OPEN_EXR'
segm_node.base_path = segm_folder
segm_node.location = 200, -200
node_tree.links.new(render_node.outputs['IndexMA'], segm_node.inputs[0])

if render:
    # Render frames
    frame_beg = scene.frame_start
    frame_end = scene.frame_end
    # camera_names = ['Headcam', 'Chestcam']
    camera_names = ['Headcam']
    camera_names = ['Camera']

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
