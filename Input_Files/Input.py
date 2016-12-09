from Aircraft_Class.aircraft_class import *

# Create an object of type aircraft called the aircraft name, M6
M6 = Aircraft()

#=========================================================================
# Problem Setup		
# Define name and number of surfaces
# 1 = 1 wing surface, 2 = 2 wing surfaces, etc.
#=========================================================================

M6.AC_name = "M6"
M6.Wings = 1
M6.H_tails = 1
M6.V_tails = 1
M6.booms = 1

# Number of wing sections (per half-span for wing and tail)
M6.num_Sections = 5


# 0 = Non-Linear (cubic) varying wing values
# 1 = Linear constant sweep leading edge, linearly varying wing values
M6.is_linear = 1

# Specify origin for aicraft build (root chord leading edge position)
M6.Xo = 0
M6.Yo = 0
M6.Zo = 0

#=========================================================================
# Wing Parameters (Design Variables)
# Initial Conditions for Optimizer
#=========================================================================
# Wingspan (feet)
M6.b_wing = 6
M6.b_wing_max = 20
M6.b_wing_min = 2
# Wing dihedral angle (degrees)
M6.dihedral = 5
M6.dihedral_max = 25
M6.dihedral_min = -10
# Quarter Chord Sweep in degrees (cubic)
# (can constrain to no sweep by making max and min 0 degrees)
s_a = 0; s_b = 0; s_c = 0; s_d = 0;
M6.sweep = np.array([s_a, s_b, s_c, s_d])
M6.sweep_max = 35
M6.sweep_min = -5		
# Chord (cubic constants: chord = ax^3+bx^2+c*x+d, x = half-span position)
ch_a = 0; ch_b = 0; ch_c = 0; ch_d = 3;
M6.chord = np.array([ch_a, ch_b, ch_c, ch_d])
M6.chord_max = 5
M6.chord_min = -5
# Distance between CG and landing gear (feet)
M6.dist_LG = 1
M6.dist_LG_max = 10
M6.dist_LG_min = 0.01
# Length of tailboom (feet)
M6.boom_len = 4
M6.boom_len_max = 10
M6.boom_len_min = 0.01
# Wing camber (cubic constants: camber = c_ax^3+c_bx^2+c_c*x + c_d, x = half-span position)
c_a = 1; c_b = 1; c_c = 1; c_d = 1
M6.camber = np.array([c_a,c_b,c_c,c_d])
M6.camber_max = 0.15
M6.camber_min = 0.1
# Percent chord at max wing camber constraint (cubic constants: max camber = mc_ax^2+mc_bx+mc_c, x = half-span position)
mc_a = 1; mc_b = 1; mc_c = 1; mc_d = 1;
M6.max_camber = np.array([mc_a,mc_b,mc_c, mc_d])
M6.max_camber_max = 0.5
M6.max_camber_min = 0.35
# Wing thickness (cubic constants: thickness = t_ax^2+t_bx+t_c, x = half-span position)
t_a = 1; t_b = 1; t_c = 1; t_d = 1;
M6.thickness = np.array([t_a,t_b,t_c, t_d])
M6.thickness_max = 0.15
M6.thickness_min = 0.1
# Percent chord at max wing thickness constraint (cubic constants: thickness = mt_ax^2+mt_bx+mt_c, x = half-span position)
mt_a = 1; mt_b = 1; mt_c = 1; mt_d = 1;
M6.max_thickness = np.array([mt_a,mt_b,mt_c,mt_d])
M6.max_thickness_max = 0.45
M6.max_thickness_min = 0.25
# Inclination angle of wing (degrees) (cubic constants: Ainc = ang_ax^3+ang_bx^2+ang_c*x + ang_d, x = half-span position)
ang_a = 1; ang_b = 1; ang_c = 1; ang_d = 1;
M6.Ainc = np.array([ang_a,ang_b, ang_c, ang_d])
M6.Ainc_max = 20
M6.Ainc_min = -20

#=========================================================================
# Tail Parameters (Design Variables)
# Initial Conditions for Optimizer
#=========================================================================
# Horizontal tail span (feet)
M6.b_htail = 3
M6.b_htail_max = 6
M6.b_htail_min = 0.1
# Vertical tail span (feet)
M6.b_vtail = 1
M6.b_vtail_max = 6
M6.b_vtail_min = 0.1
# Horizontal Chord (cubic constants: chord = ax^3+bx^2+c*x+d, x = half-span position)
ht_a = 0; ht_b = 0; ht_c = 0; ht_d = 1;
M6.htail_chord = np.array([ht_a, ht_b, ht_c, ht_d])
M6.htail_chord_max = 5
M6.htail_chord_min = -5
# Vertical Chord (cubic constants: chord = ax^3+bx^2+c*x+d, x = half-span position)
vt_a = 0; vt_b = 0; vt_c = 0; vt_d = 1;
M6.vtail_chord = np.array([vt_a, vt_b, vt_c, vt_d])
M6.vtail_chord_max = 5
M6.vtail_chord_min = -5


#=========================================================================
# Constant Parameters
#=========================================================================

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
# Desired climb rate (for carpet plot, ft/s)
M6.climb_rate = 5
# Desired bank angle (sustained load factor turn, steady level, degrees)
M6.bank_angle = 20

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


# Create object of type wing using surface 
M6.wing = Wing(M6.num_Sections, M6.is_linear, M6.b_wing, \
	M6.sweep, M6.chord, \
	M6.Xo, M6.Yo, M6.Zo,M6.dihedral, M6.boom_len, [], M6.Ainc)

M6.tail = Tail(M6.num_Sections, M6.is_linear, M6.b_htail, \
	M6.htail_chord, M6.b_vtail, M6.vtail_chord, M6.Xo, M6.Yo, \
	M6.Zo, M6.boom_len)