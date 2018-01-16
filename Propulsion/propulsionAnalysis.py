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

#Kriging Library
from pykrige.ok3d import OrdinaryKriging3D
from pykrige.uk3d import UniversalKriging3D


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
		total_Voltage = AC.cell_Num * 3.7

		RPM = AC.motor_KV/total_Voltage
		# Calcualte thrust curve
		coeff1Model = self.model['coeff1'][0]
		coeff2Model = self.model['coeff2'][0]
		coeff3Model = self.model['coeff3'][0]
		coeff4Model = self.model['coeff4'][0]
		coeff5Model = self.model['coeff5'][0]
		coeff1ModelQ = self.model['coeff1Q'][0]
		coeff2ModelQ = self.model['coeff2Q'][0]
		coeff3ModelQ = self.model['coeff3Q'][0]
		coeff4ModelQ = self.model['coeff4Q'][0]
		coeff5ModelQ = self.model['coeff5Q'][0]

		coeff1T = coeff1Model.exceute('points', AC.prop_diam, AC.prop_pitch, RPM)
		coeff2T = coeff2Model.exceute('points', AC.prop_diam, AC.prop_pitch, RPM)
		coeff3T = coeff3Model.exceute('points', AC.prop_diam, AC.prop_pitch, RPM)
		coeff4T = coeff4Model.exceute('points', AC.prop_diam, AC.prop_pitch, RPM)
		coeff5T = coeff5Model.exceute('points', AC.prop_diam, AC.prop_pitch, RPM)
		coeff1Q = coeff1ModelQ.exceute('points', AC.prop_diam, AC.prop_pitch, RPM)
		coeff2Q = coeff2ModelQ.exceute('points', AC.prop_diam, AC.prop_pitch, RPM)
		coeff3Q = coeff3ModelQ.exceute('points', AC.prop_diam, AC.prop_pitch, RPM)
		coeff4Q = coeff4ModelQ.exceute('points', AC.prop_diam, AC.prop_pitch, RPM)
		coeff5Q = coeff5ModelQ.exceute('points', AC.prop_diam, AC.prop_pitch, RPM)
		
		thrust_Curve = [coeff1T, coeff2T, coeff3T, coeff4T, coeff5T]
		torque_Curve = [coeff1Q, coeff2Q, coeff3Q, coeff4Q, coeff5Q]

		AC.propulsion.setThrustCurve(thrust_Curve)
		AC.thrust = thrust_Curve

		# Calculate max current
		speeds = np.linspace(0.0,50.0,0.5)
		torqueActual = []
		for speed in speeds:
			torqueActual.append(math.abs(speed**4*coeff1Q+speed**3*coeff2Q+speed**2*coeff3Q+speed*coeff4Q+coeff5Q))

		maxTorque = np.amax(torqueActual)
		KT = 1.0/KV
		maxCurrent = maxTorque/KV
		AC.esc_max = maxCurrent

		# Set output to updated instance of aircraft
		unknowns['out_aircraft'] = AC

		## NOTE TO BELDON
		# Reexeceute Ok3d object to get value at specific point



