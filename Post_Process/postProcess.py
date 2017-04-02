import numpy
import math
from lib_plot import plot_geo_final

def postProcess(opt_problem):
    """
    Not currently used
    - Is an example of an all-in-one post-processing script

    """   
	# Remove possibility for surpressing output with ellipsis
	numpy.set_printoptions(threshold='nan')

	# Declare input variables
	input_vars = ['weight.b_wing', 'weight.C_r', 'weight.t2', 'weight.t3',\
		 'weight.t4', 'weight.t5', 'weight.b_htail', 'weight.C_r_t', \
		 'weight.dist_LG', 'weight.boom_len','obj.camber','obj.max_camb_pos',\
		 'obj.thickness','obj.max_thick_pos' ]

	# Declare output variables
	output_vars = [ 'weight.mass', 'weight.Iyy', 'weight.Sref_wing', \
		 'weight.Sref_tail', 'weight.MAC', 'weight.x_cg', 'weight.Xle',\
		 'weight.Yle', 'weight.C', 'weight.Xle_t', 'weight.Yle_t', \
		 'weight.C_t', 'obj.NP','obj.SM', 'obj.score']

	filename = 'converged.dat'
	
	# Open Output File
	output_file = open(filename, 'w')
	
	# Write Header
	line_header = 'Case: \n'
	output_file.write(line_header)

	# Write Input Variables
	output_file.write('inputs: \n')

	# Write Remaining Input Variables
	for i in range(len(input_vars)):
		value = opt_problem[input_vars[i]]
		output_string = input_vars[i] + ': ' + str(value) + '\n'
		output_file.write(output_string)

	# Write Output Variables
	output_file.write('outputs: \n')
	for i in range(len(output_vars)):
		value = opt_problem[output_vars[i]]
		output_string = output_vars[i] + ': ' + str(value) + '\n'
		output_file.write(output_string)

	# Close file
	output_file.close()


	
	result_score = -1*opt_problem['obj.score']
	result_Sref = opt_problem['weight.Sref_wing']

	C = [opt_problem['weight.C_r'], opt_problem['weight.C_r']*opt_problem['weight.t2'],\
	 opt_problem['weight.C_r']*opt_problem['weight.t2']*opt_problem['weight.t3'],\
	  opt_problem['weight.C_r']*opt_problem['weight.t2']*opt_problem['weight.t3']*opt_problem['weight.t4'],\
	    opt_problem['weight.C_r']*opt_problem['weight.t2']*opt_problem['weight.t3']*opt_problem['weight.t4']*opt_problem['weight.t5']]

	b_wing = opt_problem['weight.b_wing']

	boom_len = opt_problem['weight.boom_len']
	dist_LG = opt_problem['weight.dist_LG']

	Yle =  [0, 1*b_wing/8,  b_wing/4, 3*b_wing/8, b_wing/2]
	Sref = b_wing/8*(C[0] + 2*C[1] + 2*C[2] + 2*C[3] + C[4])

	Xle =  [0]
	for i in range(0, len(C)-1):
		Xle.append((C[i] - C[i +1])/4 + Xle[i])


	Xle_t =[boom_len + C[0]/4.0, boom_len + C[0]/4.0]
	Yle_t = [0, opt_problem['weight.b_htail']/2.0]
	C_t = [opt_problem['weight.C_r_t'] , opt_problem['weight.C_r_t']]


	x_cg = opt_problem['weight.x_cg']
	NP =  opt_problem['obj.NP']

	plot_geo_final(Xle, Yle, C, Xle_t, Yle_t, C_t, x_cg, NP, result_score)

	plt.savefig('OPT_#.pdf', bbox_inches='tight')