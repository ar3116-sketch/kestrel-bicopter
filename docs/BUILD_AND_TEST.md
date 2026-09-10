# Assembly and qualification plan

This document organizes the remaining prototype work. It is not a completed assembly release, approved flight procedure or tested firmware configuration.

## Resolve interfaces first

1. Select and measure the actual 4S1300 battery, motors, ESCs, BMS-115WV+ servos and flight controller. Check mass, mounting holes, shaft/horn dimensions, connector access and component height against CAD.
2. Finalize the bearing/trunnion shoulder, spacer and retaining arrangement. Verify servo horn engagement, ball-link travel, positive pod retention and motor-screw clearance from windings.
3. Detail the tail splice, shell closures, gear axle retention and all missing mounting fasteners. The current tail shell is split at x=-105 mm; the internal splice is explicitly provisional.
4. Recompute mass/CG and rotor clearance whenever interfaces change. No part currently owned means exact hardware fit remains an open requirement.

## Print and inspect

- Printer basis: Centauri Carbon, 256 x256 x256 mm. Each exported piece fits by its axis-aligned bounds; confirm bed orientation, brim and supports in the slicer.
- Print small bearing, screw, shell seam and servo-retainer fit coupons first. Do not commit the complete body before confirming tolerances.
- Use the actual filament density in the mass model. Current 1.24 g/cm^3 is a planning value. Shell geometry uses a 1 mm section-coordinate inset, which is not an exact constant normal wall thickness.
- Orient crossbeam, yokes, motor cradles, crank extensions and gear to resist their actual bending/joint loads. Layer direction, voids, heat, creep, inserts and fatigue have not been qualified. No fixed infill recipe is released as sufficient.
- Verify hot motor/ESC clearances and material behavior at measured temperatures. Do not assume PLA or any other named polymer is adequate solely from a catalog strength.
- Print one of every installed STL, dry-fit, weigh, then record the real mass. Guards are optional and are not included in baseline thrust-loss assumptions.

## Suggested assembly order

1. Assemble battery keel, crossbeam and avionics deck with isolators. Dry-fit the selected battery and confirm strap access.
2. Install yokes, metal bearings and retained trunnions. Check free pod rotation and endplay before fitting motors.
3. Install servos and verified OEM-compatible horns; set mechanical neutral and attach ball links. Check independent full travel without power wiring obstructing motion.
4. Mount FC, receiver, UBEC, ESCs, buzzer and capacitor. Keep electronics accessible for continuity and polarity checks.
5. Install the power and signal harness from the wiring schedule. Protect each splice and provide strain relief; verify flexible motor-phase loops through travel using the real insulation and bend radius.
6. Fit gear, completed tail joint, shell, glazing and cowls. Check cooling paths, radio antenna clearance and access to arming/disconnect controls.
7. Weigh the complete aircraft with battery and measure three-axis CG. Adjust the battery toward CGx=0; rerun calculations for the final state.

## Electrical and control checks - props removed

- Confirm no VBAT short, polarity, capacitor polarity and insulation before applying power through an appropriate current-limited commissioning setup.
- Verify regulated 6 V only feeds servos. FC 5 V feeds receiver/buzzer; grounds are common. Never join the 6 V and 5 V positive rails.
- Confirm the exact FC target and build include servo and bicopter support. The resource proposal is motors S1/PC9 and S2/PC8; servos S9/PB14 and S10/PA6. Mapping, output protocol, rates, neutral, sign and endpoints must be verified on the actual firmware.
- Verify the receiver is ELRS/CRSF-compatible and both receive/transmit wiring directions are correct. Check arm/disarm and loss-of-signal behavior.
- Confirm every stabilizing correction acts in the proper direction. Two motors alone are insufficient; both independent tilt servos must work correctly.
- Measure simultaneous loaded servo current and BEC voltage sag. The existing 4 A initial gate leaves nominal reserve below the 5 A continuous BEC rating; it does not replace transient/stall and thermal tests.
- Motor power bypasses the FC current sensor in this layout. Use external measurement if total pack current is required; do not trust an unconnected current-sensor channel.

## Restrained mechanical and propulsion qualification

- Use a guarded, restrained instrumented rig for propeller-on testing. Verify exact motor/prop rotation, thrust, current and temperature across the actual battery voltage range, including fully charged 16.8 V and sagged conditions.
- Measure installed thrust with body/cowls and verify reserve for bank, tilt and simultaneous commands. A source-table TWR is not an installed result.
- Proof-test primary structure and tail retention for the chosen load envelope, including landing and cyclic vibration. Screened beam stress does not qualify joints or layer adhesion.
- Test servo tracking under representative thrust, gyroscopic loads and harness resistance. Catalog stall torque and no-load speed do not establish usable continuous control bandwidth.
- Measure swept prop clearance and flexible wire movement at intermediate positions. Existing CAD sampling excludes deflection, vibration, wire fatigue and manufacturing error.
- Investigate tail side-force/yaw and tailplane pitch loads before approving a wind or speed envelope. Check resonance and vibration with the complete tail fitted.

## Flight qualification remains open

The +/-10 degree pod/bank and <=45 degree/s body-rate values in the audit are candidates for investigation, not implemented settings or safe limits. No PID tune, autonomous behavior or flight mode has been validated. A competent builder must establish controlled test conditions and progressively qualify stability and maneuvering after the above gates pass. The project currently has `flight_release=false` and no completed physical tests.

Record measured configuration, weights, CG, firmware hash/settings, battery state, thrust/current curves, temperatures, response logs and pass/fail evidence. Revise the CAD and calculations to match the tested hardware before calling the result flight-qualified.
