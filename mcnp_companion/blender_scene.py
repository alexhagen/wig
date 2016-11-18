import bpy

class bscene:
    def __init__(self):
        self.scene = bpy.context.scene

        # First, delete the default cube
        bpy.ops.object.delete()
