from __future__ import division
from __future__ import print_function

from openmdao.api import Component

from scipy.optimize import *
import numpy as np

from xfoil_lib import getDataXfoil

import pyAVL

from Constants import Rho, inced_ang
from Constants import xfoil_path


class aeroAnalysis(Component):
    """
    OpenMDAO component for aerodynamic analysis via AVL
    - Uses the current iteration of the aircraft: in_aircraft
    - Modifies in_aircraft, outputs a new out_aircraft
    - ^ All of the same AC class (AC.wing, AC.tail, etc.)

    Inputs
    -------
    Aircraft_Class:	class
                    in_aircraft class


    Outputs
    -------
    Aircraft_Class:	class
                    out_aircraft class
    SM			: 	float
                    Static margin
    """

    def __init__(self):
        from Input import AC

        super(aeroAnalysis, self).__init__()

        # Input instance of aircraft - before modification
        self.add_param('in_aircraft', val=AC, desc='Input Aircraft Class')

        # Output instance of aircaft - after modification
        self.add_output('out_aircraft', val=AC, desc='Output Aircraft Class')

        # Other outputs to be used in top_level group (e.g. constraints)
        self.add_output('SM', val=0.0, desc='static margin')

    def solve_nonlinear(self, params, unknowns, resids):
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
        try:
            AC.alpha, AC.CL, AC.CD, AC.CM, AC.NP, AC.sec_CL, AC.sec_Yle, sec_Chord, velocity = getAeroCoef()
        except RuntimeError as e:
            print('TRIM FAILED')
            print(e)
            AC.alpha = [ 0 ]
            AC.CL = lambda x: 0
            AC.CD = lambda x: 0
            AC.CM = lambda x: 0
            AC.NP = 0
            AC.sec_CL = [ [ 0 ] ]
            AC.sec_Yle = [ [ 0 ] ]
            sec_Chord = [ [ 0 ] ]
            velocity = [ [ 0 ] ]
            #return False # TODO - FIX THIS TO PROPERLY ACCOUNT FOR NO-TRIM

        # Static Margine calculation
        SM = (AC.NP - AC.CG[0]) / AC.wing.MAC
        AC.SM = SM

        # Calculate cruise velocity
        AC.vel, AC.ang = calcVelCruise(AC.CL, AC.CD, AC.weight, AC.wing.sref, AC.tail.sref)

        # Get gross lift
        flapped = False
        AC.gross_F, AC.wing_f, AC.tail_f = grossLift(AC.vel, AC.ang, AC.wing.sref, AC.tail.sref, flapped, AC.CL)

        AC.sec_L = calcSecLift(velocity, AC.sec_CL, sec_Chord)

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


def getAeroCoef(geo_filename='./Aerodynamics/aircraft.txt', mass_filename='./Aerodynamics/aircraft.mass'):
    """
    Using AVL, calculate the full-vehicle aerodynamic coefficients
    *As functions of the angle of attack


    Inputs
    ----------
    geo_filename 	: 	String
        File name of the AVL geometry file for the aircraft

    mass_filename 	: 	String
        File name of the AVL geometry file for the aircraft

    Outputs
    ----------
    alpha 			: 	ndarray
                        Sweep of angle of attacks used
    CL,CD, CD, secCL, sec_Yle : Functions
        Functions that will return the value for the coeffiecent
        for a given angle of attack
        example: CL(10*np.pi/180)  <- note the use of radians

    NP : float
       X location of NP in AVL coordinate system
    """
    # Create the pyAVL case
    case = pyAVL.avlAnalysis(geo_file=geo_filename, mass_file=mass_filename)

    # Steady level flight contraints
    case.addConstraint('elevator', 0.00)
    case.addConstraint('rudder', 0.00)

    # Execute the case
    case.executeRun()

    # Calculate the neutral point
    # case.calcNP()
    NP = case.NP

    case.clearVals()

    # Create a sweep over angle of attack
    # case.alphaSweep(-15, 30, 2)
    case.alphaSweep(-15, 15, 4)

    alpha = case.alpha
    sec_CL = case.sec_CL
    sec_Yle = case.sec_Yle
    sec_Chord = case.sec_Chord
    velocity = case.velocity

    # get func for aero coeificent
    CL = np.poly1d(np.polyfit(case.alpha, case.CL, 1))
    CD = np.poly1d(np.polyfit(case.alpha, case.CD, 2))
    CM = np.poly1d(np.polyfit(case.alpha, case.CM, 2))

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
    print("NP = %f" % NP)
    print("Max Elevator deflection = %f deg" % max(case.elev_def))

    return (alpha, CL, CD, CM, NP, sec_CL, sec_Yle, sec_Chord, velocity)


# Use xfoil to get sectional values for an airfoil
alphas_tail, CLs_tail_flap = getDataXfoil(xfoil_path + '_flap.dat')[0:2]
alphas_tail_noflap, CLs_tail_noflap = getDataXfoil(xfoil_path + '.dat')[0:2]
alphas_tail = [x * np.pi / 180 for x in alphas_tail]
CL_tail_flap = np.poly1d(np.polyfit(alphas_tail, CLs_tail_flap, 2))
CL_tail_noflap = np.poly1d(np.polyfit(alphas_tail_noflap, CLs_tail_noflap, 2))


def getThrust(vel, ang):
    """
    Calculate the thrust available at a flight condition

    Inputs
    -------
    vel 		:	float
                    velocity
    ang 		:	float
                    angle of attack


    Outputs
    -------
    X_comp 		:	float
                    X component of thrust available
    Y_comp 		:	float
                    Y component of thrust available
    """

    # Thrust data (from dynamic thrust testing)
    T_0 = 18.00
    T_1 = -0.060
    T_2 = -0.015
    T_3 = 0
    T_4 = 0

    # Thrust available
    T = vel ** 4 * T_4 + vel ** 3 * T_3 + vel ** 2 * T_2 + vel * T_1 + T_0

    # X and Y components of thrust available
    X_comp = np.cos(ang) * T
    Y_comp = np.sin(ang) * T
    return (X_comp, Y_comp)


def getTailCL(ang, flapped):
    """
    Get the new CL of the tail if elevator is deflected

    Inputs
    -------
    ang 		:	float
                    angle of elevator deflection
    flapped		:	bool ('True' or 'False')
                    If elevator is deflected


    Outputs
    -------
    CL 			:	float
                    CL of the tail with/without deflection
    """

    # Call output data from tail
    if flapped:
        return CL_tail_flap(ang + inced_ang)
    else:
        return CL_tail_noflap(ang + inced_ang)


def grossLift(vel, ang, sref_wing, sref_tail, flapped, CL):
    """
    Calculate the gross lift of a configuration

    Inputs
    -------
    vel 		:	float
                    velocity
    ang 		:	float
                    angle of attack
    sref_wing   :	float
                    wing surface area
    sref_tail 	: 	float
                    tail surface area
    flapped		:	bool ('True' or 'False')
                    If elevator is deflected
    CL 			: 	function
                    CL function from AVL run


    Outputs
    -------
    gross_F 	:	float
                    gross lift of vehicle
    wing_F 		:	float
                    wing lift of vehicle
    tail_F 		:	float
                    tail lift of vehicle
    """

    # Calculate lifts using CL functions
    wing_f = 0.5 * Rho * vel ** 2 * (CL(ang) * sref_wing)
    tail_f = 0.5 * Rho * vel ** 2 * (getTailCL(ang, flapped) * sref_tail)
    l_net = wing_f + tail_f
    gross_F = l_net + getThrust(vel, ang)[1]

    return gross_F, wing_f, tail_f


def calcVelCruise(CL, CD, weight, sref_wing, sref_tail):
    """
    Calculate the cruise velocity of a configuration

    Inputs
    -------
    CL 			: 	function
                    CL function from AVL run
    CD 			: 	function
                    CD function from AVL run
    weight 		: 	float
                    weight of vehicle
    sref_wing   :	float
                    wing surface area
    sref_tail 	: 	float
                    tail surface area


    Outputs
    -------
    vel  		:	float
                    cruise velocity
    ang 		:	float
                    cruise angle of attack
    """

    def sumForces(A):
        """
        Get sum of the forces, used for fsolve
        """
        vel = A[0]
        ang = A[1]

        gross_F, wing_f, tail_f = grossLift(vel, ang, sref_wing, sref_tail, 0, CL)

        F = np.empty(2)

        F[0] = getThrust(vel, ang)[0] - 0.5 * vel ** 2 * Rho * CD(ang) * sref_wing
        F[1] = gross_F - weight

        return F

    # Fsolve to balance lift and weight
    Z = fsolve(sumForces, np.array([40, -10 * np.pi / 180])) # TODO: Fix velocity so that fsolve doesn't start at 40?

    # Return cruise velocity and angle of attack
    ang = Z[1]
    vel = Z[0]
    return (vel, ang)


def calcSecLift(velocity, sec_CL, sec_Chord):
    sec_L = []
    for n in range(len(sec_CL)):
        # sec_L[n] = [0.5*Rho*velocity[n][0]**2*sec_CL[n][x]*sec_Chord[n][x] for x in range(len(sec_CL[n]))]
        sec_L.append([0.5 * Rho * velocity[n][0] ** 2 * sec_CL[n][x] * sec_Chord[n][x] for x in range(len(sec_CL[n]))])

    return sec_L
