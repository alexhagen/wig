import bpy

class brender:
    def __init__(self, filename, objects=None):
        bpy.context.scene.objects.active.select = False
        if objects is not None:
            for object in objects:
                object.object.select = True

        camera = bpy.data.objects["Camera"]
        camera.location = (-180., -180., 120.)
        bpy.data.cameras[camera.name].clip_end = 1000.0
        bpy.data.cameras[camera.name].clip_start = 0.0
        camera_track = camera.constraints.new('TRACK_TO')
        camera_track.track_axis = "TRACK_NEGATIVE_Z"
        camera_track.up_axis = "UP_Y"
        camera_track.target = bpy.data.objects["sphere"]
        bpy.ops.object.visual_transform_apply()
        bpy.data.scenes["Scene"].render.engine = 'CYCLES'
        bpy.data.scenes["Scene"].render.filepath = filename + '.png'
        bpy.context.scene.render.use_freestyle = True
        bpy.context.scene.cycles.use_progressive_refine = True
        bpy.context.scene.cycles.samples = 50
        bpy.context.scene.cycles.max_bounces = 16
        bpy.context.scene.cycles.min_bounces = 3
        bpy.context.scene.cycles.glossy_bounces = 4
        bpy.context.scene.cycles.transmission_bounces = 16
        bpy.context.scene.cycles.volume_bounces = 4
        bpy.context.scene.cycles.transparent_max_bounces = 16
        bpy.context.scene.cycles.transparent_min_bounces = 8
        bpy.context.scene.cycles.filter_glossy = 0.05
        # bpy.context.scene.cycles.caustics_reflective = False
        # bpy.context.scene.cycles.caustics_refractive = False
        bpy.ops.render.render( write_still=True )
