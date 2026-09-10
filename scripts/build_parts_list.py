"""Generate human-readable purchase/print lists from explicit selections and CAD inventory."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
# qty, specification, mass each g, selection / interface limits, reference ID
rows=[
(2,'EMAX RS2205 2300KV motor',30,'Genuine original RS2205; 16 x 19 mm M3 mounting. Verify lead exit, shaft and screw engagement.','MOTOR'),
(2,'HQProp HQ5045BN two-blade propeller',3,'One CW and one CCW; exact blade from thrust table. Buy commercial props; never print these.','MOTOR'),
(2,'EMAX Lightning 30A ESC',8,'Legacy BLHeli; 27 x 12 x 5 mm model reserve. Confirm actual dimensions, cooling and supported input protocol.','ESC'),
(2,'Blue Bird BMS-115WV+ tilt servo',12,'6 V; 23.2 x 10 x 23 mm body. Catalog 11 +/-0.5 g; 12 g planning allowance. Ears/spline stack provisional.','SERVO'),
(1,'Matek F405-TE flight controller',10,'36 x 46 mm; verify 30.5 mm mount spacing and exact board variant. Bicopter firmware support required.','FC'),
(1,'Hobbywing UBEC 5A',21,'50 x 17 x 10 mm; set to 6 V for servos only. 5 A continuous rating; actual simultaneous servo demand unknown.','BEC'),
(1,'RadioMaster RP1 V2 ELRS 2.4 GHz receiver',2.2,'13 x 11 x 3 mm, antenna included in allocation. Requires compatible ELRS transmitter; FlySky AFHDS radio is not compatible.','RX'),
(1,'4S 1300 mAh LiPo - exact SKU OPEN',170,'76 x 38 x 31 mm maximum planning envelope, including stock leads in mass. Must support measured pack current and fit; no C-label guarantee.','BATTERY'),
(1,'XT60 aircraft-side connector',4,'Mate to battery connector; insulated solder cups and strain relief. Stock battery half is counted with battery.',''),
(1,'470 uF 35 V low-ESR capacitor',3,'Reserve diameter 10 x 16 mm; confirm ripple rating and polarity. Lead length affects suppression.',''),
(1,'5 V active buzzer',2,'Reserve diameter 10 x 5 mm; verify compatibility with FC buzzer output and polarity.',''),
(4,'MR104 bearing, 4 x 10 x 4 mm',1.3,'Metal bearings; confirm fit, shields, axial support and smooth rotation.',''),
(4,'4 mm metal trunnion / shoulder pin',2,'Nominal 14 mm modeled length. Final shoulders, spacers, retaining method and bearing stack OPEN.',''),
(2,'OEM-compatible 25T servo horn',0.8,'14 mm effective pivot-to-ball radius. Verify spline and screw; do not substitute a loose printed spline.','SERVO'),
(2,'M2 pushrod with ball-link ends',2,'35 mm center-to-center modeled link; four ball joints total. Verify travel, clearance and attachment geometry.','')]
sources={
'MOTOR':('EMAX RS2205 and test chart','https://emaxmodel.com/products/emax-rs2205-racespec-motor-cooling-series'),
'ESC':('EMAX motor / Lightning ESC combination','https://shop.emaxmodel.com/products/emax-rs2205-2300kv-2600kv-racespec-brushless-motor-with-3-4s-30a-blheli-lightning-esc-power-combo'),
'SERVO':('Blue Bird BMS-115WV+ catalog','https://www.blue-bird-model.com/products_detail/55.htm'),
'FC':('Matek F405-TE specifications and pinout','https://www.mateksys.com/?portfolio=f405-te'),
'BEC':('Hobbywing UBEC 5A','https://www.hobbywing.com/en/products/ubec-5a93.html'),
'RX':('RadioMaster RP1','https://www.radiomasterrc.com/products/rp1-expresslrs-2-4ghz-nano-receiver'),
'BATTERY':('Tattu battery family reference - not a selected SKU','https://www.genstattu.com/blog/tattu-fpv-battery-recommend'),
'PRINTER':('Elegoo Centauri Carbon','https://www.elegoo.com/pages/elegoo-centauri-carbon'),
'MIXER':('Betaflight mixer documentation','https://betaflight.com/docs/wiki/guides/current/Mixer'),
'AERO':('NASA drag equation','https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/drag-equation/'),
'COEFFICIENT':('NASA coefficient and flow-condition limitations','https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/drag-coefficient/')}
parts=[dict(quantity=q,part=n,mass_each_g=m,allocated_total_g=q*m,notes=note,reference=s,source_url=sources[s][1] if s else None) for q,n,m,note,s in rows]
assert abs(sum(p['allocated_total_g'] for p in parts)-337)<1e-6
(R/'docs/parts.json').write_text(json.dumps(parts,indent=2)+'\n')
(R/'docs/references.json').write_text(json.dumps(sources,indent=2)+'\n')
text=['# Parts list - R4 fit prototype','',
'No hardware has been purchased. This is a selection and allocation list, not a fully resolved purchase order. Vendor links are specification references; stock, prices and exact received dimensions are not guaranteed. Battery SKU, trunnion retention, mounting interfaces and loaded actuator performance must be resolved before an airworthy build.','',
'## Purchased aircraft parts','', '| Qty | Item | Allocated total g | Selection / fit notes |','|---:|---|---:|---|']
for p in parts:
 name=f"[{p['part']}]({p['source_url']})" if p['source_url'] else p['part']
 text.append(f"| {p['quantity']} | {name} | {p['allocated_total_g']:.1f} | {p['notes']} |")
text+=['','Purchased allocations total **337.0 g**. Wires, solder, remaining connectors and small installation hardware are allocated below, not added again to the above component envelopes.','',
'## Installation materials and unresolved hardware','',
'| Allowance | Budget g | Contents |','|---|---:|---|',
'| Harness and secondary connectors | 36 | Silicone wire by schedule; insulation, solder, servo plugs and power splice. Existing stock leads may cover some modeled lengths. |',
'| Fasteners, spacers and retention | 25 | M3/M2 screws, nuts, washers, FC grommets, wheel axles and pin retainers. Final stack and retention are not released. |',
'| Straps, foam, ties and insulation | 8 | Two nominal 10 mm battery straps; battery pad, FC isolation and strain relief. |',
'| Adhesive and light finish | 8 | Tail/shell joints and restrained matte-black finish. Verify adhesion/material and count actual paint mass. |','',
'Initial modeled screw schedule: 8 motor M3 screws with 7 mm under-head length, 4 FC M3 x10, 4 beam/keel M3 x22, 4 yoke M3 x10, two diameter-2 x12 mm main wheel axles and one diameter-2 x9 mm tailwheel axle. These are CAD dimensions, not approved screw lengths: check motor winding clearance, printed wall engagement, nuts and washers before use. Four FC isolators and four ball-link ends are represented; avoid double-counting ends already supplied with link assemblies. Servo ear screws, tail splice, shell closure and trunnion retention still require final detailing.','',
'Wire sizes: 14 AWG main power, 18 AWG ESC supply and motor phases, 22 AWG UBEC input, 24 AWG servo supply/signals and capacitor leads, 26 AWG low-current FC/RX signals. Use the [42-route wire schedule](../engineering/WIRE_SCHEDULE.md) for modeled lengths and termination allowances. Antenna coax and battery balance leads represent supplied assemblies, not an instruction to fabricate RF antennas or modify the pack.','',
'## Print list','',
'One of each installed STL; 40 pieces total. Names identify mirrored and separated pieces explicitly. Two optional guards add 25.4 g and are omitted from the baseline mass. All masses below assume the full CAD material volume at 1.24 g/cm^3; these are not slicer predictions. All mesh bounds fit the 256 mm printer cube, but orientation, supports, brim and tolerances must be checked in the slicer.','',
'| STL / part | Qty | CAD mass g | Bounding box mm |','|---|---:|---:|---|']
inv=json.loads((R/'engineering/inventory.json').read_text());prints=[o for o in inv if o['printed']]
for o in prints:
 path='../stl/'+('' if o['installed'] else 'optional_guards/')+o['name']+'.stl'
 text.append(f"| [{o['name']}]({path}){' (optional)' if not o['installed'] else ''} | 1 | {o['mass_g']:.2f} | "+' x '.join(f'{d:.1f}' for d in o['bbox_mm'])+' |')
text+=['','## Ground equipment - excluded from flight mass','',
'- ELRS 2.4 GHz transmitter or a compatible transmitter/module combination.','- LiPo balance charger supporting 4S, suitable supply and charging accessories.','- Scale with gram resolution, calipers, multimeter and current/voltage logging.','- Restrained thrust stand, protected actuator/load fixture and vibration measurement.','- Soldering equipment, heat-shrink, drivers and bearing/fastener fit coupons.','- Suitable filament and slicer for Centauri Carbon; qualify the actual material/process on loaded and heated joints.','',
'Commercial propellers, motors, bearings, metal pins, fasteners and servo gears remain purchased parts. More printing does not justify unqualified rotating blades or unreliable pivots.']
(R/'docs/PARTS_LIST.md').write_text('\n'.join(text)+'\n')
print('Parts list:',len(parts),'purchase rows,',len(prints),'print files')
