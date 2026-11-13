from pathlib import Path
import bpy
import math
import json
from mathutils import Vector
import sys

HERE=Path(__file__).parent
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
MODE=args[0] if args else 'assembly'
PREVIEW='--preview' in args
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.device='CPU'
scene.cycles.samples=16 if PREVIEW else 64
scene.cycles.adaptive_threshold=0.04
scene.cycles.use_denoising=True
scene.render.resolution_x=1000 if PREVIEW else 2000
scene.render.resolution_y=1000 if PREVIEW else 2000
scene.render.resolution_percentage=100
scene.render.film_transparent=True
scene.render.image_settings.file_format='PNG'
scene.render.image_settings.color_mode='RGBA'
scene.view_settings.view_transform='AgX'
scene.world.color=(0.32,0.32,0.32)

def material(name,color,metallic,roughness):
    mat=bpy.data.materials.new(name)
    mat.diffuse_color=(*color,1)
    mat.use_nodes=True
    shader=mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value=(*color,1)
    shader.inputs['Metallic'].default_value=metallic
    shader.inputs['Roughness'].default_value=roughness
    return mat

plate=material('Slate blue / presentation finish',(0.035,0.065,0.10),0.38,0.31)
steel=material('Satin steel',(0.57,0.64,0.70),0.85,0.24)
dark=material('Fasteners',(0.10,0.13,0.16),0.75,0.31)
tool=material('Tooling steel',(0.28,0.34,0.40),0.68,0.28)
gold=material('Section face / presentation highlight',(0.70,0.39,0.12),0.60,0.32)

if MODE=='section':
    section=json.loads((HERE/'geometry-section.json').read_text())
    data=section['parts']; cut=section['cut_z']
else:
    data=json.loads((HERE/'geometry.json').read_text())
    cut=None

def layer(i):
    if i in [0,6,7] or i>=34: return 0
    if i in [1,2,3]: return 0.72
    if i in [4,11,13] or 15<=i<=25: return 1.62
    return 2.65

all_vertices=[]
for item in data:
    ident=item['id']
    verts=[((x+172.617656)/100,(z-173.061604)/100,(y-113.350388)/100) for x,y,z in item['vertices']]
    offset=layer(ident) if MODE=='exploded' else 0
    verts=[(x,y,z+offset) for x,y,z in verts]
    mesh=bpy.data.meshes.new(f'CAD solid {ident:02d}')
    mesh.from_pydata(verts,[],item['triangles'])
    mesh.update()
    obj=bpy.data.objects.new(mesh.name,mesh)
    scene.collection.objects.link(obj)
    if ident in [0,5]: mat=plate
    elif ident in [6,7,8,9,12,14]: mat=steel
    elif ident>=15: mat=dark
    else: mat=tool
    mesh.materials.append(mat)
    mesh.materials.append(gold)
    for poly in mesh.polygons:
        poly.use_smooth=True
        if MODE=='section':
            if all(abs(item['vertices'][j][2]-cut)<0.0001 for j in poly.vertices):
                poly.material_index=1
                poly.use_smooth=False
    # STEP faces have separate seam vertices: weld these before angle splitting.
    bpy.context.view_layer.objects.active=obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=0.000001)
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.select_set(False)
    edges=obj.modifiers.new('Preserve machined edges','EDGE_SPLIT')
    edges.split_angle=math.radians(32)
    bevel=obj.modifiers.new('Render-only edge highlight','BEVEL')
    bevel.width=0.006
    bevel.segments=2
    bevel.limit_method='ANGLE'
    bevel.angle_limit=math.radians(35)
    normals=obj.modifiers.new('Face weighted shading','WEIGHTED_NORMAL')
    normals.keep_sharp=True
    all_vertices.extend(verts)

zmax=max(v[2] for v in all_vertices)
zmin=min(v[2] for v in all_vertices)
target=Vector((0,0.10,(zmin+zmax)/2-0.12))
bpy.ops.object.camera_add(location=(6.2,9.5,6.4 if MODE!='exploded' else 5.8))
camera=bpy.context.object
camera.location=target+Vector((6.2,9.5,6.4 if MODE!='exploded' else 5.8))
camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type='ORTHO'
camera.data.ortho_scale=6.1 if MODE!='exploded' else 8.5
scene.camera=camera

def area(name,location,energy,size,color):
    bpy.ops.object.light_add(type='AREA',location=location)
    lamp=bpy.context.object
    lamp.name=name
    lamp.data.energy=energy
    lamp.data.shape='DISK'
    lamp.data.size=size
    lamp.data.color=color
    lamp.rotation_euler=(target-lamp.location).to_track_quat('-Z','Y').to_euler()

area('Large softbox',(-3,4,8),1800,6,(0.88,0.93,1.0))
area('Front fill',(5,4,4),1100,5,(1,0.96,0.89))
area('Top rim',(0,-5,7),2200,4,(0.82,0.90,1.0))
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-0.065))
floor=bpy.context.object
floor.name='Shadow catcher'
floor.is_shadow_catcher=True
floor.data.materials.append(material('Floor',(0.8,0.8,0.8),0,0.6))
scene.render.filepath=str(HERE/(f'{MODE}-raw'+('-preview.png' if PREVIEW else '.png')))
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/f'{MODE}.blend')) if not PREVIEW else None
bpy.ops.render.render(write_still=True)
print('RENDER_DONE',MODE,scene.render.filepath,flush=True)
