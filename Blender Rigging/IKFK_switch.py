import bpy

def add_ik_constraint (target_name, bone, pole_name):
    constraint = bone.constraints.new("IK")
    constraint.target = bpy.context.view_layer.objects.active
    constraint.subtarget = target_name
    constraint.pole_target = bpy.context.view_layer.objects.active
    constraint.pole_subtarget = pole_name
    
    constraint.chain_count = 2
    constraint.pole_angle = 180

def add_copy_transform(bone_name, prefix, target_name, influence):
    armature = bpy.context.view_layer.objects.active
    bone = armature.pose.bones[bone_name]
    constraint = bone.constraints.new('COPY_TRANSFORMS')
    constraint.target = armature
    constraint.subtarget = prefix + '_' + target_name
    constraint.influence = influence
    constraint.name = prefix + '_COPY'

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

def main():
    bpy.ops.object.mode_set(mode='EDIT')
    armature = bpy.context.view_layer.objects.active
    base_bone = bpy.context.selected_editable_bones[0]
    bone_chain = []

    # Add three bones in total: Shoulder, Elbow, and Wrist
    bone_chain.append(base_bone)
    current = base_bone
    for i in range(2):
        current = current.children[0]
        bone_chain.append(current)

    copy_rename_bones(armature, bone_chain, "FK_")
    copy_rename_bones(armature, bone_chain, "IK_")

    bpy.ops.object.mode_set(mode='POSE')

    for bone in bone_chain:
        add_copy_transform(bone.name, 'FK', bone.name, 1)
        add_copy_transform(bone.name, 'IK', bone.name, 0)
    
    root_bone = bpy.context.object.pose.bones['ROOT']
    root_bone['IKFK_Switch'] = 1.0
    id_props = root_bone.id_properties_ui('IKFK_Switch')
    id_props.update(min=0, max=1)
    root_bone.property_overridable_library_set('["IKFK_Switch"]', True)


    for edit_bone in bone_chain:
        bone = bpy.context.object.pose.bones[edit_bone.name]
        ik_curve = bone.constraints['IK_COPY'].driver_add('influence')
        ik_driver = ik_curve.driver
        fk_curve = bone.constraints['FK_COPY']

        ik_driver.type = 'SCRIPTED'
        ik_driver.expression = 'IKFK_Switch'

        v = ik_driver.variables.new()
        v.name = 'IKFK_Switch'

        t = v.targets[0]
        t.id_type = 'OBJECT'
        t.id = bpy.data.objects[armature.name]
        t.data_path = 'pose.bones["ROOT"]["IKFK_Switch"]'

main()