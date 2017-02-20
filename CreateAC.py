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
from Input import AC
from Aircraft_Class.gen_files import gen_mass, gen_geo


class createAC(Component):
	"""
		createAC: Updates the aircraft parameters after every iteration of MDO
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

		# Parameter(s) of aicraft to be modified within this component
		# self.add_param('b_wing',val=0.0, desc='wing span')						
		# self.add_param('dihedral',val = 0.0, desc='wing dihedral')						
		# self.add_param('sweep',val =  np.array([0.0, 0.0, 0.0, 00.0]), desc = 'wing sweep')
		self.add_param('chord',val = np.array([0.0, 0.0, 0.0, 0]), desc = 'wing chord')	
		# self.add_param('dist_LG',val = 0.0, desc = 'Distance b/w LG and CG')					
		# self.add_param('boom_len',val = 0.0, desc='Length of Tailboom')						
		# self.add_param('camber',val = np.array([0.0 , 0.0, 0.0,0.0]), desc='Wing Camber')
		# self.add_param('max_camber',val = np.array([0.0 , 0.0, 0.0,0.0]), desc='Percent chord of max camber')	
		# self.add_param('thickness',val = np.array([0.0 , 0.0, 0.0,0.0]), desc='wing thickness')
		# self.add_param('max_thickness',val = np.array([0.0 , 0.0, 0.0,0.0]), desc='Percent chord of max thickness')	# Vertical Tail Span
		# self.add_param('Ainc',val = p.array([0.0 , 0.0, 0.0,0.0]), desc = 'Angle of Incidence')	
		# self.add_param('c_r_ht',val = np.array([0.0 , 0.0, 0.0,0.0]), desc ='Horiz. tail chord')
		# self.add_param('c_r_vt',val = np.array([0.0 , 0.0, 0.0,0.0]), desc = 'Vert. tail chord')
		# self.add_param('b_htail',val = 0.0, desc = 'Horiz. tail span')
		# self.add_param('b_vtail',val = 0.0, desc = 'Vert. tail span')

		# Output instance of aircaft - after modification
		self.add_output('aircraft', val=AC ,desc='score ')


	def solve_nonlinear(self,params,unknowns,resids):
		# Used passed in instance of aircraft
		AC = params['def_aircraft']
	
		# Modify instance of aircraft - This is where analysis would happen
		# AC.wing.b_wing = params['b_wing']
		# AC.wing.dihedral = params['dihedral']
		# AC.sweep = params['sweep']
		AC.wing.chord = params['chord']
		# AC.dist_LG = params['dist_LG']
		# AC.boom_len = params['boom_len']
		# AC.camber = params['camber']
		# AC.max_camber = params['max_camber']
		# AC.thickness = params['thickness']
		# AC.max_thickness = params['max_thickness']
		# AC.wing.Ainc = params['Ainc']
		# AC.tail.c_r_ht = params['c_r_ht']
		# AC.tail.c_r_vt = params['c_r_vt']
		# AC.tail.b_htail = params['b_htail']
		# AC.tail.b_vtail = params['b_vtail']


		# Update aircraft before analysis
		AC.wing.updateAircraft()

		# Create AVL geometry file
		gen_geo(AC)

		# Set output to updated instance of aircraft
		unknowns['aircraft'] = AC


		