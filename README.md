# Kestrel Mini R4

A matte-black, Black Hawk inspired **bicopter**, modeled in FreeCAD with electronics and wiring. Two lift motors and two independent tilt servos provide the control inputs. There is no tail rotor.

![Kestrel exterior](images/exterior.png)

**Fit prototype, not flight-qualified.** Estimated mass is **665 g**, or **731 g with 10% growth**. Calculations support takeoff in principle. Actual thrust, servo tracking, printed strength, assembly retention and flight-controller integration still need physical verification.

## Start here

- [PDF build and engineering guide](output/pdf/Kestrel_Mini_R4_Build_Guide.pdf)
- [Parts list: buy, print and bench equipment](docs/PARTS_LIST.md)
- [FreeCAD assembly](cad/Kestrel_Mini_R4.FCStd) and [STEP](cad/Kestrel_Mini_R4.step)
- [40 installed STL pieces](stl/) and [2 optional guards](stl/optional_guards/)
- [Wiring overview](engineering/wiring_overview.svg) and [42-route wire schedule](engineering/WIRE_SCHEDULE.md)
- [Engineering review](engineering/ENGINEERING_REVIEW.md), [flight audit](engineering/INDEPENDENT_FLIGHT_AUDIT.md), and [tail assessment](engineering/TAIL_ASSESSMENT.md)
- [Assembly and qualification plan](docs/BUILD_AND_TEST.md)
- [Reproduction instructions](REPRODUCE.md)

Open the FCStd in FreeCAD. Run `OPEN_KESTREL.FCMacro` for shell visibility and independent tilt inspection. The +/-25 degree sliders show geometric articulation; they are not validated operating limits. The native file is a grouped installation model, with provisional purchased-part envelopes and a Python geometry generator, rather than a fully constrained assembly/feature history.

## What the calculations say

| Case | Estimated mass | Vertical thrust/weight at 12 V | At 16 V |
|---|---:|---:|---:|
| Baseline | 665 g | 1.82 | 2.29 |
| 10% mass growth | 731 g | 1.65 | 2.09 |

These use the published original EMAX RS2205 2300KV / HQ5045BN two-blade table with an **assumed 15% installation loss**. The assumption is not a measured guarantee. At the growth mass and low voltage, the design misses its preferred 1.8 vertical margin. Bank, tilt, simultaneous commands and gusts consume reserve. Fresh-pack 16.8 V is outside the available thrust table.

The tail prints weigh **30.9 g**, already counted in the baseline. The calculated CG lies 0.82 mm aft of the rotor pivot plane. The tail is not inherently incompatible with bicopter control, but crosswind and its added rotational inertia matter; see the dedicated assessment. No wind envelope is approved.

![Installed electronics and wiring](images/electronics_wiring.png)

## Evidence and open work

The R4 checks report 167 valid physical shapes, 42 closed printable meshes, 22 sampled rotor poses and 42 neutral wire routes. Minimum prop-to-fixed clearance in the sampled poses is 9.906 mm. The wiring check uses finite mesh sampling, not continuous flexible-harness simulation. No physical tests, CFD, validated full-flight simulation or flight qualification have been completed.

Battery SKU, final hardware interfaces, tail splice and retention, motor/ESC/servo thermal performance and exact firmware configuration remain open. Do not treat a successful CAD or mathematical check as proof of an airworthy build.

The manufacturer material in `source/` is retained for engineering traceability; see [NOTICE](NOTICE.md). This project is an independent hobby design and is not affiliated with Sikorsky, Lockheed Martin or the hardware manufacturers.
