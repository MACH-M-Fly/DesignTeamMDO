from Aircraft_Class.aircraft_class import *

# Create an object of type aircraft called the aircraft name, M6
# SI Units only: kg, m, s

AC = Aircraft()

#=========================================================================
# Problem Setup		
# Define name and number of surfaces
# 1 = 1 wing surface, 2 = 2 wing surfaces, etc.
#=========================================================================

AC.AC_name = "M6"
AC.wings = 1
AC.h_tails = 1
AC.v_tails = 1
AC.booms = 1

# Select Mission (1 for M-Fly max payload, 2 for MACH lap-time)
AC.mission = 2

# Number of wing sections (per half-span for wing and tail)
num_sections_wing = 5
num_sections_tail = 5


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
# Wingspan (m)
b_wing = 1.8
# Wing dihedral angle (degrees)
dihedral = 5.0


# Quarter Chord Sweep in degrees (cubic)
# (can constrain to no sweep by making max and min 0 degrees)
s_a = 0; s_b = 0; s_c = 0; s_d = 0.0;
sweep = np.array([s_a, s_b, s_c, s_d])
		
# Chord (cubic constants: chord = ax^3+bx^2+c*x+d, x = half-span position)
ch_a = .0; ch_b = .0; ch_c = .0; ch_d = 0.35;
chord = np.array([ch_a, ch_b, ch_c, ch_d])

# Distance between LE of wing and landing gear (m)
AC.dist_LG = 0.01

# Length of tailboom (m)
AC.boom_len = 0.75

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
ainc = np.array([ang_a,ang_b, ang_c, ang_d])


#=========================================================================
# Tail Parameters (Design Variables)
# Initial Conditions for Optimizer
#=========================================================================
# Horizontal tail span (m)
b_htail = 0.75

# Vertical tail span (m)
b_vtail = 0.2

# Horizontal Chord (cubic constants: chord = ax^3+bx^2+c*x+d, x = half-span position)
ht_a = 0; ht_b = 0; ht_c = 0; ht_d = 0.1;
htail_chord = np.array([ht_a, ht_b, ht_c, ht_d])

# Vertical Chord (cubic constants: chord = ax^3+bx^2+c*x+d, x = half-span position)
vt_a = 0; vt_b = 0; vt_c = 0; vt_d = 0.1;
vtail_chord = np.array([vt_a, vt_b, vt_c, vt_d])



#=========================================================================
# Constant Parameters
#=========================================================================

#       =========================================================================
#		Propulsion
#       =========================================================================
# Thrust (quadratic thrust curve: Thrust (N) = a*u^2 + b*u + c, u = velocity)
a = 1; b = 1; c = 1;
AC.thrust = {a,b,c}
# Lap perimiter (m)
AC.lap_perim = 350
# Coefficient of rolling friction (mu)
AC.mu = 0.8
# Runway length (m)
AC.runway_length = 200
# Desired climb rate (for carpet plot, m/s)
AC.climb_rate = 0.4
# Desired bank angle (sustained load factor turn, steady level, degrees)
AC.bank_angle = 20

#       =========================================================================
#		Weights
#       =========================================================================
# Spar density (kg/m)
AC.spar_lindens = 5*0.453592*0.3048/3
# density of aluminum (kg/m^3)
AC.spar_den = 2700.0
# Leading Edge (LE) density (kg/m)
AC.LE_lindens = 5*0.453592*0.3048/4
# Trailing Edge (TE) density (kg/m)
AC.TE_lindens = 5*0.453592*0.3048/4
# Spar density (kg/m)
AC.spar_lindens_t = 1*0.25
# Tail Leading Edge (LE) density (kg/m)
AC.LE_lindens_t = 5*0.453592*0.3048*0.25
# Tail Trailing Edge (TE) density (kg/m)
AC.TE_lindens_t = 5*0.453592*0.3048*0.15
# Rib Mass (kg/r) per 0.05 meter of rib
AC.k_ribs = 0.0065
# Rib spanwise desnity (# of ribs per m)
AC.rib_lindens = 4
# Tail Rib Mass (kg/r) per 0.1 meter of rib
AC.k_ribs_t = 0.0045
# Tail Rib spanwise desnity (# of ribs per m)
AC.rib_lindens_t = 4
# Motor mass (kg)
AC.m_motor = 1*0.3
# Battery mass (kg)
AC.m_battery = 1*0.34
# Propeller mass (kg)
AC.m_propeller = 1*0.0
# Electronics mass (kg)
AC.m_electronics = 1*0.2
# Fuselage mass (kg)
#AC.m_fuselage = 1*0.453592
# Ultrakote density (kg/m^2)
AC.ultrakote_Density = 0.1318

# Create an instance of AC for wing values
AC.wing = Wing(num_sections_wing, AC.is_linear, b_wing, sweep, chord, AC.Xo, \
		AC.Yo, AC.Zo, dihedral, camber,max_camber, thickness, max_thickness)

# Create an instance of AC for tail values
AC.tail = Tail(num_sections_tail, AC.is_linear, b_htail, \
		htail_chord, b_vtail, vtail_chord, AC.Xo, AC.Yo, \
		AC.Zo, AC.boom_len)


def updateAircraft(cur_AC):
	
	# Create an instance of AC for wing values
	AC.wing = Wing(cur_AC.wing.num_sections, cur_AC.is_linear, cur_AC.wing.b_wing, cur_AC.wing.sweep, \
		cur_AC.wing.chord, cur_AC.Xo, cur_AC.Yo, cur_AC.Zo, cur_AC.wing.dihedral, cur_AC.wing.camber, \
		cur_AC.wing.max_camber, cur_AC.wing.thickness, cur_AC.wing.max_thickness)


	# Add wing structural parameters ('elliptical', 'uniform', 'lin_decrease', 'lin_increase')
	AC.wing.dist_type = 'elliptical'

	# Add wing structural parameters ('C', R', 'I')
	AC.wing.spar_type = 'C'

	# Add spar dimensions (m)
	outer_radius = 0.015
	inner_radius = outer_radius*0.75
	AC.wing.spar_dim = [outer_radius, inner_radius]

	# Spar Young's Modulus
	AC.wing.spar_E = 68.9e9

	# Create an instance of AC for tail values
	AC.tail = Tail(cur_AC.tail.num_sections, cur_AC.is_linear, cur_AC.tail.b_htail, \
		cur_AC.tail.htail_chord, cur_AC.tail.b_vtail, cur_AC.tail.vtail_chord, cur_AC.Xo, cur_AC.Yo, \
		cur_AC.Zo, AC.boom_len)

	AC.tail.boom_Type = 'C'

	outer_radius = 0.015
	inner_radius = outer_radius*0.75
	AC.tail.boom_Dim = [outer_radius, inner_radius]

	AC.tail.boom_E = 68.9e9
	



	AC.score = 0

updateAircraft(AC)


print('=============== Initial vehicle Parameters =============')
# print('Weight (lbs)', AC.weight)
print('CDp', AC.CD_p)
print('Tailboom Length', AC.boom_len)
print('Iyy', AC.Iyy)
print('Mission', AC.mission)
# print('CG (x,y,z)', AC.CG)


print('=============== Initial wing Parameters =============')
print('AC.wing.num_Sections: ', AC.wing.num_sections)
print('AC.wing.is_linear: ', AC.wing.is_linear)
print('AC.wing.b_wing: ', AC.wing.b_wing)
print('AC.wing.sweep: ', AC.wing.sweep)
print('AC.wing.Sref', AC.wing.sref)
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
print('AC.wing.Ainc: ', AC.wing.ainc)
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
print('AC.tail.num_Sections: ', AC.tail.num_sections)
print('AC.tail.is_linear: ', AC.tail.is_linear)
print('AC.tail.b_htail: ', AC.tail.b_htail)
print('AC.tail.Sref', AC.tail.sref)
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