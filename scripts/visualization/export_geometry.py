from pathlib import Path
import json
from OCP.STEPControl import STEPControl_Reader
from OCP.IFSelect import IFSelect_RetDone
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID, TopAbs_FACE, TopAbs_REVERSED
from OCP.TopoDS import TopoDS
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.gp import gp_Pnt

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).parent
reader=STEPControl_Reader()
assert reader.ReadFile(str(ROOT/'cad/assembly.step'))==IFSelect_RetDone
reader.TransferRoots()
shape=reader.OneShape()
explorer=TopExp_Explorer(shape,TopAbs_SOLID)
solids=[]
while explorer.More():
    solid=TopoDS.Solid_s(explorer.Current())
    bounds=Bnd_Box(); BRepBndLib.Add_s(solid,bounds)
    prop=GProp_GProps(); BRepGProp.VolumeProperties_s(solid,prop)
    solids.append((solid,list(bounds.Get()),prop.Mass(),BRepCheck_Analyzer(solid).IsValid()))
    explorer.Next()
print('SOLIDS',len(solids),flush=True)
for i,(_,bounds,vol,valid) in enumerate(solids):
    print(i,[round(v,2) for v in bounds], 'volume',round(vol,2),'valid',valid,flush=True)

def mesh(solid):
    BRepMesh_IncrementalMesh(solid,0.12,False,0.22,True).Perform()
    vertices=[]; triangles=[]
    exp=TopExp_Explorer(solid,TopAbs_FACE)
    while exp.More():
        face=TopoDS.Face_s(exp.Current())
        loc=TopLoc_Location()
        tri=BRep_Tool.Triangulation_s(face,loc)
        if tri is not None:
            offset=len(vertices)
            transform=loc.Transformation()
            for j in range(1,tri.NbNodes()+1):
                p=tri.Node(j).Transformed(transform)
                vertices.append([p.X(),p.Y(),p.Z()])
            for j in range(1,tri.NbTriangles()+1):
                a,b,c=tri.Triangle(j).Get()
                if face.Orientation()==TopAbs_REVERSED:
                    b,c=c,b
                triangles.append([offset+a-1,offset+b-1,offset+c-1])
        exp.Next()
    return {'vertices':vertices,'triangles':triangles}

data=[]
for i,(solid,bounds,vol,valid) in enumerate(solids):
    data.append({'id':i,'bounds':bounds,'volume':vol,'valid':valid,**mesh(solid)})
(OUT/'geometry.json').write_text(json.dumps(data,separators=(',',':')),encoding='utf-8')
print('Exported',sum(len(s['triangles']) for s in data),'triangles',flush=True)

# Keep the rear half in STEP coordinates, through the tooling axis.
cut_z=(solids[11][1][2]+solids[11][1][5])/2
clip=BRepPrimAPI_MakeBox(gp_Pnt(-1000,-1000,-1000),gp_Pnt(1000,1000,cut_z)).Shape()
sections=[]
for i,(solid,bounds,vol,valid) in enumerate(solids):
    if bounds[2] > cut_z+0.001:
        continue
    op=BRepAlgoAPI_Common(solid,clip); op.Build()
    assert op.IsDone()
    section=op.Shape()
    if section.IsNull():
        continue
    item={'id':i,'bounds':bounds,'volume':vol,'valid':BRepCheck_Analyzer(section).IsValid(),**mesh(section)}
    if item['triangles']:
        sections.append(item)
(OUT/'geometry-section.json').write_text(json.dumps({'cut_z':cut_z,'parts':sections},separators=(',',':')),encoding='utf-8')
print('Section exported:',len(sections),'bodies; cut at',cut_z,flush=True)
