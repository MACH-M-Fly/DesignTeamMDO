
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




class AeroAnalysis(Component):
	'''calculate score'''
	# set up interface to the framework
	def __init__(self ):
		super(obj,self).__init__()

		self.add_param('aircraft',val=aircraft(),desc='Wing Span [m]')


		# # set up outputs

		self.add_output('score', val= 0.0,desc='score ')
		self.add_output('N', val = 0.0, desc = 'number of laps')
		self.add_output('SM', val = 0.0, desc = 'static margin')
		self.add_output('NP', val = 0.0, desc = 'Netual point')
		self.add_output('tot_time', val = 0.0, desc = 'time')

	def solve_nonlinear(self,params,unknowns,resids):
		# make all input variables local for ease
		# C = [params['C1'], params['C2'], params['C3'], params['C4'], params['C5']]
		b_wing = params['b_wing']
		Sref_wing = params['Sref_wing']
		Sref_tail = params['Sref_tail']

		# print(params['mass'])




		# unknowns['SM'] = 0.0
		unknowns['N'] = 0
		unknowns['score'] = 0.0
		unknowns['tot_time'] = 300
		unknowns['NP'] = MAC/4.0




		print('\n')
		print('============== output =================')
		print('N: ' + str(unknowns['N']))	
		print('SM: ' + str(unknowns['SM']))
		print('Score: ' + str( unknowns['score']))
		print('\n')

			# print('==============================================')
