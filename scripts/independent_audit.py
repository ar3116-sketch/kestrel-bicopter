"""Independent force, mass, control and gyroscopic screens. No CAD mutation.
Run: python3 independent_audit.py [path/to/revision]
Uses source-reference constants explicitly; nothing here qualifies hardware.
"""
from pathlib import Path
import json, math, sys

OUT = Path(__file__).resolve().parents[1] / 'engineering'
MODEL = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
C = json.loads((MODEL/'engineering/calculations.json').read_text())
INV = json.loads((MODEL/'engineering/inventory.json').read_text())
MOV = json.loads((MODEL/'engineering/moving_objects.json').read_text())
g = 9.80665
mass = C['nominal_mass_g']
growth = C['mass_with_10percent_growth_g']
W = mass*g/1000
cg = C['cg_mm']
h = (35-cg[2])/1000
a = -cg[0]/1000
d = .117
Ixx,Iyy,Izz = C['inertia_kg_m2']
curves = {
 12:[(1,62),(3,162),(5,236),(7,311),(9.1,374),(11,439),(13,490),(15.3,548),(17.3,611),(20.7,712)],
 16:[(1,76),(3,183),(5,283),(7.1,352),(9.1,426),(11,497),(13,560),(15,628),(17,692),(19,754),(21,812),(23.3,878),(25.4,936),(27.3,997),(29.9,1024)]}

def interp(x, pts):
    for (x0,y0),(x1,y1) in zip(pts,pts[1:]):
        if x0<=x<=x1:return y0+(y1-y0)*(x-x0)/(x1-x0)
    raise ValueError('No extrapolation')

rows=[]
for mg in [mass,growth,800]:
    for V in [12,16]:
        for factor in [.85,.75,.65]:
            imax = min(24,curves[V][-1][0])
            f = interp(imax,curves[V])*factor*2
            amps = interp(mg/(2*factor), [(t,i) for i,t in curves[V]])
            rows.append(dict(mass_g=mg,voltage_V=V,installed_factor_assumed=factor,
                max_total_gf=f,hover_motor_A=amps,
                hover_total_with_5W_A=2*amps+5/V,
                vertical_TW=f/mg,pod20_TW=f/mg*math.cos(math.radians(20)),
                pod20_bank20_TW=f/mg*math.cos(math.radians(20))**2,
                pod20_bank20_with_10pct_diff_headroom_TW=f/mg*math.cos(math.radians(20))**2/1.1))

# Full 12-state, four-input small-disturbance hover model with zero X/Y CG error.
# States x,y,z,vx,vy,vz,phi,theta,psi,p,q,r; RH body X forward/Y left/Z up.
# Inputs collective N, differential N (L-R), common tilt rad, differential tilt rad (R-L)/2.
# xdd=g(theta+dc), ydd=-g phi; qdd coefficient through h. This is a local
# controllability calculation, NOT proof of a stable implemented controller.
n=12
A=[[0.]*n for _ in range(n)]
B=[[0.]*4 for _ in range(n)]
for r,c in [(0,3),(1,4),(2,5),(6,9),(7,10),(8,11)]: A[r][c]=1.
A[3][7]=g;A[4][6]=-g
B[5][0]=1000/mass;B[9][1]=d/Ixx;B[3][2]=g;B[10][2]=h*W/Iyy;B[11][3]=d*W/Izz
def mm(A,B):return [[sum(a*b for a,b in zip(row,col)) for col in zip(*B)] for row in A]
K=[row[:] for row in B];AB=B
for _ in range(n-1):
    AB=mm(A,AB)
    for row,new in zip(K,AB):row.extend(new)
def rank(M):
    M=[row[:] for row in M]; rr=0
    for col in range(len(M[0])):
        pivot=max(range(rr,len(M)), key=lambda j:abs(M[j][col]), default=rr)
        if rr==len(M) or abs(M[pivot][col])<1e-8:continue
        M[rr],M[pivot]=M[pivot],M[rr]
        s=M[rr][col];M[rr]=[v/s for v in M[rr]]
        for j in range(len(M)):
            if j!=rr:
                s=M[j][col];M[j]=[v-s*w for v,w in zip(M[j],M[rr])]
        rr+=1
        if rr==len(M):break
    return rr

trim=math.atan2(a,h)
authority=[]
for deg in [-20,-10,0,10,20]:
    angle=math.radians(deg)
    my=W*(h*math.tan(angle)-a)
    mz=d*W*math.tan(angle)
    authority.append(dict(angle_deg=deg,pitch_Nm_at_level_Fz_equals_W=my,
        pitch_accel_rad_s2=my/Iyy,yaw_Nm_zero_common_tilt=mz,yaw_accel_rad_s2=mz/Izz))

# Motion changes CG: rotate mass-envelope centroids about the actual transverse axes.
byname={o['name']:o for o in INV if o.get('installed',True)}
shifts=[]
for angle_deg in [-20,20]:
    angle=math.radians(angle_deg); sx=sz=0.
    for names in MOV.values():
        for name in names:
            o=byname.get(name)
            if not o:continue
            x,y,z=o['center_mm']; zr=z-35
            sx+=o['mass_g']*(x*math.cos(angle)+zr*math.sin(angle)-x)
            sz+=o['mass_g']*(-x*math.sin(angle)+zr*math.cos(angle)-zr)
    shifts.append(dict(common_tilt_deg=angle_deg,delta_CG_x_mm=sx/mass,delta_CG_z_mm=sz/mass,
        scope='listed moving shapes only, excluding linkage mass motion and wire flex'))

# Gyro torque under body roll: Omega_x cross H_z acts along pod hinge/servo axis Y.
# Prop mass is budgeted, not measured; uniform radial mass gives mR^2/3.
# The upper radial bound mR^2 is prop-only and excludes motor bell inertia.
R=.0635;mp=.003
Jrod=mp*R*R/3;Jradial=mp*R*R
gyro=[]
base_servo_load=C['servo'].get('base_quasistatic_load_Nm',C['servo']['screen_load_Nm'])
working=C['servo']['working_screen_Nm']
selected_servo=C['servo'].get('model','EMAX ES08MD II')
for rpm in [16000,20080,22830]:
    omega=rpm*2*math.pi/60
    for rate in [45,90,180]:
        p=math.radians(rate)
        t=Jrod*omega*p
        gyro.append(dict(rpm=rpm,roll_deg_s=rate,prop_only_uniform_radial_gyro_Nm=t,
            prop_only_radial_bound_gyro_Nm=Jradial*omega*p,
            base_plus_prop_estimate_Nm=base_servo_load+t,
            quarter_stall_margin_ratio=working/(base_servo_load+t),
            motor_bell_inertia='unknown, additional'))

mass_gates=[]
for factor in [.85,.75,.65]:
    maxmass=2*712*factor/1.8
    mass_gates.append(dict(installed_factor_assumed=factor,
        mass_g_for_1p8_vertical_at12V=maxmass,
        nominal_g_to_meet_1p8_after10pct_growth=maxmass/1.1,
        mass_g_for_1p6_at20deg_at12V=2*712*factor*math.cos(math.radians(20))/1.6))

ans=dict(audited_revision=MODEL.name,nominal_mass_g=mass,growth_mass_g=growth,
    source_table_transcription='Visually checked against source/motor_2.jpg; matches R3',
    cg_mm=cg,pivot_z_mm=35,pitch_arm_m=h,
    trim_deg_positive_is_thrust_toward_nose=math.degrees(trim),
    common_tilt_remaining_symmetric_deg=max(0,20-abs(math.degrees(trim))),
    linear_full_state_controllability_rank=rank(K),local_model_states=n,
    force_cases=rows,mass_gates=mass_gates,authority=authority,moving_cg_shifts=shifts,
    rotor_gyro=gyro,prop_inertia_uniform_radial_kg_m2=Jrod,
    prop_inertia_radial_bound_kg_m2=Jradial,
    note='Preliminary force/control screens; no measured hardware performance or validated flight dynamics.')
(OUT/'independent_audit_calculations.json').write_text(json.dumps(ans,indent=2))

table='\n'.join(f"| {r['mass_g']:.0f} | {r['voltage_V']} | {r['vertical_TW']:.2f} | {r['pod20_TW']:.2f} | {r['pod20_bank20_TW']:.2f} | {r['hover_total_with_5W_A']:.1f} |" for r in rows if r['installed_factor_assumed']==.85)
sensitivity='\n'.join(f"| {r['installed_factor_assumed']:.2f} | {r['vertical_TW']:.2f} | {r['pod20_TW']:.2f} |" for r in rows if r['mass_g']==growth and r['voltage_V']==12)
gyrotable='\n'.join(f"| {r['rpm']} | {r['roll_deg_s']} | {r['prop_only_uniform_radial_gyro_Nm']:.4f} | {r['base_plus_prop_estimate_Nm']:.4f} | {r['quarter_stall_margin_ratio']:.2f} |" for r in gyro if r['rpm'] in [16000,20080])
if 'Blue Bird' in selected_servo:
    revision_status='R3 omitted a body-roll gyroscopic servo load. R4 addresses that omission with a stronger provisional servo and explicit gyro/crank load screens; the improved calculated reserve is still conditional on actual rotating mass, RPM, servo tracking and structural proof.'
    selected_note=f"The audited revision provisionally selects **{selected_servo}**. Its quarter-catalogue screen is {working:.4f} N·m. The following prop-only estimate table uses that selected screen, not the superseded EMAX screen."
    selected_gyro=C['servo']['gyro_cases']
    bounded_note='\n'.join(f"| {r['body_roll_deg_s']} | {r['gyro_torque_bound_Nm']:.4f} | {r['total_load_screen_Nm']:.4f} | {r['quarter_catalogue_margin_ratio']:.2f} |" for r in selected_gyro)
    bounded_note=f'''R4 also applies the deliberately larger bound J = (0.003×0.0635²) + (0.030×0.01395²) = 1.7935×10⁻⁵ kg·m²: all prop mass at its tip radius and all motor mass at the bell outer radius. This overbounds the motor bell only if received prop/motor masses and radii do not exceed those modeled. RPM is bounded to the source table's 24,600 RPM for this screen; actual fresh-pack RPM is not established.

| Roll °/s | Bounded gyro N·m | Prior load + bounded gyro N·m | Quarter-catalogue screen / sum |
|---:|---:|---:|---:|
{bounded_note}

The retained 8×7 mm, 52 mm crank is now screened at 0.08 N·m, rounded above the 45°/s bounded total. Nominal bending stress is {C['servo']['crank_stress_MPa']:.2f} MPa and tip deflection {C['servo']['crank_deflection_mm']:.2f} mm. A stronger servo does not strengthen this crank. Stress concentrations, material orientation, joint stiffness and fatigue are still open; proof-load and tracking checks are required.'''
else:
    revision_status='In particular, the existing servo budget omits a roll-rate gyroscopic load that can consume its small reserve.'
    selected_note='The audited revision retains EMAX ES08MD II; its quarter-stall screening assumption is used in the table below.'
    bounded_note='The exact motor-bell inertia was not bounded in the audited revision. The assumed prop-only inertia cannot establish a complete load envelope.'
report=f'''# Independent flight-feasibility audit — {MODEL.name}

Audit date: 9 September 2026. Inputs are the saved {MODEL.name} inventory, mass calculation, moving-object list, EMAX thrust image and engineering review. This audit does not alter the CAD. The companion `independent_audit.py` and `independent_audit_calculations.json` reproduce the additional screens. The audited revision is **{MODEL.name}**; rerun after any inventory or propulsion changes.

## Finding

**The two-motor/two-servo arrangement can produce lift and all primary attitude-control moments in theory. At the saved nominal mass of {mass:.1f} g, the matched EMAX motor/prop data supports a plausible takeoff and gentle-maneuver prototype. It does not establish that this aircraft will maneuver reliably.** The source arithmetic is correct, but the installation factor, actual battery/ESC performance and dynamic servo loads are not established. {revision_status}

The 10% growth build is {growth:.1f} g. It remains below 800 g, but the weight limit is not a flight-performance guarantee. The report's own preferred 1.8 vertical / 1.6 at 20° thrust gates are not both retained at this mass at 12 V. These are chosen engineering targets, not universal physical thresholds; ideal takeoff needs more than 1.0 plus sufficient control reserve.

## Lift arithmetic independently reproduced

The original [EMAX matched thrust table](https://cdn.shopify.com/s/files/1/0469/7358/3518/t/3/assets/RS2205-2.jpg?v=1598532544) visually matches every current/thrust point transcribed in the saved script. At 12 V the table ends at 712 gf per motor and 20.7 A; at 16 V, interpolation at 24 A gives 897.33 gf. Applying the **assumed**, not measured, 0.85 installation factor gives total 1,210.4 / 1,525.5 gf. No extrapolation beyond source tables was used.

| Mass g | Loaded V | Vertical T/W | Vertical component at 20° pod tilt | At 20° pod tilt + 20° bank | Hover pack A, 5 W hotel assumption |
|---:|---:|---:|---:|---:|---:|
{table}

The bank column is an illustrative force-projection calculation, using cos(20°)² for orthogonal bank and fore/aft tilt. It excludes translation dynamics and control allocation saturation. It is not a demonstrated maneuver. If another 10% per-motor differential-thrust headroom is reserved, divide that column by 1.1. Do not interpret (T/W−1)g as a tested climb acceleration.

At 12 V and factor 0.85, the greatest mass meeting 1.8 vertical T/W is **672.4 g**; nominal mass would need to be **611.3 g** to retain that target after 10% growth. The corresponding 1.6 target at 20° permits **710.9 g**. These give explicit weight targets if these margins are required, rather than treating every sub-800 g build as equivalent.

Installation sensitivity at the {growth:.1f} g growth mass, 12 V:

| Assumed installed fraction of stand thrust | Vertical T/W | At 20° |
|---:|---:|---:|
{sensitivity}

The 0.75 and 0.65 fractions are stress cases, not measurements or claimed worst-case bounds. A 15% loss allowance cannot be declared guaranteed conservative without testing actual body obstruction, prop, voltage and motor temperature. The optional guards need their own thrust measurement; absence of contact does not establish aerodynamic efficiency.

12 V is 3.0 V/cell for 4S and is used only as an adverse loaded-voltage screen. This audit does not recommend flying the battery down to that voltage. Actual landing thresholds require the chosen pack and measured sag. A fresh 4S pack is 16.8 V, outside the 16 V current table; full-throttle current at 16.8 V is unqualified. The 24 A number is a calculation cap and has not been enforced by hardware or firmware.

## Control, balance and simultaneous maneuvers

With +X toward the nose, +Y left and +Z up, let positive pod angle point thrust toward +X. Relative to the CG, the pivots have forward offset a = −CGx = {a*1000:.3f} mm, half-spacing d = 117 mm and height h = {h*1000:.3f} mm. Ignoring prop reaction and gyroscopic torque, the exact body-axis force/moment terms are:

```
Fz = TL cos(deltaL) + TR cos(deltaR)
Fx = TL sin(deltaL) + TR sin(deltaR)
Mx = d [TL cos(deltaL) - TR cos(deltaR)]       [small CGy correction omitted]
My = h Fx - a Fz
Mz = d [TR sin(deltaR) - TL sin(deltaL)]
```

This confirms independent collective, roll, pitch and yaw authority near hover. An additional ideal 12-state small-disturbance model including position, velocity, attitude and angular rates has controllability rank **{rank(K)}/12** when balanced. Thus the architecture is not inherently missing a control axis. This mathematical result assumes usable actuators and a correctly implemented controller. It is not a stability test of Betaflight, real servo delay, or the manufactured vehicle.

**Trim convention correction:** under the explicitly defined positive-forward-thrust convention, moment-free equal pod tilt is atan(a/h) = **{math.degrees(trim):+.2f}°**. The original R3 `hover_trim_angle_deg` used atan(CGx/h), the opposite sign; R4 uses atan(−CGx/h) and records the convention. A numerical sign is meaningless without its physical convention. To remain stationary the body attitude must compensate the tilted thrust vector. Keeping the body level with this pod trim alone produces horizontal force. Balance the battery toward measured CGx = 0 rather than treating a low battery as passive stabilization.

With ±20° absolute pod travel, trim alone leaves approximately **{20-abs(math.degrees(trim)):.2f}°** symmetric common/differential command reserve in the tighter direction. If common tilt is dc and differential tilt is dd, **|dc| + |dd| ≤ 20°**. Maximum pitch and maximum yaw cannot both be requested independently. The 20° thrust table does not demonstrate simultaneous pitch, yaw, roll and climb at their individual maxima.

At the nominal level force Fz=W, the ideal ±20° common-tilt pitch moments span {authority[0]['pitch_Nm_at_level_Fz_equals_W']:.3f} to {authority[-1]['pitch_Nm_at_level_Fz_equals_W']:.3f} N·m. Ideal zero-common-tilt differential yaw at 20° is about {authority[-1]['yaw_Nm_zero_common_tilt']:.3f} N·m. Those magnitudes indicate nonzero useful control authority. The inertia estimates are bounding-box approximations, so the associated angular accelerations in the JSON are screening values only.

The modeled moving pod centroids shift X CG by roughly {abs(shifts[-1]['delta_CG_x_mm']):.3f} mm at common 20° tilt (excluding moving-link and wire mass). That is small, but is another reason not to treat the neutral CG and moment arms as exact constants throughout motion.

The 10% mass-growth allowance is a total-weight allowance, not a guarantee of balance. As a sensitivity example, 10 g added 200 mm aft of the pivot would move the present X CG aft by approximately {abs((mass*cg[0]-2000)/(mass+10)-cg[0]):.2f} mm. Moving a 170 g battery forward by roughly 12 mm would compensate that added moment, if the received hardware and tray allow the travel. The assembled CG must be measured after cosmetic finishing and hardware substitutions.

The previous 18 attitude-only simulations deliberately choose stable feedback gains for a simplified model. They check numerical responses within that model; they do not validate actual firmware, longitudinal translation, sensor vibration, transport delay, coupled saturation, gust rejection or a six-degree-of-freedom flight envelope. Their successful convergence must not be presented as proof that the airframe has been flight-simulated and passed.

## Servo gyroscopic torque during roll: R3 gap and R4 correction

The earlier [EMAX digital servo drawing](https://cdn.shopify.com/s/files/1/0469/7358/3518/t/3/assets/EMX-SV-0276-DES-1.jpg?v=1598527275) gives 2 kgf·cm stall torque at 6 V (0.1961 N·m). Its 0.10 s/60° speed is **no-load** speed. Neither is a published continuous loaded rating. The old R3 quarter-stall working screen was 0.0490 N·m against 0.0372 N·m assumed load, leaving only 0.0118 N·m.

{selected_note}

Gyroscopic torque is Omega × H, with H = Jrotor omega. During pod tilt about Y the gyro reaction is chiefly about X and loads the bearings/frame. **During aircraft roll about X, the gyro torque is about Y, the free pod hinge axis; holding pod angle therefore requires servo/linkage torque.** Opposite rotor spin can cancel a net airframe effect, but it does not eliminate each servo's load. This follows from [angular-momentum dynamics](https://ocw.mit.edu/courses/16-07-dynamics-fall-2009/resources/mit16_07f09_lec30/).

Using the modeled 3 g prop mass and 63.5 mm radius as a uniform radial-blade estimate gives Jprop = mR²/3 = {Jrod:.3e} kg·m². This mass distribution is assumed. Motor-bell inertia is additional and unknown; the simple radial mass bound mR² is three times the prop estimate. The added servo load may add to or subtract from existing loads with direction; the table conservatively adds magnitudes.

| RPM | Roll rate °/s | Prop-only gyro estimate N·m | Prior load + prop gyro N·m | Selected quarter-catalogue screen / sum |
|---:|---:|---:|---:|---:|
{gyrotable}

The original R3 1.32 servo margin was therefore **not a demonstrated maneuvering margin**. A 90°/s roll could nearly exhaust the EMAX screen using the prop alone; 180°/s exceeded it. Exact prop/bell inertia, thrust-axis eccentricity, loaded tracking, linkage friction and temperature must be measured or conservatively bounded. No aggressive roll-rate limit is approved by this calculation.

{bounded_note}

## Power, structure and practical open items

- The 4S 1,300 mAh / 170 g battery is an envelope, not a selected verified SKU. At the growth mass, nominal-factor hover is ~19–22 A pack current; the maximum calculation is about 42–49 A with a 5 W hotel assumption. Two servos plus avionics may draw more than 5 W during maneuvers. Verify loaded voltage, pack temperature, capacity and actual current; a printed C rating alone does not prove this.
- The 49 A main-lead example dissipates roughly 6.3 W in the modeled 14 AWG positive/negative copper pair at 20°C; resistance rises with temperature. Six 18 AWG phase wires add heating whose current is phase RMS, not simply measured battery current. These resistance calculations do not prove thermal ampacity inside a closed black shell.
- The 5 A BEC supply rating is separate from actual servo transient current. Exact digital-servo stall current and transient rail behavior remain unknown. The existing separate 6 V servo supply/common-ground architecture is appropriate in principle; power integrity still needs measurement.
- The 3–4 minute energy estimate assumes 80% nominal pack energy and constant static power. It is an approximate hover-energy calculation, not a guaranteed usable flight duration. It excludes wind, maneuver duty cycle, actual voltage/efficiency evolution and battery aging.
- The beam calculation and nominal static loads are arithmetically consistent, but assumed filament E/allowable, layer orientation, creep, fastener joints, torsional gyro loads, fatigue, wheel gear and impact are not qualified. CAD shape validity and sampled clearance checks do not establish those properties.
- [Betaflight's documented BI layout](https://betaflight.com/docs/wiki/guides/current/Mixer) uses two motors and two servos. Actual firmware must contain the mixer, have correct pin resources and signs, and demonstrate loaded control behavior. Counter-rotating props and correct motor/servo directions remain essential.

## Candidate restricted test envelope and release gates

These numbers define a **bench-qualification target and later initial-flight candidate**, not an approved safe operating envelope. With the selected {selected_servo} there is currently no substantiated free-flight maneuver envelope. A reduced rate helps the calculated load, but cannot be certified until rotor inertia and loaded servo behavior are known.

1. Use the exact matched motor/prop pair, selected pack and final body. Weigh the complete aircraft with battery. Prefer a measured mass no greater than 672 g if relying on the 12 V / 0.85 reference and the 1.8 thrust target; a heavier build requires its own measured thrust result. Guards require a separate installed test.
2. At the intended lowest loaded operating voltage, demonstrate at least 1.8× measured all-up weight in total vertical thrust, and at least 1.6× weight in the worst planned projected-thrust condition. Do not use 12 V as the automatic battery landing setting. Derive actual alarms from selected-pack sag tests and manufacturer limits. Also test fresh-pack current at 16.8 V; measured temperatures/current must satisfy actual component continuous limits with margin.
3. Begin actuator qualification with ±10° pod travel, at most 10° bank and roll/pitch/yaw rate requests no greater than 45°/s. This deliberately small candidate range still requires the load checks below. Combined common/differential tilt must satisfy the absolute pod limit; retain independent physical stops and at least 3 mm measured loaded prop clearance.
4. Measure or bound prop plus rotating-bell inertia. Apply torque about the pod hinge representing measured thrust eccentricity, gravity, wire drag, tilt acceleration and **Jrotor·omega·45°/s** roll gyro load. At worst rotor RPM and warm operating conditions, demonstrate repetitive ±10° tracking without binding, loss of position, rail sag, thermal runaway or damage. Record step/oscillation phase delay and backlash. A fixture should reproduce loads; a hand near a running prop is not a load-test method. If continuous loaded tracking is insufficient, change servo/linkage and repeat mass/clearance/power checks rather than claiming the old stall torque is enough.
5. Verify both servos operating simultaneously keep their rail and the FC supply within actual specifications; check startup/transients, radio failsafe, mixer signs and motor order with props removed. Preserve firmware and resource configuration. Only after loaded actuator, propulsion, structural retention and vibration checks pass should the restrained response be used to set initial feedback gains and authorize short gentle free-flight trials. A tether changes dynamics and does not itself demonstrate free-flight stability.

The small-angle projection at 10° pod tilt plus 10° bank retains cos(10°)² = 0.970 of available thrust. This quantifies the proposed force benefit; it does not resolve gyro load, servo delay, gusts or coupled control saturation. Expand rate/angle/climb requests only from measured response and repeat the relevant projections/load checks.

## Selected R4 servo envelope and remaining interface work

The manufacturer's [Blue Bird BMS-115WV+](https://www.blue-bird-model.com/products_detail/55.htm) lists **23.2×10×23 mm**, **11±0.5 g**, catalogue torque **5.5 kgf·cm at 6 V**, speed **0.13 s/60° at 6 V**, dual ball bearings and a 25-tooth horn spline. It supports signals up to 333 Hz. R4 selects this installation envelope with **12 g per servo planning mass** and an initial 50 Hz signal configuration. Mounting ears, shaft location, spline, horn radius and cable exit still require a received-part interface check; it is not asserted to be a drop-in replacement or an exact vendor solid.

At one quarter of that catalogue torque, the same **unvalidated** screen is 0.135 N·m, compared with the earlier EMAX screen of 0.049 N·m. This offers substantially more numerical room for gyroscopic torque. The catalogue figure is not established here as continuous torque and published stall current was not found on that page. Thermal/current/tracking qualification still applies. Selection alone does not establish loaded bandwidth or justify higher-rate servo configuration.

## Defensible design status

**Lift feasibility: supported conditionally by matched reference data. Local control architecture: theoretically controllable. Under-800 g mass: projected, not weighed. Stable maneuvering, power/thermal limits and structural service life: unproven.** The key engineering issues are weak low-voltage reserve after growth, trim and combined-command limits, and body-roll gyroscopic servo/crank loading. R4 explicitly calculates these and adopts a stronger provisional servo. None of those changes makes the whole aircraft flight-verified.
'''
(OUT/'INDEPENDENT_FLIGHT_AUDIT.md').write_text(report)
print(json.dumps({k:ans[k] for k in ['audited_revision','nominal_mass_g','growth_mass_g','trim_deg_positive_is_thrust_toward_nose','linear_full_state_controllability_rank','moving_cg_shifts']},indent=2))
