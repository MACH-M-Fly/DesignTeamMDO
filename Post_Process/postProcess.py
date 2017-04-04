import numpy
import math
from lib_plot import *
# from lib_plot import plot_geo_final

# def postProcess(opt_problem):
#     # """
#     # Not currently used
#     # - Is an example of an all-in-one post-processing script

#     # """   
# 	# Remove possibility for surpressing output with ellipsis
# 	numpy.set_printoptions(threshold='nan')

# 	# Declare input variables
# 	input_vars = ['weight.b_wing', 'weight.C_r', 'weight.t2', 'weight.t3',\
# 		 'weight.t4', 'weight.t5', 'weight.b_htail', 'weight.C_r_t', \
# 		 'weight.dist_LG', 'weight.boom_len','obj.camber','obj.max_camb_pos',\
# 		 'obj.thickness','obj.max_thick_pos' ]

# 	# Declare output variables
# 	output_vars = [ 'weight.mass', 'weight.Iyy', 'weight.Sref_wing', \
# 		 'weight.Sref_tail', 'weight.MAC', 'weight.x_cg', 'weight.Xle',\
# 		 'weight.Yle', 'weight.C', 'weight.Xle_t', 'weight.Yle_t', \
# 		 'weight.C_t', 'obj.NP','obj.SM', 'obj.score']

# 	filename = 'converged.dat'
	
# 	# Open Output File
# 	output_file = open(filename, 'w')
	
# 	# Write Header
# 	line_header = 'Case: \n'
# 	output_file.write(line_header)

# 	# Write Input Variables
# 	output_file.write('inputs: \n')

# 	# Write Remaining Input Variables
# 	for i in range(len(input_vars)):
# 		value = opt_problem[input_vars[i]]
# 		output_string = input_vars[i] + ': ' + str(value) + '\n'
# 		output_file.write(output_string)

# 	# Write Output Variables
# 	output_file.write('outputs: \n')
# 	for i in range(len(output_vars)):
# 		value = opt_problem[output_vars[i]]
# 		output_string = output_vars[i] + ': ' + str(value) + '\n'
# 		output_file.write(output_string)

# 	# Close file
# 	output_file.close()


	
# 	result_score = -1*opt_problem['obj.score']
# 	result_Sref = opt_problem['weight.Sref_wing']

# 	C = [opt_problem['weight.C_r'], opt_problem['weight.C_r']*opt_problem['weight.t2'],\
# 	 opt_problem['weight.C_r']*opt_problem['weight.t2']*opt_problem['weight.t3'],\
# 	  opt_problem['weight.C_r']*opt_problem['weight.t2']*opt_problem['weight.t3']*opt_problem['weight.t4'],\
# 	    opt_problem['weight.C_r']*opt_problem['weight.t2']*opt_problem['weight.t3']*opt_problem['weight.t4']*opt_problem['weight.t5']]

# 	b_wing = opt_problem['weight.b_wing']

# 	boom_len = opt_problem['weight.boom_len']
# 	dist_LG = opt_problem['weight.dist_LG']

# 	Yle =  [0, 1*b_wing/8,  b_wing/4, 3*b_wing/8, b_wing/2]
# 	Sref = b_wing/8*(C[0] + 2*C[1] + 2*C[2] + 2*C[3] + C[4])

# 	Xle =  [0]
# 	for i in range(0, len(C)-1):
# 		Xle.append((C[i] - C[i +1])/4 + Xle[i])


# 	Xle_t =[boom_len + C[0]/4.0, boom_len + C[0]/4.0]
# 	Yle_t = [0, opt_problem['weight.b_htail']/2.0]
# 	C_t = [opt_problem['weight.C_r_t'] , opt_problem['weight.C_r_t']]


# 	x_cg = opt_problem['weight.x_cg']
# 	NP =  opt_problem['obj.NP']

# 	plot_geo_final(Xle, Yle, C, Xle_t, Yle_t, C_t, x_cg, NP, result_score)

# 	plt.savefig('OPT_#.pdf', bbox_inches='tight')

def printParameters(AC, param_str):
	if param_str == 'Initial':
		print('\n================  Initial Results ===================')
	else:
		print('\n================  Final Results ===================')

	print("Total Build Hours: 		%f" % AC.total_hours)
	print("Wingspan: 				%f" % AC.wing.b_wing)
	print("Boom Length: 			%f" % AC.boom_len)
	print("Chord Values:			" + ', '.join("%f" % n for n in AC.wing.chord_vals))
	print("Chord Cubic Terms:		" + ', '.join("%f" % n for n in AC.wing.chord))
	print("Sweep Values:			" + ', '.join("%f" % n for n in AC.wing.sweep_vals))
	print("Sweep Cubic Terms:		" + ', '.join("%f" % n for n in AC.wing.sweep))
	print("Horiz. Tail Span:	 	%f" % AC.tail.b_htail)
	print("HT Chord Values:		" + ', '.join("%f" % n for n in AC.tail.htail_chord_vals))
	print("HT Chord Cubic Terms:	" + ', '.join("%f" % n for n in AC.tail.htail_chord))
	
	print('\n########    Performance Metrics  #######')
	print("Number of Laps:	%d" % AC.N)
	print("Score:			%f" % AC.score)
	print("Total Time:		%f" % AC.tot_time)

	print('\n########     Weight Breakdown    #######')
	print('Aircraft Mass:	%f kg' % AC.mass)
	print('Wing Mass:		%f kg' % AC.mass_wing)
	print('Tail Mass:		%f kg' % AC.mass_tail)

	print('\n########  Aerodynamics Analysis  #######')
	print("CL: %f" % AC.CL(AC.ang))
	print("CD: %f" % AC.CD(AC.ang))
	print("CM: %f" % AC.CM(AC.ang))
	print("NP: %f" % AC.NP)
	print("SM: %f" % AC.SM)

	print('\n########   Structural Analysis   #######')
	print('Gross Lift:				%f N (%f kg)' % (AC.gross_F, AC.gross_F/9.81))
	print("Wing Max Stress:		%.3f MPa" % (AC.sig_max/1.E6))
	print("Wing Max Deflection:	%.3f mm" % (AC.y_max*1.E3))
	print("Tail Max Stress:		%.3f MPa" % (AC.sig_max_tail/1.E6))
	print("Tail Max Deflection:	%.3f mm" % (AC.y_max_tail*1.E3))
	print("CG:						" + ', '.join("%f" % n for n in AC.CG))

	print("\n#####\n")

def postProcess_Main(in_ac, out_ac):
	# Print starting parameters
	# printParameters(in_ac, 'Initial')

	# Print final parameters
	printParameters(out_ac, 'Final')

	# Output final geometry of aircraft
	plotGeoFinalDuo(in_ac, out_ac)