#python stantdard libraries 
from __future__ import division
from time import localtime, strftime, time

# addition python libraries 
import numpy as np
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from scipy.integrate import cumtrapz

#open MDAO libraries
from openmdao.api import IndepVarComp, Component, Problem, Group
from openmdao.api import ScipyOptimizer, ExecComp, SqliteRecorder
from openmdao.drivers.pyoptsparse_driver import pyOptSparseDriver
from openmdao.drivers.latinhypercube_driver import OptimizedLatinHypercubeDriver
from scipy.optimize import *
from sympy import Symbol, nsolve

# Import self-created components
from Input_Files.Input import AC
from aircraft_structure.py import *

class structAnalysis(Component):
	"""
		structAnalysis: Uses the current iteration of the aircraft, performs structure
		analysis to get maximum stress and deflection
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
		self.add_output('output_data', val=AC,desc='Example of Output Data')


	def solve_nonlinear(self,params,unknowns,resids):
		# Used passed in instance of aircraft
		AC = params['def_aircraft']
	
		# Modify instance of aircraft - This is where analysis would happen
		sig_max, y_max = run_structAnalysis(AC);

		# AC.wing.b_wing = params['b_wing']

		# Set output to updated instance of aircraft
		# unknowns['output_data'] = 2*AC.wing.b_wing

# Insert component analysis functions here

# Calculate area moment of inertia for input spar
def calcI(shape, dim):
	# spar is hollow circle
	# dim should be [outer radius, inner radius]
	if shape == 'C':
		c = dim[0];
		I = np.pi/4*(dim[0]**4 - dim[1]**4);

  	# spar is hollow rectangle
  	# dim should be [outer width, outer height, inner width, inner height]
	elif shape == 'R':
		c = dim[1]/2;
		I = 1./12*(dim[0]*dim[1]**3 - dim[2]*dim[3]**3);

  	#spar is I-beam
  	# dim should be [flange width, flange height, web width, web height]
  	elif shape == 'I':

	  	"""
		I beam definition

		       Flange Width
		  < ---------------- >
		  ____________________
		 |          1         |  ^   Flange Height 
		 |____________________|  v
		        |      |  ^     
		        |      |  |     
		        |      |       
		        |   2  |  | Web Height    
		        |      |       
		        |      |  |           
		  ______|______|__v___             ^ Z
		 |          3         |            |
		 |____________________| ___datum    ----> Y

		        <----->
		        Web Width
	    """

  		A = np.zeros(3); y = np.zeros(3); Is = np.zeros(3);

  		# calculate centroid of I beam
  		A[0] = dim[0]*dim[1]; A[1] = dim[2]*dim[3]; A[2] = A[0];
  		y[0] = dim[1] + dim[1]/2 + dim[3]; y[1] = dim[1] + dim[3]/2; y[2] = dim[1]/2;
  		ybar = np.inner(A, y)/np.sum(A);

  		# calculate area moment of inertia
  		Is[0] = 1./12*(dim[0]*dim[1]**3); Is[1] = 1./12*(dim[2]*dim[3]**3); Is[2] = Is[0];
  		d = abs(y - ybar);
  		I = np.sum(Is + A*np.power(d,2));
  		c = ybar;

	return c, I

# Calculate distributed forces
def distLoad(x, mag, dist_type):
	# elliptically distributed load
	if dist_type == 'elliptical':
		A = x[-1]; B = mag;
		w = B*np.sqrt(1 - (x/A)**2);

	# uniformly distributed load
	elif dist_type == 'uniform':
		w = mag*np.ones(len(x));

	# linearly decreasing distributed load
	elif dist_type == 'lin_decrease':
		w = mag - mag/x[-1]*x;

	# linearly increasing distributed load
	elif dist_type == 'lin_increase':
		w = mag/x[-1]*x;

	return w

# Calculate cumulative integral values needed for beam theory equations
def getIntegrals(x, w):
	w1 = cumtrapz(w, x, initial=0);
	w2 = cumtrapz(w1, x, initial=0);
	w3 = cumtrapz(w2, x, initial=0);
	w4 = cumtrapz(w3, x, initial=0);

	return w1, w2, w3, w4

# Solves beam theory differential equations
def calcDistribution(x, w, I, E, c):
	# Inputs: x - positions along the spar
	#		  w - biggest magnitude for distributed load
	#		  I - area moment of inertia
	# 		  E - Young's modulus
	# 		  c - distance b/w neutral point and farthest point in the neutral plane
	# Outputs:V - shear force distribution
	#		  M - moment distribution
	#		  Theta - distribution of slope of beam in degrees
	# 		  y - beam deflection distribution
	# 		  sigma - stress distribution

	EI = E*I;
	w1, w2, w3, w4 = getIntegrals(x, w/EI)

	# Set boundary conditions
	C1 = w1[-1];				# V(L) = 0
	C2 = w2[-1] - C1*x[-1];		# M(L) = 0
	C3 = w3[0];					# Theta(0) = 0
	C4 = w4[0];					# y(0) = 0

	# Get shear distribution
	V = (C1 - w1)*EI;

	# Get moment distribution
	M = (C1*x + C2 - w2)*EI;

	# Get slope distribution
	Theta = 0.5*C1*x**2 + C2*x + C3 - w3;
	Theta = np.degrees(Theta);

	# Get deflection distribution
	y = 1./6*C1*x**3 + 0.5*C2*x**2 + C3*x + C4 - w4;

	# Get stress distribution
	sigma = -c*M/I;

	return V, M, Theta, y, sigma

# Runs main structure analysis
def run_structAnalysis(AC):
	x = np.linspace(0, AC.Wing.b_wing/2.0, 1001)
	w = distLoad(x, AC.mag, AC.Wing.spar.dist_type)
	c, I = calcI(AC.Wing.spar.type, AC.Wing.spar.dim)
	V, M, Theta, y, sigma = calcDistribution(x, w, I, AC.Wing.spar.E, c)

	return max(sigma), max(y)
