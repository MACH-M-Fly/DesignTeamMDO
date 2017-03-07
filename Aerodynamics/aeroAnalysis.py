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
from xfoil_lib import xfoil_alt, getData_xfoil

from Input import AC
import pyAVL



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

		# Calculate cruise velocity
		AC.vel, AC.ang = calc_velcruise(AC.CL, AC.CD, AC.weight, AC.wing.Sref, AC.tail.Sref)

		# Get gross lift
		flapped = False
		AC.gross_F = gross_lift(AC.vel, AC.ang, AC.wing.Sref, AC.tail.Sref, flapped, AC.CL)

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

	case = pyAVL.avlAnalysis(geo_file=geo_filename, mass_file = mass_filename)


	# stead level flight contraints
	case.addConstraint('elevator', 0.00)
	case.addConstraint('rudder', 0.00)


	case.executeRun()

	#print '----------------- Neutral Point ----------------'
	case.calcNP()
	NP = case.NP
	
	case.clearVals()


	case.alphaSweep(-15, 30, 2)
	# case.calcNP()



	# get func for aero coeificent
	CL = np.poly1d(np.polyfit(case.alpha,case.CL, 1))
	CD = np.poly1d(np.polyfit(case.alpha,case.CD, 2))
	CM = np.poly1d(np.polyfit(case.alpha,case.CM, 2))

	# # ----------------- Plot Outputs --------------------------
	plt.figure(4)
	plt.subplot(411)
	plt.ylabel('CL')
	plt.xlabel('Alpha')
	plt.plot( np.degrees(case.alpha), case.CL, 'b-o')

	plt.subplot(412)
	plt.xlabel('CD')
	plt.ylabel('CL')
	plt.plot( case.CD, case.CL, 'b-o')


	plt.subplot(413)
	plt.ylabel('CM')
	plt.xlabel('Alpha')
	plt.plot(np.degrees(case.alpha), case.CM, 'b-o')


	plt.subplot(414)
	plt.ylabel('Elvator Deflection')
	plt.xlabel('Alpha')
	plt.plot(np.degrees(case.alpha), case.elev_def, 'b-o')



	plt.show()

	return (CL, CD, CM, NP)
# Declare Constants

Rho = 1.225 # make global
# Sref_tail = 0.212
g = 9.81
mu_k = 0.005

inced_ang = -5.0 *np.pi/180.0

# xfoil_path = '/home/creynol/Joint_MDO_v1/Aerodynamics/xfoil/elev_data'
xfoil_path = 'Aerodynamics/xfoil/elev_data'


alphas_tail, CLs_tail_flap = getData_xfoil(xfoil_path+ '_flap.dat')[0:2]
alphas_tail_noflap,CLs_tail_noflap = getData_xfoil(xfoil_path+ '.dat')[0:2]
alphas_tail = [x * np.pi/180 for x in alphas_tail]
CL_tail_flap = np.poly1d(np.polyfit(alphas_tail,CLs_tail_flap, 2))
CL_tail_noflap = np.poly1d(np.polyfit(alphas_tail_noflap,CLs_tail_noflap, 2))



def thrust(vel, ang):
	T_0 = 18.00
	T_1 = -0.060
	T_2 = -0.015
	T_3 = 0 #-7*10**-5*3.28**3
	T_4 = 0 # 4*10**-7*3.28**4

	T = vel**4*T_4 + vel**3*T_3 + vel**2*T_2 + vel*T_1 + T_0
			#X comp   # Y Comp
	return (np.cos(ang)*T, np.sin(ang)*T )


def tail_CL(ang, flapped):
	if (flapped):
		return CL_tail_flap(ang + inced_ang)
	else:
		return CL_tail_noflap(ang + inced_ang)

def gross_lift(vel, ang, Sref_wing, Sref_tail, flapped, CL):
	l_net = 0.5*Rho*vel**2*(CL(ang)*Sref_wing + tail_CL(ang, flapped)*Sref_tail)

	gross_F = l_net + thrust(vel,ang)[1]

	return gross_F




def calc_velcruise(CL, CD, weight, Sref_wing, Sref_tail):	
	def sum_forces (A):
		vel = A[0]
		ang = A[1]


		F = np.empty(2)

		F[0] = thrust(vel, ang)[0] - 0.5*vel**2*Rho*CD(ang)*Sref_wing
		F[1] = gross_lift(vel, ang, Sref_wing, Sref_tail, 0, CL) - weight
		# print(F)
		return F

 	Z = fsolve(sum_forces,np.array([40, -10*np.pi/180]))

 	ang = Z[1]
 	vel =  Z[0]

 	return (vel, ang)


