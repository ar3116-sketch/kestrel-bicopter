"""KESTREL MINI R4. Run inside FreeCAD. mm, grams. Provisional interfaces.
Original geometry; parameter-driven generator, not a scaled Samson export.
"""
import FreeCAD as App, FreeCADGui as Gui, Part, MeshPart
import math, json, os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
V=App.Vector
P={'rotor_y':117.0,'pivot_z':35.0,'prop_z':58.0,'prop_radius':63.5,
   'guard_inner_radius':69.5,'guard_outer_radius':71.1,'tilt_limit_deg':25,
   'density_print_g_cm3':1.24,'battery_mass_g':170.0,'battery_x':39.0,'guards_installed':False}
(ROOT/'engineering/parameters.json').write_text(json.dumps(P,indent=2))
if 'Kestrel_Mini_R4' in App.listDocuments(): App.closeDocument('Kestrel_Mini_R4')
doc=App.newDocument('Kestrel_Mini_R4')
doc.Label='Kestrel R4 — Black Hawk inspired bicopter'
groups={}
for name in ['Airframe','Shell','Electronics','Wiring','Hardware','LeftTilt','RightTilt','Reference']:
    groups[name]=doc.addObject('App::DocumentObjectGroup',name)
records=[]; moving={1:[],-1:[]}; wire_records=[]; wire_channels={}
olive=(0.10,0.105,0.11); dark=(0.065,0.07,0.075); trim=(0.19,0.20,0.21)
orange=(0.10,0.11,0.12); metal=(0.46,0.49,0.51); green=(0.08,0.33,0.23)
def box(x,y,z,dx,dy,dz): return Part.makeBox(dx,dy,dz,V(x,y,z))
def cyl(r,h,p,axis=(0,0,1)):return Part.makeCylinder(r,h,V(*p),V(*axis))
def tube(ro,ri,h,p,axis=(0,0,1)):return cyl(ro,h,p,axis).cut(cyl(ri,h,p,axis))
def fuse(shapes):
    s=shapes[0]
    for t in shapes[1:]:s=s.fuse(t)
    return s.removeSplitter()
def beam(a,b,r):
    a,b=V(*a),V(*b);d=b-a
    return Part.makeCylinder(r,d.Length,a,d.normalize())
def prism(points,vec):
    chunks=[]
    for i in range(1,len(points)-1):
        q=[V(*points[0]),V(*points[i]),V(*points[i+1]),V(*points[0])]
        chunks.append(Part.Face(Part.makePolygon(q)).extrude(V(*vec)))
    return fuse(chunks)
def add(name,shape,group,color=dark,printed=False,mass=None,note='',side=0,trans=0):
    if printed and len(shape.Solids)>1:
        objs=[add(name if i==0 else name+'_segment_'+str(i+1),ss,group,color,True,None,note,side,trans) for i,ss in enumerate(shape.Solids)]
        return objs[0]
    o=doc.addObject('PartDesign::Feature' if printed else 'Part::Feature',name)
    o.Label=name.replace('_',' ');o.Shape=shape
    o.addProperty('App::PropertyString','Evidence','Engineering').Evidence=note or ('Designed geometry; print and fit verification pending' if printed else 'Simplified installation envelope; verify received part')
    o.addProperty('App::PropertyBool','Printable','Engineering').Printable=printed
    o.addProperty('App::PropertyBool','Installed','Engineering').Installed=not (name.startswith('P13_') and not P['guards_installed'])
    if not o.Installed:o.Label='OPTIONAL — '+o.Label
    o.addProperty('App::PropertyFloat','BudgetMass_g','Engineering').BudgetMass_g=(shape.Volume/1000*P['density_print_g_cm3'] if printed else (mass or 0))
    o.addProperty('App::PropertyString','Material','Engineering').Material='PETG planning density 1.24 g/cm3' if printed else 'Purchased / see BOM'
    o.ViewObject.ShapeColor=color;o.ViewObject.LineColor=(0.08,0.09,0.09);o.ViewObject.DisplayMode='Flat Lines' if group in ['Hardware','Electronics'] else 'Flat Lines';o.ViewObject.Transparency=trans
    groups[group].addObject(o)
    if side:moving[side].append(o)
    records.append(o)
    return o
def holes(s,coords,r,z,h):
    for x,y in coords:s=s.cut(cyl(r,h,(x,y,z)))
    return s
def screw(name,x,y,z,length=10,r=1.5,side=0):
    return add(name,cyl(r,length,(x,y,z-length)).fuse(cyl(r*1.8,2,(x,y,z))), 'Hardware',metal,side=side)
def route(name,points,diam,color,net,awg,source,dest,slack=0):
    # Swept smooth BSpline centerline and circular insulation envelope.
    curve=Part.BSplineCurve();curve.interpolate([V(*p) for p in points])
    edge=curve.toShape();path=Part.Wire([edge]);tangent=edge.tangentAt(edge.FirstParameter)
    section=Part.Wire([Part.makeCircle(diam/2,V(*points[0]),tangent)])
    sh=path.makePipeShell([section],True,False)
    clearance_section=Part.Wire([Part.makeCircle(diam/2+.6,V(*points[0]),tangent)])
    wire_channels[name]=path.makePipeShell([clearance_section],True,False)
    o=add(name,sh,'Wiring',color,note='Insulated wire envelope; hand dressed route; endpoint function not exact pad geometry')
    o.addProperty('App::PropertyString','Net','Electrical').Net=net
    o.addProperty('App::PropertyString','Endpoints','Electrical').Endpoints=source+' -> '+dest
    o.addProperty('App::PropertyInteger','AWG','Electrical').AWG=awg
    o.addProperty('App::PropertyLength','RouteLength','Electrical').RouteLength=edge.Length
    wire_records.append({'name':name,'net':net,'awg':awg,'length_mm':round(edge.Length,2),'cut_length_mm':math.ceil(edge.Length+slack+15),'from':source,'to':dest,'slack_extra_mm':slack})
    return o
# Structural tray with open battery pocket, rail webs, through bolts and strap slots.
tray=box(-58,-27,-36,116,54,3)
for xa,dx in [(-54,25),(-14,36),(39,20)]:tray=tray.cut(box(xa,-19,-37,dx,38,5))
tray=tray.fuse(box(-58,-27,-33,116,3,36)).fuse(box(-58,24,-33,116,3,36))
for xa in [-55,22]:
    for ya in [-28,23]:tray=tray.cut(box(xa,ya,-31,33,5,27))
for x in [-57,52]:
    for y in [-27,24]:tray=tray.cut(box(x,y-1,-28,12,5,24))
for x in [-25,33]:
    for y in [-24,20]:tray=tray.cut(box(x,y,-38,12,4,6))
for y in [-25.5,25.5]:
    for x in [-11,11]:tray=tray.cut(cyl(1.6,15,(x,y,-2)))
for xx in [-17,5]:
    for yy in [-29,22]:tray=tray.fuse(box(xx,yy,0,12,7,12))
tray=holes(tray,[(x,y) for x in [-11,11] for y in [-25.5,25.5]],1.6,0,14)
fore=prism([(46,-26,-36),(55,-26,-36),(78,-20,-36),(78,20,-36),(55,26,-36),(46,26,-36)],(0,0,3))
fore=fore.cut(box(56,-14,-37,15,28,5))
tray=tray.fuse(fore)
for xx in [3,61]:
    for yy in [-22,20]:tray=tray.cut(box(xx,yy,-38,10,2,7))
add('P01_Battery_keel',tray,'Airframe',dark,True)
# Center crossbeam, closed thin-wall box at z12..26, removable bolted root.
cross=box(-12,-84,12,24,168,14).cut(box(-10,-85,14,20,170,10))
cross=cross.fuse(box(-18,-33,8,36,66,4))
cross=cross.cut(box(-18,-19,7,36,38,5))
cross=holes(cross,[(x,y) for x in [-11,11] for y in [-25.5,25.5]],1.6,7,21)
for s in [-1,1]:
    # Servo outrigger and bearing-yoke joint at y=75/82.
    yy=22 if s==1 else -54
    cross=cross.fuse(box(-55,yy,24,45,32,3))
    cross=cross.fuse(beam((-48,s*48,24),(-10,s*75,14),2.5))
    cross=holes(cross,[(-49,s*78),(-31,s*78),(0,s*76)],1.6,10,20)
add('P02_Crossbeam',cross.removeSplitter(),'Airframe',olive,True)
# Avionics deck with isolated FC mounting positions (36x46 board, 30.5 holes).
deck=box(-27,-23,-5,54,46,2)
deck=holes(deck,[(x,y) for x in [-15.25,15.25] for y in [-15.25,15.25]],1.6,-6,5)
for x in [-24,24]:
    for y in [-23,20]:deck=deck.fuse(box(x-2,y,-6,4,6,4))
add('P03_Avionics_deck',deck,'Airframe',dark,True)
for x in [-15.25,15.25]:
    for y in [-15.25,15.25]:
        add('FC_grommet',tube(3,1.6,3,(x,y,-3)),'Hardware',(0.35,0.35,0.36))
        screw('FC_M3',x,y,3,10)
fc=holes(box(-23,-18,0,46,36,1.6),[(x,y) for x in [-15.25,15.25] for y in [-15.25,15.25]],2,0,2)
add('U1_Matek_F405_TE',fc,'Electronics',green,mass=10,note='Matek published 36x46 mm and 10g; pads/component positions approximate; 30.5mm mount to verify')
add('U1_CPU',box(-6,-6,1.6,12,12,1.4),'Electronics',dark)
add('U1_USB',box(17,-4,1.6,7,8,3),'Electronics',metal)
for y in [-15,15]:
    for x in [-18,-12,-6,0,6,12,18]:add('U1_pad',box(x-1,y-1,1.61,2,2,.1),'Electronics',(0.8,.62,.2))
for fcobj in records:
    if fcobj.Name.startswith(('U1_','FC_','P03_')):
        fs=fcobj.Shape.copy();fs.translate(V(0,0,6));fcobj.Shape=fs
add('B1_4S_1300_LiPo',box(P['battery_x']-38,-19,-31,76,38,31),'Electronics',(.20,.21,.23),mass=170,note='Tattu 4S1300 class; reserve 76x38x31mm and 170g including stock leads; final SKU to confirm')
add('B1_Label',box(9,-19.2,-26,45,.2,21),'Electronics',orange)
add('Battery_pad',box(0,-20,-33,78,40,2),'Hardware',(.22,.22,.23))
for x in [3,61]:
    strap=box(x,-22,-37,10,44,37.8).cut(box(x-1,-20,-36,12,40,36))
    add('Battery_hook_loop_strap',strap,'Hardware',(.1,.1,.1))
add('U2_Hobbywing_5A_UBEC',box(-81,-8.5,-16,50,17,10),'Electronics',(.13,.13,.15),mass=21,note='Hobbywing UBEC5A 50x17x10mm 21g; set output to 6.0V, servos only')
add('U3_RP1_receiver',box(-59,6,5,13,11,3),'Electronics',green,mass=2.2,note='RadioMaster RP1 V2 13x11x3mm, 2.2g including antenna; ELRS radio required')
add('C1_470uF_35V',cyl(5,16,(-44,-16,-21),(1,0,0)),'Electronics',(.1,.12,.15),mass=3)
add('J1_XT60',box(-22,-8,-24,16,16,8),'Electronics',(0.85,.60,.12),mass=4)
add('J2_4S_balance',box(-16,10,-27,7,13,6),'Electronics',(.88,.88,.82))
add('Power_splice_insulated',box(40,-7,9,12,14,5),'Electronics',(.35,.15,.13))
add('Buzzer_5V',cyl(5,5,(60,0,1)),'Electronics',dark,mass=2)
# Continuous utility-helicopter fuselage, rebuilt to eliminate patched skin and floating glazing.
stations=[(-255,3,-27,-19),(-225,7,-30,-8),(-175,13,-34,7),(-120,24,-39,21),(-95,30,-39,27),(-35,31,-39,27),(35,31,-39,27),(58,30,-39,12),(78,25,-38,5),(92,17,-34,-1),(101,8,-28,-8),(105,2.5,-19,-15)]
# Monotone Hermite profile sampling: preserves straight keel/roof without cubic-loft overshoot.
key_stations=stations[:]
def generic_profile_value(rows,index,x):
    xs=[p[0] for p in rows]; ys=[p[index] for p in rows]
    hs=[xs[i+1]-xs[i] for i in range(len(xs)-1)]
    ds=[(ys[i+1]-ys[i])/hs[i] for i in range(len(hs))]
    slopes=[ds[0]]
    for i in range(1,len(xs)-1):
        if ds[i-1]*ds[i]<=0:slopes.append(0)
        else:
            a=2*hs[i]+hs[i-1];b=hs[i]+2*hs[i-1]
            slopes.append((a+b)/(a/ds[i-1]+b/ds[i]))
    slopes.append(ds[-1])
    j=next((i for i in range(len(hs)) if x<=xs[i+1]),len(hs)-1)
    t=(x-xs[j])/hs[j]
    return (2*t**3-3*t**2+1)*ys[j]+(t**3-2*t**2+t)*hs[j]*slopes[j]+(-2*t**3+3*t**2)*ys[j+1]+(t**3-t**2)*hs[j]*slopes[j+1]
def profile_value(index,x):
    if index==3 and 35<=x<=58:return 27-(15/23)*(x-35)
    return generic_profile_value(key_stations,index,x)
xs=[]
for a,b in zip(key_stations,key_stations[1:]):
    n=math.ceil((b[0]-a[0])/7)
    xs.extend(a[0]+(b[0]-a[0])*i/n for i in range(n))
xs.append(key_stations[-1][0])
stations=[(x,*[profile_value(i,x) for i in [1,2,3]]) for x in xs]

def section(x,w,bot,top):
    mid=(bot+top)/2; ht=top-bot
    yz=[(-w,mid+.25*ht),(-.75*w,top),(.75*w,top),(w,mid+.25*ht),(w,mid-.3*ht),(.92*w,bot),(-.92*w,bot),(-w,mid-.3*ht)]
    return Part.makePolygon([V(x,y,z) for y,z in yz]+[V(x,*yz[0])])
import sys
sys.path.insert(0,str(ROOT/'scripts'))
from profile_surfaces import build_profile_solid
outer=build_profile_solid(key_stations,profile_value,breakpoints=(35,58))
inner=build_profile_solid(key_stations,profile_value,wall=1.0,cap_inset=1.2,breakpoints=(35,58))
hood=prism([(-26,-31,8),(-24,-31,20),(-14,-31,29),(13,-31,29),(24,-31,20),(26,-31,8)],(0,62,0))
hood_inside=prism([(-24,-29,6),(-22,-29,19),(-13,-29,27.5),(12,-29,27.5),(22,-29,19),(24,-29,6)],(0,58,0))
skin=outer.fuse(hood).cut(inner.fuse(hood_inside)).removeSplitter()
# Port sizes are tied to the crossbeam section, not broad holes across the cabin.
for yy in [-35,29]:skin=skin.cut(box(-13.5,yy,10.5,27,6,17))
for yy in [-35,27]:skin=skin.cut(box(17,yy,1,14,8,10))
# Rear harness exits under the engine cover and antenna feedthrough.
# Servo lead exits are cut to the routed harness below, without a rectangular opening.
skin=skin.cut(cyl(2.7,26,(-114,0,8)))
tail_skin=skin.common(box(-270,-40,-45,165,80,140))
cabin=skin.common(box(-105,-40,-45,250,80,140))
upper=cabin.common(box(-107,-40,-22,252,80,100))
lower=cabin.common(box(-107,-40,-45,252,80,23))
glass_region=upper.common(box(38,-40,-15,34,80,60))
mullions=glass_region.common(box(37,-1.1,-23,80,2.2,65)).fuse(glass_region.common(box(58,-40,-23,1.5,80,65)))
glass=glass_region.cut(mullions)
upper=upper.cut(glass_region).fuse(mullions).removeSplitter()
# Shallow physical cargo-door seams, confined to 0.22mm of the exterior skin.
seam_skin=outer.cut(build_profile_solid(key_stations,profile_value,wall=.22,cap_inset=.3,breakpoints=(35,58)))
for side in [-1,1]:
    yy=22 if side==1 else -40
    for xa,xb in [(-94,-56),(-51,-13)]:
        mask=fuse([box(xa,yy,-20,.55,18,42),box(xb,yy,-20,.55,18,42),box(xa,yy,21.45,xb-xa+.55,18,.55),box(xa,yy,-20,xb-xa+.55,18,.55)])
        upper=upper.cut(seam_skin.common(mask))
side_glass=[]
for side in [-1,1]:
    window_mask=box(-89,22 if side==1 else -40,-10,28,18,28).fuse(box(-46,22 if side==1 else -40,-10,28,18,28)).fuse(box(18,22 if side==1 else -40,-10,18,18,27))
    panel=upper.common(window_mask)
    side_glass.append(panel)
    upper=upper.cut(panel)
for idx,panel in enumerate(side_glass):add('P09_Cabin_side_glazing_'+str(idx),panel,'Shell',(.13,.19,.22),True,note='Fitted separate glazing; removed from upper shell, no overlapping sheets')
add('P06_Cabin_upper',upper,'Shell',olive,True,note='Continuous fitted upper skin and physical windshield mullions; no overlapping color sheets')
add('P07_Cabin_lower',lower,'Shell',olive,True,note='Straight cabin keel and low nose line; electronics envelope checked; seam at z=-22mm')
add('P08_Windshield',glass,'Shell',(.13,.19,.22),True,note='Separate fitted cosmetic glazing panels; actual thickness 1.0mm class; not flight visibility glazing')
add('P19_Tapered_tail_boom',tail_skin,'Shell',olive,True,note='Continuous tail profile; split at x=-105mm for printer fit; internal splice not released')
# Tail backbone supports the long boom; closed tube avoids a broad exposed flat plank.
spine=beam((-241,0,-20),(-90,0,12),1.5).fuse(box(-99,-6,8,21,12,6)).removeSplitter()
add('P04_Tail_spine',spine,'Airframe',dark,True,note='Long tail spine; rear segment follows rising boom; fit/reinforcement proof required')
fin=prism([(-256,0,-24),(-229,0,-24),(-267,0,43),(-281,0,46)],(0,1.3,0))
add('P05_Vertical_tail_fin',fin,'Shell',olive,True)
stab=prism([(-239,-24,-14),(-224,-24,-14),(-208,0,-14),(-224,24,-14),(-239,24,-14)],(0,0,1.2))
add('P05_Horizontal_tailplane',stab,'Shell',olive,True)
for side in [-1,1]:
    def wing_section(y,sc):
        pts=[(-20*sc,y,13),(-14*sc,y,29),(9*sc,y,32),(26*sc,y,24),(18*sc,y,12)]
        return Part.makePolygon([V(*q) for q in pts]+[V(*pts[0])])
    out=Part.makeLoft([wing_section(side*31,1),wing_section(side*83,.65)],True,True)
    inn=out.makeOffsetShape(-1.0,.05,fill=False)
    shoulder=out.cut(inn).cut(box(-13,-90,7,26,180,20))
    add('P17_Shoulder_cowl_'+str(side),shoulder,'Shell',olive,True)
    # Engine-style fairing over each servo: an open bottom and defined shaft hole.
    # Smooth tapered nacelle; vertical service sides clear the actual servo envelope.
    cap_st=[(-81,4,22,29),(-73,10,22,37),(-61,15.2,22,42),(-53,15.2,22,43),(-28,15.2,22,43),(-22,11,22,39),(-18,5,22,32)]
    def cap_profile(index,x):return generic_profile_value(cap_st,index,x)
    cap_outer=build_profile_solid(cap_st,cap_profile)
    cap_inner=build_profile_solid(cap_st,cap_profile,wall=1.05,cap_inset=1.0)
    cap_outer.translate(V(0,side*35,0));cap_inner.translate(V(0,side*35,0))
    cover=cap_outer.cut(cap_inner).cut(box(-80,side*35-16,20,61,32,4))
    cover=cover.cut(cyl(3,10,(-35,side*43,35),(0,side,0)))
    cover=cover.cut(cyl(3.5,9,(-16,side*35,33),(-1,0,0)))
    cover=cover.cut(box(-64,19 if side==1 else -33,24,10,14,13))
    for xx in [-70,-66,-62]:cover=cover.cut(box(xx,20 if side==1 else -50,32,1.3,30,2))
    add('P20_Servo_engine_cowl_'+str(side),cover,'Shell',olive,True)
    # Narrow covered cable raceway beneath the leading side of each shoulder.
    race=box(10,31 if side==1 else -85,1,17,54,10).cut(box(11.2,32.2 if side==1 else -83.8,2.2,14.6,51.6,7.6))
    add('P22_Cable_raceway_'+str(side),race,'Shell',dark,True,note='Removable raceway; keeps fixed phase extensions hidden and accessible; hinge loop remains free')
    # Black Hawk style fixed wheel gear; printed wheels are fit prototypes with M2 axle bores.
    leg=fuse([beam((35,side*26,-27),(24,side*37,-47),2.4),beam((16,side*25,-30),(24,side*37,-47),1.8),box(29,23 if side==1 else -28,-32,13,5,5)])
    leg=leg.fuse(cyl(3.2,4.5,(24,side*36,-49),(0,side,0))).cut(cyl(1.1,12,(24,side*35,-49),(0,side,0)))
    add('P10_Main_gear_'+str(side),leg,'Airframe',dark,True)
    wheel=Part.makeTorus(5,2,V(24,side*43,-49),V(0,1,0)).fuse(tube(3.5,1.1,4,(24,side*43-2,-49),(0,1,0))).removeSplitter()
    add('P23_Main_wheel_'+str(side),wheel,'Airframe',dark,True,note='Printed 14mm diameter wheel; M2 metal axle and positive retention to fit-test')
    add('Main_gear_M2_axle_'+str(side),cyl(1,12,(24,side*35,-49),(0,side,0)),'Hardware',metal)
rearleg=fuse([beam((-175,0,-28),(-186,0,-40),2.2),box(-193,-3.5,-52,10,7,11)])
rearleg=rearleg.cut(box(-194,-1.9,-53,12,3.8,10)).cut(cyl(1.1,9,(-188,-4.5,-49),(0,1,0)))
add('P24_Tailwheel_fork',rearleg,'Airframe',dark,True)
rearwheel=Part.makeTorus(4,1.5,V(-188,0,-49),V(0,1,0)).fuse(tube(2.8,1.1,3,(-188,-1.5,-49),(0,1,0))).removeSplitter()
add('P25_Tailwheel',rearwheel,'Airframe',dark,True)
add('Tailwheel_M2_axle',cyl(1,9,(-188,-4.5,-49),(0,1,0)),'Hardware',metal)

# Rear tire radius is 1.5mm smaller; lower its assembly to share the main-wheel ground plane.
for gear in records:
    if gear.Name.startswith(('P24_','P25_','Tailwheel_')):
        gs=gear.Shape.copy();gs.translate(V(0,0,-1.5));gear.Shape=gs

# Complete independent tilt pods. Fixed yokes, four metal bearings, split metal trunnions.
for side in [1,-1]:
    tag='L' if side==1 else 'R';cy=117*side; grp='LeftTilt' if side==1 else 'RightTilt'
    def mirror(sh):
        if side==1:return sh
        return sh.mirror(V(0,0,0),V(0,1,0))
    yoke=fuse([box(-9,73,8,18,74,4),box(-8,91,11,16,4,32),box(-8,139,11,16,4,32)])
    for yy in [91,139]:yoke=yoke.cut(cyl(5.1,6,(0,yy-1,35),(0,1,0)))
    yoke=holes(yoke,[(0,76),(0,82)],1.6,7,7)
    add('P11_'+tag+'_bearing_yoke',mirror(yoke),'Airframe',olive,True)
    for yy in [91,139]:
        add(tag+'_MR104_bearing',mirror(tube(5,2,4,(0,yy,35),(0,1,0))),'Hardware',metal,mass=1.3,note='MR104 4x10x4mm bearing envelope; fit coupon required')
    for yy,length in [(86,14),(134,14)]:
        add(tag+'_M4_trunnion',mirror(cyl(2,length,(0,yy,35),(0,1,0))),'Hardware',metal,mass=2,side=side,note='Metal smooth shoulder trunnion with spacers/retention; detailed stack needs received hardware')
    # Motor cradle plus integral crank bridging over inboard bearing.
    cradle=box(-18,99,30,36,36,4)
    for yy in [99,131]:cradle=cradle.fuse(box(-6,yy,31,12,4,9))
    cradle=cradle.fuse(box(-4,99,33,8,4,19.5)).fuse(box(-4,50,45.5,8,52,7))
    cradle=cradle.cut(cyl(1.1,8,(0,49,49),(0,1,0)))
    cradle=cradle.cut(cyl(2.1,40,(0,97,35),(0,1,0)))
    cradle=holes(cradle,[(x,117+y) for x in [-8,8] for y in [-9.5,9.5]],1.6,29,7)
    cradle=cradle.cut(cyl(4.2,7,(0,117,29)))
    add('P12_'+tag+'_motor_cradle',mirror(cradle),grp,orange,True,side=side)
    motor=cyl(13.95,16.7,(0,117,34)).fuse(cyl(2.5,15,(0,117,50.7)))
    add('M_'+tag+'_RS2205_2300KV',mirror(motor),grp,dark,mass=30,side=side,note='EMAX drawing 27.9mm dia,31.7 overall,16x19 M3 pattern; internal detail omitted')
    add(tag+'_Motor_bell_band',mirror(tube(14,13.8,4,(0,117,45))),grp,(.12,.13,.14),side=side)
    for x in [-8,8]:
        for dy in [-9.5,9.5]:add(tag+'_motor_M3',cyl(1.5,7,(x,side*(117+dy),29)).fuse(cyl(2.7,2,(x,side*(117+dy),27))),'Hardware',metal,side=side,note='M3 bottom-entry screw envelope; verify 3mm engagement without touching windings')
    # Commercial prop silhouette; intentionally not exported as printable.
    blade=prism([(5,113,58),(20,109,58),(63.5,112,58),(62,121,58),(18,123,58),(5,120,58)],(0,0,1.5))
    blade2=blade.copy();blade2.rotate(V(0,117,58),V(0,0,1),180)
    prop=fuse([blade,blade2,tube(6.5,2.5,5,(0,117,56))])
    prop.rotate(V(0,117,58),V(0,0,1),side*24)
    add('PROP_'+tag+'_HQ5045BN_BUY_DO_NOT_PRINT',mirror(prop),grp,dark,mass=3,side=side,note='Commercial CW/CCW 5 inch prop; visualization only, not an aerodynamic CAD blade')
    guard=tube(71.1,69.5,12,(0,117,51))
    for angle in [0,120,240]:
        a=math.radians(angle)
        guard=guard.fuse(beam((16*math.cos(a),117+16*math.sin(a),32),(70*math.cos(a),117+70*math.sin(a),52),1.8))
    add('P13_'+tag+'_tilting_guard',mirror(guard.removeSplitter()),grp,olive,True,side=side,note='Light visual/stand-off ring; no rotor containment or positive thrust augmentation credit; spoke bonds require proof')
    # Digital servo horizontal, output axis parallel to aircraft Y.
    servo=box(-52.1,23.5,30,23.2,23,10).fuse(cyl(2,4.8,( -35,46.2,35),(0,1,0)))
    add('A_'+tag+'_BMS115WVplus',mirror(servo),'Electronics',dark,mass=12,note='Blue Bird BMS-115WV+: 23.2x10x23mm, catalog 11+/-0.5g; 12g planning; 6V 5.5kgcm catalog torque, 0.13s/60deg no-load; exact spline and ear positions provisional')
    horn=beam((-35,52,35),(-35,52,49),2)
    add(tag+'_OEM_servo_horn',mirror(horn),'Hardware',(.87,.86,.8),mass=.8)
    link=beam((-35,52,49),(0,52,49),1)
    add(tag+'_M2_ball_link',mirror(link),'Hardware',metal,mass=2,note='35mm center-to-center linkage at neutral; equal14mm horns; spherical ends required')
    for x in [-35,0]:add(tag+'_ball_joint',mirror(Part.makeSphere(2.4,V(x,52,49))),'Hardware',dark)
    clamp=box(-55,22,26.5,29,30,2.5).cut(box(-53,23,26,25,27,5))
    # keep a connected rail pair with aft bridge
    add('P14_'+tag+'_servo_retainer',mirror(clamp),'Airframe',orange,True,note='Prototype retainer; exact OEM mounting ears and screw seats require measurement')
    esc=box(29,side*14-6,3,27,12,5)
    add('ESC_'+tag+'_Lightning30A',esc,'Electronics',dark,mass=8,note='Reserve 27x12x5mm 8g per ESC; final heatshrink dimension must be measured; no BEC')
    # ESC mounts + insulation retained with a tie.
    add('P15_'+tag+'_ESC_tray',box(27,side*14-8,1,31,16,2),'Airframe',olive,True)
    # Primary branches tucked inside body. Red/black kept adjacent.
    route(tag+'_ESC_VBAT',[(46,0,12),(42,side*7,10),(31,side*14,8)],2.5,(.85,.09,.05),'VBAT',18,'Power splice +','ESC '+tag+' +')
    route(tag+'_ESC_GND',[(46,3,12),(43,side*8,10),(34,side*14,8)],2.5,(.08,.08,.09),'GND',18,'Power splice -','ESC '+tag+' -')
    for k,color in enumerate([(.85,.68,.10),(.16,.28,.66),(.70,.15,.12)]):
        # Service loop below/aft of pivot; phase wires must flex as pod tilts.
        route(tag+'_Phase_'+str(k),[(53,side*(12+k*2),6),(35,side*(22+k*2),5),(24,side*(31+k*2),6),(12+k*3,side*55,6),(12+k*3,side*83,6),(24+k*2,side*99,18),(22+k*2,side*113,36),(13.5,side*(115+k*2),37)],2.5,(.12,.13,.14),'PHASE_'+tag+str(k),18,'ESC '+tag+' phase'+str(k),'Motor '+tag+' phase'+str(k),20)
    for k,color in enumerate([(.88,.39,.1),(.75,.1,.08),(.10,.10,.10)]):
        route(tag+'_Servo_'+str(k),[(-52,side*(25+k*2),31),(-58,side*(25+k*2),27),(-54,side*(20+k*2),10),(-43+k*2,side*17,5),((-8 if k==0 else -38),side*(12 if k==0 else 2+k*2),(10 if k==0 else -11))],1.3,color,('SERVO_'+tag if k==0 else '6V_SERVO' if k==1 else 'GND'),24,'Servo '+tag,('FC S9/S10' if k==0 else 'UBEC output'))
    route(tag+'_ESC_signal',[(13,side*15,8),(22,side*22,5),(39,side*19,5)],.9,(.9,.9,.9),'ESC_'+tag,26,'FC S1/S2','ESC '+tag+' signal')
    route(tag+'_ESC_signal_ground',[(16,side*15,8),(25,side*24,5),(42,side*19,5)],.9,(.1,.1,.1),'GND',26,'FC GND','ESC '+tag+' signal GND')
# Power, FC regulated supply, receiver, balance harness and antenna.
route('Battery_stock_positive',[(1,-5,-10),(-3,-7,-14),(-7,-5,-20)],3.5,(.85,.1,.06),'VBAT',14,'B1 pack +','XT60 battery half +')
route('Battery_stock_negative',[(1,5,-10),(-3,7,-14),(-7,5,-20)],3.5,(.08,.08,.09),'GND',14,'B1 pack -','XT60 battery half -')
route('B1_positive',[(-20,-5,-20),(-24,-14,-17),(-18,-21.25,-16),(-6,-21.25,-16),(12,-21.25,-16),(26.5,-21.25,-16),(26.5,-22.25,-8),(26.5,-22.25,0),(26.5,-22.25,10),(31,-18,13),(46,-3,12)],3.5,(.88,.1,.06),'VBAT',14,'XT60 +','Power splice +')
route('B1_negative',[(-20,5,-20),(-24,14,-17),(-18,21.25,-16),(-6,21.25,-16),(12,21.25,-16),(26.5,21.25,-16),(26.5,22.25,-8),(26.5,22.25,0),(26.5,22.25,10),(31,18,13),(46,3,12)],3.5,(.08,.08,.09),'GND',14,'XT60 -','Power splice -')
for k,color in enumerate([(.8,.1,.08),(.08,.08,.08)]):
    route('UBEC_input_'+str(k),[(45,(-4 if k==0 else 4),12),(25,-19+k,7),(0,-19+k,5),(-30,-18+k*2,4),(-32,-4+k*6,-11)],1.6,color,'VBAT' if k==0 else 'GND',22,'Power splice','UBEC input')
    route('FC_input_'+str(k),[(45,k*4,12),(30,5+k*3,12),(20,5+k*3,10),(13,k*4,8)],1.1,color,'VBAT' if k==0 else 'GND',26,'Power splice','FC battery input')
    route('Capacitor_'+str(k),[(45,-3+k*6,12),(25,-20+k,7),(0,-20+k,5),(-28,-20+k,5),(-35,-20+k*2,-3),(-28,-18+k*4,-21)],1.1,color,'VBAT' if k==0 else 'GND',24,'Power splice','C1')
for k,color in enumerate([(.8,.1,.08),(.08,.08,.08),(.1,.5,.9),(.9,.9,.85)]):
    route('Receiver_'+str(k),[(-48,8+k*2,7),(-39,10+k*2,7),(-23,10+k*2,8)],.9,color,['5V_FC','GND','CRSF_TX','CRSF_RX'][k],26,'RP1 '+['5V','GND','TX','RX'][k],'FC '+['5V','GND','RX2','TX2'][k])
for k in range(5):route('Balance_'+str(k),[(1,10,-27+k),(-4,16,-29+k),(-12,21,-24+k)],.8,(.12,.12,.13) if k<4 else (.8,.1,.1),'CELL_TAP_'+str(k),26,'B1 balance tap','J2 pin '+str(k+1))
route('Antenna_coax',[(-57,14,7),(-75,10,20),(-100,3,21),(-114,0,22),(-114,0,25),(-114,0,29),(-114,0,32)],1.1,(.12,.12,.13),'RF',30,'RP1 UFL','T antenna')
add('RP1_T_antenna',beam((-114,-32.5,32),(-114,32.5,32),1),'Electronics',dark)
add('P16_Antenna_mast',tube(2.5,1.9,10,(-114,0,23)),'Airframe',orange,True)
for k in [0,1]:route('Buzzer_wire_'+str(k),[(60+k*2,0,3),(65,6+k*2,3),(18,11+k*2,8)],.8,[(.8,.1,.08),(.1,.1,.1)][k],'BUZZER+' if k==0 else 'BUZZER-',26,'Buzzer','FC buzzer pad')
# Defined small service channels where neutral harnesses pass through printed covers.
# 0.6 mm radial assembly clearance, not broad styling cutouts.
channel_pairs=[]
for tag,sidekey in [('L','1'),('R','_1')]:
    for k in range(3):
        channel_pairs += [(tag+'_Phase_'+str(k),'P22_Cable_raceway_'+sidekey), (tag+'_Phase_'+str(k),'P06_Cabin_upper')]
        channel_pairs += [(tag+'_Servo_'+str(k),'P20_Servo_engine_cowl_'+sidekey),(tag+'_Servo_'+str(k),'P06_Cabin_upper')]
channel_pairs += [('B1_positive','P01_Battery_keel'),('B1_negative','P01_Battery_keel'),('B1_positive','P03_Avionics_deck'),('B1_negative','P03_Avionics_deck')]
channel_pairs += [('Antenna_coax','P06_Cabin_upper'),('Antenna_coax','P19_Tapered_tail_boom'),('B1_negative','P15_L_ESC_tray'),('B1_positive','P15_R_ESC_tray')]
for wire_name,part_name in channel_pairs:
    part=doc.getObject(part_name)
    if part:
        part.Shape=part.Shape.cut(wire_channels[wire_name]).removeSplitter()
        part.Evidence += '; locally cleared harness passage with 0.6mm radial assembly allowance'

# Physical airframe bolts; installation miscellany mass budgeted separately.
for x in [-11,11]:
    for y in [-25.5,25.5]:screw('Beam_keel_M3',x,y,28,22)
for side in [-1,1]:
    for y in [76,82]:screw('Yoke_joint_M3',0,side*y,14,10)
# Reference volumetric sweeps off by default.
for side in [-1,1]:
    disk=cyl(63.5,4,(0,side*117,56))
    add('Rotor_disc_reference_'+str(side),disk,'Reference',(.3,.7,.85),trans=85).ViewObject.Visibility=False
    for ang in [-25,25]:
        d=disk.copy();d.rotate(V(0,side*117,35),V(0,1,0),ang)
        add('Tilt_limit_'+str(side)+'_'+str(ang),d,'Reference',(.9,.5,.12),trans=90).ViewObject.Visibility=False
for o in records:
    if o.Printable:o.BudgetMass_g=o.Shape.Volume/1000*P['density_print_g_cm3']
doc.recompute()
sheet=doc.addObject('Spreadsheet::Sheet','DesignBasis')
for row,(k,v) in enumerate(P.items(),1):sheet.set('A'+str(row),k);sheet.set('B'+str(row),str(v))
sheet.set('A12','Status');sheet.set('B12','R4 ENGINEERING PROTOTYPE - NOT FLIGHT RELEASED')
sheet.setColumnWidth('A',225);sheet.setColumnWidth('B',340)
physical=[o for o in records if o not in groups['Reference'].Group]
inventory=[]
for o in physical:
    bb=o.Shape.BoundBox
    item={'name':o.Name,'label':o.Label,'printed':o.Printable,'installed':o.Installed,'volume_mm3':o.Shape.Volume,'mass_g':o.BudgetMass_g,'center_mm':([sum(s.CenterOfMass[j]*s.Volume for s in o.Shape.Solids)/sum(s.Volume for s in o.Shape.Solids) for j in range(3)] if o.Shape.Solids else [0,0,0]),'bbox_mm':[bb.XLength,bb.YLength,bb.ZLength],'valid':o.Shape.isValid(),'solids':len(o.Shape.Solids),'evidence':o.Evidence}
    inventory.append(item)
    if o.Printable:
        shape=o.Shape.copy();bb=shape.BoundBox;shape.translate(V(-bb.XMin,-bb.YMin,-bb.ZMin))
        mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.12,AngularDeflection=.25,Relative=False)
        stl_dir=ROOT/'stl' if o.Installed else ROOT/'stl/optional_guards'
        stl_dir.mkdir(exist_ok=True)
        mesh.write(str(stl_dir/(o.Name+'.stl')))
(ROOT/'engineering/inventory.json').write_text(json.dumps(inventory,indent=2))
(ROOT/'engineering/wiring_routes.json').write_text(json.dumps(wire_records,indent=2))
# Preserve reference to original placements for articulate macro.
(ROOT/'engineering/moving_objects.json').write_text(json.dumps({str(k):[o.Name for o in v] for k,v in moving.items()},indent=2))
doc.recompute()
for o in physical:
    o.ViewObject.DisplayMode='Flat Lines'
    o.ViewObject.Deviation=.10;o.ViewObject.AngularDeflection=10.0
    if o in groups['Shell'].Group or o in groups['Airframe'].Group:
        mats=list(o.ViewObject.ShapeAppearance)
        for mat in mats:
            mat.SpecularColor=(0.,0.,0.);mat.Shininess=0.;mat.AmbientColor=(.22,.22,.22)
            if 'glazing' in o.Name or 'Windshield' in o.Name:mat.SpecularColor=(.18,.18,.18);mat.Shininess=.3
        o.ViewObject.ShapeAppearance=mats
    if o in groups['Shell'].Group:
        o.ViewObject.LineColor=(.14,.15,.16);o.ViewObject.LineWidth=1.

for o in physical:
    if not o.Installed:o.ViewObject.Visibility=False
vp=App.ParamGet('User parameter:BaseApp/Preferences/View')
vp.SetUnsigned('BackgroundColor',0xDEE2E6FF);vp.SetBool('Simple',True);vp.SetBool('Gradient',False)
Gui.activeDocument().activeView().viewAxonometric();Gui.activeDocument().activeView().fitAll()
doc.saveAs(str(ROOT/'cad/Kestrel_Mini_R4.FCStd'))
Part.export([o for o in physical if o.Installed],str(ROOT/'cad/Kestrel_Mini_R4.step'))
Gui.activeDocument().activeView().saveImage(str(ROOT/'images/exterior.png'),1800,1400,'Current')
for o in groups['Shell'].Group:o.ViewObject.Visibility=False
Gui.activeDocument().activeView().saveImage(str(ROOT/'images/electronics_wiring.png'),1800,1400,'Current')
for o in groups['Shell'].Group:o.ViewObject.Visibility=True
print(json.dumps({'parts':len(physical),'print_parts':sum(o.Printable for o in physical),'printed_mass_g':sum(o.BudgetMass_g for o in physical if o.Printable),'purchased_allocated_g':sum(o.BudgetMass_g for o in physical if not o.Printable),'invalid':[o.Name for o in physical if not o.Shape.isValid()]}))
