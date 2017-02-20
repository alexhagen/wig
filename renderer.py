import subprocess
class renderer:
    def __init__(self, filename):
        self.filename = filename + '_blend'
        self.render = "brender('%s')\n" % (self.filename) + \
            "bpy.ops.wm.save_as_mainfile(filepath=%s.blend)" % (self.filename)
        self.header = "import bpy\n" + \
            "from mcnp_companion.mcnp_companion.blender_matl import bmatl\n" + \
            "from mcnp_companion.mcnp_companion.blender_render import brender\n" + \
            "from mcnp_companion.mcnp_companion.blender_light import blight\n" + \
            "from mcnp_companion.mcnp_companion.blender_scene import bscene\n" + \
            "from mcnp_companion.mcnp_companion.blender_geo import bgeo\n" + \
            "\n" + \
            "scene = bscene()\n"
        self.matl = ''
        self.geo = ''

    def run(self):
        with open(self.filename + '.py', 'w') as f:
            f.write(self.header)
            f.write(self.matl)
            f.write(self.geo)
            f.write(self.render)
        subprocess.Popen(['blender --python=%s --background' % \
            (self.filename + '.py')], shell=True)

    def add_geo(self, str):
        self.geo += "%s\n" % str

    def add_matl(self, str):
        self.matl += "%s\n" % str
