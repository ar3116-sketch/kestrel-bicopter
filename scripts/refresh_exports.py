import FreeCAD as App, Part, MeshPart, json
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=App.getDocument('Kestrel_Mini_R4')
I=[];mesh_checks=[]
physical=[o for o in D.Objects if hasattr(o,'Printable') and o not in D.Reference.Group]
for o in physical:
 if o.Printable:o.BudgetMass_g=o.Shape.Volume/1000*1.24
 bb=o.Shape.BoundBox;solids=o.Shape.Solids
 I.append({'name':o.Name,'label':o.Label,'printed':o.Printable,'installed':o.Installed,'volume_mm3':o.Shape.Volume,'mass_g':o.BudgetMass_g,'center_mm':[sum(t.CenterOfMass[j]*t.Volume for t in solids)/sum(t.Volume for t in solids) for j in range(3)],'bbox_mm':[bb.XLength,bb.YLength,bb.ZLength],'valid':o.Shape.isValid(),'solids':len(solids),'evidence':o.Evidence})
 if o.Printable:
  sh=o.Shape.copy();sh.translate(App.Vector(-bb.XMin,-bb.YMin,-bb.ZMin))
  mesh=MeshPart.meshFromShape(Shape=sh,LinearDeflection=.12,AngularDeflection=.25,Relative=False)
  stl_dir=R/'stl' if o.Installed else R/'stl/optional_guards'
  stl_dir.mkdir(exist_ok=True)
  mesh.write(str(stl_dir/(o.Name+'.stl')))
  mesh_checks.append({'name':o.Name,'installed':o.Installed,'closed':mesh.isSolid(),'facets':mesh.CountFacets,'fits_256_cube_in_export_orientation':max(bb.XLength,bb.YLength,bb.ZLength)<256})
(R/'engineering/inventory.json').write_text(json.dumps(I,indent=2))
(R/'engineering/mesh_checks.json').write_text(json.dumps(mesh_checks,indent=2))
expected={x['name']+'.stl' for x in I if x['printed'] and x['installed']}
for p in (R/'stl').glob('*.stl'):
 if p.name not in expected:p.unlink()
D.recompute();D.save()
Part.export([o for o in physical if o.Installed],str(R/'cad/Kestrel_Mini_R4.step'))
print({'objects':len(I),'prints':len(mesh_checks),'bad_meshes':[x for x in mesh_checks if not x['closed'] or not x['fits_256_cube_in_export_orientation']]})
