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

import pyAVL
from Input_Files.Input import AC


class aeroAnalysis(Component):
	"""
		aeroAnalysis: Uses the current iteration of the aircraft, performs
		AVL aerodynamic analysis
		Inputs:
			- Aircraft_Class: Input aircraft instance
			- Design variables: These will be modified based on new MDO iteration
		Outputs:
			- Aircraft_Class: Output and modified aircraft instance 
	"""

	def __init__(self ):
		super(aeroAnalysis,self).__init__()

		# Input instance of aircraft - before modification
		self.add_param('in_aircraft',val=AC, desc='Input Aircraft Class')

		# Output instance of aircaft - after modification
		self.add_output('out_aircraft',val=AC, desc='Output Aircraft Class')

	def solve_nonlinear(self,params,unknowns,resids):
		# Used passed in instance of aircraft
		AC = params['in_aircraft']
	
		# Call aero analysis to get CL, CD, CM and NP - Add to class
		AC.CL, AC.CD, AC.CM, AC.NP = getAeroCoef()

		# Set output to updated instance of aircraft
		unknowns['out_aircraft'] = AC


def getAeroCoef(geo_filename = './Aerodynamics/aircraft.txt', mass_filename = './Aerodynamics/aircraft.mass'):
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
	'''

	case = pyAVL.avlAnalysis(geo_file=geo_filename , mass_file =mass_filename )


	# stead level flight contraints
	case.addConstraint('elevator', 0.00)
	case.addConstraint('rudder', 0.00)

	case.alphaSweep(-8, 15, 1)
	# case.calcNP()


	# print '----------------- alpha sweep ----------------'
	# print 'Angle      Cl         Cd         Cm'
	# for i in xrange(len(case.alpha)):
	#     print '%8f   %8f   %8f   %8f   '%(case.alpha[i]*(180/np.pi),case.CL[i],case.CD[i],case.CM[i])




	# case.alpha = [x * np.pi/180 for x in case.alpha]

	# get func for aero coeificent
	CL = np.poly1d(np.polyfit(case.alpha,case.CL, 1))
	CD = np.poly1d(np.polyfit(case.alpha,case.CD, 2))
	CM = np.poly1d(np.polyfit(case.alpha,case.CM, 2))

	NP = case.calcNP()

	# ----------------- Plot Outputs --------------------------
	# plt.figure(3)
	# plt.subplot(311)
	# plt.ylabel('CL')
	# plt.xlabel('Alpha')
	# plt.plot(case.alpha, case.CL, 'b-o')

	# plt.subplot(312)
	# plt.xlabel('CD')
	# plt.ylabel('CL')
	# plt.plot( case.CD, case.CL, 'b-o')


	# plt.subplot(313)
	# plt.ylabel('CM')
	# plt.xlabel('Alpha')
	# plt.plot(case.alpha, case.CM, 'b-o')
	# plt.show()


	return (CL, CD, CM, NP)


