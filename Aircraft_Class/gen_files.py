import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import os

def gen_mass(AC, filename = 'aircraft.mass'):
	"""
	gen_mass: Generates AVL mass file
	Inputs:
		AC: Aircraft with attributes, m_total, cg, I
	Outputs:
		None, just "outs" the mass file
	"""
	try:
		os.remove('./aircraft.mass')
	except:
		pass

	f = open('./aircraft.mass', 'w')


	def out(cmd):
		f.write(cmd + '\n')

	out('Lunit = 1.0 m')
	out('Tunit = 1.0 s')
	out('Munit = 1 kg')
	out('g   = 9.81')
	out('rho = 1.225')
	out('#-------------------------')

	out('# Mass Xcg Ycg Zcg     Ixx Iyy Izz Ixy Ixz Iyz Component')
	out('# (kg) (m) (m) (m)     (kg-m^2) (kg-m^2) (kg-m^2) (kg-m^2) (kg-m^2) (kg-m^2)')
	out('*   1.    1.    1.    1.    1.     1.    1.    1.    1.    1.')
	out('+   0.    0.    0.    0.    0.     0.    0.    0.    0.    0.') 
	out( str(AC.mass) + ' ' + str(AC.CG[0]) + ' ' + str(AC.CG[1]) + ' ' + str(AC.CG[2]) + ' ' + str(AC.I[0]) + ' ' + str(AC.I[1])  + ' ' + str(AC.I[2]) + ' ' + str(AC.I[3]) + ' ' + str(AC.I[4]) + ' ' + str(AC.I[5]) +	' !	Aircraft')

def gen_geo(AC):
	"""
	gen_geo: Generates AVL geometry file

	Inputs:
		AC: Airctaft with attributes: Sref, MAC, b_wing, cg, CDp, Xle, ...
		Yle, C, Xle_t, Yle_t, C_t

	Outputs:
		None, just "outs" the AVL geometry file
	"""

	# Assign gen_geo needs from the aircraft attribute
	Sref = AC.wing.Sref
	MAC = AC.wing.MAC
	b_wing = AC.wing.b_wing
	cg = AC.wing.CG
	CDp = 0.0
	Xle = AC.wing.Xle
	Yle = AC.wing.Yle
	C = AC.wing.chord_vals
	Xle_t = AC.tail.Xle_ht
	Yle_t = AC.tail.Yle_ht
	C_t = AC.tail.htail_chord_vals

	print("Chords", C)
	incAng = [0,   0,    0,  0,   0  ]

	try:
		os.remove('./Aerodynamics/aircraft.txt')
	except:
		pass

	f = open('./Aerodynamics/aircraft.txt', 'w')


	def out(cmd):
		f.write(cmd + '\n')

	out('MACH MDAO AVL\n')
		
	out('#======================================================')
	out('#------------------- Geometry File --------------------')
	out('#======================================================')
	out('# AVL Conventions')
	out('# SI Used: m, kg, etc\n')

	out('#Mach')
	out('0.0')
	out('#IYsym   IZsym   Zsym')
	out(' 0       0       0')
	out('#Sref    Cref    b_wing')
	out(str(Sref) + '  ' + str(MAC) + '  '+ str(b_wing)) 
	out('#Xref    Yref    Zref')
	out(str(cg[0]) + ' '+ str(cg[1]) + ' '+ str(cg[2])) 
	out('# CDp')
	out(str(CDp) + '\n')

	out('#======================================================')
	out('#--------------------- Main Wing ----------------------')
	out('#======================================================')
	out('SURFACE')
	out('Wing')
	out('#Nchordwise  Cspace   [Nspan   Sspace]')
	out('     7        1.0      20      -2.0')
	out('YDUPLICATE')
	out('0.0')
	out('SCALE')
	out('1.0  1.0  1.0')
	out('TRANSLATE')
	out('0.0  0.0  0.0')
	out('ANGLE')
	out('0.0')
	out('#------------------------------------------------------\n')

	for i in range(0, len(C)):
		out('SECTION')
		out('#Xle  Yle  Zle  |  Chord   Ainc   Nspan   Sspace')
		out(str(Xle[i]) + '    ' + str(Yle[i]) + '    0       '+ str(C[i]) + '     '+ str(incAng[i])+'      '+ '5      3')
		out('AFILE')
		out('airfoils/A_'+str(i+1) + '.dat')



	# Horizontal surface data
	out('')
	out('#======================================================')
	out('#------------------- Horizontal Tail ------------------')
	out('#======================================================')
	out('SURFACE')
	out('Horizontal Tail')
	out('#Nchordwise  Cspace   Nspan   Sspace')
	out('7       1.0           10        -2 ')
	out('YDUPLICATE')
	out('0.0')
	out('SCALE')
	out('1.0  1.0  1.0')
	out('TRANSLATE')
	out('0.0  0.0  0.0')
	out('ANGLE')
	out('0')	
	out('')
	out('#------------------TAIL ROOT/ELEVATOR------------------')
	out('SECTION')
	out('#Xle   Yle     Zle     Chord   Ainc')
	out(str(Xle_t[0]) + '  ' +  str(Yle_t[0]) + '   0.0  '+ str(C_t[0]) +'  0.000')
	out('NACA')
	out('0012')
	out('CLAF')
	out('1.1078')
	out('')
	out('CONTROL')
	out('#surface gain xhinge hvec SgnDup')
	out('Elevator -1.00 0.5 0 1 0 1.00')
	out('')
	out('#--------------------TAIL Tip--------------------------')
	out('SECTION')
	out('#Xle   Yle     Zle     Chord   Ainc')
	out(str(Xle_t[1]) + '  ' +  str(Yle_t[1]) + ' 0.000   '+ str(C_t[1]) +'  0.000')
	out('NACA')
	out('0012')
	out('CLAF')
	out('1.1078')
	out('')
	out('CONTROL')
	out('#surface gain xhinge hvec SgnDup')
	out('Elevator -1.00 0.5 0 1 0 1.00')
	out('')
	out('#======================================================')
	out('#------------------- Vertical Tail --------------------')
	out('#======================================================')
	out('SURFACE')
	out('Vertical Tail')
	out('# Nchordwise Cspace Nspanwise Sspace')
	out('10 1.00 10 -2.0')
	out('# YDUPLICATE')
	out('# 0.0')
	out('#Xscale Yscale Zscale')
	out('SCALE')
	out('1.0 1.0 1.0')
	out('')
	out('ANGLE')
	out('0.0')
	out('TRANSLATE')
	out('0.0 0.0 0.0')
	out('')
	out('INDEX')
	out('2')
	out('')
	out('#----------------------ROOT/RUDDER---------------------')
	out('SECTION')
	out('#Xle   Yle     Zle     Chord   Ainc')
	out(str(Xle_t[0]) + ' 0.0   0 ' +str(C_t[0]) + '   0.000')
	out('NACA')
	out('0012')
	out('CLAF')
	out('1.1078')
	out('')
	out('CONTROL')
	out('#surface gain xhinge hvec SgnDup')
	out('Rudder 1.00 0.5 0 0 1 -1.00')
	out('')
	out('#-----------------------TIP/RUDDER---------------------')
	out('SECTION')
	out('#Xle   Yle     Zle     Chord   Ainc')
	out(str(Xle_t[0]) + ' 0.0   0.2  ' +str(C_t[0]) + '   0.000')
	out('NACA')
	out('0012')
	out('CLAF')
	out('1.1078')
	out('CONTROL')
	out('#surface gain xhinge hvec SgnDup')
	out('Rudder 1.00 0.5 0 0 1 -1.00')
	out('#------------------------------------------------------')
	out('\n\n')
	out('# -- END OF FILE --')

	f.close()
	# close file


	# plt.draw()
	# plt.pause(1)


# -- END OF FILE --			