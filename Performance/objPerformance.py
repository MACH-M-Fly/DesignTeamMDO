from __future__ import division

from openmdao.api import IndepVarComp, Component, Problem, Group
from openmdao.api import ScipyOptimizer, ExecComp, SqliteRecorder
# from openmdao.drivers.pyoptsparse_driver import pyOptSparseDriver
from openmdao.drivers.latinhypercube_driver import OptimizedLatinHypercubeDriver

from scipy.optimize import *
# from sympy import Symbol, nsolve
import numpy as np
import matplotlib.pyplot as plt

# Add xfoil library to python path
import sys

sys.path.insert(0, 'Aerodynamics/xfoil/')

from Aerodynamics.xfoil_lib import getDataXfoil

from Aerodynamics.aeroAnalysis import getThrust

import math

from Constants import Rho, g, mu_k, inced_ang
from Constants import xfoil_path


class objPerformance(Component):
    """
    OpenMDAO component for performance analysis for 0: lap-time objective or
    1: maximum payload
    Obj 1) M-Fly: Maximum payload, limited runway
    Obj 2) MACH: Minimum lap time, given lap perimiter


    Inputs
    -------
    Aircraft_Class:	class
                    in_aircraft class (now has data from upstream components)


    Outputs
    -------
    Aircraft_Class:	class
                    out_aircraft class
    score		: 	float
                    Objective function score
    sum_y      	: 	float
                    net lift at the end of the runway
    N 			:	int
                    Number of laps (MACH)
    NP 			: 	float
                    Neutral point
    tot_time	:	float
                    total time per lap (MACH)
    chord_vals 	:	ndarray
                    Chord value at each section, returned to top level for constraining
    htail_ chord_vals 	:	ndarray
                    Tail chord value at each section, returned to top level for constraining
    """

    def __init__(self):
        super(objPerformance, self).__init__()

        from Input import AC

        # Input instance of aircraft - before modification
        self.add_param('in_aircraft', val=AC, desc='Input Aircraft Class')

        # Output instance of aircaft - after modification
        self.add_output('out_aircraft', val=AC, desc='Output Aircraft Class')

        # Other outputs to be used in top_level group (e.g. constraints)
        self.add_output('score', val=0.0, desc='score')
        self.add_output('sum_y', val=0.0, desc='Net Lift at End of Runway')
        self.add_output('N', val=0.0, desc='number of laps')
        self.add_output('NP', val=0.0, desc='Netual point')
        self.add_output('tot_time', val=0.0, desc='time')
        self.add_output('chord_vals', val=np.zeros((AC.wing.num_sections, 1)), desc='chord values')
        self.add_output('htail_chord_vals', val=np.zeros((AC.tail.num_sections, 1)), desc='tail chord values')
        self.add_output('takeoff_distance', val=0.0, desc='Takeoff Distance')

    def solve_nonlinear(self, params, unknowns, resids):
        # Used passed in instance of aircraft
        AC = params['in_aircraft']

        # Specifically using the values of camber/thickness at each spanwise split
        # print('Camber: '+ str(AC.wing.camber_vals))
        # print('Max camber pos: '+ str(AC.wing.max_camber_vals))
        # print('Thickness: '+ str(AC.wing.thickness_vals))
        # print('Max thickness position: '+ str(AC.wing.max_thickness_vals))

        # SM = (AC.NP - AC.CG[0])/AC.wing.MAC
        # print("Static Margin", SM)
        # print("Neutral Point", AC.NP)
        # print("Center of Gravity", AC.CG[0])

        # Run M-Fly maximum payload mission
        if AC.mission == 1:

                # Need to modify it so that payload weight is being determined
                sum_y, dist, vel, ang, ang_vel, time = runwaySim_small(AC.CL, AC.CD, AC.CM, AC.wing.sref, AC.tail.sref_ht, AC.weight, AC.boom_len,
                                          AC.dist_LG, AC.wing.MAC, AC.Iyy, AC)

                #AC.actual_takeoff = dist
                unknowns['takeoff_distance'] = dist
                unknowns['out_aircraft'] = AC
                score = -100. * AC.m_payload / math.sqrt(AC.mass_empty)
                print('############')
                print('Performance')
                print('############')
                print('Takeoff Dist:  %.3f m'% (dist))
                print('Takeoff Time:  %.3f s'% (time))
                print('Takeoff Velo:  %.3f s' % (vel))
                unknowns['score'] = score
                AC.score = score
                unknowns['sum_y'] = sum_y

        # Run MACH lap-time objective
        elif AC.mission == 2:

            # Call num_laps function for MACH mission
            N, tot_time, sum_y = num_laps(AC.CL, AC.CD, AC.CM, AC.wing.sref, AC.tail.sref, AC.weight, AC.boom_len,
                                          AC.dist_LG, AC.wing.MAC, AC.Iyy)
            score = -1 * (N * 100 - tot_time / 100.0)

            # Print output
            print("Net Lift ", sum_y,
                  ' Score: ' + str(score) + ' N: ' + str(N) + ' Total Time: ' + str(tot_time) + ' SM: ' + str(AC.SM))
            print('\n')

        # print('\n')
        # print('\n')
        # print('============== output =================')
        # print('N: ' + str(N))
        # print(
        # print('Score: ' + str(score))
        # print('\n')
            AC.N = N
            AC.tot_time = tot_time
            AC.score = score
            AC.tot_time = tot_time

            # Set output to updated instance of aircraft
            unknowns['out_aircraft'] = AC
            unknowns['score'] = score
            unknowns['sum_y'] = sum_y
            unknowns['chord_vals'] = AC.wing.chord_vals
            unknowns['htail_chord_vals'] = AC.tail.htail_chord_vals

        # Faulty mision input
        else:
            print('###################################################')
            print('Error: Mission select must be 1 (M-Fly) or 2 (MACH)')
            print('###################################################')

            unknowns['out_aircraft'] = AC

        # Assign number of laps(N), total flight time (tot_time), neutral point(NP),
        # static margin (SM), and objective value to instance of AC



alphas_tail, CLs_tail_flap = getDataXfoil(xfoil_path + '_flap.dat')[0:2]
alphas_tail_noflap, CLs_tail_noflap = getDataXfoil(xfoil_path + '.dat')[0:2]
alphas_tail = [x * np.pi / 180 for x in alphas_tail]
CL_tail_flap = np.poly1d(np.polyfit(alphas_tail, CLs_tail_flap, 2))
CL_tail_noflap = np.poly1d(np.polyfit(alphas_tail_noflap, CLs_tail_noflap, 2))


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


def grossLift(vel, ang, sref_wing, sref_tail, flapped, CL, AC):
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
    gross_F = l_net + getThrust(vel, ang, AC)[1]

    return gross_F, wing_f, tail_f


def calcVelCruise(CL, CD, weight, sref_wing, sref_tail):
    """
    Calculate the cruise performance of a configuration

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

        gross_F, wing_f, tail_f = grossLift(vel, ang, sref_wing, sref_tail, 0, CL, AC)

        F = np.empty(2)

        F[0] = getThrust(vel, ang, AC)[0] - 0.5 * vel ** 2 * Rho * CD(ang) * sref_wing
        F[1] = gross_F - weight

        return F

    # Fsolve to balance lift and weight
    Z = fsolve(sumForces, np.array([20, -10 * np.pi / 180]))

    # Return cruise velocity and angle of attack
    ang = Z[1]
    vel = Z[0]
    return (vel, ang)


def calcClimb(CL, CD, weight, sref_wing, sref_tail):
    """
    Calculate the climb performance of a configuration

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
    vel_climb 	:	float
                    climb velocity
    V_climb 	:	float
                    climb velocity
    horz_Vel 	: 	float
                    horizontal velocity in climb
    AoA_climb 	: 	float
                    angle of attack in climb
    """

    def sumForces(A):
        """
        Get sum of the forces, used for fsolve
        """
        vel = A[0]
        gamma = A[1]
        F = np.empty(2)
        F[0] = getThrust(vel, ang)[0] - 0.5 * vel ** 2 * Rho * CD(ang) * sref_wing - weight * np.sin(gamma)
        F[1] = grossLift(vel, ang, sref_wing, sref_tail, 0, CL)[0] - weight * np.cos(gamma)

        return F

    # Pull out the solution
    sol = np.empty((0, 3), float)
    A = np.zeros((1, 3))
    AoA = []

    # Iterate through angles of attack
    for ang in np.linspace(0 * np.pi / 180, 5 * np.pi / 180, 30):
        AoA.append(ang)
        # print(ang)
        Z = fsolve(sumForces, np.array([15.0, 0 * np.pi / 180]), )

        A[0, 0] = Z[0]
        A[0, 1] = Z[1]
        A[0, 2] = np.sin(Z[1]) * Z[0]

        sol = np.append(sol, A, axis=0)

    # Calculate climb velocity
    V_climb = np.max(sol[:, 2])

    index = np.where(sol[:, 2] == V_climb)[0][0]

    # Calculate AOA and climb velocity
    AoA_climb = AoA[index]
    vel_climb = sol[index, 0]

    # fig, ax1 = plt.subplots()
    # ax1.plot(AoA, sol[:,1], 'b-')
    # ax1.set_xlabel('time (s)')
    # # Make the y-axis label and tick labels match the line color.
    # ax1.set_ylabel('gamma', color='b')
    # for tl in ax1.get_yticklabels():
    #     tl.set_color('b')

    # ax2 = ax1.twinx()
    # ax2.plot(AoA, sol[:,2] , 'r-')
    # ax2.set_ylabel('V_climb', color='r')
    # for tl in ax2.get_yticklabels():
    #     tl.set_color('r')

    # plt.show()

    # Horizontal velocity
    horz_Vel = np.cos(sol[index, 1]) * vel_climb

    return (vel_climb, V_climb, horz_Vel, AoA_climb)


def calcCruise_time(dist, velocity):
    """
    Calculate the cruising time

    Inputs
    -------
    dist 		: 	float
                    distance (m) of runway
    velocity 	:	float
                    cruise velocity (m/s)


    Outputs
    -------
    time 		:	float
                    time that vehicle can cruise
    """

    time = dist / velocity
    return time


def calcTurn_time(bank_angle, velocity, weight, Sref_wing, turn_angle):
    """
    Calculate the turn performance of a configuration

    Inputs
    -------
    bank_angle 	:	float
                    bank angle for turning
    velocity 	: 	float
                    velocity for the turn
    weight 		: 	float
                    weight of vehicle
    sref_wing   :	float
                    wing surface area
    turn_angle  :	float
                    angle to turn (in plane parallel to ground)


    Outputs
    -------
    time 		: 	float
                    time to execute a turn
    """

    # Halve velocity in turn (assumption)
    velocity = velocity / 2
    bank_angle_r = bank_angle * np.pi / 180

    # Get turning radius and CL for turn
    rad = velocity ** 2 / (np.tan(bank_angle) * g)
    CL = (weight * 2) / (np.cos(bank_angle_r) * Sref_wing * Rho * velocity ** 2)

    # Calculate time for the turn maneuver
    time = (rad * 2 * np.pi * (turn_angle / 360)) / velocity

    return time


def runwaySim_small(CL, CD, CM, sref_wing, sref_tail, weight, boom_len, dist_LG, MAC, Iyy, AC):
    """
    Runway simulation to find maximum payload

    Inputs
    -------
    CL 			: 	function
                    CL function from AVL run
    CD 			: 	function
                    CD function from AVL run
    CM 			: 	function
                    CM function from AVL run
    sref_wing   :	float
                    wing surface area
    sref_tail 	: 	float
                    tail surface area
    weight 		: 	float
                    weight of vehicle
    boom_len    :	float
                    length of tailboom
    dist_LG 	: 	float
                    distance between leading edge and CG
    MAC 		: 	float
                    MAC of wing
    Iyy 		:  	float
                    inertia of vehicle


    Outputs
    -------
    sum_y 		:	float
                    net lift at the end of the runway
    dist 		:	float
                    distance needed to takeoff
    ang 	 	: 	float
                    angle of attack at takeoff
    ang_vel 	: 	float
                    angular pitch velocity at takeoff
    time 		: 	float
                    time to takeoff
    """

    # Speify no flaps used for takeoff
    Flapped = 0

    # This should be a design variable eventually
    landingGearHeight = 0.1  # [m]
    # print (landingGearHeight - dist_LG)
    # print landingGearHeight
    max_rot_ang = np.arctan(0.1 / (boom_len - dist_LG))

    # print max_rot_ang*180/np.pi
    # exit()
    # max_rot_ang = 10*np.pi/180.0

    # Declare functions for kinematic varibles (F = ma and M = I*ang_a)

    # Get velocity
    def getVelocity(vel):
        return vel

    # Get acceleration
    def getAcceleration(vel, ang):
        # Calculate the normal force from the runway (weight - lift)
        N = weight - grossLift(vel, ang, sref_wing, sref_tail, Flapped, CL, AC)[0]
        # If N < 0, N = 0 (no normal force)
        if N < 0:
            N = 0

        # Calculate the acceleration as thrust - drag - runway friction
        mass = weight / g
        drag = 0.5 * vel ** 2 * Rho * CD(ang) * sref_wing
        accel = (getThrust(vel, ang, AC)[0] - drag - mu_k * N) / mass

        # Return acceleration
        return accel

    # Get angular velocity
    def getVelocity_ang(ang, ang_vel):
        # Ensure that the aircraft cannot rotate forward
        if (ang <= 0.0 and ang_vel < 0.0):
            return 0
        # Ensure that we cannot exceed the limit for the tail (tail cannot go into ground)
        elif (ang >= max_rot_ang and ang_vel > 0.0):
            return 0
        # Otherwise, a = a_vel
        else:
            return ang_vel

    # Get angular acceleration
    def getAcceleration_ang(vel, ang, ang_vel):
        # Calculate the dynamic pressure
        q = 0.5 * Rho * vel ** 2

        # Calculate the moments due to the tail and the wing
        moment_tail = - q * getTailCL(ang, Flapped) * sref_tail * (boom_len - dist_LG)
        moment_wing = q * (CM(ang) * sref_wing * MAC + CL(ang) * sref_wing * dist_LG)

        # damping_moment =  -np.sign(a_vel)*0.5*Rho*a_vel**2*50*sref_wing

        # Determine the angular acceleration from the moment of inertia, mass, landing gear distribution, and the moments
        mass = weight / g
        ang_accel = 1.0 / (Iyy + (weight / g) * dist_LG ** 2) * (moment_wing + moment_tail)  # +damping_moment

        # TODO - Check the above weight for the landing gear?

        # Ensure that the angular acceleration is 0 so nose doesn't rotate into ground
        if (ang <= 0.0 and ang_accel < 0.0):
            ang_accel = 0

        # Add an opposite angular acceleration "jerk" if the tail bangs into the ground
        elif (ang >= max_rot_ang and ang_vel >= 0.0):
            ang_accel = -30 * ang_vel

            # If flapped, then set the tail into the ground
            if (abs(ang_accel) < 10 ** -27 and Flapped):
                ang_accel = 0

        # Return the resulting angular accelerations
        return ang_accel

    # Main loop
    i = 0

    dist = 0.0
    vel = 0.0
    ang = 0.0
    ang_vel = 0.0

    #accel = getAcceleration(vel, ang)
    #ang_accel = getAcceleration_ang(vel, ang, ang_vel)

    v_stall = np.sqrt(2 * weight / (Rho * sref_wing * 1.7))

    time = 0.0
    dt = 0.05
    time_elap = 0.0

    DT = [dt]

    sum_y = grossLift(vel, ang, sref_wing, sref_tail, Flapped, CL, AC)[0] - weight

    # While loop until no more net lift at the end oft he runway
    # -  Uses a momentum buildup
    while sum_y <= 0.0 and time_elap < 60.0 and dist < 70.0:
        # F = ma yeilds two second order equations => system of 4 first order
        # runge Kutta 4th to approximate kinimatic varibles at time = time + dt
        k1_dist = dt * getVelocity(vel)
        k1_vel = dt * getAcceleration(vel, ang)
        k1_ang = dt * getVelocity_ang(ang, ang_vel)
        k1_ang_vel = dt * getAcceleration_ang(vel, ang, ang_vel)

        k2_dist = dt * getVelocity(vel + 0.5 * k1_vel)
        k2_vel = dt * getAcceleration(vel + 0.5 * k1_vel, ang + 0.5 * k1_ang)
        k2_ang = dt * getVelocity_ang(ang_vel + 0.5 * k1_ang, ang + 0.5 * k1_ang)
        k2_ang_vel = dt * getAcceleration_ang(vel + 0.5 * k1_vel, ang + 0.5 * k1_ang,
                                              ang_vel + 0.5 * k1_ang_vel)

        k3_dist = dt * getVelocity(vel + 0.5 * k2_vel)
        k3_vel = dt * getAcceleration(vel + 0.5 * k2_vel, ang + 0.5 * k2_ang)
        k3_ang = dt * getVelocity_ang(ang_vel + 0.5 * k2_ang, ang + 0.5 * k2_ang)
        k3_ang_vel = dt * getAcceleration_ang(vel + 0.5 * k2_vel, ang + 0.5 * k2_ang,
                                              ang_vel + 0.5 * k2_ang_vel)

        k4_dist = dt * getVelocity(vel + k3_vel)
        k4_vel = dt * getAcceleration(vel + k3_vel, ang + k3_ang)
        k4_ang = dt * getVelocity_ang(ang_vel + k3_ang, ang + k3_ang)
        k4_ang_vel = dt * getAcceleration_ang(vel + k3_vel, ang + k3_ang, ang_vel + k3_ang_vel)

        dist = dist + 1.0 / 6 * (k1_dist + 2 * k2_dist + 2 * k3_dist + k4_dist)
        vel = vel + 1.0 / 6 * (k1_vel + 2 * k2_vel + 2 * k3_vel + k4_vel)
        ang = ang + 1.0 / 6 * (k1_ang + 2 * k2_ang + 2 * k3_ang + k4_ang)
        ang_vel = ang_vel + 1.0 / 6 * (k1_ang_vel + 2 * k2_ang_vel + 2 * k3_ang_vel + k4_ang_vel)
        #accel = getAcceleration(vel, ang)
        #ang_accel = getAcceleration_ang(vel, ang, ang_vel)

        i = i + 1

        if abs(ang_vel) < 10 ** -8 and Flapped:
            ang_vel = 0.0

        if ang > max_rot_ang:
            ang = max_rot_ang
        elif ang < 0.0:
            ang = 0.0

        # Change time step as pilot deflect elevator, safe bet to just use the small timestep
        if (vel < 0.92 * (v_stall + 2.0)) or (
                abs(ang_vel) == 0.0 and (ang < 10 ** -10 or ang >= max_rot_ang)):
            dt = 0.05
        else:
            dt = 0.05
        #DT.append(dt)

        time = time + dt
        time_elap = time

        sum_y = grossLift(vel, ang, sref_wing, sref_tail, Flapped, CL, AC)[0] - weight

        if vel > v_stall + 2.0:
            Flapped = 1

    # # 400 ft runway length in meters
    # runway_len = 137.8

    # if (sum_y > 0.0 and dist[i] <= runway_len):
    # 	takeoff = 1
    # else:
    # 	takeoff = sum_y

    # ============== Ploting ===============

    # plt.figure(1)
    # plt.subplot(611)
    # plt.ylabel('Angle)')
    # plt.xlabel('time')
    # plt.plot(time, ang, 'b')

    # plt.subplot(612)
    # plt.ylabel('ang velocity')
    # plt.xlabel('time')
    # plt.plot(time, ang_vel, 'b')

    # plt.subplot(613)
    # plt.ylabel('ang acceleration')
    # plt.xlabel('time')
    # plt.plot(time, ang_accel, 'b')

    # plt.subplot(614)
    # plt.ylabel('distance')
    # plt.xlabel('time')
    # plt.plot(time, dist, 'b')

    # plt.subplot(615)
    # plt.ylabel('Velocity')
    # plt.xlabel('time')
    # plt.plot(time, vel, 'b')

    # plt.subplot(616)
    # plt.ylabel('Acceleration')
    # plt.xlabel('time')
    # plt.plot(time, accel, 'b')

    # # plt.subplot(717)
    # # plt.ylabel('dt')
    # # plt.xlabel('time')
    # # plt.plot(time, DT, 'b')

    # print('weight: ' + str(weight))
    # print('Sum Y:' + str(sum_y))
    # print('Distance: ' + str(dist[i]))
    # print('vel: ' + str(vel[i]))
    # print('ang: ' + str(ang[i]*180.0/np.pi) + ' max_rot_ang: ' + str(max_rot_ang*180.0/np.pi))
    # print('ang_vel: ' + str(ang_vel[i]))
    # print('time: ' + str(time[i]))
    # print('steps: ' + str(len(time)))
    # print('\n')

    # plt.show()

    return sum_y, dist, vel, ang, ang_vel, time


def num_laps(CL, CD, CM, sref_wing, sref_tail, weight, boom_len, dist_LG, MAC, Iyy):
    """
    Runway simulation to find maximum payload

    Inputs
    -------
    CL 			: 	function
                    CL function from AVL run
    CD 			: 	function
                    CD function from AVL run
    CM 			: 	function
                    CM function from AVL run
    sref_wing   :	float
                    wing surface area
    sref_tail 	: 	float
                    tail surface area
    weight 		: 	float
                    weight of vehicle
    boom_len    :	float
                    length of tailboom
    dist_LG 	: 	float
                    distance between leading edge and CG
    MAC 		: 	float
                    MAC of wing
    Iyy 		:  	float
                    inertia of vehicle


    Outputs
    -------
    N 			: 	int
                    Number of laps (MACH)
    time 		: 	float
                    time to takeoff
    sum_y 		:	float
                    net lift at the end of the runway

    """

    max_time = 4 * 60.0
    N = 0

    # Allowable runway length
    leg_len = 400 * 0.3048

    # No flaps used for runway assistance
    Flapped = 0

    # Get performance for cruise and climb
    cruise_vel, cruise_Ang = calcVelCruise(CL, CD, weight, sref_wing, sref_tail)
    climb_vel, climb_hvel, horz_Vel, AoA_climb = calcClimb(CL, CD, weight, sref_wing, sref_tail)

    # Check if blimp is too slow/cannot climb
    # if climb_vel <= 0.5 or cruise_vel <= 6.0:
    # 	print('Can not Climb/Cruise is slow' + ' V_climb: ' + str(climb_vel) + ' Vel_Cruise: ' + str(cruise_vel))
    # 	return 0, 0.0

    # if climb_vel <= 0.5 or cruise_vel < 7.0 :
    # 	print('Can not Climb' + ' V_climb: ' + str(climb_vel) + '  cruise_vel=' + str(cruise_vel))
    # 	return 0, 0.0

    # print('cruise_vel =' + str(cruise_vel)+  ' cruise_Ang: ' + str(cruise_Ang) + 'climb_vel = ' + str(climb_vel) + ' climb_hvel =' + str(climb_hvel))

    # ==========================  beign takeoff ===========================
    # Find time to takeoff
    sum_y, dist, vel, ang, ang_vel, time = runwaySim_small(CL, CD, CM, sref_wing, sref_tail, weight, boom_len, dist_LG,
                                                           MAC, Iyy)

    # If takeoff not achieved, return a factor of N
    if sum_y < 0:
        print('Failed to Takeoff')
        # print('Takeoff Distance', dist)F
        # print 'sum_y', sum_y

        # return -dist/leg_len, -dist/leg_len, sum_y
        return sum_y, 250, sum_y

    # return 0, 999

    alt_cruise = 15.5

    time_to_alt = alt_cruise / climb_vel

    time += time_to_alt
    dist += climb_hvel * time_to_alt

    # Iterate until distance to takeoff is less than runway distance
    if dist < leg_len:
        time += calcCruise_time(leg_len - dist, cruise_vel)

    time += calcTurn_time(35, cruise_vel, sref_wing, weight, 180)
    time += calcCruise_time(leg_len, cruise_vel)
    time += calcTurn_time(40, cruise_vel, sref_wing, weight, 360)
    time += calcCruise_time(leg_len, cruise_vel)
    time += calcTurn_time(35, cruise_vel, sref_wing, weight, 180)
    time += calcCruise_time(leg_len, cruise_vel)

    while time < max_time:
        N = N + 1

        time += calcCruise_time(leg_len, cruise_vel)
        time += calcTurn_time(35, cruise_vel, sref_wing, weight, 180)
        time += calcCruise_time(leg_len, cruise_vel)
        time += calcTurn_time(40, cruise_vel, sref_wing, weight, 360)
        time += calcCruise_time(leg_len, cruise_vel)
        time += calcTurn_time(35, cruise_vel, sref_wing, weight, 180)
        time += calcCruise_time(leg_len, cruise_vel)

    # print(N)
    return N, time, sum_y
