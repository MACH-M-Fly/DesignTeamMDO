
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



from Input_Files.Input import AC


class createAC(Component):
	'''calculate score'''
	# set up interface to the framework
	def __init__(self ):
		super(createAC,self).__init__()

		self.add_param('def_aircraft',val=AC, desc='Aircraft Class')
		self.add_param('span',val=0.0, desc='wing span')


		# # set up outputs

		self.add_output('aircraft', val=AC,desc='score ')
		# self.add_output('N', val = 0.0, desc = 'number of laps')
		# self.add_output('SM', val = 0.0, desc = 'static margin')
		# self.add_output('NP', val = 0.0, desc = 'Netual point')
		# self.add_output('tot_time', val = 0.0, desc = 'time')

	def solve_nonlinear(self,params,unknowns,resids):
		# make all input variables local for ease
		# C = [params['C1'], params['C2'], params['C3'], params['C4'], params['C5']]
		AC = params['def_aircraft']
	
		# print AC.

		# print(params['mass'])
		AC.wing.b_wing = params['span']


		unknowns['aircraft'] = AC

		# # unknowns['SM'] = 0.0
		# unknowns['N'] = 0
		# unknowns['score'] = 0.0
		# unknowns['tot_time'] = 300
		# unknowns['NP'] = MAC/4.0




		# print('\n')
		# print('============== output =================')
		# print('N: ' + str(unknowns['N']))	
		# print('SM: ' + str(unknowns['SM']))
		# print('Score: ' + str( unknowns['score']))
		# print('\n')

			# print('==============================================')


