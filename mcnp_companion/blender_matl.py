import bpy

class bmatl:
    def __init__(self):
        pass

    def flat(self, name="Flat", color=(1.0, 1.0, 1.0)):
        flat = bpy.data.materials.new(name)
        flat.diffuse_color = color
        self.matl = flat
        return self

    def concrete(self, scale=10.0):
        concrete = bpy.data.materials.new("Concrete")
        concrete.use_nodes = True
        nodes = concrete.node_tree.nodes
        for key in nodes.values():
            nodes.remove(key)
        links = concrete.node_tree.links
        v1 = nodes.new("ShaderNodeTexVoronoi")
        v1.coloring = "INTENSITY"
        v1.inputs[1].default_value = scale * 1.0

        v2 = nodes.new("ShaderNodeTexVoronoi")
        v2.coloring = "CELLS"
        v2.inputs[1].default_value = scale * 50.0

        v3 = nodes.new("ShaderNodeTexVoronoi")
        v3.coloring = "CELLS"
        v3.inputs[1].default_value = scale * 100.0

        v4 = nodes.new("ShaderNodeTexVoronoi")
        v4.coloring="INTENSITY"
        v4.inputs[1].default_value = scale * 5.0

        v5 = nodes.new("ShaderNodeTexVoronoi")
        v5.coloring = "CELLS"
        v5.inputs[1].default_value = scale * 200.0

        v6 = nodes.new("ShaderNodeTexVoronoi")
        v6.coloring = "CELLS"
        v6.inputs[1].default_value = scale * 75.0

        m1 = nodes.new("ShaderNodeMixRGB")
        m1.blend_type = "BURN"

        m2 = nodes.new("ShaderNodeMixRGB")
        m2.blend_type = "BURN"

        links.new(v1.outputs[1], m1.inputs[0])
        links.new(v2.outputs[1], m1.inputs[1])
        links.new(v3.outputs[1], m1.inputs[2])

        links.new(v4.outputs[1], m2.inputs[0])
        links.new(v5.outputs[1], m2.inputs[1])
        links.new(v6.outputs[1], m2.inputs[2])

        m3 = nodes.new("ShaderNodeMixRGB")
        m3.blend_type = "MIX"

        links.new(m1.outputs[0], m3.inputs[1])
        links.new(m2.outputs[0], m3.inputs[2])

        f = nodes.new("ShaderNodeFresnel")
        f.inputs[0].default_value = 4.0

        d = nodes.new("ShaderNodeBsdfDiffuse")
        links.new(m3.outputs[0], d.inputs[0])

        g = nodes.new("ShaderNodeBsdfGlossy")
        g.inputs[1].default_value = 0.40
        links.new(m3.outputs[0], g.inputs[0])

        m4 = nodes.new("ShaderNodeMixShader")
        links.new(f.outputs[0], m4.inputs[0])
        links.new(d.outputs[0], m4.inputs[1])
        links.new(g.outputs[0], m4.inputs[2])

        v7 = nodes.new("ShaderNodeTexVoronoi")
        v7.coloring = "INTENSITY"
        v7.inputs[1].default_value = 1000.0

        i = nodes.new("ShaderNodeInvert")
        links.new(v7.outputs[1], i.inputs[0])

        output = nodes.new("ShaderNodeOutputMaterial")
        links.new(m4.outputs[0], output.inputs[0])
        links.new(i.outputs[0], output.inputs[2])
        self.mat_out = output
        self.matl = concrete
        self.nodes = nodes
        self.links = links
        return self

    def water(self):
        water = bpy.data.materials.new("Water")
        water.use_nodes = True
        nodes = water.node_tree.nodes
        for key in nodes.values():
            nodes.remove(key)
        links = water.node_tree.links
        ########
        # Shader
        # make a fresnel node
        fresnel = nodes.new(type='ShaderNodeFresnel')
        # set its ior to 1.050
        fresnel.inputs[0].default_value = 1.050
        # make a refraction node
        s_ref_bsdf = nodes.new(type='ShaderNodeBsdfRefraction')
        # set the fresnel nodes output to the ior of the refraction node
        links.new(fresnel.outputs[0], s_ref_bsdf.inputs[2])
        # make a glossy node
        s_gloss_bsdf = nodes.new('ShaderNodeBsdfGlass')
        # remove all roughness
        s_gloss_bsdf.inputs[1].default_value = 0.0
        # make a mix shader
        s_mix = nodes.new('ShaderNodeMixShader')
        links.new(s_ref_bsdf.outputs[0], s_mix.inputs[1])
        #links.new(fresnel.outputs[0], s_mix.inputs[0])
        links.new(s_gloss_bsdf.outputs[0], s_mix.inputs[2])
        ##############
        # Displacement
        # Make a voronoi texture
        d_voronoi_1 = nodes.new('ShaderNodeTexVoronoi')
        # set its scale to 40
        d_voronoi_1.inputs[1].default_value = 40.0
        # make a voronoi texture
        d_voronoi_2 = nodes.new('ShaderNodeTexVoronoi')
        # set its scale to 80
        d_voronoi_2.inputs[1].default_value = 80.0
        # make a multiply node
        d_mult_1 = nodes.new('ShaderNodeMath')
        d_mult_1.operation = 'MULTIPLY'
        # set its value to 0.70
        d_mult_1.inputs[1].default_value = 0.7
        # link the second voronoi Fac output to Multiply value input
        links.new(d_voronoi_2.outputs[1], d_mult_1.inputs[0])
        # Make an add node
        d_add = nodes.new('ShaderNodeMath')
        d_add.operation = 'ADD'
        # link the first voronoi fac output to the first value input
        links.new(d_voronoi_1.outputs[1], d_add.inputs[0])
        # link the first multiply node ouput to the second value input
        links.new(d_mult_1.outputs[0], d_add.inputs[1])
        # make another multiply node
        d_mult_2 = nodes.new('ShaderNodeMath')
        d_mult_2.operation = 'MULTIPLY'
        # set its second value to -0.2
        d_mult_2.inputs[1].default_value = -0.2
        # link the add node's output to the first value input
        links.new(d_add.outputs[0], d_mult_2.inputs[0])
        # Make a material output
        material_output = nodes.new('ShaderNodeOutputMaterial')
        # link from the sahder and displacement groups to the outputs
        links.new(s_mix.outputs[0], material_output.inputs[0])
        links.new(d_mult_2.outputs[0], material_output.inputs[2])
        for node in nodes:
            node.update()
        self.mat_out = material_output
        self.nodes = nodes
        self.links = links
        self.matl = water
        return self


    def source(self):
        source = bpy.data.materials.new("Source")
        source.use_nodes = True
        nodes = source.node_tree.nodes
        for key in nodes.values():
            nodes.remove(key)
        links = source.node_tree.links
        #
        e = nodes.new(type='ShaderNodeEmission')
        print(e.inputs.items())
        e.inputs[0].default_value = (0.1797, 0.6836, 0.6406, 1.)
        e.inputs[1].default_value = 0.1
        # Make a material output
        material_output = nodes.new('ShaderNodeOutputMaterial')
        # link from the shader and displacement groups to the outputs
        links.new(e.outputs[0], material_output.inputs[0])
        for node in nodes:
            node.update()
        self.mat_out = material_output
        self.nodes = nodes
        self.links = links
        self.matl = source
        return self

    def cutaway(self):
        nodes = self.nodes
        links = self.links
        material_output = self.mat_out
        g = nodes.new(type='ShaderNodeTexCoord')

        srgb = nodes.new(type='ShaderNodeSeparateXYZ')

        links.new(g.outputs[0], srgb.inputs[0])
        gt = nodes.new(type='ShaderNodeMath')
        gt.operation = 'LESS_THAN'
        gt.inputs[1].default_value = 0.5
        links.new(srgb.outputs[1], gt.inputs[0])
        input_matl = material_output.inputs[0].links[0].from_node
        t = nodes.new(type='ShaderNodeBsdfTransparent')
        m2 = nodes.new(type='ShaderNodeMixShader')
        links.new(gt.outputs[0], m2.inputs[0])
        links.new(input_matl.outputs[0], m2.inputs[1])
        links.new(t.outputs[0], m2.inputs[2])
        # link from the shader and displacement groups to the outputs
        links.new(m2.outputs[0], material_output.inputs[0])
        self.nodes = nodes
        self.links = links
        self.matl = self.matl
        return self
