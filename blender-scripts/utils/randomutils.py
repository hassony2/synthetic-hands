import bpy
import math
from mathutils import Vector
import random


def move_on_sphere(obj, arm, center_bone, radius=1):
    """Moves the obj to a random point on the sphere of center center
    with given radius
    """

    obj.parent = None
    phi_deg = random.randint(0, 180)
    phi = math.radians(phi_deg)
    theta_deg = random.randint(0, 360)
    theta = math.radians(theta_deg)

    x = radius * math.sin(phi) * math.cos(theta)
    y = radius * math.sin(phi) * math.sin(theta)
    z = radius * math.cos(phi)

    hand_location_rel = center_bone.location
    hand_location = arm.matrix_world * center_bone.matrix * hand_location_rel
    old_x, old_y, old_z = hand_location
    new_x, new_y, new_z = old_x + x, old_y + y, old_z + z
    obj.location = Vector((new_x, new_y, new_z))
