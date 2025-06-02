import bpy

def add_ik_constraint (target_name, bone, pole_name):
    constraint = bone.constraints.new("IK")
    constraint.target = bpy.context.view_layer.objects.active
    constraint.subtarget = target_name
    constraint.pole_target = bpy.context.view_layer.objects.active
    constraint.pole_subtarget = pole_name
    
    constraint.chain_count = 2
    constraint.pole_angle = 180

def add_copy_transform(bone_name, target_name, constraint_name, influence):
    armature = bpy.context.view_layer.objects.active
    bone = armature.pose.bones[bone_name]
    constraint = bone.constraints.new('COPY_TRANSFORMS')
    constraint.target = armature
    constraint.subtarget = target_name
    constraint.influence = influence
    constraint.name = constraint_name

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

    return copied_bones
    

def main():
    bpy.ops.object.mode_set(mode='EDIT')
    armature = bpy.context.view_layer.objects.active
    base_bone = bpy.context.selected_editable_bones[0]
    bone_chain = []
    bone_chain.append(base_bone)
    current = base_bone

    # 2 gets shoulder, elbow, and wrist
    for i in range(2):
        current = current.children[0]
        bone_chain.append(current)

    fk_bones = copy_rename_bones(armature, bone_chain, "FK_")
    ik_bones = copy_rename_bones(armature, bone_chain, "IK_")

    bpy.ops.object.mode_set(mode='POSE')

    for bone in bone_chain:
        add_copy_transform(bone.name, 'FK_' + bone.name, 'FK_COPY', 1)
        add_copy_transform(bone.name, 'IK_' + bone.name, 'IK_COPY', 0)
    
    root_bone = bpy.context.object.pose.bones['ROOT']
    root_bone['IK FK'] = 1.0


main()