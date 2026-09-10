# Parts list - R4 fit prototype

No hardware has been purchased. This is a selection and allocation list, not a fully resolved purchase order. Vendor links are specification references; stock, prices and exact received dimensions are not guaranteed. Battery SKU, trunnion retention, mounting interfaces and loaded actuator performance must be resolved before an airworthy build.

## Purchased aircraft parts

| Qty | Item | Allocated total g | Selection / fit notes |
|---:|---|---:|---|
| 2 | [EMAX RS2205 2300KV motor](https://emaxmodel.com/products/emax-rs2205-racespec-motor-cooling-series) | 60.0 | Genuine original RS2205; 16 x 19 mm M3 mounting. Verify lead exit, shaft and screw engagement. |
| 2 | [HQProp HQ5045BN two-blade propeller](https://emaxmodel.com/products/emax-rs2205-racespec-motor-cooling-series) | 6.0 | One CW and one CCW; exact blade from thrust table. Buy commercial props; never print these. |
| 2 | [EMAX Lightning 30A ESC](https://shop.emaxmodel.com/products/emax-rs2205-2300kv-2600kv-racespec-brushless-motor-with-3-4s-30a-blheli-lightning-esc-power-combo) | 16.0 | Legacy BLHeli; 27 x 12 x 5 mm model reserve. Confirm actual dimensions, cooling and supported input protocol. |
| 2 | [Blue Bird BMS-115WV+ tilt servo](https://www.blue-bird-model.com/products_detail/55.htm) | 24.0 | 6 V; 23.2 x 10 x 23 mm body. Catalog 11 +/-0.5 g; 12 g planning allowance. Ears/spline stack provisional. |
| 1 | [Matek F405-TE flight controller](https://www.mateksys.com/?portfolio=f405-te) | 10.0 | 36 x 46 mm; verify 30.5 mm mount spacing and exact board variant. Bicopter firmware support required. |
| 1 | [Hobbywing UBEC 5A](https://www.hobbywing.com/en/products/ubec-5a93.html) | 21.0 | 50 x 17 x 10 mm; set to 6 V for servos only. 5 A continuous rating; actual simultaneous servo demand unknown. |
| 1 | [RadioMaster RP1 V2 ELRS 2.4 GHz receiver](https://www.radiomasterrc.com/products/rp1-expresslrs-2-4ghz-nano-receiver) | 2.2 | 13 x 11 x 3 mm, antenna included in allocation. Requires compatible ELRS transmitter; FlySky AFHDS radio is not compatible. |
| 1 | [4S 1300 mAh LiPo - exact SKU OPEN](https://www.genstattu.com/blog/tattu-fpv-battery-recommend) | 170.0 | 76 x 38 x 31 mm maximum planning envelope, including stock leads in mass. Must support measured pack current and fit; no C-label guarantee. |
| 1 | XT60 aircraft-side connector | 4.0 | Mate to battery connector; insulated solder cups and strain relief. Stock battery half is counted with battery. |
| 1 | 470 uF 35 V low-ESR capacitor | 3.0 | Reserve diameter 10 x 16 mm; confirm ripple rating and polarity. Lead length affects suppression. |
| 1 | 5 V active buzzer | 2.0 | Reserve diameter 10 x 5 mm; verify compatibility with FC buzzer output and polarity. |
| 4 | MR104 bearing, 4 x 10 x 4 mm | 5.2 | Metal bearings; confirm fit, shields, axial support and smooth rotation. |
| 4 | 4 mm metal trunnion / shoulder pin | 8.0 | Nominal 14 mm modeled length. Final shoulders, spacers, retaining method and bearing stack OPEN. |
| 2 | [OEM-compatible 25T servo horn](https://www.blue-bird-model.com/products_detail/55.htm) | 1.6 | 14 mm effective pivot-to-ball radius. Verify spline and screw; do not substitute a loose printed spline. |
| 2 | M2 pushrod with ball-link ends | 4.0 | 35 mm center-to-center modeled link; four ball joints total. Verify travel, clearance and attachment geometry. |

Purchased allocations total **337.0 g**. Wires, solder, remaining connectors and small installation hardware are allocated below, not added again to the above component envelopes.

## Installation materials and unresolved hardware

| Allowance | Budget g | Contents |
|---|---:|---|
| Harness and secondary connectors | 36 | Silicone wire by schedule; insulation, solder, servo plugs and power splice. Existing stock leads may cover some modeled lengths. |
| Fasteners, spacers and retention | 25 | M3/M2 screws, nuts, washers, FC grommets, wheel axles and pin retainers. Final stack and retention are not released. |
| Straps, foam, ties and insulation | 8 | Two nominal 10 mm battery straps; battery pad, FC isolation and strain relief. |
| Adhesive and light finish | 8 | Tail/shell joints and restrained matte-black finish. Verify adhesion/material and count actual paint mass. |

Initial modeled screw schedule: 8 motor M3 screws with 7 mm under-head length, 4 FC M3 x10, 4 beam/keel M3 x22, 4 yoke M3 x10, two diameter-2 x12 mm main wheel axles and one diameter-2 x9 mm tailwheel axle. These are CAD dimensions, not approved screw lengths: check motor winding clearance, printed wall engagement, nuts and washers before use. Four FC isolators and four ball-link ends are represented; avoid double-counting ends already supplied with link assemblies. Servo ear screws, tail splice, shell closure and trunnion retention still require final detailing.

Wire sizes: 14 AWG main power, 18 AWG ESC supply and motor phases, 22 AWG UBEC input, 24 AWG servo supply/signals and capacitor leads, 26 AWG low-current FC/RX signals. Use the [42-route wire schedule](../engineering/WIRE_SCHEDULE.md) for modeled lengths and termination allowances. Antenna coax and battery balance leads represent supplied assemblies, not an instruction to fabricate RF antennas or modify the pack.

## Print list

One of each installed STL; 40 pieces total. Names identify mirrored and separated pieces explicitly. Two optional guards add 25.4 g and are omitted from the baseline mass. All masses below assume the full CAD material volume at 1.24 g/cm^3; these are not slicer predictions. All mesh bounds fit the 256 mm printer cube, but orientation, supports, brim and tolerances must be checked in the slicer.

| STL / part | Qty | CAD mass g | Bounding box mm |
|---|---:|---:|---|
| [P01_Battery_keel](../stl/P01_Battery_keel.stl) | 1 | 35.28 | 136.0 x 58.0 x 48.0 |
| [P02_Crossbeam](../stl/P02_Crossbeam.stl) | 1 | 45.18 | 73.0 x 168.0 x 19.0 |
| [P03_Avionics_deck](../stl/P03_Avionics_deck.stl) | 1 | 6.30 | 54.0 x 49.0 x 4.0 |
| [P09_Cabin_side_glazing_0](../stl/P09_Cabin_side_glazing_0.stl) | 1 | 0.53 | 18.0 x 4.5 x 27.0 |
| [P09_Cabin_side_glazing_0_segment_2](../stl/P09_Cabin_side_glazing_0_segment_2.stl) | 1 | 1.10 | 28.0 x 4.8 x 28.0 |
| [P09_Cabin_side_glazing_0_segment_3](../stl/P09_Cabin_side_glazing_0_segment_3.stl) | 1 | 1.03 | 28.0 x 5.3 x 28.0 |
| [P09_Cabin_side_glazing_1](../stl/P09_Cabin_side_glazing_1.stl) | 1 | 0.53 | 18.0 x 4.5 x 27.0 |
| [P09_Cabin_side_glazing_1_segment_2](../stl/P09_Cabin_side_glazing_1_segment_2.stl) | 1 | 1.10 | 28.0 x 4.8 x 28.0 |
| [P09_Cabin_side_glazing_1_segment_3](../stl/P09_Cabin_side_glazing_1_segment_3.stl) | 1 | 1.03 | 28.0 x 5.3 x 28.0 |
| [P06_Cabin_upper](../stl/P06_Cabin_upper.stl) | 1 | 25.70 | 210.0 x 62.0 x 51.0 |
| [P07_Cabin_lower](../stl/P07_Cabin_lower.stl) | 1 | 22.95 | 208.8 x 62.0 x 17.0 |
| [P08_Windshield](../stl/P08_Windshield.stl) | 1 | 1.45 | 20.0 x 29.9 x 40.0 |
| [P08_Windshield_segment_2](../stl/P08_Windshield_segment_2.stl) | 1 | 0.74 | 12.5 x 28.8 x 26.3 |
| [P08_Windshield_segment_3](../stl/P08_Windshield_segment_3.stl) | 1 | 1.45 | 20.0 x 29.9 x 40.0 |
| [P08_Windshield_segment_4](../stl/P08_Windshield_segment_4.stl) | 1 | 0.74 | 12.5 x 28.8 x 26.3 |
| [P19_Tapered_tail_boom](../stl/P19_Tapered_tail_boom.stl) | 1 | 22.77 | 150.0 x 56.6 x 64.5 |
| [P04_Tail_spine](../stl/P04_Tail_spine.stl) | 1 | 3.15 | 163.3 x 12.0 x 35.5 |
| [P05_Vertical_tail_fin](../stl/P05_Vertical_tail_fin.stl) | 1 | 2.19 | 52.0 x 1.3 x 70.0 |
| [P05_Horizontal_tailplane](../stl/P05_Horizontal_tailplane.stl) | 1 | 1.64 | 31.0 x 48.0 x 1.2 |
| [P17_Shoulder_cowl__1](../stl/P17_Shoulder_cowl__1.stl) | 1 | 4.32 | 46.0 x 52.0 x 20.0 |
| [P20_Servo_engine_cowl__1](../stl/P20_Servo_engine_cowl__1.stl) | 1 | 4.33 | 63.0 x 30.4 x 21.0 |
| [P22_Cable_raceway__1](../stl/P22_Cable_raceway__1.stl) | 1 | 4.03 | 17.0 x 54.0 x 10.0 |
| [P10_Main_gear__1](../stl/P10_Main_gear__1.stl) | 1 | 1.28 | 27.7 x 17.5 x 26.7 |
| [P23_Main_wheel__1](../stl/P23_Main_wheel__1.stl) | 1 | 0.64 | 14.0 x 4.0 x 14.0 |
| [P17_Shoulder_cowl_1](../stl/P17_Shoulder_cowl_1.stl) | 1 | 4.32 | 46.0 x 52.0 x 20.0 |
| [P20_Servo_engine_cowl_1](../stl/P20_Servo_engine_cowl_1.stl) | 1 | 4.33 | 63.0 x 30.4 x 21.0 |
| [P22_Cable_raceway_1](../stl/P22_Cable_raceway_1.stl) | 1 | 4.03 | 17.0 x 54.0 x 10.0 |
| [P10_Main_gear_1](../stl/P10_Main_gear_1.stl) | 1 | 1.28 | 27.7 x 17.5 x 26.7 |
| [P23_Main_wheel_1](../stl/P23_Main_wheel_1.stl) | 1 | 0.64 | 14.0 x 4.0 x 14.0 |
| [P24_Tailwheel_fork](../stl/P24_Tailwheel_fork.stl) | 1 | 0.82 | 19.6 x 7.0 x 25.5 |
| [P25_Tailwheel](../stl/P25_Tailwheel.stl) | 1 | 0.29 | 11.0 x 3.0 x 11.0 |
| [P11_L_bearing_yoke](../stl/P11_L_bearing_yoke.stl) | 1 | 10.64 | 18.0 x 74.0 x 35.0 |
| [P12_L_motor_cradle](../stl/P12_L_motor_cradle.stl) | 1 | 10.37 | 36.0 x 85.0 x 22.5 |
| [P13_L_tilting_guard](../stl/optional_guards/P13_L_tilting_guard.stl) (optional) | 1 | 12.68 | 142.2 x 142.2 x 32.7 |
| [P14_L_servo_retainer](../stl/P14_L_servo_retainer.stl) | 1 | 0.60 | 29.0 x 30.0 x 2.5 |
| [P15_L_ESC_tray](../stl/P15_L_ESC_tray.stl) | 1 | 1.22 | 31.0 x 16.0 x 2.0 |
| [P11_R_bearing_yoke](../stl/P11_R_bearing_yoke.stl) | 1 | 10.64 | 18.0 x 74.0 x 35.0 |
| [P12_R_motor_cradle](../stl/P12_R_motor_cradle.stl) | 1 | 10.37 | 36.0 x 85.0 x 22.5 |
| [P13_R_tilting_guard](../stl/optional_guards/P13_R_tilting_guard.stl) (optional) | 1 | 12.68 | 142.2 x 142.2 x 32.7 |
| [P14_R_servo_retainer](../stl/P14_R_servo_retainer.stl) | 1 | 0.60 | 29.0 x 30.0 x 2.5 |
| [P15_R_ESC_tray](../stl/P15_R_ESC_tray.stl) | 1 | 1.22 | 31.0 x 16.0 x 2.0 |
| [P16_Antenna_mast](../stl/P16_Antenna_mast.stl) | 1 | 0.10 | 5.0 x 5.0 x 10.0 |

## Ground equipment - excluded from flight mass

- ELRS 2.4 GHz transmitter or a compatible transmitter/module combination.
- LiPo balance charger supporting 4S, suitable supply and charging accessories.
- Scale with gram resolution, calipers, multimeter and current/voltage logging.
- Restrained thrust stand, protected actuator/load fixture and vibration measurement.
- Soldering equipment, heat-shrink, drivers and bearing/fastener fit coupons.
- Suitable filament and slicer for Centauri Carbon; qualify the actual material/process on loaded and heated joints.

Commercial propellers, motors, bearings, metal pins, fasteners and servo gears remain purchased parts. More printing does not justify unqualified rotating blades or unreliable pivots.
