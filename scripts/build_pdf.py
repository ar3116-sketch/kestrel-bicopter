"""Create the concise R4 build/engineering guide. Requires reportlab and Pillow."""
from pathlib import Path
import json, math, re
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, Flowable, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from PIL import Image as PILImage
R=Path(__file__).resolve().parents[1]
OUT=R/'output/pdf/Kestrel_Mini_R4_Build_Guide.pdf';OUT.parent.mkdir(parents=True,exist_ok=True)
C=json.loads((R/'engineering/calculations.json').read_text());T=json.loads((R/'engineering/tail_assessment.json').read_text())
B=json.loads((R/'docs/parts.json').read_text());I=json.loads((R/'engineering/inventory.json').read_text());W=json.loads((R/'engineering/wiring_routes.json').read_text());refs=json.loads((R/'docs/references.json').read_text())
ink=colors.HexColor('#162329');muted=colors.HexColor('#53636b');accent=colors.HexColor('#167d8d');pale=colors.HexColor('#edf3f4');line=colors.HexColor('#d4dfe2')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle('TitleK',fontName='Helvetica-Bold',fontSize=35,leading=39,textColor=ink,spaceAfter=13))
styles.add(ParagraphStyle('HeadingK',fontName='Helvetica-Bold',fontSize=21,leading=26,textColor=ink,spaceAfter=14))
styles.add(ParagraphStyle('SubK',fontName='Helvetica-Bold',fontSize=11.5,leading=15,textColor=accent,spaceBefore=12,spaceAfter=7))
styles.add(ParagraphStyle('BodyK',fontName='Helvetica',fontSize=9.5,leading=14,textColor=ink,spaceAfter=8))
styles.add(ParagraphStyle('SmallK',fontName='Helvetica',fontSize=8,leading=11,textColor=muted,spaceAfter=6))
styles.add(ParagraphStyle('CellK',fontName='Helvetica',fontSize=7.7,leading=10.3,textColor=ink))
styles.add(ParagraphStyle('CellHeadK',fontName='Helvetica-Bold',fontSize=7.7,leading=10,textColor=colors.white))
S=[]
def clean(s):
 for a,b in [('—','-'),('–','-'),('‑','-'),('−','-'),('±','+/-'),('→',' to '),('°',' deg'),('×','x'),('’',"'"),('“','"'),('”','"')]:s=s.replace(a,b)
 return s

def p(s,style='BodyK'):
 return Paragraph(clean(s),styles[style])
def add(s,style='BodyK'):S.append(p(s,style))
def title(n,t):
 if S:S.append(PageBreak())
 add(f'{n:02d} / KESTREL MINI R4','SmallK');add(t,'HeadingK')
def sub(t):add(t,'SubK')
def table(rows,widths,small=False):
 data=[[p(escape(str(v)), 'CellHeadK' if k==0 else 'CellK') for v in row] for k,row in enumerate(rows)]
 tab=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
 tab.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),ink),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,pale]),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('LINEBELOW',(0,-1),(-1,-1),.5,line)]))
 S.append(tab);S.append(Spacer(1,8))
def photo(name,w=500,hmax=325):
 f=R/'images'/name
 with PILImage.open(f) as im: iw,ih=im.size
 h=w*ih/iw
 if h>hmax:w*=hmax/h;h=hmax
 S.append(Image(str(f),width=w,height=h,hAlign='CENTER'))

def bullet(t):add('&#8226; '+t)

# 1
title(1,'Build & engineering guide')
add('KESTREL<br/>MINI R4','TitleK')
add('Black Hawk inspired styling. Two independently tilting lift pods.','BodyK')
photo('exterior.png',500,305)
table([['NOMINAL MASS','WITH 10% GROWTH','INSTALLED PRINTS'],['665 g','731 g','40 pieces']], [167,167,166])
add('<b>Design / fit prototype - flight qualification remains open.</b> The CAD includes electronics, wiring and a lightweight tail. Published motor data support takeoff in theory under the stated assumptions; the aircraft has not been built or flown.')
add('Revision R4 | 9 September 2026 | Units: mm, g, N and N m. Baseline uses a 4S1300 LiPo, commercial 5-inch props and no optional guards.','SmallK')
# 2
title(2,'Purchase list / electronics')
add('No hardware is owned. These selections establish the CAD and calculation basis. Buy only after resolving the marked interfaces; a similar-looking substitute invalidates the existing fit or thrust evidence. Reference IDs link to manufacturer pages on page 13.','BodyK')
rows=[['Qty','Selected part','Total g','Key fit / selection requirement']]
for b in B[:11]:rows.append([b['quantity'],b['part']+' ['+b['reference']+']' if b['reference'] else b['part'],f"{b['allocated_total_g']:.1f}",b['notes']])
table(rows,[27,161,45,267])
add('Battery selection is OPEN. The 170 g allocation includes stock leads; confirm actual pack current capability, mass and dimensions. Four 21700 cells would put this layout near 799 g before contingency and require packaging changes.','SmallK')
# 3
title(3,'Mechanical parts & bench equipment')
rows=[['Qty','Purchased mechanical part','Total g','Interface requirement']]
for b in B[11:]:rows.append([b['quantity'],b['part'],f"{b['allocated_total_g']:.1f}",b['notes']])
table(rows,[27,161,45,267])
sub('Installation allowances - 77 g total')
table([['Budget','Included material','g'],['Harness','Wire, solder, secondary connectors, insulated power splice','36'],['Hardware','Other screws, nuts, spacers, isolators, axles and retainers','25'],['Installation','Straps, foam, ties and insulation','8'],['Finish','Adhesive and restrained matte-black finish','8']],[88,377,35])
add('Modeled fastener dimensions: eight motor M3 x7, four FC M3 x10, four beam/keel M3 x22, four yoke M3 x10; two diameter-2 x12 mm main axles and one diameter-2 x9 mm tail axle. Lengths require received-hardware verification. Motor screw ends must clear windings. Tail splice, shell closure, servo ear screws and trunnion retention are not fully detailed.')
sub('Ground equipment - outside aircraft mass')
bullet('ELRS 2.4 GHz transmitter/module compatible with RP1; the initial FlySky radio suggestion does not match this receiver.')
bullet('4S-compatible LiPo balance charger and supply; scale, calipers, multimeter, current/voltage logging and soldering tools.')
bullet('Restrained thrust and actuator test fixtures, vibration measurement, fit coupons and appropriate filament/slicer.')
add('Purchased component allocations total 337 g. Do not count supplied horns, link ends, battery connectors or stock leads twice. Exact hardware is still a fit and qualification task.','SmallK')
# 4/5 prints
prints=sorted([o for o in I if o['printed'] and o['installed']],key=lambda o:o['name'])
for idx,group in enumerate([prints[:20],prints[20:]]):
 title(4+idx,f'Print inventory / {idx+1} of 2')
 add('One of each listed STL. Names correspond exactly to files in stl/. Separated glazing pieces and mirrored parts have individual files. CAD masses use full material volume at 1.24 g/cm^3; confirm slicer mass and actual print weight.','SmallK')
 rows=[['STL name (without .stl)','CAD g','Bounding box, mm']]
 for o in group:rows.append([o['name'],f"{o['mass_g']:.2f}",' x '.join(f'{v:.1f}' for v in o['bbox_mm'])])
 table(rows,[292,53,155])
 if idx==1:
  opt=[o for o in I if o['printed'] and not o['installed']]
  sub('Optional guards - omitted from baseline')
  table([['STL name','CAD g','Bounding box, mm']]+[[o['name'],f"{o['mass_g']:.2f}",' x '.join(f'{v:.1f}' for v in o['bbox_mm'])] for o in opt],[292,53,155])
  add('Installed printed mass: 250.90 g. Optional guards add 25.37 g. All 42 meshes fit the printer cube by bounding box; brim, supports and print orientation still need a slicer check.','SmallK')
# 6
class Wiring(Flowable):
 def __init__(self):Flowable.__init__(self);self.width=500;self.height=218
 def draw(self):
  c=self.canv
  def box(x,y,w,h,txt):
   c.setFillColor(pale);c.setStrokeColor(line);c.roundRect(x,y,w,h,5,stroke=1,fill=1);c.setFillColor(ink);c.setFont('Helvetica-Bold',8)
   for i,t in enumerate(txt):c.drawCentredString(x+w/2,y+h-14-i*11,t)
  def link(points,color=accent):
   c.setStrokeColor(color);c.setLineWidth(1.3);path=c.beginPath();path.moveTo(*points[0])
   for pt in points[1:]:path.lineTo(*pt)
   c.drawPath(path)
  box(0,147,108,48,['4S LiPo','XT60 connector']);box(144,147,125,48,['Insulated VBAT splice','+ common ground'])
  box(323,167,175,38,['2 x ESC -> 2 x motors']);box(323,106,175,38,['6 V UBEC -> 2 x servos']);box(144,31,125,53,['Matek FC','VBAT input / 5 V output']);box(323,31,175,53,['5 V receiver + buzzer','CRSF + buzzer control'])
  link([(108,171),(144,171)]);link([(269,176),(295,176),(295,186),(323,186)]);link([(269,165),(288,165),(288,125),(323,125)]);link([(202,147),(202,84)]);link([(269,56),(323,56)])
  c.setFont('Helvetica',7);c.setFillColor(muted);c.drawString(7,118,'470 uF / 35 V across');c.drawString(7,107,'VBAT and GND; verify polarity')
  link([(144,161),(126,161),(126,102),(104,102)])
  c.setDash(3,2);link([(249,84),(279,94),(310,94),(310,116),(323,116)]);link([(239,84),(274,99),(304,99),(304,174),(323,174)]);c.setDash()
  c.setFillColor(muted);c.drawString(145,7,'Dashed: FC control signals. All grounds common; keep 5 V and 6 V positives separate.')
title(6,'Power & control wiring')
S.append(Wiring());S.append(Spacer(1,8))
photo('electronics_wiring.png',490,238)
add('<b>Servo rail:</b> dedicated regulated 6 V from UBEC. <b>Logic rail:</b> FC 5 V to receiver/buzzer. Grounds are common; do not join positive regulated rails. Main motor current bypasses the FC current sensor in this layout, so total pack current needs external measurement.')
add('<b>Proposed FC resources:</b> S1/PC9 and S2/PC8 motors; S9/PB14 and S10/PA6 tilt servos. CRSF uses RX2/PA3 and TX2/PA2. Confirm actual firmware target, servo support, BI mixer, direction, neutral, endpoints and protocol with props removed. Older ESCs are not assumed to support DShot.','SmallK')
# 7/8
for idx,group in enumerate([W[:21],W[21:]]):
 title(7+idx,f'Wire schedule / {idx+1} of 2')
 add('Neutral modeled paths. Cut estimate adds 15 mm for terminations and another 20 mm on each phase extension. Existing motor, servo and battery leads may replace extensions; hand dress and measure first. Endpoint names indicate function, not exact solder-pad geometry.','SmallK')
 rows=[['Wire','AWG','Route / cut mm','Endpoint functions']]
 for w in group:rows.append([w['name'],w['awg'],f"{w['length_mm']:.0f} / {w['cut_length_mm']:.0f}",w['from']+' -> '+w['to']])
 table(rows,[137,35,75,253])
 add('42 routes are modeled and checked at neutral. Flexible travel, wire fatigue, wire-to-wire contact and every terminal/electronics pair are not continuously verified. Supplied antenna coax and pack balance leads are reference assemblies; do not fabricate or cut them from this table.','SmallK')
# 9
title(9,'Lift, mass & control feasibility')
table([['Case','Mass g','TWR at 12 V','TWR at 16 V'],['Nominal',f"{C['nominal_mass_g']:.1f}",'1.82','2.29'],['10% growth',f"{C['mass_with_10percent_growth_g']:.1f}",'1.65','2.09'],['Target ceiling','800','1.51','1.91']],[190,90,110,110])
add('TWR = installed total static thrust / weight. The EMAX table covers original RS2205 2300KV motors with HQ5045BN two-blade props. An assumed 0.85 installed-thrust factor gives 1210 gf at 12 V and 1525 gf at 16 V, with a 24 A per-motor calculation ceiling where source data permit it. Neither factor nor limit is enforced firmware.')
add('At nominal mass, simultaneous 20 degree pod tilt and 20 degree bank reduce vertical TWR to 1.61 at 12 V; at growth mass this falls to 1.46, before extra differential-command reserve. The growth case misses the preferred 1.8 vertical gate at low voltage. Fresh 16.8 V and hardware substitutes require new measurements.')
sub('Two motors are enough only with the tilt mechanism')
table([['Command','Bicopter response'],['Climb / descend','Both motors change total thrust.'],['Roll / lateral translation','Differential motor thrust rolls the aircraft; bank redirects thrust.'],['Pitch / forward-back motion','Coordinated common pod tilt and body attitude redirect thrust.'],['Yaw / turn heading','Opposite pod tilt creates a yaw moment.']],[145,355])
add('The local ideal model has sufficient control inputs, but pitch and yaw share servo travel: |common| + |differential| must stay within the absolute pod limit. TWR and controllability do not establish closed-loop stability.')
sub('Servo and endurance limits')
add('BMS-115WV+ catalog torque is 5.5 kgf cm at 6 V; the audit uses one-quarter of that only as an assumed working screen. A bounded 45 deg/s roll gives approximately 0.0735 N m total servo load versus a 0.1348 N m screen. At 180 deg/s the screen is exceeded. Real rotating inertia, RPM, heat, friction, linkage flex and loaded response remain unknown.')
add('Estimated hover endurance is roughly 3-4 minutes with 80% of 4S1300 nominal energy and a 5 W avionics/servo allowance. This is a static estimate, not measured endurance or a landing timer. See the full independent audit for equations and sensitivity cases.','SmallK')
# 10
title(10,'Tail / balance and crosswind')
photo('profile.png',490,158)
add(f'Tail prints total <b>{T["tail_allocated_mass_g"]:.2f} g</b>, already included in the 665 g estimate. The current calculated CG is <b>0.82 mm aft of the rotor pivot plane</b>. Removing the tail parts without rebalancing would shift CG to 7.28 mm forward. Hardware and finish remain in shared allowances.')
add('The long tail accounts for about 43% of the coarse pitch inertia estimate and 25% of yaw inertia. It therefore changes response even though it is only about 5% of total mass. The passive tail does not need a tail rotor and does not inherently prevent bicopter flight.')
sub('Uniform side-flow sensitivity - no approved wind limit')
add('Boom + fin summed side area is 71.38 cm^2, with a 179 mm area-weighted arm behind CG. Use N = 0.5 rho V^2 C integral[(CGx-x) dA], rho=1.225 kg/m^3. C=1.0-1.5 is an arbitrary sensitivity range, not measured or bounded aerodynamic data. Fin/boom overlap is double-counted; other aircraft surfaces and interference are excluded.')
rows=[['Side flow','Tail yaw moment, C=1.0-1.5','Ideal yaw candidate used']]
for v in [3,5,8,10]:
 a=[k for k in T['cases'] if k['crosswind_m_s']==v]
 rows.append([f'{v} m/s',f"{a[0]['yaw_moment_Nm']:.3f}-{a[1]['yaw_moment_Nm']:.3f} N m",f"{100*a[0]['fraction_of_ideal_yaw_candidate']:.0f}-{100*a[1]['fraction_of_ideal_yaw_candidate']:.0f}%"])
table(rows,[85,240,175])
add('The comparison uses about 0.114 N m ideal yaw authority near hover, after reserving common trim within an unqualified +/-10 degree absolute pod-angle candidate. It assumes coordinated thrust and no simultaneous maneuver demand. At the higher sensitivity cases the tail alone can consume most or all of that candidate authority.')
add('<b>Conclusion:</b> mass and balance are plausible with the tail, but crosswind, pitch loads, vibration and tail-joint strength still need measurement. No wind speed in this table is a safe or approved operating limit. Full method and reproducible calculations: engineering/TAIL_ASSESSMENT.md.','SmallK')
# 11
title(11,'Printing & assembly sequence')
sub('Start with fit coupons, then structural pieces')
add('Centauri Carbon basis: 256 mm cube. All STL bounds fit, but supports, brim and orientation still require review. Print bearing, screw, shell seam and servo-retainer fit coupons before committing the complete aircraft.')
add('Use actual material density when weighing the build. The current shell uses a 1 mm section-coordinate inset, not a guaranteed constant surface-normal wall. Layer orientation, infill, heat, creep and fatigue need qualification; no universal slicer recipe is asserted to be sufficient.')
steps=[('1. Resolve the hardware','Measure actual battery, motors, ESCs, servos and FC. Finalize trunnion shoulders/spacers/retainers, spline fit, motor screw engagement and tail splice. The existing envelopes are provisional.'),('2. Assemble the structure','Dry-fit keel, crossbeam, avionics deck and yokes. Install metal bearings and positively retained pins. Check endplay and independent pod rotation.'),('3. Fit actuators and electronics','Set verified mechanical neutral, fit horns/links and check range. Install FC isolation, receiver, dedicated servo BEC, ESCs, buzzer and capacitor with service access.'),('4. Route and inspect wiring','Follow net functions and measure actual cut lengths. Insulate the splice and provide strain relief. Check phase-wire bend radius throughout travel; neutral CAD fit does not establish flex life.'),('5. Close the body and tail','Resolve the x=-105 mm tail splice and tailwheel/gear retention before fitting shell and glazing. Check cooling, antenna placement and disconnect access.'),('6. Weigh and rebalance','Measure completed mass and three-axis CG with battery. Aim for CGx near zero using battery position; rerun the audit if geometry, hardware or weight changes.')]
for h,b in steps:sub(h);add(b)
add('Detailed task list: docs/BUILD_AND_TEST.md. This sequence organizes prototype assembly; unresolved joints prevent it from being a fully released manufacturing instruction.','SmallK')
# 12
title(12,'Verification & remaining gates')
table([['Completed computer checks','Scope / practical limit'],['167 valid physical CAD shapes','Topological validity; not stress, fatigue or actual hardware fit.'],['42 closed print meshes','40 installed, 2 optional; bounding box within printer limits.'],['22 sampled rotor poses','Selected fixed-part pairs; minimum prop clearance 9.906 mm. No continuous or deflected motion proof.'],['42 neutral wire routes','179,487 finite samples; no detected hits in completed scope. Not a flexible-harness or complete terminal-contact proof.'],['Mass, thrust and control screens','Source-based calculations and idealized models. No measured powertrain or tested flight tune.']],[168,332])
sub('Required before flight qualification')
bullet('Props removed: continuity, polarity, separated regulated rails, firmware mixer/resources, motor/servo direction, endpoints, neutral and loss-of-signal behavior.')
bullet('Loaded electrical tests: simultaneous servo current, BEC sag, capacitor behavior and temperatures. Check the actual ESC protocol. Main pack current needs external measurement in this layout.')
bullet('Restrained propeller-on tests: exact installed thrust/current over actual pack voltage, motor/ESC temperature and body interference. Fresh-pack operation needs evidence.')
bullet('Mechanical tests: layer/joint strength, crank flex, tail splice proof, pin/axle retention, vibration, cyclic durability and real harness movement.')
bullet('Dynamic tests: loaded servo tracking including gyroscopic loads; tail crosswind and pitch moments; actual controller response and reserve under simultaneous commands.')
add('The +/-10 degree pod/bank and <=45 deg/s body-rate values are investigation candidates, not implemented settings or approved limits. No PID tune, full-flight simulation, CFD or physical flight test has been completed.')
add('<b>Status: flight_release = false.</b> Keep measured configuration, firmware hash/settings, scale/CG results, thrust curves, thermal logs and pass/fail evidence together. A valid solid and TWR above one do not alone establish reliable flight.')
# 13
title(13,'References & project files')
add('Primary specification references underpin the selected components. Exact battery SKU and generic hardware remain open. Reference pages are not a promise of current availability or endorsement. Full source snapshots and pinned Betaflight revisions are included in source/.','SmallK')
for k,(name,url) in refs.items():
 add(f'<b>[{k}]</b> <link href="{escape(url)}" color="#167d8d">{escape(name)}</link>','BodyK')
add('NASA references support the force equation and coefficient limitations; the numerical tail areas, coefficients and moments are this project\'s own explicitly limited calculations.','SmallK')
sub('Where to find the detail')
table([['Folder / file','Contents'],['cad/','Native FreeCAD model and STEP assembly'],['stl/','Installed printable pieces; optional guards in subfolder'],['engineering/','Full audits, tail assessment, wire schedule, calculations and geometry-check evidence'],['docs/','Purchase/print list, machine-readable parts and build/test plan'],['scripts/','Geometry, analysis, audits, documentation and validation generators'],['REPRODUCE.md','Commands, dependencies and limits of reproducibility'],['NOTICE.md','Manufacturer references and third-party source attribution']],[155,345])
add('Repository: <link href="https://github.com/ar3116-sketch/kestrel-bicopter" color="#167d8d">github.com/ar3116-sketch/kestrel-bicopter</link>','BodyK')
add('Design intent: a small, matte-black, helicopter-inspired bicopter. This independent hobby project is not affiliated with the Black Hawk manufacturer or component vendors. No general open-source license has been selected.','SmallK')

def page(canvas,doc):
 canvas.saveState();w,h=doc.pagesize
 canvas.setStrokeColor(line);canvas.setLineWidth(.6);canvas.line(47,47,w-47,47)
 canvas.setFont('Helvetica',7.5);canvas.setFillColor(muted);canvas.drawString(47,33,'KESTREL MINI R4  /  DESIGN PROTOTYPE  /  2026-09-09');canvas.drawRightString(w-47,33,str(doc.page));canvas.restoreState()
doc=SimpleDocTemplate(str(OUT),pagesize=(595.28,841.89),rightMargin=47.64,leftMargin=47.64,topMargin=42,bottomMargin=62,title='Kestrel Mini R4 - Build and Engineering Guide',author='Kestrel project',subject='Parts, wiring, CAD and preliminary flight feasibility')
doc.build(S,onFirstPage=page,onLaterPages=page)
print(OUT)
