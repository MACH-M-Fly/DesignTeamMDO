from Aircraft_Class.aircraft_class import *

# Create an object of type aircraft called the aircraft name, M6

AC = Aircraft()

#=========================================================================
# Problem Setup		
# Define name and number of surfaces
# 1 = 1 wing surface, 2 = 2 wing surfaces, etc.
#=========================================================================

AC.AC_name = "M6"
AC.Wings = 1
AC.H_tails = 1
AC.V_tails = 1
AC.booms = 1

# Number of wing sections (per half-span for wing and tail)
AC.num_Sections = 5


# 0 = Non-Linear (cubic) varying wing values
# 1 = Linear constant sweep leading edge, linearly varying wing values
AC.is_linear = 0

# Specify origin for aicraft build (root chord leading edge position)
AC.Xo = 0
AC.Yo = 0
AC.Zo = 0

#=========================================================================
# Wing Parameters (Design Variables)
# Initial Conditions for Optimizer
#=========================================================================
# Wingspan (feet)
AC.b_wing = 6
AC.b_wing_max = 20
AC.b_wing_min = 2
# Wing dihedral angle (degrees)
AC.dihedral = 5
AC.dihedral_max = 25
AC.dihedral_min = -10
# Quarter Chord Sweep in degrees (cubic)
# (can constrain to no sweep by making max and min 0 degrees)
s_a = 0; s_b = 0; s_c = 0; s_d = 10;
AC.sweep = np.array([s_a, s_b, s_c, s_d])
AC.sweep_max = 35
AC.sweep_min = -5		
# Chord (cubic constants: chord = ax^3+bx^2+c*x+d, x = half-span position)
ch_a = -.03; ch_b = -2; ch_c = -0.5; ch_d = 3;
AC.chord = np.array([ch_a, ch_b, ch_c, ch_d])
AC.chord_max = 5
AC.chord_min = -5
# Distance between CG and landing gear (feet)
AC.dist_LG = 1
AC.dist_LG_max = 10
AC.dist_LG_min = 0.01
# Length of tailboom (feet)
AC.boom_len = 4
AC.boom_len_max = 10
AC.boom_len_min = 0.01
# Wing camber (cubic constants: camber = c_ax^3+c_bx^2+c_c*x + c_d, x = half-span position)
c_a = 1; c_b = 1; c_c = 1; c_d = 1
AC.camber = np.array([c_a,c_b,c_c,c_d])
AC.camber_max = 0.15
AC.camber_min = 0.1
# Percent chord at max wing camber constraint (cubic constants: max camber = mc_ax^2+mc_bx+mc_c, x = half-span position)
mc_a = 1; mc_b = 1; mc_c = 1; mc_d = 1;
AC.max_camber = np.array([mc_a,mc_b,mc_c, mc_d])
AC.max_camber_max = 0.5
AC.max_camber_min = 0.35
# Wing thickness (cubic constants: thickness = t_ax^2+t_bx+t_c, x = half-span position)
t_a = 1; t_b = 1; t_c = 1; t_d = 1;
AC.thickness = np.array([t_a,t_b,t_c, t_d])
AC.thickness_max = 0.15
AC.thickness_min = 0.1
# Percent chord at max wing thickness constraint (cubic constants: thickness = mt_ax^2+mt_bx+mt_c, x = half-span position)
mt_a = 1; mt_b = 1; mt_c = 1; mt_d = 1;
AC.max_thickness = np.array([mt_a,mt_b,mt_c,mt_d])
AC.max_thickness_max = 0.45
AC.max_thickness_min = 0.25
# Inclination angle of wing (degrees) (cubic constants: Ainc = ang_ax^3+ang_bx^2+ang_c*x + ang_d, x = half-span position)
ang_a = 1; ang_b = 1; ang_c = 1; ang_d = 1;
AC.Ainc = np.array([ang_a,ang_b, ang_c, ang_d])
AC.Ainc_max = 20
AC.Ainc_min = -20

#=========================================================================
# Tail Parameters (Design Variables)
# Initial Conditions for Optimizer
#=========================================================================
# Horizontal tail span (feet)
AC.b_htail = 3
AC.b_htail_max = 6
AC.b_htail_min = 0.1
# Vertical tail span (feet)
AC.b_vtail = 1
AC.b_vtail_max = 6
AC.b_vtail_min = 0.1
# Horizontal Chord (cubic constants: chord = ax^3+bx^2+c*x+d, x = half-span position)
ht_a = 0; ht_b = 0; ht_c = 0; ht_d = 1;
AC.htail_chord = np.array([ht_a, ht_b, ht_c, ht_d])
AC.htail_chord_max = 5
AC.htail_chord_min = -5
# Vertical Chord (cubic constants: chord = ax^3+bx^2+c*x+d, x = half-span position)
vt_a = 0; vt_b = 0; vt_c = 0; vt_d = 1;
AC.vtail_chord = np.array([vt_a, vt_b, vt_c, vt_d])
AC.vtail_chord_max = 5
AC.vtail_chord_min = -5


#=========================================================================
# Constant Parameters
#=========================================================================

#       =========================================================================
#		Propulsion
#       =========================================================================
# Thrust (quadratic thrust curve: Thrust (lbs) = a*u^2 + b*u + c, u = velocity)
a = 1; b = 1; c = 1;
AC.thrust = {a,b,c}
# Lap perimiter (feet)
AC.lap_perim = 350
# Coefficient of rolling friction (mu)
AC.mu = 0.8
# Runway length (feet)
AC.runway_length = 200
# Desired climb rate (for carpet plot, ft/s)
AC.climb_rate = 5
# Desired bank angle (sustained load factor turn, steady level, degrees)
AC.bank_angle = 20

#       =========================================================================
#		Weights
#       =========================================================================
# Spar density (lbs/ft)
AC.spar_lindens = 5
# Leading Edge (LE) density (lbs/ft)
AC.LE_lindens = 5
# Trailing Edge (TE) density (lbs/ft)
AC.TE_lindens = 5
# Rib chordwise density (lbs/ft)
AC.k_ribs = 1;
# Rib spanwise desnity (# of ribs per ft)
AC.rib_lindens = 2
# Tail Rib chordwise density (lbs/ft)
AC.k_ribs_t = 1;
# Tail Rib spanwise desnity (# of ribs per ft)
AC.rib_lindens_t = 2 
# Motor mass (lbs)
AC.m_motor = 2
# Battery mass (lbs)
AC.m_battery = 1
# Propeller mass (lbs)
AC.m_propeller = 1
# Electronics mass
AC.m_electronics = 1
# Fuselage mass
AC.m_fuselage = 1


# Create object of type wing using surface 
AC.wing = Wing(AC.num_Sections, AC.is_linear, AC.b_wing, \
	AC.sweep, AC.chord, \
	AC.Xo, AC.Yo, AC.Zo,AC.dihedral, AC.boom_len, [], AC.Ainc)

AC.tail = Tail(AC.num_Sections, AC.is_linear, AC.b_htail, \
	AC.htail_chord, AC.b_vtail, AC.vtail_chord, AC.Xo, AC.Yo, \
	AC.Zo, AC.boom_len)