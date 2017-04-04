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
from Input import AC, updateAircraft
from Aircraft_Class.aircraft_class import *


class createAC(Component):
	"""
	OpenMDAO component for updating the aircaft (AC) after each iteration of MDO

	Inputs
	-------
	Aircraft_Class  :   class
						in_aircraft class
	design variables: 	many variables
						Variables for modification


	Outputs
	-------
	Aircraft_Class  :   class
						out_aircraft class

	"""

	def __init__(self ):
		super(createAC,self).__init__()

		# Input instance of aircraft - before modification
		self.add_param('def_aircraft',val=AC, desc='Aircraft Class')

		# Parameter(s) of aicraft to be modified within this component
		# - I.e. design variables
		# - Uncomment the variables to be used
		self.add_param('b_wing',val = 3.2, desc='wing span')
		# self.add_param('dihedral',val = 0.0, desc='wing dihedral')
		self.add_param('sweep',val = np.array([0.0, 0.0, 0.0, 0.0]), desc = 'wing sweep')
		self.add_param('chord',val = np.array([0.0, 0.0, 0.0, 0.72]), desc = 'wing chord')
		# self.add_param('dist_LG',val = 0.0, desc = 'Distance b/w LG and CG')
		self.add_param('boom_len',val = 1.60, desc='Length of Tailboom')
		# self.add_param('camber',val = np.array([0.0 , 0.0, 0.0,0.0]), desc='Wing Camber')
		# self.add_param('max_camber',val = np.array([0.0 , 0.0, 0.0,0.0]), desc='Percent chord of max camber')	
		# self.add_param('thickness',val = np.array([0.0 , 0.0, 0.0,0.0]), desc='wing thickness')
		# self.add_param('max_thickness',val = np.array([0.0 , 0.0, 0.0,0.0]), desc='Percent chord of max thickness')	# Vertical Tail Span
		# self.add_param('Ainc',val = p.array([0.0 , 0.0, 0.0,0.0]), desc = 'Angle of Incidence')	
		self.add_param('htail_chord',val = np.array([0.0 , 0.0, 0.0,0.325]), desc = 'Horiz. tail chord')
		self.add_param('vtail_chord',val = np.array([0.0 , 0.0, 0.0,0.325]), desc = 'Vert. tail chord')
		self.add_param('b_htail',val = 1.30, desc = 'Horiz. tail span')
		self.add_param('b_vtail',val = 0.37, desc = 'Vert. tail span')

		# Output instance of aircaft - after modification
		self.add_output('aircraft', val=AC ,desc='score')


	def solve_nonlinear(self,params,unknowns,resids):
		# Used passed in instance of aircraft
		AC = params['def_aircraft']
	
		# Uncomment to reveal more design variables for use in the MDO
		AC.wing.b_wing = params['b_wing']
		# AC.wing.dihedral = params['dihedral']
		AC.wing.sweep = params['sweep']
		AC.wing.chord = params['chord']
		# AC.dist_LG = params['dist_LG']
		AC.boom_len = params['boom_len']
		# AC.camber = params['camber']
		# AC.max_camber = params['max_camber']
		# AC.thickness = params['thickness']
		# AC.max_thickness = params['max_thickness']
		# AC.wing.Ainc = params['Ainc']
		AC.tail.htail_chord = params['htail_chord']
		AC.tail.vtail_chord = params['vtail_chord']
		AC.tail.b_htail = params['b_htail']
		AC.tail.b_vtail = params['b_vtail']


		# Update aircraft before analysis
		updateAircraft(AC)

		# Set output to updated instance of aircraft
		unknowns['aircraft'] = AC


		