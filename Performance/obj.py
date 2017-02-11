# LAP TIME
from __future__ import division

from openmdao.api import IndepVarComp, Component, Problem, Group
from openmdao.api import ScipyOptimizer, ExecComp, SqliteRecorder
from openmdao.drivers.pyoptsparse_driver import pyOptSparseDriver
from openmdao.drivers.latinhypercube_driver import OptimizedLatinHypercubeDriver

from scipy.optimize import *
from sympy import Symbol, nsolve
import numpy as np
import matplotlib.pyplot as plt

from time import localtime, strftime, time


from xfoil.xfoil_lib import xfoil_alt, getData_xfoil
from lib_aero import get_aeroCoef, num_laps




class obj(Component):
	'''calculate score'''
	# set up interface to the framework
	def __init__(self ):
		super(obj,self).__init__()

		# self.add_param('b_wing',val=3.33,desc='Wing Span [m]')
		# self.add_param('Sref_wing',val=6.0,desc='Wing Area [m^2]')
		# self.add_param('Sref_tail',val=6.0,desc='Wing Area [m^2]')

		# self.add_param('Iyy',val=0.4,desc='Mass Momment of inertia [Kg*m^2]')

		# self.add_param('mass',val=0.4,desc='mass [kg]')
		# self.add_param('MAC',val=0.4,desc='Mean Aerodynamic Chord [m]')
		# self.add_param('x_cg',val=0.4,desc='x center of gravity')

		# self.add_param('dist_LG', val=0.15,desc='offset of lading gear location')
		# self.add_param('boom_len', val=0.6,desc='tail boom length [m]')	
			
		# self.add_param('camber', val=np.zeros(5))	
		# self.add_param('thickness', val=np.zeros(5))	
		# self.add_param('max_camb_pos', val=np.zeros(5))	
		# self.add_param('max_thick_pos', val=np.zeros(5))	


		# # # set up outputs

		# self.add_output('score', val= 0.0,desc='score ')
		# self.add_output('N', val = 0.0, desc = 'number of laps')
		# self.add_output('SM', val = 0.0, desc = 'static margin')
		# self.add_output('NP', val = 0.0, desc = 'Netual point')
		# self.add_output('tot_time', val = 0.0, desc = 'time')

	def solve_nonlinear(self,params,unknowns,resids):
		# make all input variables local for ease
		# C = [params['C1'], params['C2'], params['C3'], params['C4'], params['C5']]
		# b_wing = params['b_wing']
		# Sref_wing = params['Sref_wing']
		# Sref_tail = params['Sref_tail']
		# Iyy = params['Iyy']
		# dist_LG = params['dist_LG']
		# boom_len = params['boom_len']
		# mass = params['mass']
		# weight = mass*9.81
		# MAC = params['MAC']
		# x_cg = params['x_cg']
		# camber = params['camber']
		# thickness = params['thickness']
		# max_camb_pos = params['max_camb_pos']
		# max_thick_pos = params['max_thick_pos']
		# print(params['mass'])


				# print(CL(13*np.pi/180.0))

		print('camber: '+ str(camber))
		print('max camber pos: '+ str(max_camb_pos))
		print('thickness: '+ str(thickness))
		print('max thickness pos: '+ str(max_thick_pos))


		N,tot_time = num_laps(AC.CL, AC.CD, AC.CM, AC.wing.Sref_wing, AC.tail.Sref_tail, weight, boom_len, dist_LG, MAC, Iyy)

		unknowns['score'] = -1*(N*10- tot_time/100.0)



		unknowns['N'] = N
		unknowns['tot_time'] = tot_time
		unknowns['NP'] = NP
		unknowns['SM'] = SM





		print('\n')
		print('============== output =================')
		print('N: ' + str(unknowns['N']))	
		print('SM: ' + str(unknowns['SM']))
		print('Score: ' + str( unknowns['score']))
		print('\n')

			# print('==============================================')
