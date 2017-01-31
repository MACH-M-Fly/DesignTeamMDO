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
from openmdao.drivers.pyoptsparse_driver import pyOptSparseDriver
from openmdao.drivers.latinhypercube_driver import OptimizedLatinHypercubeDriver
from scipy.optimize import *
from sympy import Symbol, nsolve

# Import self-created components
from Input_Files.Input import AC

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
		self.add_param('def_aircraft',val=AC, desc='Aircraft Class')

		# Output instance of aircaft - after modification
		self.add_output('output_data', val=0.0,desc='Example of Output Data')


	def solve_nonlinear(self,params,unknowns,resids):
		# Used passed in instance of aircraft
		AC = params['def_aircraft']
	
		# Modify instance of aircraft - This is where analysis would happen
		AC.wing.b_wing = params['b_wing']

		# Set output to updated instance of aircraft
		unknowns['output_data'] = 2*AC.wing.b_wing



# Insert component analysis functions here