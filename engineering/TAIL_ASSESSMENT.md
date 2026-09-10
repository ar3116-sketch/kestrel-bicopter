# Tail assessment - Kestrel Mini R4

The tail does not inherently prevent a bicopter from flying. It is included in the existing mass and balance calculation, but its aerodynamic effect is not yet qualified. This aircraft uses two independently tilting propulsion pods for control; the decorative helicopter tail needs no tail rotor.

## Mass and balance

The boom, spine, fin, horizontal tailplane and tailwheel prints total **30.86 g**. This is already included in the **664.9 g** nominal aircraft, not an additional charge. Tail hardware mass is in the shared fastener allowance; adhesive/finish are also shared, so this is not a separately weighed complete tail. The calculated CG is x = **-0.82 mm**, close to the rotor pivot plane x = 0. Tail component CG is x = -167.3 mm. Removing these parts without moving anything else would put CG at x = **7.28 mm**; that is a sensitivity calculation, not a recommended modification.

| Tail component | Allocated g | CG x, mm |
|---|---:|---:|
| P19 Tapered tail boom | 22.768 | -159.92 |
| P04 Tail spine | 3.147 | -121.45 |
| P05 Vertical tail fin | 2.187 | -256.45 |
| P05 Horizontal tailplane | 1.643 | -227.04 |
| P24 Tailwheel fork | 0.822 | -185.20 |
| P25 Tailwheel | 0.290 | -188.00 |
| Tailwheel M2 axle | 0.000 | -188.00 |

The same bounding-box inertia approximation used in the main audit assigns these tail parts 0.000957 kg m^2 in pitch and 0.000944 kg m^2 in yaw, approximately 43% and 25% of the respective totals. The long lever arm matters more than the modest mass alone. These are coarse geometry-based estimates, not measured inertia.

## Crosswind sensitivity, not an operating wind limit

The generator's own cubic tail-boom silhouette is integrated at 0.05 mm spacing from x=-255 to -105 mm. Boom side area is 57.81 cm^2; fin side area is 13.57 cm^2. Their sum is 71.38 cm^2, with area-weighted lever arm 179.0 mm aft of CG. The overlap is double-counted, shielding is omitted, and the rest of the aircraft is excluded. This is not a whole-aircraft force bound.

Use q = 0.5 rho V^2 and yaw moment N = q C integral[(CGx-x) dA], with rho=1.225 kg/m^3. Coefficients C=1.0 and 1.5 are arbitrary sensitivity inputs; neither is a measured value or guaranteed upper bound. Wind is uniform sideways relative flow, not forward speed or rotor downwash. [NASA drag equation](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/drag-equation/) and [coefficient limitations](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/drag-coefficient/) explain why area and matching flow conditions matter.

For comparison only, a +/-10 degree absolute pod-angle candidate, less 1.54 degrees common trim, leaves 8.46 degrees differential tilt. Near hover, ideal yaw moment is approximately m g d tan(delta) = **0.114 N m**, with d=0.117 m. This assumes coordinated thrust and no additional pitch/roll demand, actuator lag or saturation. The angle is not an implemented or flight-qualified limit.

| Crosswind m/s | Assumed C | Tail yaw N m | Fraction of ideal candidate |
|---:|---:|---:|---:|
| 3 | 1.0 | 0.007 | 6% |
| 3 | 1.5 | 0.011 | 9% |
| 5 | 1.0 | 0.020 | 17% |
| 5 | 1.5 | 0.029 | 26% |
| 8 | 1.0 | 0.050 | 44% |
| 8 | 1.5 | 0.075 | 66% |
| 10 | 1.0 | 0.078 | 69% |
| 10 | 1.5 | 0.117 | 103% |

The tail can consume a meaningful fraction of heading-control authority in crosswind. These calculations do not establish a safe wind speed, stability, damping, gust response or combined maneuver envelope. Tailplane pitch loads in forward flight/downwash, fin flow separation, vibration, rotor/fuselage interference, and full-aircraft aerodynamic moments remain unmodeled. A passive tail may tend to align the aircraft with relative wind; the active controller still has to hold the commanded heading.

## What must be checked on the prototype

- Weigh the completed tail and whole aircraft; measure CG with the actual battery and hardware. Rebalance toward x=0 and rerun the audit if any mass or geometry changes.
- Resolve and proof-load the internal tail splice/retention and long spine. Check resonance, flex, landing loads and fastener retention; no structural tail release is implied by a valid CAD solid.
- Measure side force/yaw torque and tailplane pitch loads in a restrained instrumented fixture across representative flow directions, including rotor-on effects. Compare to measured control authority with reserve for simultaneous commands.
- Verify firmware mixing, loaded servo response, motor thrust, vibration and loss-of-signal behavior before controlled flight qualification. Initial evaluation belongs in still air; no outdoor wind envelope is approved.

Run `python3 scripts/tail_audit.py` after `scripts/analyze.py` to regenerate this assessment.
