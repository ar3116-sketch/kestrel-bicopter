"""Read-only integrity and cross-document consistency checks (standard library)."""
from pathlib import Path
import hashlib,json,re,zipfile,math
R=Path(__file__).resolve().parents[1]
manifest=json.loads((R/'MANIFEST_SHA256.json').read_text())
for name,want in manifest.items():
 f=R/name
 assert f.is_file(),f'Missing {name}'
 assert hashlib.sha256(f.read_bytes()).hexdigest()==want,f'Changed since package: {name}'
load=lambda p:json.loads((R/p).read_text())
c=load('engineering/calculations.json');i=load('engineering/inventory.json');b=load('docs/parts.json');t=load('engineering/tail_assessment.json')
assert math.isclose(sum(p['allocated_total_g'] for p in b),c['purchased_allocated_g'],abs_tol=1e-8)
assert math.isclose(sum(o['mass_g'] for o in i if o['installed'] and o['printed']),c['printed_g'],abs_tol=1e-8)
assert math.isclose(t['tail_allocated_mass_g'],sum(o['mass_g'] for o in i if o['installed'] and 'tail' in o['name'].lower()),abs_tol=1e-8)
for o in i:
 if o['printed']:
  path=R/'stl'/('' if o['installed'] else 'optional_guards')/(o['name']+'.stl');assert path.exists(),path
with zipfile.ZipFile(R/'cad/Kestrel_Mini_R4.FCStd') as z:assert z.testzip() is None and 'GuiDocument.xml' in z.namelist()
w=load('engineering/wire_sampling_check.json')
assert w['cad_sha256']==hashlib.sha256((R/'cad/Kestrel_Mini_R4.FCStd').read_bytes()).hexdigest()
assert w['canonical_build_sha256']==hashlib.sha256((R/'scripts/build_freecad.py').read_bytes()).hexdigest()
assert load('engineering/verification_summary.json')['flight_release'] is False
# Check file references in the user-facing entry points and parts list.
for name in ['README.md','START_HERE.md','docs/PARTS_LIST.md']:
 p=R/name
 for dest in re.findall(r'\]\(([^)]+)\)',p.read_text()):
  if not dest.startswith(('http:','https:','#')):assert (p.parent/dest.split('#')[0]).exists(),(name,dest)
print(f'PASS: {len(manifest)} file hashes; CAD GUI data; print files; BOM/mass/tail consistency; local links; prototype status.')
