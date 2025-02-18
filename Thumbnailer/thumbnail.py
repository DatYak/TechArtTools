import bpy
from math import radians, degrees

bg_path = "//background.png"
square_resolution = 512

def take_screencapture(output_dir, focal_object):

    #Deselect All
    bpy.ops.object.select_all(action='DESELECT')

    scene = bpy.context.scene
    comp = scene.node_tree

    render_settings = bpy.context.scene.render
    oldResolution = [render_settings.resolution_x, render_settings.resolution_y]
    render_settings.resolution_x = square_resolution
    render_settings.resolution_y = square_resolution

    #Compositor
    if (comp.nodes.get("IconBG") == None):
        image_node = comp.nodes.new(type="CompositorNodeImage")
        image_node.image = bpy.data.images.load(bpy.path.abspath(bg_path))
        image_node.name = "IconBG"
    else:
        image_node = comp.nodes.get("IconBG")

    if (comp.nodes.get("IconAlpha")== None):
        alpha_node = comp.nodes.new(type="CompositorNodeAlphaOver")
        alpha_node.name = "IconAlpha"
    else:
        alpha_node = comp.nodes.get("IconAlpha")
        
    comp.links.new(comp.nodes["Render Layers"].outputs["Image"], alpha_node.inputs[2])
    comp.links.new(image_node.outputs["Image"], alpha_node.inputs[1])
    comp.links.new(alpha_node.outputs["Image"], comp.nodes["Composite"].inputs["Image"])

    #Light
    light_data = bpy.data.lights.new(name="Icon Light", type="SUN")
    light_data.energy = 10
    light_object = bpy.data.objects.new(name="icon_sun", object_data=light_data)
    bpy.context.collection.objects.link(light_object)
    
    #make it active 
    bpy.context.view_layer.objects.active = light_object

    #change rotation
    light_object.rotation_euler = (radians(60), radians(30), 0)
            

    #Camera
    camera_data = bpy.data.cameras.new(name="Icon Camera")
    camera_object = bpy.data.objects.new(name="icon_camera",object_data=camera_data)
    bpy.context.collection.objects.link(camera_object)

    #make it active
    bpy.context.view_layer.objects.active = camera_object
    bpy.context.scene.camera = camera_object

    camera_object.location = ( 7, -7, 2.5)

    camera_look_constraint = camera_object.constraints.new(type="TRACK_TO")
    camera_look_constraint.target = focal_object
    camera_look_constraint.track_axis = 'TRACK_NEGATIVE_Z'
    camera_look_constraint.up_axis = 'UP_Y'

    camera_object.location += focal_object.location

    #Update Scene
    dg = bpy.context.evaluated_depsgraph_get() 
    dg.update()

    bpy.context.scene.render.film_transparent = True 
    bpy.context.scene.render.filepath = output_dir
    bpy.ops.render.render(write_still = True)

    #Restore prior settings
    render_settings.resolution_x = oldResolution[0]
    render_settings.resolution_y = oldResolution[1]

    #remove added camera/lights
    bpy.ops.object.select_all(action='DESELECT')
    light_object.select_set(True)
    camera_object.select_set(True)
    bpy.ops.object.delete()

# Get the selected objects
selected_objects = bpy.context.selected_objects

# Check if there are any selected objects
if selected_objects:
    # Get all objects in the scene
    all_objects = bpy.data.objects

    # Hide all objects
    for obj in all_objects:
        obj.hide_render = True

    for subject in selected_objects:
        subject.hide_render = False
        fileName = subject.name
        take_screencapture(bpy.path.abspath("//" + fileName + "_Icon512"), subject)
        subject.hide_render = True

    #Re-show objects
    for obj in bpy.data.objects:
        obj.hide_render = False