import bpy

def applyIKConstraint (target, bone, pole):
    constraint = bone.constraints.new("IK")
    constraint.target = bpy.context.view_layer.objects.active
    constraint.subtarget = target.name
    constraint.pole_target = bpy.context.view_layer.objects.active
    constraint.pole_subtarget = pole.name
    
    constraint.chain_count = 2
    constraint.pole_angle = 180
    

selected_bones = bpy.context.selected_pose_bones

target = None
bone = None
pole = None

for bone in selected_bones:
    bone_name = bone.name
    if (bone_name.find("_pole") != -1):
        pole = bone
    if (bone_name.find("_target") != -1):
        target = bone

selected_bones.remove(target)
selected_bones.remove(pole)

bone = selected_bones[0]

applyIKConstraint(target=target, bone=bone, pole=pole)