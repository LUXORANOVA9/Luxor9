import bpy, math
# Luxor9 optional 3D signal-tunnel pass. Render transparent PNG sequence and composite in Remotion/FFmpeg.
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.resolution_x=720; scene.render.resolution_y=1280; scene.render.resolution_percentage=100
scene.render.fps=30
scene.render.film_transparent=True
scene.render.engine='BLENDER_EEVEE_NEXT'
world=scene.world; world.color=(0.005,0.007,0.008)
bpy.ops.object.camera_add(location=(0,-12,0), rotation=(math.radians(90),0,0))
cam=bpy.context.object; scene.camera=cam; cam.data.lens=48
for i in range(-5,6):
    bpy.ops.mesh.primitive_cube_add(location=(i*0.7,0,0), scale=(0.012,5.5,0.012))
    o=bpy.context.object
    mat=bpy.data.materials.new(f'rail{i}'); mat.diffuse_color=(0.29,0.83,0.82,1); mat.use_nodes=True
    bsdf=mat.node_tree.nodes.get('Principled BSDF'); bsdf.inputs['Base Color'].default_value=(0.29,0.83,0.82,1); bsdf.inputs['Emission Color'].default_value=(0.29,0.83,0.82,1); bsdf.inputs['Emission Strength'].default_value=3
    o.data.materials.append(mat)
cam.location.z=-1; cam.keyframe_insert('location',frame=1); cam.location.z=1; cam.keyframe_insert('location',frame=180)
scene.render.filepath='renders/luxor9_3d_'
