import bpy
import os

bg_path = "//background.png"
square_resolution = 512

def take_screencapture(output_dir):
    
    scene = bpy.context.scene
    comp = scene.node_tree

    render_settings = bpy.context.scene.render
    oldResolution = [render_settings.resolution_x, render_settings.resolution_y]
    render_settings.resolution_x = square_resolution
    render_settings.resolution_y = square_resolution

    #compositor
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

    bpy.context.scene.render.film_transparent = True 
    bpy.context.scene.render.filepath = output_dir
    bpy.ops.render.render(write_still = True)

    #Restore prior settings
    render_settings.resolution_x = oldResolution[0]
    render_settings.resolution_y = oldResolution[1]

take_screencapture(bpy.path.abspath("//render"))