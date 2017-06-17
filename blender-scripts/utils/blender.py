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

