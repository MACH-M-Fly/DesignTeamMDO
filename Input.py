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

# Select Mission (1 for M-Fly max payload, 2 for MACH lap-time)
AC.mission = 2

# Number of wing sections (per half-span for wing and tail)
num_Sections_wing = 5
num_Sections_tail = 5


# 0 = Non-Linear (cubic) varying wing values
# 1 = Linear constant sweep leading edge, linearly varying wing values
is_linear = 0

# Specify origin for aicraft build (root chord leading edge position)
Xo = 0
Yo = 0
Zo = 0

#=========================================================================
# Wing Parameters (Design Variables)
# Initial Conditions for Optimizer
#=========================================================================
# Wingspan (feet)
b_wing = 3.0

# Wing dihedral angle (degrees)
dihedral = 5.0


# Quarter Chord Sweep in degrees (cubic)
# (can constrain to no sweep by making max and min 0 degrees)
s_a = 0; s_b = 0; s_c = 0; s_d = 10;
sweep = np.array([s_a, s_b, s_c, s_d])
		
# Chord (cubic constants: chord = ax^3+bx^2+c*x+d, x = half-span position)
ch_a = .0; ch_b = .0; ch_c = .0; ch_d = 1.;
chord = np.array([ch_a, ch_b, ch_c, ch_d])

# Distance between CG and landing gear (feet)
AC.dist_LG = 1

# Length of tailboom (feet)
AC.boom_len = 4

# Wing camber (cubic constants: camber = c_ax^3+c_bx^2+c_c*x + c_d, x = half-span position)
c_a = 1; c_b = 1; c_c = 1; c_d = 1
camber = np.array([c_a,c_b,c_c,c_d])
camber_max = 0.15
camber_min = 0.1
# Percent chord at max wing camber constraint (cubic constants: max camber = mc_ax^2+mc_bx+mc_c, x = half-span position)
mc_a = 1; mc_b = 1; mc_c = 1; mc_d = 1;
max_camber = np.array([mc_a,mc_b,mc_c, mc_d])

# Wing thickness (cubic constants: thickness = t_ax^2+t_bx+t_c, x = half-span position)
t_a = 1; t_b = 1; t_c = 1; t_d = 1;
thickness = np.array([t_a,t_b,t_c, t_d])
thickness_max = 0.15
thickness_min = 0.1
# Percent chord at max wing thickness constraint (cubic constants: thickness = mt_ax^2+mt_bx+mt_c, x = half-span position)
mt_a = 1; mt_b = 1; mt_c = 1; mt_d = 1;
max_thickness = np.array([mt_a,mt_b,mt_c,mt_d])

# Inclination angle of wing (degrees) (cubic constants: Ainc = ang_ax^3+ang_bx^2+ang_c*x + ang_d, x = half-span position)
ang_a = 1; ang_b = 1; ang_c = 1; ang_d = 1;
Ainc = np.array([ang_a,ang_b, ang_c, ang_d])


#=========================================================================
# Tail Parameters (Design Variables)
# Initial Conditions for Optimizer
#=========================================================================
# Horizontal tail span (feet)
b_htail = 1.0

# Vertical tail span (feet)
b_vtail = 1.0

# Horizontal Chord (cubic constants: chord = ax^3+bx^2+c*x+d, x = half-span position)
ht_a = 0; ht_b = 0; ht_c = 0; ht_d = 1;
htail_chord = np.array([ht_a, ht_b, ht_c, ht_d])

# Vertical Chord (cubic constants: chord = ax^3+bx^2+c*x+d, x = half-span position)
vt_a = 0; vt_b = 0; vt_c = 0; vt_d = 1;
vtail_chord = np.array([vt_a, vt_b, vt_c, vt_d])



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


# Create an instance of AC for wing values
AC.wing = Wing(num_Sections_wing, is_linear, b_wing, \
	sweep, chord, \
	Xo, Yo, Zo, dihedral, camber, max_camber, thickness, max_thickness ,Afiles=[], Ainc=np.array([]))

# Add wing structural parameters ('elliptical', 'uniform', 'lin_decrease', 'lin_increase')
AC.wing.dist_type = 'elliptical'

# Add wing structural parameters ('C', R', 'I')
AC.wing.spar_type = 'C'

# Add spar dimensions (m)
outer_radius = 0.1 
inner_radius = 0.09
AC.wing.spar_dim = [outer_radius, inner_radius]

# Spar Young's Modulus
AC.wing.spar_E = 1.0e6

# Create an instance of AC for tail values
AC.tail = Tail(num_Sections_tail, is_linear, b_htail, \
	htail_chord, b_vtail, vtail_chord, Xo, Yo, \
	Zo, AC.boom_len)


AC.score = 0


print('=============== Initial vehicle Parameters =============')
print('Weight (lbs)', AC.weight)
print('CDp', AC.CD_p)
print('Tailboom Length', AC.boom_len)
print('Iyy', AC.Iyy)
print('Mission', AC.mission)
print('CG (x,y,z)', AC.CG)


print('=============== Initial wing Parameters =============')
print('AC.wing.num_Sections: ', AC.wing.num_Sections)
print('AC.wing.is_linear: ', AC.wing.is_linear)
print('AC.wing.b_wing: ', AC.wing.b_wing)
print('AC.wing.sweep: ', AC.wing.sweep)
print('AC.wing.Sref', AC.wing.Sref)
print('AC.wing.chord: ', AC.wing.chord)
print('Chord Values at Section" ', AC.wing.chord_vals)
print('AC.wing.Xo: ', AC.wing.Xo)
print('AC.wing.Yo: ', AC.wing.Yo)
print('AC.wing.Zo: ', AC.wing.Zo)
print('AC.wing.Xle: ', AC.wing.Xle)
print('AC.wing.Yle: ', AC.wing.Yle)
print('AC.wing.Zle: ', AC.wing.Zle)
print('AC.wing.dihedral: ', AC.wing.dihedral)
print('AC.wing.Afiles: ', AC.wing.Afiles)
print('AC.wing.Ainc: ', AC.wing.Ainc)
print('AC.wing.sec_span: ', AC.wing.sec_span)
print('AC.wing.MAC', AC.wing.MAC)
print('AC.camber: ', AC.wing.camber)
print('Camber Values at Section', AC.wing.camber_vals)
print('AC.max_camber: ', AC.wing.max_camber)
print('Max Camber Position at Section', AC.wing.max_camber_vals)
print('AC.thickness: ', AC.wing.thickness)
print('Thickness Values at Section', AC.wing.thickness_vals)
print('AC.max_thickness: ', AC.wing.max_thickness)
print('Max Thickness Values at Section', AC.wing.max_thickness_vals)

print('\n')
print('=============== Initial tail Parameters =============')
print('AC.tail.num_Sections: ', AC.tail.num_Sections)
print('AC.tail.is_linear: ', AC.tail.is_linear)
print('AC.tail.b_htail: ', AC.tail.b_htail)
print('AC.tail.Sref', AC.tail.Sref)
print('AC.tail.htail_chord: ', AC.tail.htail_chord)
print('Horiz. Tail Chord Values at Section" ', AC.tail.htail_chord_vals)
print('AC.tail.b_vtail: ', AC.tail.b_vtail)
print('AC.tail.vtail_chord: ', AC.tail.vtail_chord)
print('Vert. Tail Chord Values at Section" ', AC.tail.vtail_chord_vals)
print('AC.tail.Xo: ', AC.tail.Xo)
print('AC.tail.Yo: ', AC.tail.Yo)
print('AC.tail.Zo: ', AC.tail.Zo)
print('AC.tail.Xle_ht: ', AC.tail.Xle_ht)
print('AC.tail.Yle_ht: ', AC.tail.Yle_ht)
print('AC.tail.Zle_ht: ', AC.tail.Zle_ht)
print('AC.tail.boom_len: ', AC.tail.boom_len)
print('AC.tail.sec_span_htail: ', AC.tail.sec_span_htail)
print('AC.tail.sec_span_vtail: ', AC.tail.sec_span_vtail)
print('\n')

# print 
# exit()