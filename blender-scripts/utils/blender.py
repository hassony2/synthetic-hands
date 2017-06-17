import bpy

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


def set_cycle_nodes(scene, params, background_img):
    # Get relevant folder paths
    folders = params["folders"]
    depth_folder = folders["depth"]
    segm_folder = folders["segm"]

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

