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
from xfoil_lib import xfoilAlt, getDataXfoil

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
		self.add_output('SM', val = 0.0, desc = 'static margin')

	def solve_nonlinear(self,params,unknowns,resids):
		# Used passed in instance of aircraft
		AC = params['in_aircraft']

		# print('================  Current Results ===================')
		# print('\n')
		# print("Chord Values", AC.wing.chord_vals)
		# print("Chord Cubic Terms", AC.wing.chord)
		# print("Wingspan", AC.wing.b_wing)
		# print("Boom Length", AC.boom_len)
		# print("Sweep Cubic Terms", AC.wing.sweep)
		# print("Sweep Values", AC.wing.sweep_vals)
		# print("Horiz. Tail Chord Values", AC.tail.htail_chord_vals)
		# print("Horiz. Tail  Chord Cubic Terms", AC.tail.htail_chord)
	
		# Call aero analysis to get CL, CD, CM and NP - Add to class
		AC.alpha, AC.CL, AC.CD, AC.CM, AC.NP, AC.secCL, AC.sec_Yle = getAeroCoef()

		# Static Margine calculation
		SM = (AC.NP - AC.CG[0])/AC.wing.MAC
		AC.SM = SM

		# Calculate cruise velocity
		AC.vel, AC.ang = calcVelCruise(AC.CL, AC.CD, AC.weight, AC.wing.sref, AC.tail.sref)

		# Get gross lift
		flapped = False
		AC.gross_F, AC.wing_f, AC.tail_f = grossLift(AC.vel, AC.ang, AC.wing.sref, AC.tail.sref, flapped, AC.CL)

		# print('Wing Lift = %f' % AC.wing_f)
		# print('Tail Lift = %f' % AC.tail_f)

		print("Cruise Velocity = %f m/s" % AC.vel)
		print("Cruise AOA = %f degrees" % AC.ang)
		print("CL of aircraft = %f" % AC.CL(AC.ang))
		print("CD of aircraft = %f" % AC.CD(AC.ang))
		print("SM = %f" % AC.SM)

		# Set output to updated instance of aircraft
		unknowns['out_aircraft'] = AC
		unknowns['SM'] = AC.SM


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


	# steady level flight contraints
	case.addConstraint('elevator', 0.00)
	case.addConstraint('rudder', 0.00)


	case.executeRun()

	#print '----------------- Neutral Point ----------------'
	case.calcNP()
	NP = case.NP
	
	case.clearVals()


	# case.alphaSweep(-15, 30, 2)
	case.alphaSweep(-15, 15, 4)
	# case.calcNP()

	alpha = case.alpha
	secCL = case.sec_CL
	sec_Yle = case.sec_Yle

	# get func for aero coeificent
	CL = np.poly1d(np.polyfit(case.alpha,case.CL, 1))
	CD = np.poly1d(np.polyfit(case.alpha,case.CD, 2))
	CM = np.poly1d(np.polyfit(case.alpha,case.CM, 2))

	# # ----------------- Plot Outputs --------------------------
	# plt.figure(4)
	# plt.subplot(411)
	# plt.ylabel('CL')
	# plt.xlabel('Alpha')
	# plt.plot( np.degrees(case.alpha), case.CL, 'b-o')

	# plt.subplot(412)
	# plt.xlabel('CD')
	# plt.ylabel('CL')
	# plt.plot( case.CD, case.CL, 'b-o')


	# plt.subplot(413)
	# plt.ylabel('CM')
	# plt.xlabel('Alpha')
	# plt.plot(np.degrees(case.alpha), case.CM, 'b-o')


	# plt.subplot(414)
	# plt.ylabel('Elvator Deflection')
	# plt.xlabel('Alpha')
	# plt.plot(np.degrees(case.alpha), case.elev_def, 'b-o')



	# plt.show()
	print("NP = %f"% NP)
	print("Max Elevator deflection = %f deg" % max(case.elev_def))

	return (alpha, CL, CD, CM, NP, secCL, sec_Yle)
# Declare Constants

Rho = 1.225 # make global
# Sref_tail = 0.212
g = 9.81
mu_k = 0.005

inced_ang = -5.0 *np.pi/180.0

# xfoil_path = '/home/creynol/Joint_MDO_v1/Aerodynamics/xfoil/elev_data'
xfoil_path = 'Aerodynamics/xfoil/elev_data'


alphas_tail, CLs_tail_flap = getDataXfoil(xfoil_path+ '_flap.dat')[0:2]
alphas_tail_noflap,CLs_tail_noflap = getDataXfoil(xfoil_path+ '.dat')[0:2]
alphas_tail = [x * np.pi/180 for x in alphas_tail]
CL_tail_flap = np.poly1d(np.polyfit(alphas_tail,CLs_tail_flap, 2))
CL_tail_noflap = np.poly1d(np.polyfit(alphas_tail_noflap,CLs_tail_noflap, 2))



def getThrust(vel, ang):
	T_0 = 18.00
	T_1 = -0.060
	T_2 = -0.015
	T_3 = 0 #-7*10**-5*3.28**3
	T_4 = 0 # 4*10**-7*3.28**4

	T = vel**4*T_4 + vel**3*T_3 + vel**2*T_2 + vel*T_1 + T_0
			#X comp   # Y Comp
	return (np.cos(ang)*T, np.sin(ang)*T )


def getTailCL(ang, flapped):
	if (flapped):
		return CL_tail_flap(ang + inced_ang)
	else:
		return CL_tail_noflap(ang + inced_ang)

def grossLift(vel, ang, sref_wing, sref_tail, flapped, CL):

	wing_f = 0.5*Rho*vel**2*(CL(ang)*sref_wing)
	tail_f = 0.5*Rho*vel**2*(getTailCL(ang, flapped)*sref_tail)
	l_net = wing_f + tail_f

	gross_F = l_net + getThrust(vel,ang)[1]

	return gross_F, wing_f, tail_f




def calcVelCruise(CL, CD, weight, sref_wing, sref_tail):	
	def sumForces (A):
		vel = A[0]
		ang = A[1]

		gross_F, wing_f, tail_f = grossLift(vel, ang, sref_wing, sref_tail, 0, CL)

		F = np.empty(2)

		F[0] = getThrust(vel, ang)[0] - 0.5*vel**2*Rho*CD(ang)*sref_wing
		F[1] = gross_F - weight
		
		return F

 	Z = fsolve(sumForces,np.array([40, -10*np.pi/180]))

 	ang = Z[1]
 	vel =  Z[0]

 	return (vel, ang)


