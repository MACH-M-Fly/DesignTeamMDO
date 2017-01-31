'''
 Aero.py
 - Obtain aerodynamic parameters for aircraft (cl, cd, L/D, etc.)
 - Run AVL for whole vehicle
 - Modify airfoils in AVL

Inputs:
- Aircraft_Class
 
Outputs:
- Aero data (CL, CD, neutral point)
- Loads data

'''

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





class exampleComponent(Component):
	"""
		exampleComponent: Uses the current iteration of the aircraft, performances
		"input analysis name" analysis
		Inputs:
			- Aircraft_Class: Input aircraft instance
			- Design variables: These will be modified based on new MDO iteration
		Outputs:
			- Aircraft_Class: Output and modified aircraft instance 
	"""

	def __init__(self ):
		super(createAC,self).__init__()

		# Input instance of aircraft - before modification
		self.add_param('def_aircraft',val=AC, desc='Input Aircraft Class')

		# Output instance of aircaft - after modification

		# # set up outputs
		self.add_param('out_aircraft',val=AC, desc='Output Aircraft Class')

		self.add_output('SM', val = 0.0, desc = 'static margin')
		self.add_output('NP', val = 0.0, desc = 'Netual point')
		self.add_output('tot_time', val = 0.0, desc = 'time')

	def solve_nonlinear(self,params,unknowns,resids):
		# Used passed in instance of aircraft
		AC = params['def_aircraft']
	
		# Modify instance of aircraft - This is where analysis would happen
		AC.wing.b_wing = params['b_wing']

		# Set output to updated instance of aircraft
		unknowns['lift_coefficient'] = 2*AC.wing.b_wing


		print('\n')
		print('============== output =================')
		print('N: ' + str(unknowns['N']))	
		print('SM: ' + str(unknowns['SM']))
		print('Score: ' + str( unknowns['score']))
		print('\n')


def get_aeroCoef(geo_filename = 'aircraft.txt', mass_filename = 'aircraft.mass'):
		'''
        Summary:

       
        Inputs
        ----------
        geo_filename : String
            File name of the AVL geometry file for the aircraft

        mass_filename : String
            File name of the AVL geometry file for the aircraft

        Outputs
        ----------
        CL,CD, CD : Functions
            Functions that will return the value for the coeffiecent 
            for a given angle of attack 
            example: CL(10*np.pi/180)  <- note the use of radians

        NP : float
           X location of NP in AVL coordinate system

    
        # Examples
        # --------
        # >>> # Take unique square in x-z plane and and 10 along z-direction (spanWise)
        # >>> # and the along x-direction (chordWise)
        # >>> leList = [[0, 0, 0], [0, 0, 1]]
        # >>> teList = [[1, 0, 0], [0, 0, 1]]
        # >>> DVCon.addThicknessConstraints2D(leList, teList, 10, 3, 
        #                         lower=1.0, scaled=True)
        # '''


	avl_run(filename, 0, 12 )
	
	alphas, CLs, CDs, CMs = getData_AVL(filename +'_data.dat')[0:4]
	NP = getNP_AVL('stab.txt')


	alphas = [x * np.pi/180 for x in alphas]
	
	# get func for aero coeificent
	CL = np.poly1d(np.polyfit(alphas,CLs, 1))
	CD = np.poly1d(np.polyfit(alphas,CDs, 2))
	CM = np.poly1d(np.polyfit(alphas,CMs, 2))


	# ----------------- Plot Outputs --------------------------
	# plt.figure(3)
	# plt.subplot(311)
	# plt.ylabel('CL')
	# plt.xlabel('Alpha')
	# plt.plot(alphas, CLs, 'b')

	# plt.subplot(312)
	# plt.ylabel('CD')
	# plt.xlabel('Alpha')
	# plt.plot(alphas, CDs, 'b')


	# plt.subplot(313)
	# plt.ylabel('CM')
	# plt.xlabel('Alpha')
	# plt.plot(alphas, CMs, 'b')

	# convert to radians

	
	return (CL, CD, CM, NP)


