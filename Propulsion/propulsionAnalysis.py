#python stantdard libraries 
from __future__ import division
from time import localtime, strftime, time

# addition python libraries 
import numpy as np
import matplotlib.animation as animation
import matplotlib.pyplot as plt

#open MDAO libraries
from openmdao.api import IndepVarComp, Component, Problem, Group
from openmdao.api import ScipyOptimizer, ExecComp, SqliteRecorder
#from openmdao.drivers.pyoptsparse_driver import pyOptSparseDriver
from openmdao.drivers.latinhypercube_driver import OptimizedLatinHypercubeDriver
from scipy.optimize import *
from sympy import Symbol, nsolve

# Import self-created components
from Input import AC
import APCdat_parser

# Change the name of your componenet here
class propulsionAnalysis(Component):
	"""
		Propulsion Analysis: Uses the current iteration of the aircraft, performances
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
		self.add_param('in_aircraft',val=AC, desc='Input Aircraft Class')

		# Output instance of aircaft - after modification
		self.add_output('out_aircraft',val=AC, desc='Output Aircraft Class')

		# Initialize Kriging Model
		self.model = createKriging([8,10],[5,8],[1000, 10000])


	def solve_nonlinear(self,params,unknowns,resids):
		# Used passed in instance of aircraft
		AC = params['in_aircraft']

		# Calculate battery parameters
		# Set it such that the only in increments of 3.7 V

		# Calculate RPM using KV

		# Calcualte thrust curve

		# Set output to updated instance of aircraft
		unknowns['out_aircraft'] = AC

		## NOTE TO BELDON
		# Reexeceute Ok3d object to get value at specific point



