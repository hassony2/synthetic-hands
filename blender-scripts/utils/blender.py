import bpy
from bpy_extras.object_utils import world_to_camera_view
import numpy as np
import random

from utils.debug import timeit


def coordinates(scene, cam, armature, keypoint_bones, use_tail=False):
    """
    :param use_tail: to use tail instead of head as bone keypoint
    """
    bone_nb = len(keypoint_bones)
    coords_2d = np.empty((bone_nb, 2))
    coords_3d = np.empty((bone_nb, 3))
    for i, bone_name in enumerate(keypoint_bones):
        bone = armature.pose.bones[bone_name]
        if use_tail:
            coord_3d = armature.matrix_world * bone.tail
        else:
            coord_3d = armature.matrix_world * bone.head
        coord_2d = list(world_to_camera_view(scene, cam, coord_3d))
        coords_3d[i] = list(coord_3d)
        render_scale = scene.render.resolution_percentage / 100
        x_render = int(scene.render.resolution_x * render_scale)
        y_render = int(scene.render.resolution_y * render_scale)
        coords_2d[i] = [coord_2d[0] *
                        x_render, coord_2d[1] * y_render]
    return coords_2d, coords_3d


@timeit
def render(scene, cam, rgb_folder, img_name):
    """
    Render images according to cycle nodes
    """
    scene.camera = cam
    scene.render.filepath = rgb_folder + img_name
    scene.render.image_settings.file_format = 'PNG'
    bpy.ops.render.render(write_still=True)


@timeit
def render_frames(scene, cam, arm, folders,
                  bone_names, file_template="render-{0:04d}",
                  frame_nb=None, rendering_idx=None):
    """
    Renders images and annotations

    :frame_nb: idx of the frame to render, random if None
    """

    if frame_nb is None:
        frame_nbs = list(range(scene.frame_start, scene.frame_end + 1))
        frame_nb = random.choice(frame_nbs)
    scene.frame_set(frame_nb)
    bpy.context.scene.camera = cam

    # Render images
    suffix = "{0:04d}".format(frame_nb)
    if rendering_idx is not None:
        suffix = str(rendering_idx) + "-" + suffix
    img_name = file_template + suffix
    render(scene, cam, folders['rgb'], img_name)

    # Save coordinates
    coords_2d, coords_3d = coordinates(
        scene, cam, arm, bone_names)
    annot_file_2d = folders['coord_2d'] + img_name + ".txt"
    annot_file_3d = folders['coord_3d'] + img_name + ".txt"
    np.savetxt(annot_file_2d, coords_2d)
    np.savetxt(annot_file_3d, coords_3d)

@timeit
def follow_bone(armature, camera_name="Camera",
                bone_name="mixamorig_RightHandMiddle4",
                track_axis=None, track_axis_neg=False,
                up_axis=None):
    cam = bpy.context.scene.objects[camera_name]
    track_bone = cam.constraints.new('TRACK_TO')
    track_bone.target = armature
    if track_axis:
        if track_axis_neg:
            track_bone.track_axis = 'TRACK_NEGATIVE_' + track_axis.upper()
        else:
            track_bone.track_axis = 'TRACK_' + track_axis.upper()
    if up_axis:
        track_bone.up_axis = 'UP_' + up_axis.upper()
    track_bone.subtarget = bone_name
    return track_bone


@timeit
def set_cycle_nodes(scene, background_img, filename,
                    segm=True, segm_folder=None,
                    segm_mats=[],
                    depth_folder=None):
    """
    :param scene: blender scene
    :param background_img: blender image
    :param segm_mats: list of names in blender of materials to segment
    """

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
    depth_node.file_slots[0].path = filename
    depth_node.location = 200, 0
    node_tree.links.new(render_node.outputs['Z'], depth_node.inputs[0])

    # Add segmentation
    # Activate 'IndexMA' output for render layer
    if segm:
        scene.render.layers['RenderLayer'].use_pass_material_index = True

        # Set material index
        for i, mat in enumerate(segm_mats):
            body_mat = bpy.data.materials[mat]
            body_mat.pass_index = i + 1

        # Add material index render int (<==> segmentation)
        segm_node = node_tree.nodes.new('CompositorNodeOutputFile')
        segm_node.format.file_format = 'OPEN_EXR'
        segm_node.base_path = segm_folder
        segm_node.file_slots[0].path = filename
        segm_node.location = 200, -200
        node_tree.links.new(
            render_node.outputs['IndexMA'], segm_node.inputs[0])
    return segm_node, depth_node
