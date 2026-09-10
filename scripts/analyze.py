"""Reproducible preliminary engineering screens; not flight qualification."""
from pathlib import Path
import json,math,hashlib
R=Path(__file__).resolve().parents[1]
all_inv=json.loads((R/'engineering/inventory.json').read_text())
inv=[x for x in all_inv if x.get('installed',True)]
optional_mass=sum(x['mass_g'] for x in all_inv if not x.get('installed',True))
wires=json.loads((R/'engineering/wiring_routes.json').read_text())
p=json.loads((R/'engineering/parameters.json').read_text())
# Transcribed from EMAX RS2205-2.jpg, original 2300KV + HQ5045BN two blade.
curves={12:[(1,62),(3,162),(5,236),(7,311),(9.1,374),(11,439),(13,490),(15.3,548),(17.3,611),(20.7,712)],
16:[(1,76),(3,183),(5,283),(7.1,352),(9.1,426),(11,497),(13,560),(15,628),(17,692),(19,754),(21,812),(23.3,878),(25.4,936),(27.3,997),(29.9,1024)]}
def interp(x,points):
    assert points[0][0]<=x<=points[-1][0],(x,points[0],points[-1])
    for (xa,ya),(xb,yb) in zip(points,points[1:]):
        if xa<=x<=xb:return ya+(yb-ya)*(x-xa)/(xb-xa)
    return points[-1][1]
extra=[('Harness and secondary connectors',36,[7,0,4]),('Other fasteners, spacers, retaining hardware',25,[0,0,15]),('Straps, foam, ties, insulation',8,[39,0,-25]),('Adhesive and light finish',8,[-8,0,0])]
modeled=sum(x['mass_g'] for x in inv);printed=sum(x['mass_g'] for x in inv if x['printed'])
mass=modeled+sum(e[1] for e in extra);budget=mass*1.10
cg=[(sum(x['mass_g']*x['center_mm'][j] for x in inv)+sum(e[1]*e[2][j] for e in extra))/mass for j in range(3)]
inertia=[]
for axis in range(3):
    oth=[j for j in range(3) if j!=axis]
    val=sum(x['mass_g']/1e9*(sum((x['center_mm'][j]-cg[j])**2 for j in oth)+sum(x['bbox_mm'][j]**2 for j in oth)/12) for x in inv)
    val+=sum(e[1]/1e9*sum((e[2][j]-cg[j])**2 for j in oth) for e in extra)
    inertia.append(val)
h=(35-cg[2])/1000;d=.117;g=9.80665;eta=.85
cases=[]
for m in [mass,budget,800]+([mass+optional_mass] if optional_mass else []):
    for v in [12,16]:
        thrust=m/(2*eta)
        amps=interp(thrust,[(t,i) for i,t in curves[v]])
        power=2*v*amps+5 # avionics + typical servo load allowance
        max_i=min(24,curves[v][-1][0])
        tmax=interp(max_i,curves[v])*eta
        cases.append({'mass_g':m,'voltage_V':v,'installed_derating':eta,'hover_per_motor_A':amps,'hover_total_A':2*amps+5/v,'hover_power_W':power,'usable_energy_Wh':14.8*1.3*.8,'endurance_min':14.8*1.3*.8/power*60,'screen_current_limit_per_motor_A':max_i,'installed_max_total_gf':2*tmax,'TW_vertical':2*tmax/m,'TW_at_20deg':2*tmax*math.cos(math.radians(20))/m,'TW_at_20deg_pod_and_20deg_bank':2*tmax*math.cos(math.radians(20))**2/m,'TW_at_10deg_pod_and_10deg_bank':2*tmax*math.cos(math.radians(10))**2/m,'meets_preferred_1p8_vertical':2*tmax/m>=1.8,'meets_preferred_1p6_at20':2*tmax*math.cos(math.radians(20))/m>=1.6})
# Simple beam screen: primary rectangular box, root local stress multiplier 2.
I=(24*14**3-20*10**3)/12;load=10.1;span=90;E=1500
sigma=load*span*7/I;deflection=load*span**3/(3*E*I)
# 52mm integral crank extension, unchanged 8x7 section. R4 includes an 0.08Nm
# load screen (rounded above bounded gyro + prior loads at candidate 45deg/s).
# This is not proof of printed joint, fatigue or continuous strength.
crank_screen_torque=.08
crank_force=crank_screen_torque/.014;crank_I=8*7**3/12
crank_stress=crank_force*52*3.5/crank_I
crank_deflection=crank_force*52**3/(3*E*crank_I)
servo={'model':'Blue Bird BMS-115WV+','catalogue_torque_6V_kgf_cm':5.5,'catalogue_torque_6V_Nm':5.5*.0980665,'catalogue_no_load_speed_6V_s_per_60deg':.13,'continuous_torque_rating':'not established','stall_current_A':None,'working_screen_Nm':5.5*.0980665/4,'working_screen_evidence':'assumed quarter of catalogue torque; not a manufacturer continuous rating','thrust_axis_error_mm_assumed':2,
       'thrust_offset_Nm':load*.002,'gravity_Nm_assumed':.004,'acceleration_Nm_assumed':.003,'harness_friction_Nm_assumed':.01,
       'crank_stress_MPa':crank_stress,'crank_deflection_mm':crank_deflection,'crank_screen_torque_Nm':crank_screen_torque,'crank_section_mm':[8,7],'crank_span_mm':52,'crank_load_test_required':True}
servo['base_quasistatic_load_Nm']=sum(servo[k] for k in ['thrust_offset_Nm','gravity_Nm_assumed','acceleration_Nm_assumed','harness_friction_Nm_assumed'])
# Rotor H changes during body roll: Omega_X cross H_Z loads the servo hinge Y.
# Bounds assume prop <=3g, <=63.5mm radius and rotating motor mass <=30g at
# <=13.95mm radius. All motor mass at rim deliberately overbounds the bell.
# RPM bound is source table max, not a claim that fresh-pack speed is limited.
prop_J_est=.003*.0635**2/3
rotor_J_bound=.003*.0635**2+.030*.01395**2
omega_bound=24600*2*math.pi/60
gyro_cases=[]
for roll_rate in [45,90,180]:
    torque=rotor_J_bound*omega_bound*math.radians(roll_rate)
    total=servo['base_quasistatic_load_Nm']+torque
    gyro_cases.append({'body_roll_deg_s':roll_rate,'source_max_rpm_assumed':24600,'rotor_inertia_radial_bound_kg_m2':rotor_J_bound,'gyro_torque_bound_Nm':torque,'total_load_screen_Nm':total,'quarter_catalogue_margin_ratio':servo['working_screen_Nm']/total})
servo['gyro_cases']=gyro_cases
servo['prop_only_uniform_radial_inertia_estimate_kg_m2']=prop_J_est
servo['rotor_inertia_radial_bound_kg_m2']=rotor_J_bound
servo['screen_load_Nm']=gyro_cases[0]['total_load_screen_Nm']
servo['screen_scope']='45deg/s body roll at24600RPM radial mass bound, plus prior loads; all masses/RPM require verification'
servo['working_margin_ratio']=servo['working_screen_Nm']/servo['screen_load_Nm']
# Conservative DC resistance screening only. Phase RMS differs from battery current.
rho={14:.008286,18:.02095,20:.03331,22:.05296,24:.08422,26:.1339,30:.3386}
wire_checks=[]
for w in wires:
    if 'Phase' in w['name'] or 'ESC_VBAT' in w['name'] or 'ESC_GND' in w['name'] or w['name'] in ['B1_positive','B1_negative']:
        ohm=rho[w['awg']]*w['cut_length_mm']/1000
        current=22 if w['awg']==14 else 11
        wire_checks.append({'name':w['name'],'awg':w['awg'],'one_conductor_ohm_20C':ohm,'illustrative_current_A':current,'drop_V':current*ohm,'heat_W':current**2*ohm,'upper_screen_current_A':49 if w['awg']==14 else 24,'heat_at_upper_screen_W':((49 if w['awg']==14 else 24)**2)*ohm})
# Local force/moment allocation rank, hover basis [dTL,dTR,dL,dR].
T=mass/1000*g/2
allocation=[[1,1,0,0],[d,-d,0,0],[0,0,h*T,h*T],[0,0,-d*T,d*T]]
det=-4*d*d*h*T*T
assert abs(det)>1e-9 and h>0
# Attitude-only actuator-lag screening. NOT executable FC tuning.
def simulate(wn,zeta,lag,gain,axis):
    dt=.002;x=math.radians(10);vel=0;act=0;trace=[]
    coeff=mass/1000*g*(h if axis=='pitch' else d)/inertia[1 if axis=='pitch' else 2]
    for step in range(4001):
        cmd=-(wn*wn*x+2*zeta*wn*vel)/coeff
        cmd=max(-math.radians(20),min(math.radians(20),cmd))
        rate=max(-2,min(2,(cmd-act)/lag));act+=rate*dt
        accel=coeff*gain*act
        vel+=accel*dt;x+=vel*dt
        if step%25==0:trace.append([round(step*dt,3),math.degrees(x),math.degrees(act)])
    return {'lag_s':lag,'gain_ratio':gain,'axis':axis,'final_error_deg':math.degrees(x),'final_rate_deg_s':math.degrees(vel),'peak_abs_deg':max(abs(t[1]) for t in trace),'trace':trace}
sims=[simulate(4,.85,lag,gain,axis) for lag in [.04,.08,.15] for gain in [.5,1,1.5] for axis in ['pitch','yaw']]
results={'status':'PRELIMINARY ENGINEERING PROTOTYPE; physical flight qualification open','printed_g':printed,'optional_guards_g':optional_mass,'mass_with_optional_guards_g':mass+optional_mass,'purchased_allocated_g':modeled-printed,'installation_allowances':extra,'nominal_mass_g':mass,'mass_with_10percent_growth_g':budget,'margin_to_800g_with_growth':800-budget,'cg_mm':cg,'cg_evidence':'uniform envelopes and allowances, not measured','inertia_kg_m2':inertia,'inertia_evidence':'component bounding-box approximation, not tensor from mass-distributed hardware','pitch_lever_m':h,'hover_trim_angle_deg':math.degrees(math.atan2(-cg[0],h*1000)),'hover_trim_convention':'positive tilt points thrust toward +X nose; body attitude must compensate to hold world thrust vertical','cases':cases,'structure':{'beam_I_mm4':I,'load_N_each':load,'span_mm':span,'assumed_E_MPa':E,'stress_MPa':sigma,'stress_with_Kt2_MPa':2*sigma,'deflection_mm':deflection,'assumed_working_allowable_MPa':5,'margin_after_Kt2':5/(2*sigma),'evidence':'beam hand calculation; no FEA, anisotropy fatigue temperature and joint compliance not solved'},'servo':servo,'wire_checks':wire_checks,'control_allocation':allocation,'allocation_determinant':det,'simulations':sims,'ideal_induced_power_W':(mass/1000*g)**1.5/math.sqrt(2*1.225*2*math.pi*.0635**2),'21700_alternative_mass_g':mass-170+4*71+20,'21700_note':'4S1P only; no custom pack CAD supplied; extra pack volume, cooling and tray require redesign; 90A is not used as an unconditional current rating'}
results['qualification_candidate']={'status':'UNQUALIFIED candidate for bench evaluation; not approved flight limits','pod_absolute_angle_deg':10,'bank_angle_deg':10,'body_rate_deg_s':45,'source_rpm_screen':24600,'measured_thrust_gate_vertical_TW':1.8,'measured_thrust_gate_projected_TW':1.6,'combined_tilt_constraint':'abs(common tilt)+abs(differential tilt)<=absolute pod limit','unknowns':'loaded bandwidth, current, actual rotor inertia/RPM, structural crank joints, firmware and flight behavior'}
results['mass_gate_at_12V_85pct']={'max_g_for_1p8_vertical':2*712*.85/1.8,'nominal_g_for_1p8_after10pct_growth':2*712*.85/1.8/1.1,'max_g_for_1p6_at20deg':2*712*.85*math.cos(math.radians(20))/1.6}
(R/'engineering/calculations.json').write_text(json.dumps(results,indent=2))
(R/'engineering/propulsion_reference.json').write_text(json.dumps({'source':'https://cdn.shopify.com/s/files/1/0469/7358/3518/t/3/assets/RS2205-2.jpg?v=1598532544','motor':'Genuine EMAX RS2205 2300KV','prop':'HQ5045BN two blade','curves_current_A_thrust_gf':curves,'interpolation':'piecewise linear, no extrapolation','derating_assumed':eta},indent=2))
print(json.dumps({k:results[k] for k in ['printed_g','nominal_mass_g','mass_with_10percent_growth_g','cg_mm','pitch_lever_m','21700_alternative_mass_g']},indent=2))
print('Nominal thrust cases',[(c['voltage_V'],round(c['TW_vertical'],2),round(c['TW_at_20deg'],2),round(c['endurance_min'],1)) for c in cases[:2]])
print('Attitude-only sim cases',len(sims),'settled under .5deg',sum(abs(s['final_error_deg'])<.5 for s in sims))
assert all(x['valid'] and x['solids']>=1 for x in inv)
assert all(max(x['bbox_mm'])<244 for x in inv if x['printed'])
assert abs(interp(29.9,curves[16])-1024)<1e-9
assert len(wires)==len({w['name'] for w in wires})
