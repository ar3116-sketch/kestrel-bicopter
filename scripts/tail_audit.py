"""Tail mass bookkeeping and a deliberately limited crosswind sensitivity screen.
Uses the R4 generator's own cubic profile, without opening/mutating FreeCAD.
No aerodynamic coefficient, wind envelope or flight controller is validated here.
"""
from pathlib import Path
import ast, json, math
R=Path(__file__).resolve().parents[1]
inv=json.loads((R/'engineering/inventory.json').read_text())
c=json.loads((R/'engineering/calculations.json').read_text())
tail=[o for o in inv if 'tail' in o['name'].lower() and o['installed']]
m=sum(o['mass_g'] for o in tail); M=c['nominal_mass_g']; cg=c['cg_mm']
tcg=[sum(o['mass_g']*o['center_mm'][j] for o in tail)/m for j in range(3)]
removed=[(M*cg[j]-m*tcg[j])/(M-m) for j in range(3)]
I=[]
for axis in range(3):
 other=[j for j in range(3) if j!=axis]
 I.append(sum(o['mass_g']/1e9*(sum((o['center_mm'][j]-cg[j])**2 for j in other)+sum(o['bbox_mm'][j]**2 for j in other)/12) for o in tail))
# Only literal station data and the pure arithmetic profile function are loaded.
tree=ast.parse((R/'scripts/build_freecad.py').read_text()); ns={}
for node in tree.body:
 if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='stations' for t in node.targets) and isinstance(node.value,ast.List): ns['rows']=ast.literal_eval(node.value)
 if isinstance(node,ast.FunctionDef) and node.name=='generic_profile_value':exec(compile(ast.Module(body=[node],type_ignores=[]),'profile','exec'),ns)
f=ns['generic_profile_value'];rows=ns['rows']
# Midpoint numerical integration, <=0.05 mm station spacing. The silhouette
# is the full boom height, including shell cavity as a closed body would be.
n=3000;dx=150/n;A=0;Q=0
for i in range(n):
 x=-255+(i+.5)*dx; h=f(rows,3,x)-f(rows,2,x)
 A+=h*dx;Q+=h*dx*(cg[0]-x)
fin=next(o for o in tail if o['name']=='P05_Vertical_tail_fin')
Af=fin['volume_mm3']/1.3;Qf=Af*(cg[0]-fin['center_mm'][0])
# Fin overlaps boom slightly; sum double-counts overlap and omits shielding.
area=(A+Af)/1e6; first_moment=(Q+Qf)/1e9
angle=10-abs(c['hover_trim_angle_deg']);yaw=M/1000*9.80665*.117*math.tan(math.radians(angle))
cases=[]
for v in [3,5,8,10]:
 for cf in [1,1.5]:
  q=.5*1.225*v*v;N=q*cf*first_moment
  cases.append(dict(crosswind_m_s=v,assumed_force_coefficient=cf,side_force_N=q*cf*area,yaw_moment_Nm=N,fraction_of_ideal_yaw_candidate=N/yaw))
out=dict(status='sensitivity screen only; no aerodynamic qualification',tail_members=tail,tail_allocated_mass_g=m,tail_cg_mm=tcg,aircraft_cg_mm=cg,hypothetical_cg_without_tail_mm=removed,tail_bbox_inertia_about_aircraft_cg_kg_m2=I,tail_fraction_of_bbox_inertia=[I[j]/c['inertia_kg_m2'][j] for j in range(3)],boom_side_area_m2=A/1e6,fin_side_area_m2=Af/1e6,summed_side_area_m2=area,area_first_moment_m3=first_moment,ideal_yaw_candidate_Nm=yaw,differential_tilt_after_trim_deg=angle,cases=cases,physical_tests_performed=False)
(R/'engineering/tail_assessment.json').write_text(json.dumps(out,indent=2)+'\n')
lines=['# Tail assessment - Kestrel Mini R4','',
'The tail does not inherently prevent a bicopter from flying. It is included in the existing mass and balance calculation, but its aerodynamic effect is not yet qualified. This aircraft uses two independently tilting propulsion pods for control; the decorative helicopter tail needs no tail rotor.','',
f'## Mass and balance\n\nThe boom, spine, fin, horizontal tailplane and tailwheel prints total **{m:.2f} g**. This is already included in the **{M:.1f} g** nominal aircraft, not an additional charge. Tail hardware mass is in the shared fastener allowance; adhesive/finish are also shared, so this is not a separately weighed complete tail. The calculated CG is x = **{cg[0]:.2f} mm**, close to the rotor pivot plane x = 0. Tail component CG is x = {tcg[0]:.1f} mm. Removing these parts without moving anything else would put CG at x = **{removed[0]:.2f} mm**; that is a sensitivity calculation, not a recommended modification.','',
'| Tail component | Allocated g | CG x, mm |','|---|---:|---:|']
lines += [f"| {o['label']} | {o['mass_g']:.3f} | {o['center_mm'][0]:.2f} |" for o in tail]
lines += ['',f'The same bounding-box inertia approximation used in the main audit assigns these tail parts {I[1]:.6f} kg m^2 in pitch and {I[2]:.6f} kg m^2 in yaw, approximately {100*I[1]/c["inertia_kg_m2"][1]:.0f}% and {100*I[2]/c["inertia_kg_m2"][2]:.0f}% of the respective totals. The long lever arm matters more than the modest mass alone. These are coarse geometry-based estimates, not measured inertia.','',
'## Crosswind sensitivity, not an operating wind limit','',
f'The generator\'s own cubic tail-boom silhouette is integrated at 0.05 mm spacing from x=-255 to -105 mm. Boom side area is {A/100:.2f} cm^2; fin side area is {Af/100:.2f} cm^2. Their sum is {area*1e4:.2f} cm^2, with area-weighted lever arm {first_moment/area*1000:.1f} mm aft of CG. The overlap is double-counted, shielding is omitted, and the rest of the aircraft is excluded. This is not a whole-aircraft force bound.','',
'Use q = 0.5 rho V^2 and yaw moment N = q C integral[(CGx-x) dA], with rho=1.225 kg/m^3. Coefficients C=1.0 and 1.5 are arbitrary sensitivity inputs; neither is a measured value or guaranteed upper bound. Wind is uniform sideways relative flow, not forward speed or rotor downwash. [NASA drag equation](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/drag-equation/) and [coefficient limitations](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/drag-coefficient/) explain why area and matching flow conditions matter.','',
f'For comparison only, a +/-10 degree absolute pod-angle candidate, less {abs(c["hover_trim_angle_deg"]):.2f} degrees common trim, leaves {angle:.2f} degrees differential tilt. Near hover, ideal yaw moment is approximately m g d tan(delta) = **{yaw:.3f} N m**, with d=0.117 m. This assumes coordinated thrust and no additional pitch/roll demand, actuator lag or saturation. The angle is not an implemented or flight-qualified limit.','',
'| Crosswind m/s | Assumed C | Tail yaw N m | Fraction of ideal candidate |','|---:|---:|---:|---:|']
lines += [f"| {a['crosswind_m_s']} | {a['assumed_force_coefficient']:.1f} | {a['yaw_moment_Nm']:.3f} | {100*a['fraction_of_ideal_yaw_candidate']:.0f}% |" for a in cases]
lines += ['',
'The tail can consume a meaningful fraction of heading-control authority in crosswind. These calculations do not establish a safe wind speed, stability, damping, gust response or combined maneuver envelope. Tailplane pitch loads in forward flight/downwash, fin flow separation, vibration, rotor/fuselage interference, and full-aircraft aerodynamic moments remain unmodeled. A passive tail may tend to align the aircraft with relative wind; the active controller still has to hold the commanded heading.','',
'## What must be checked on the prototype','',
'- Weigh the completed tail and whole aircraft; measure CG with the actual battery and hardware. Rebalance toward x=0 and rerun the audit if any mass or geometry changes.','- Resolve and proof-load the internal tail splice/retention and long spine. Check resonance, flex, landing loads and fastener retention; no structural tail release is implied by a valid CAD solid.','- Measure side force/yaw torque and tailplane pitch loads in a restrained instrumented fixture across representative flow directions, including rotor-on effects. Compare to measured control authority with reserve for simultaneous commands.','- Verify firmware mixing, loaded servo response, motor thrust, vibration and loss-of-signal behavior before controlled flight qualification. Initial evaluation belongs in still air; no outdoor wind envelope is approved.','',
'Run `python3 scripts/tail_audit.py` after `scripts/analyze.py` to regenerate this assessment.']
(R/'engineering/TAIL_ASSESSMENT.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['tail_members','cases']},indent=2)); print(cases)
