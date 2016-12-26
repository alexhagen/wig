import bpy

class blight:
  def __init__(self):
    pass

  def sun(self, location=(10., 10., 10.), strength=10.0):
    # Now add a sun
    lamp_data = bpy.data.lamps.new(name="Sun", type='SUN')
    lamp_data.use_nodes = True
    lamp_data.node_tree.nodes['Emission'].inputs[1].default_value = strength
    lamp_object = bpy.data.objects.new(name="Sun", object_data=lamp_data)
    bpy.context.scene.objects.link(lamp_object)
    lamp_object.location = location
    bpy.ops.object.transform_apply(location=True, scale=True)

    lamp_object.select = True
    bpy.context.scene.objects.active = lamp_object

  def point(self, location=(0., 0., 0.), strength=1.0, name="Point",
            color=(1.0, 1.0, 1.0, 1.)):
    lamp_data = bpy.data.lamps.new(name=name, type='POINT')
    lamp_data.use_nodes = True
    lamp_data.node_tree.nodes['Emission'].inputs[1].default_value = strength
    lamp_object = bpy.data.objects.new(name=name, object_data=lamp_data)
    bpy.context.scene.objects.link(lamp_object)
    lamp_object.location = location
    lamp_object.color = color
    bpy.ops.object.transform_apply(location=True)
    lamp_object.select = True
    bpy.context.scene.objects.active = lamp_object
