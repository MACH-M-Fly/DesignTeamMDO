import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import os

def genMass(AC):
	"""
	gen_mass: Generates AVL mass file
	
	Inputs:
		AC: Aircraft with all current attributes
	Outputs:
		None, just "outs" the mass file
	"""

	try:
		os.remove('./Aerodynamics/aircraft.mass')
	except:
		pass

	f = open('./Aerodynamics/aircraft.mass', 'w')


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

	f.close()

def genGeo(AC):
	"""
	genGeo: Generates AVL geometry file

	Inputs:
		AC: Airctaft with attributes: Sref, MAC, b_wing, cg, CDp, Xle, ...
		Yle, C, Xle_t, Yle_t, C_t

	Outputs:
		None, just "outs" the AVL geometry file
	"""

	# Assign genGeo needs from the aircraft attribute
	Sref = AC.wing.sref
	MAC = AC.wing.MAC
	b_wing = AC.wing.b_wing
	cg = AC.wing.CG
	CDp = 0.0
	Xle = AC.wing.Xle
	Yle = AC.wing.Yle
	C = AC.wing.chord_vals
	Xle_ht = AC.tail.Xle_ht
	Yle_ht = AC.tail.Yle_ht
	Xle_vt = AC.tail.Xle_vt
	Zle_vt = AC.tail.Zle_vt
	C_ht = AC.tail.htail_chord_vals
	C_vt = AC.tail.vtail_chord_vals

	# print("Chords", C)
	incAng = np.zeros((1, AC.wing.num_sections))[0]

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
		out('Aerodynamics/airfoils/A_'+str(i+1) + '.dat')
		# out('airfoils/E420.dat')
		out('')


	# Horizontal surface data
	out('')
	out('#======================================================')
	out('#------------------- Horizontal Tail ------------------')
	out('#======================================================')
	out('SURFACE')
	out('Horizontal Tail')
	out('#Nchordwise  Cspace   Nspan   Sspace')
	out('10       1.0           20         2 ')
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
	inds = [0, len(C_ht) - 1]
	# for i in range(0, len(C_ht)):
	for i in inds:
		out('SECTION')
		out('#Xle  Yle  Zle  |  Chord   Ainc   Nspan   Sspace')
		out(str(Xle_ht[i]) + '    ' + str(Yle_ht[i]) + '    0       '+ str(C_ht[i]) + '     '+ str(0.0) +'      '+ ' ')
		out('NACA')
		out('0012')
		out('CLAF')
		out('1.1078')
		out('')
		if ( (i == 0) | (i == (len(C_ht) - 1)) ):
			out('CONTROL')
			out('#surface gain xhinge hvec SgnDup')
			out('Elevator -1.00 0.5 0 1 0 1.00')
			out('')

	# out('#------------------TAIL ROOT/ELEVATOR------------------')
	# out('SECTION')
	# out('#Xle   Yle     Zle     Chord   Ainc')
	# out(str(Xle_ht[0]) + '  ' +  str(Yle_ht[0]) + '   0.0  '+ str(C_t[0]) +'  0.000')
	# out('NACA')
	# out('0012')
	# out('CLAF')
	# out('1.1078')
	# out('')
	# out('CONTROL')
	# out('#surface gain xhinge hvec SgnDup')
	# out('Elevator -1.00 0.5 0 1 0 1.00')
	# out('')
	# out('#--------------------TAIL Tip--------------------------')
	# out('SECTION')
	# out('#Xle   Yle     Zle     Chord   Ainc')
	# out(str(Xle_ht[1]) + '  ' +  str(Yle_ht[1]) + ' 0.000   '+ str(C_t[1]) +'  0.000')
	# out('NACA')
	# out('0012')
	# out('CLAF')
	# out('1.1078')
	# out('')
	# out('CONTROL')
	# out('#surface gain xhinge hvec SgnDup')
	# out('Elevator -1.00 0.5 0 1 0 1.00')
	# out('')
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
	# for i in range(0, len(C_vt)):
	inds = [0, len(C_vt) - 1]
	for i in inds:
		out('SECTION')
		out('#Xle  Yle  Zle  |  Chord   Ainc   Nspan   Sspace')
		out(str(Xle_vt[i]) + ' 0 ' + str(Zle_vt[i]) +  '  '+ str(C_vt[i]) + '     '+ str(0.0) +'      '+ ' ')
		out('NACA')
		out('0012')
		out('CLAF')
		out('1.1078')
		out('')
		if ( (i == 0) | (i == (len(C_vt) - 1)) ):
			out('CONTROL')
			out('#surface gain xhinge hvec SgnDup')
			out('Rudder 1.00 0.5 0 0 1 -1.00')
			out('')

	# out('SECTION')
	# out('#Xle   Yle     Zle     Chord   Ainc')
	# out(str(Xle_vt[0]) + ' 0.0   0 ' +str(C_vt[0]) + '   0.000')
	# out('NACA')
	# out('0012')
	# out('CLAF')
	# out('1.1078')
	# out('')
	# out('CONTROL')
	# out('#surface gain xhinge hvec SgnDup')
	# out('Rudder 1.00 0.5 0 0 1 -1.00')
	# out('')
	# out('#-----------------------TIP/RUDDER---------------------')
	# out('SECTION')
	# out('#Xle   Yle     Zle     Chord   Ainc')
	# out(str(Xle_vt[0]) + ' 0.0   0.2  ' +str(C_vt[0]) + '   0.000')
	# out('NACA')
	# out('0012')
	# out('CLAF')
	# out('1.1078')
	# out('CONTROL')
	# out('#surface gain xhinge hvec SgnDup')
	# out('Rudder 1.00 0.5 0 0 1 -1.00')
	# out('#------------------------------------------------------')
	out('\n\n')
	out('# -- END OF FILE --')

	f.close()
	# close file


	# plt.draw()
	# plt.pause(1)


# -- END OF FILE --			