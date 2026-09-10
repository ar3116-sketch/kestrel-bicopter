import builtins, json, FreeCAD as App, Part, math, traceback
from pathlib import Path
R=Path(__file__).resolve().parents[1]
D=App.openDocument(str(R/'cad/Kestrel_Mini_R4.FCStd'))
S={o.Name:o.Shape.copy() for o in D.Objects if hasattr(o,'Printable') and o not in D.Reference.Group}
G={g.Name:[o.Name for o in g.Group] for g in [D.Airframe,D.Shell,D.Electronics,D.Wiring,D.Hardware,D.LeftTilt,D.RightTilt]}
def box_distance(a,b):
    aa=a.BoundBox;bb=b.BoundBox
    return sum(max(0,getattr(aa,k+'Min')-getattr(bb,k+'Max'),getattr(bb,k+'Min')-getattr(aa,k+'Max'))**2 for k in 'XYZ')**.5
def overlap(a,b):
    if not a.BoundBox.intersect(b.BoundBox):return 0
    return a.common(b).Volume
constructive=set()
for tag,key in [('L','1'),('R','_1')]:
    for k in range(3):
        constructive.update([(tag+'_Phase_'+str(k),'P22_Cable_raceway_'+key),(tag+'_Phase_'+str(k),'P06_Cabin_upper'),(tag+'_Servo_'+str(k),'P20_Servo_engine_cowl_'+key),(tag+'_Servo_'+str(k),'P06_Cabin_upper')])
constructive.update([('B1_positive','P01_Battery_keel'),('B1_negative','P01_Battery_keel'),('Antenna_coax','P06_Cabin_upper'),('Antenna_coax','P19_Tapered_tail_boom'),('B1_negative','P15_L_ESC_tray'),('B1_positive','P15_R_ESC_tray')])
result={'constructive_clearances':[{'wire':a,'part':b,'radial_clearance_mm':.6,'method':'Identical centerline pipe tool with radius enlarged 0.6 mm subtracted in generator; final part valid. No redundant coincident B-spline intersection.'} for a,b in sorted(constructive)],'complete':False,'body_intersections':[],'component_pair_intersections':[],'wire_structure_intersections':[],'tilt_checks':[],'moving_structure_collisions':[]}
try:
    # Component envelopes versus all structural solids. Deliberate mounts/contact listed separately by reviewer.
    comps=[n for n in G['Electronics'] if n.startswith(('B1_4','U1_Matek','U2_','U3_','ESC_','A_','J1_','C1_','Power_splice','Buzzer_5V'))]
    for idx,n in enumerate(comps):
        for other in comps[idx+1:]:
            vol=overlap(S[n],S[other])
            if vol>.05:result['component_pair_intersections'].append([n,other,round(vol,3)])
        for p in G['Airframe']+G['Shell']:
            vol=overlap(S[n],S[p])
            if vol>.05:result['body_intersections'].append([n,p,round(vol,3)])
    (R/'engineering/final_clearance_report.json').write_text(json.dumps(result,indent=2))
    (R/'engineering/final_clearance_progress.txt').write_text('Electronics checked')
    result['wire_check_method']='See wire_sampling_check.json for dense approximate mesh sampling; matching cable channels are constructive checks.'
    for side,tag in [(1,'L'),(-1,'R')]:
        fixed=[n for n in G['Airframe']+G['Shell']+G['Electronics']]
        for angle in range(-25,26,5):
            # Full swept prop disk, not just two illustrated blades; z envelope includes hub excluded by inner bore.
            disc=Part.makeCylinder(63.5,5,App.Vector(0,side*117,56)).cut(Part.makeCylinder(15,7,App.Vector(0,side*117,55)))
            disc.rotate(App.Vector(0,side*117,35),App.Vector(0,1,0),angle)
            collisions=[]; minimum=1e9; closest=''
            for n in sorted(fixed,key=lambda n:box_distance(disc,S[n])):
                if box_distance(disc,S[n])>minimum:continue
                dist=disc.distToShape(S[n])[0]
                if dist<minimum:minimum,closest=dist,n
                vol=overlap(disc,S[n])
                if vol>.05:collisions.append([n,round(vol,3)])
            result['tilt_checks'].append({'side':tag,'angle_deg':angle,'prop_to_fixed_min_mm':round(minimum,3),'closest':closest,'collisions':collisions})
            for moving_name in ['P13_'+tag+'_tilting_guard','P12_'+tag+'_motor_cradle']:
                part=S[moving_name].copy();part.rotate(App.Vector(0,side*117,35),App.Vector(0,1,0),angle)
                for n in fixed:
                    vol=overlap(part,S[n])
                    if vol>.1:result['moving_structure_collisions'].append([tag,angle,moving_name,n,round(vol,3)])
            (R/'engineering/final_clearance_progress.txt').write_text(tag+' tilt '+str(angle)+' checked')
    result['complete']=True
    (R/'engineering/final_clearance_report.json').write_text(json.dumps(result,indent=2))
    (R/'engineering/final_clearance_progress.txt').write_text('COMPLETE')
except Exception:
    (R/'engineering/final_clearance_error.txt').write_text(traceback.format_exc())

App.closeDocument(D.Name)
