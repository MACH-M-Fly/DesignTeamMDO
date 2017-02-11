'''
# ObjPerformance.py
# - Evaluate aircraft performance based on objective
# Obj 1) M-Fly: Maximum payload, limited runway
# Obj 2) MACH: Minimum lap time, given lap perimiter

Inputs:
- Aircraft_Class
- Data from Aero(CL, CD, neutral point)

Outputs:
- Objective Function (1: Payload or 2: lap time)
- Takeoff distance (constraint)
- Climb rate (constraint)

'''

from runwaysim.lib_runwaysim_small import runway_sim_small


from openmdao.api import IndepVarComp, Component, Problem, Group
from openmdao.api import ScipyOptimizer, ExecComp, SqliteRecorder
from openmdao.drivers.pyoptsparse_driver import pyOptSparseDriver
from openmdao.drivers.latinhypercube_driver import OptimizedLatinHypercubeDriver

from scipy.optimize import *
from sympy import Symbol, nsolve
import numpy as np
import matplotlib.pyplot as plt

from time import localtime, strftime, time
from AVL.avl_lib import *
from xfoil.xfoil_lib import xfoil_alt, getData_xfoil
from lib_aero import get_aeroCoef, num_laps

from test_class import Surface




# Mission select (1 for M-Fly max payload)
Mission = 1



class obj(Component):
	'''calculate score'''
	# set up interface to the framework
	def __init__(self ):
		super(createAC,self).__init__()

		# Input instance of aircraft - before modification
		self.add_param('def_aircraft',val=AC, desc='Aircraft Class')

		# Output instance of aircaft - after modification
		self.add_output('output_data', val=0.0,desc='Example of Output Data')


		# Set up outputs
		self.add_output('score', val= 0.0,desc='score ')
		self.add_output('N', val = 0.0, desc = 'number of laps')
		self.add_output('SM', val = 0.0, desc = 'static margin')
		self.add_output('NP', val = 0.0, desc = 'Netual point')
		self.add_output('tot_time', val = 0.0, desc = 'time')

	def solve_nonlinear(self,params,unknowns,resids):
		# Used passed in instance of aircraft
		AC = params['def_aircraft']
	
		# Modify instance of aircraft - This is where analysis would happen
		AC.wing.b_wing = params['b_wing']


		print('camber: '+ str(camber))
		print('max camber pos: '+ str(max_camb_pos))
		print('thickness: '+ str(thickness))
		print('max thickness pos: '+ str(max_thick_pos))

		not_stall = 1

		for i in range(0, len(camber)):
			name = 'A_' + str(i+1) 


			# print(name)
			xfoil_alt(name, camber[i], max_camb_pos[i], thickness[i], max_thick_pos[i] , 400000, 13)
			# print('yes')
			try:		# print('\n')
				Cl = getData_xfoil(name +'_data.dat')[1]
	
			except:
				Cl =[]
			


			if (not Cl):
				not_stall = 0
				print(name + ' Stalled')
				break


		if not_stall:

			try:
				CL, CD, CM, NP = get_aeroCoef(filename = 'aircraft')
				# print(CL(13*np.pi/180.0))

				SM = (NP-x_cg)/MAC

				if (SM >= 0.12 and SM <= 0.20):
					N,tot_time = num_laps(CL, CD, CM, Sref_wing, Sref_tail, weight, boom_len, dist_LG, MAC, Iyy)

					unknowns['score'] = -1*(N*10- tot_time/100.0)

				else:
					print('BAD SM: ' + str(SM))
					N = 0
					tot_time= 0.0
					unknowns['score'] = abs(0.16 - SM)


				unknowns['N'] = N
				unknowns['tot_time'] = tot_time
				unknowns['NP'] = NP
				unknowns['SM'] = SM
				
			except: #Exception, e:

				# raise
				# print('-------------------AVL FAILED-------------------')

				# unknowns['SM'] = 0.0
				unknowns['N'] = 0
				unknowns['score'] = 0.0
				unknowns['tot_time'] = 0.0
				unknowns['NP'] = MAC/4.0


		else:

			# unknowns['SM'] = 0.0
			unknowns['N'] = 0
			unknowns['score'] = 0.0
			unknowns['tot_time'] = 300
			unknowns['NP'] = MAC/4.0


		# print('Score: ' + str(unknowns['score']))
		# print('Score: ' + str(unknowns['score']) +' N: ' + str(unknowns['N']) +' Total Time: '+ str(unknowns['tot_time']))
		# print('\n')


		print('\n')
		print('============== output =================')
		print('N: ' + str(unknowns['N']))	
		print('SM: ' + str(unknowns['SM']))
		print('Score: ' + str( unknowns['score']))
		print('\n')

		params['test_class'].out()

			# print('==============================================')

