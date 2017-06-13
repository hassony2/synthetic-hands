import bpy
import math
import random
from mathutils import Vector

bpy.ops.object.mode_set(mode='EDIT')
armature = bpy.data.objects["Armature"]


def new_bone(name, armature, reference,
             parent=None, tail_vector=Vector([0, 10, 0])):
    """
    :param reference: Bone at which tail we place the head of new bone
    :param tail_vector: offset between head and tail
    """
    bpy.ops.object.mode_set(mode='EDIT')
    if not armature.data.edit_bones.get(name):
        new_bone = armature.data.edit_bones.new(name)
    else:
        new_bone = armature.data.edit_bones[name]
    if parent is not None:
        new_bone.parent = parent

    # Position new bone
    new_bone.head = reference.tail
    new_bone.tail = reference.tail + tail_vector
    return new_bone

left_forearm = armature.data.edit_bones["mixamorig:LeftForeArm"]
left_shoulder = armature.data.edit_bones["mixamorig:LeftShoulder"]
left_hand_ik_bone = new_bone('LeftHandIK', armature=armature, reference=left_forearm,
                             parent=left_shoulder, tail_vector=Vector([0, 20, 0]))


right_forearm = armature.data.edit_bones["mixamorig:RightForeArm"]
right_shoulder = armature.data.edit_bones["mixamorig:RightShoulder"]
right_hand_ik_bone = new_bone('RightHandIK', armature=armature, reference=right_forearm,
                              parent=right_shoulder, tail_vector=Vector([0, 20, 0]))


def add_ik_chain(armature, tail_ik_bone, target_ik_bone_name,
                 ik_chain_length=1, ik_name='IK'):
    bpy.ops.object.mode_set(mode='POSE')
    # Add IK constraint
    ik_constraint = tail_ik_bone.constraints.new('IK')
    ik_constraint.name = ik_name
    ik_constraint.target = armature
    ik_constraint.subtarget = target_ik_bone_name
    ik_constraint.chain_count = ik_chain_length
    ik_constraint.lock_rotation_y = True
    ik_constraint.lock_rotation_z = True
    ik_constraint.owner_space = 'LOCAL'


pose_left_forearm = armature.pose.bones["mixamorig:LeftForeArm"]
add_ik_chain(armature, tail_ik_bone=pose_left_forearm,
             target_ik_bone_name='LeftHandIK', ik_chain_length=2)

pose_right_forearm = armature.pose.bones["mixamorig:RightForeArm"]
add_ik_chain(armature, tail_ik_bone=pose_right_forearm,
             target_ik_bone_name='RightHandIK', ik_chain_length=2)


def set_parent(armature, child_name, parent_name=None):
    """
    child and parent being bones of armature
    Sets parent of child_name to bone parent_name
    """
    bpy.ops.object.mode_set(mode='EDIT')
    child = armature.data.edit_bones[child_name]
    if parent_name is not None:
        parent = armature.data.edit_bones[parent_name]
    else:
        parent = None
    child.parent = parent


def limit_rotation(bone, limits={"x":[0, 0], "y":[0, 0], "z":[0, 0]}):
    """
    Limits rotation on axis limiting the angles (in degrees)
    """
    bpy.ops.object.mode_set(mode='POSE')
    constraint = bone.constraints.new('LIMIT_ROTATION')
    for axis, limit in limits.items():
        if axis == 'x':
            constraint.use_limit_x = True
            constraint.min_x = math.radians(limit[1])
            constraint.max_x = math.radians(limit[0])
        if axis == 'y':
            constraint.use_limit_y = True
            constraint.min_y = math.radians(limit[0])
            constraint.max_y = math.radians(limit[1])
        if axis == 'z':
            constraint.use_limit_z = True
            constraint.min_z = math.radians(limit[0])
            constraint.max_z = math.radians(limit[1])
    constraint.owner_space = 'LOCAL'


angle_constraints = {1: [0, 90], 2: [-5, 120], 3: [-10, 50]}
for side in ["Left", "Right"]:
    hand_name = "mixamorig:{side}Hand".format(side=side)
    for finger in ["Thumb", "Index", "Middle", "Ring", "Pinky"]:
        finger_tip_name = "mixamorig:{side}Hand{finger}3".format(
            side=side, finger=finger)
        finger_tip = armature.pose.bones.get(finger_tip_name)
        ik_target_name = "mixamorig:{side}Hand{finger}4".format(
            side=side, finger=finger)
        set_parent(armature, child_name=ik_target_name,
                   parent_name=hand_name)
        add_ik_chain(armature, tail_ik_bone=finger_tip,
                     target_ik_bone_name=ik_target_name, ik_chain_length=3)

        if finger != "Thumb":
            finger_base_name = "mixamorig:{side}Hand{finger}1".format(
                side=side, finger=finger)
            finger_base = armature.pose.bones[finger_base_name]
            limit_rotation(finger_base, limits={"z": [0, 0], "y": [-5, 5]})
