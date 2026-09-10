"""Package validated prototype artifacts; this is not a flight release."""
from pathlib import Path
import json,hashlib,zipfile,datetime
R=Path(__file__).resolve().parents[1]
load=lambda n:json.loads((R/'engineering'/n).read_text())
I=load('inventory.json');C=load('calculations.json');M=load('mesh_checks.json');F=load('final_clearance_report.json');W=load('wire_sampling_check.json');L=load('landing_gear_check.json')
assert all(x['valid'] and x['solids']>=1 for x in I)
assert all(x['closed'] and x['fits_256_cube_in_export_orientation'] for x in M)
assert F['complete'] and len(F['tilt_checks'])==22
assert not F['body_intersections'] and not F['component_pair_intersections'] and not F['moving_structure_collisions']
assert not any(x['collisions'] for x in F['tilt_checks'])
assert W['complete'] and not W['hits'] and not W['ambiguous_hits']
assert W['cad_sha256']==hashlib.sha256((R/'cad/Kestrel_Mini_R4.FCStd').read_bytes()).hexdigest()
assert W['canonical_build_sha256']==hashlib.sha256((R/'scripts/build_freecad.py').read_bytes()).hexdigest()
assert all(x['overlap_mm3']<1e-6 for x in L)
assert C['mass_with_10percent_growth_g']<800 and max(abs(x) for x in C['cg_mm'][:2])<2
with zipfile.ZipFile(R/'cad/Kestrel_Mini_R4.FCStd') as z:
 assert z.testzip() is None and 'GuiDocument.xml' in z.namelist()
summary={'revision':'R4 — matte-black Black Hawk inspired bicopter','native_document_reopened':True,'valid_physical_shapes':len(I),'closed_print_meshes_including_optional':len(M),'installed_prints':sum(x['printed'] and x['installed'] for x in I),'optional_prints':sum(x['printed'] and not x['installed'] for x in I),'wire_routes':W['route_count'],'wire_samples':W['total_wire_samples'],'wire_method':'Approximate mesh ray-parity sampling; continuous clearance and motion flex are not proven','fixed_BRep_sampled_rotor_poses':22,'prop_to_fixed_min_mm':min(x['prop_to_fixed_min_mm'] for x in F['tilt_checks']),'detected_unresolved_intersections_in_completed_checks':0,'tilt_inspector_test':'left +20 / right -20 degrees; both reset to neutral, confirmed','nominal_mass_g':C['nominal_mass_g'],'mass_with_10percent_growth_g':C['mass_with_10percent_growth_g'],'cg_mm':C['cg_mm'],'flight_release':False,'physical_tests_performed':False,'scope':'Shape/mesh validity, selected packaging pairs, approximate neutral wire fitting, sampled rotor clearance, basic structure/power/control calculations. Received hardware interfaces, retention, printed strength/fatigue, actual thrust, loaded servo tracking, firmware integration and stable flight remain open.'}
(R/'engineering/verification_summary.json').write_text(json.dumps(summary,indent=2))
files=[R/'START_HERE.md',R/'OPEN_KESTREL.FCMacro',R/'REPRODUCE.md',R/'cad/Kestrel_Mini_R4.FCStd',R/'cad/Kestrel_Mini_R4.step']
files+=list((R/'stl').rglob('*.stl'))
files += [R/'images'/n for n in ['exterior.png','profile.png','electronics_wiring.png']]
files += [R/'engineering'/n for n in ['ENGINEERING_REVIEW.md','INDEPENDENT_FLIGHT_AUDIT.md','WIRE_SCHEDULE.md','wiring_overview.svg','parameters.json','inventory.json','calculations.json','independent_audit_calculations.json','propulsion_reference.json','servo_reference.json','wiring_routes.json','moving_objects.json','final_clearance_report.json','wire_sampling_check.json','landing_gear_check.json','mesh_checks.json','verification_summary.json']]
files += [R/'scripts'/n for n in ['build_freecad.py','profile_surfaces.py','analyze.py','independent_audit.py','check_fixed_clearances.py','check_wire_samples.py','refresh_exports.py','write_report.py','wiring_diagram.py','package_release.py']]
files += [p for p in (R/'source').iterdir() if p.is_file() and p.suffix!='.py']
# Repository additions: preserve the complete build guide and reviewable evidence.
files += [R/'README.md',R/'NOTICE.md',R/'.gitignore',R/'requirements-docs.txt']
files += list((R/'docs').glob('*.md'))+list((R/'docs').glob('*.json'))
files += [R/'engineering/TAIL_ASSESSMENT.md',R/'engineering/tail_assessment.json']
files += [R/'scripts'/n for n in ['build_parts_list.py','tail_audit.py','build_pdf.py','verify_repository.py']]
files += [R/'output/pdf/Kestrel_Mini_R4_Build_Guide.pdf']
files=sorted(set(files))
assert all(p.is_file() for p in files)
manifest={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}
(R/'MANIFEST_SHA256.json').write_text(json.dumps(manifest,indent=2));files.append(R/'MANIFEST_SHA256.json')
(R/'outputs').mkdir(exist_ok=True)
zpath=R/'outputs/Kestrel_Mini_R4_Repository.zip'
with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(files):z.write(p,str(Path('Kestrel_Mini_R4')/p.relative_to(R)))
with zipfile.ZipFile(zpath) as z:assert z.testzip() is None
print(json.dumps({'zip':str(zpath),'files':len(files),'size_MB':round(zpath.stat().st_size/1e6,2),'summary':summary},indent=2))
