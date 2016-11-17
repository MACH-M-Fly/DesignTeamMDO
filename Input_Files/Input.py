from Aircraft_Class.aircraft_class import *


M6 = Aircraft()


#   =========================================================================
#		Define name and number of surfaces
#		1 = 1 wing surface, 2 = 2 wing surfaces, etc.
#       =========================================================================

M6.AC_name = "M6"
M6.Wings = 1
M6.H_tails = 1
M6.V_tails = 1
M6.booms = 1

# Number of wing sections
# Per half-wing		
M6.num_Sections = 5

# 0 = Non-Linear (cubic) interpolation between spanwise sections
# 1 = Linear interpolation between spanwise sections 
M6.is_linear = 1

# Specify origin for aicraft build (root chord leading edge position)
M6.Xo = 100
M6.Yo = 0
M6.Zo = 100

#       =========================================================================
#		Geometry Design Variables
#		Initial Conditions for Optimizer
#       =========================================================================
# Wingspan (feet)
M6.b_wing = 5
M6.b_wing_max = 20
M6.b_wing_min = 2
# Quarter Chord Sweep in degrees for each section
# (can constrain to no sweep by making max and min 0 degrees)
M6.sweep = np.array([10, 10, 10, 10, 10])
M6.sweep_max = 35
M6.sweep_min = -5		
# Chord (quadratic constants: chord = ax^3+bx^2+c*x+d, x = half-span position)
ch_a = 1; ch_b = 1; ch_c = 1; ch_d = 1;
M6.chord = np.array([ch_a, ch_b, ch_c, ch_d])
M6.chord_max = 5
M6.chord_min = -5
# Horizontal tail chord (feet)
M6.c_r_ht = 1
M6.c_r_ht_max = 5
M6.c_r_ht_min = 0.01
# Vertical tail chord (feet)
M6.c_r_vt = 1
M6.c_r_vt_max = 5
M6.c_r_vt_min = 0.01
# Distance between CG and landing gear (feet)
M6.dist_LG = 1
M6.dist_LG_max = 10
M6.dist_LG_min = 0.01
# Length of tailboom (feet)
M6.boom_len = 2
M6.boom_len_max = 10
M6.boom_len_min = 0.01
# Wing camber (quadratic constants: camber = c_ax^3+c_bx^2+c_c*x + c_d, x = half-span position)
c_a = 1; c_b = 1; c_c = 1; c_d = 1
M6.camber = np.array([c_a,c_b,c_c,c_d])
M6.camber_max = 0.15
M6.camber_min = 0.1
# Percent chord at max wing camber constraint (quadratic constants: max camber = mc_ax^2+mc_bx+mc_c, x = half-span position)
mc_a = 1; mc_b = 1; mc_c = 1; mc_d = 1;
M6.max_camber = np.array([mc_a,mc_b,mc_c, mc_d])
M6.max_camber_max = 0.5
M6.max_camber_min = 0.35
# Wing thickness (quadratic constants: thickness = t_ax^2+t_bx+t_c, x = half-span position)
t_a = 1; t_b = 1; t_c = 1; t_d = 1;
M6.thickness = np.array([t_a,t_b,t_c, t_d])
M6.thickness_max = 0.15
M6.thickness_min = 0.1
# Percent chord at max wing thickness constraint (quadratic constants: thickness = mt_ax^2+mt_bx+mt_c, x = half-span position)
mt_a = 1; mt_b = 1; mt_c = 1; mt_d = 1;
M6.max_thickness = np.array([mt_a,mt_b,mt_c,mt_d])
M6.max_thickness_max = 0.45
M6.max_thickness_min = 0.25
# Inclination angle of wing (degrees)
ang_a = 1; ang_b = 1; ang_c = 1; ang_d = 1;
M6.Ainc = np.array([ang_a,ang_b, ang_c, ang_d])
M6.Ainc_max = 20
M6.Ainc_min = -20


#       =========================================================================
#		Constant Parameters
#       =========================================================================

#       =========================================================================
#		Propulsion
#       =========================================================================
# Thrust (quadratic thrust curve: Thrust (lbs) = a*u^2 + b*u + c, u = velocity)
a = 1; b = 1; c = 1;
M6.thrust = {a,b,c}
# Lap perimiter (feet)
M6.lap_perim = 350
# Coefficient of rolling friction (mu)
M6.mu = 0.8
# Runway length (feet)
M6.runway_length = 200

#       =========================================================================
#		Weights
#       =========================================================================
# Spar density (lbs/ft)
M6.spar_lindens = 5
# Leading Edge (LE) density (lbs/ft)
M6.LE_lindens = 5
# Trailing Edge (TE) density (lbs/ft)
M6.TE_lindens = 5
# Rib chordwise density (lbs/ft)
M6.k_ribs = 1;
# Rib spanwise desnity (# of ribs per ft)
M6.rib_lindens = 2
# Tail Rib chordwise density (lbs/ft)
M6.k_ribs_t = 1;
# Tail Rib spanwise desnity (# of ribs per ft)
M6.rib_lindens_t = 2 
# Motor mass (lbs)
M6.m_motor = 2
# Battery mass (lbs)
M6.m_battery = 1
# Propeller mass (lbs)
M6.m_propeller = 1
# Electronics mass
M6.m_electronics = 1
# Fuselage mass
M6.m_fuselage = 1

#       =========================================================================
#		Post-Processing
#       =========================================================================	
# Desired climb rate (for carpet plot, ft/s)
M6.climb_rate = 5
# Desired bank angle (sustained load factor turn, steady level, degrees)
M6.bank_angle = 20



M6.Wing = Surface(M6.num_Sections, M6.is_linear, M6.b_wing, \
	M6.sweep, M6.chord, M6.Xo, M6.Yo, M6.Zo, [], M6.Ainc)
