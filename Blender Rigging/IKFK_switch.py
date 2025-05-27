import bpy

def apply_ik_constraint (target, bone, pole):
    constraint = bone.constraints.new("IK")
    constraint.target = bpy.context.view_layer.objects.active
    constraint.subtarget = target.name
    constraint.pole_target = bpy.context.view_layer.objects.active
    constraint.pole_subtarget = pole.name
    
    constraint.chain_count = 2
    constraint.pole_angle = 180
    

#selected_bones = bpy.context.selected_pose_bones

# target = None
# bone = None
# pole = None

# for bone in selected_bones:
#     bone_name = bone.name
#     if (bone_name.find("_pole") != -1):
#         pole = bone
#     if (bone_name.find("_target") != -1):
#         target = bone

def copy_rename_bones(armature, bone_chain, prefix):
    root_bone_name = prefix + bone_chain[0].name
    parent = root_bone_name
    copied_bones = []
    for bone in bone_chain:
        copy_bone = armature.data.edit_bones.new(prefix + bone.name)
        copy_bone.length = bone.length
        copy_bone.matrix = bone.matrix.copy()
        if(parent != copy_bone.name):
            copy_bone.parent = armature.data.edit_bones[parent]
            parent = copy_bone.name
        copied_bones.append(copy_bone)

        return copy_bone
    

def copy_bones(num_links):
    bpy.ops.object.mode_set(mode='EDIT')
    armature = bpy.context.view_layer.objects.active
    root_bone = bpy.context.selected_editable_bones[0]
    bone_chain = []
    bone_chain.append(root_bone)
    for i in range(num_links - 1):
        bone_chain.append(root_bone.children[i])

    fk_bones = copy_rename_bones(armature, bone_chain, "FK_")
    ik_bones = copy_rename_bones(armature, bone_chain, "IK_")


copy_bones(2)