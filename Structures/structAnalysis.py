# python stantdard libraries
from __future__ import division

# addition python libraries
import numpy as np
from scipy.integrate import cumtrapz

# open MDAO libraries
from openmdao.api import Component

import time

struct_run_time = []

class structAnalysis(Component):
    """
    OpenMDAO component for structural analysis
    - Wing spar stress and deflection
    - Tail boom stress and deflection

    Inputs
    -------
    Aircraft_Class	:	class
                        in_aircraft class


    Outputs
    -------
    Aircraft_Class	:	class
                        out_aircraft class
    stress_wing 	:	float
                        stress in wing spar
    stress_tail 	:	float
                        stress in tail boom
    """

    def __init__(self):
        super(structAnalysis, self).__init__()

        from Input import AC

        # Input instance of aircraft - before modification
        self.add_param('in_aircraft', val=AC, desc='Input Aircraft Class')

        # Output instance of aircaft - after modification
        self.add_output('out_aircraft', val=AC, desc='Output Aircraft Class')

        # Other outputs to be used in top_level group (e.g. constraints)
        self.add_output('stress_wing', val=0.0, desc='Stress on wing')
        self.add_output('stress_tail', val=0.0, desc='Stress on tail')

    def solve_nonlinear(self, params, unknowns, resids):
        # Used passed in instance of aircraft
        AC = params['in_aircraft']

        start_time = time.time()

        # Modify instance of aircraft - This is where analysis would happen
        AC.sig_max, AC.y_max, AC.sig_max_tail, AC.y_max_tail = runStructAnalysis(AC)

        # Set output to updated instance of aircraft
        unknowns['out_aircraft'] = AC
        unknowns['stress_wing'] = AC.sig_max
        unknowns['stress_tail'] = AC.sig_max_tail

        # Print to screen
        print("Max Stress on Wing Spar = %E Pa" % AC.sig_max)
        print("Max Stress on Tail Boom = %E Pa" % AC.sig_max_tail)

        struct_run_time.append(time.time() - start_time)


# Calculate area moment of inertia for input spar
def calcI(shape, dim):
    # spar is hollow circle
    # dim should be [outer radius, inner radius]
    if shape == 'C':
        c = dim[0]
        I = np.pi / 4 * (dim[0] ** 4 - dim[1] ** 4)

    # spar is hollow rectangle
    # dim should be [outer width, outer height, inner width, inner height]
    elif shape == 'R':
        c = dim[1] / 2
        I = 1. / 12 * (dim[0] * dim[1] ** 3 - dim[2] * dim[3] ** 3)

    # spar is I-beam
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

        A = np.zeros(3)
        y = np.zeros(3)
        Is = np.zeros(3)

        # calculate centroid of I beam
        A[0] = dim[0] * dim[1]
        A[1] = dim[2] * dim[3]
        A[2] = A[0]
        y[0] = dim[1] + dim[1] / 2 + dim[3]
        y[1] = dim[1] + dim[3] / 2
        y[2] = dim[1] / 2
        ybar = np.inner(A, y) / np.sum(A)

        # calculate area moment of inertia
        Is[0] = 1. / 12 * (dim[0] * dim[1] ** 3)
        Is[1] = 1. / 12 * (dim[2] * dim[3] ** 3)
        Is[2] = Is[0]
        d = abs(y - ybar)
        I = np.sum(Is + A * np.power(d, 2))
        c = ybar
    else:
        raise ValueError('Invalid shape provided to structAnalysis.py')

    return c, I


# Calculate distributed forces
def distLoad(x, gross_F, dist_type):
    # elliptically distributed load
    if dist_type == 'elliptical':
        A = x[-1]
        B = 4 * gross_F / (np.pi * A)
        w = B * np.sqrt(1 - (x / A) ** 2)

    # uniformly distributed load
    elif dist_type == 'uniform':
        # TODO - Define mag
        length = x[-1] - x[0]
        mag = gross_F / length
        w = mag * np.ones(len(x))

    # linearly decreasing distributed load
    elif dist_type == 'lin_decrease':
        # TODO - Define mag
        w = gross_F - gross_F / x[-1] * x

    # linearly increasing distributed load
    elif dist_type == 'lin_increase':
        # TODO - Define mag
        w = gross_F / x[-1] * x

    else:
        raise ValueError('Invalid distribution type provided to structAnalysis.py')

    return w


# Calculate cumulative integral values needed for beam theory equations
def getIntegrals(x, w):
    w1 = cumtrapz(w, x, initial=0)
    w2 = cumtrapz(w1, x, initial=0)
    w3 = cumtrapz(w2, x, initial=0)
    w4 = cumtrapz(w3, x, initial=0)

    return w1, w2, w3, w4


# Solves beam theory differential equations
def calcDistribution(x, w, I, E, c):
    """
    Inputs: x - positions along the spar
            w - biggest magnitude for distributed load
            I - area moment of inertia
            E - Young's modulus
            c - distance b/w neutral point and farthest point in the neutral plane
    Outputs:V - shear force distribution
            M - moment distribution
            theta - distribution of slope of beam in degrees
            y - beam deflection distribution
            sigma - stress distribution
    """

    EI = E * I
    w1, w2, w3, w4 = getIntegrals(x, w / EI)

    # Set boundary conditions
    C1 = w1[-1]  # V(L) = 0
    C2 = w2[-1] - C1 * x[-1]  # M(L) = 0
    C3 = w3[0]  # theta(0) = 0
    C4 = w4[0]  # y(0) = 0

    # Get shear distribution
    V = (C1 - w1) * EI

    # Get moment distribution
    M = (C1 * x + C2 - w2) * EI

    # Get slope distribution
    theta = 0.5 * C1 * x ** 2 + C2 * x + C3 - w3
    theta = np.degrees(theta)

    # Get deflection distribution
    y = 1. / 6 * C1 * x ** 3 + 0.5 * C2 * x ** 2 + C3 * x + C4 - w4

    # Get stress distribution
    sigma = -c * M / I

    return V, M, theta, y, sigma


def calcPointLoad(x, L, P, I, E, c):
    M = P * L

    # y = P / (6 * E * I) * (-x ** 3 + 3 * L ** 2 * x - 2 * L ** 3)
    y = P * x ** 2 * (3 * L - x)/(6 * E * I)
    sigma = np.ones_like(x, dtype=float) * -c * M / I

    return M, y, sigma

def calcPointLoadSimplySupported(x, l, L, P, I, E):
    M = P * L

    # y = P / (6 * E * I) * (-x ** 3 + 3 * L ** 2 * x - 2 * L ** 3)
    y = (P * x / (6 * E * I)) * (2 * l * L + 3 * L * x - x**2)

    return y


# Runs main structure analysis
def runStructAnalysis(AC):
    # Calls AVL to get max forces on wing and tail

    # structure analysis on wing
    x = np.linspace(0, AC.wing.b_wing / 2.0, 1001)
    w = distLoad(x, AC.wing_f / 2.0, AC.wing.dist_type)
    c, I = calcI(AC.wing.spar_type, AC.wing.spar_dim)
    V, M, theta, y, sigma = calcDistribution(x, w, I, AC.wing.spar_E, c)

    # structure analysis on tail
    m_empenage = AC.mass_tail + AC.mass_boom / 2.
    x_tail = np.linspace(0, AC.boom_len, 1001)
    c_tail, I_tail = calcI(AC.tail.boom_Type, AC.tail.boom_Dim)
    M_tail, y_tail, sigma_tail = calcPointLoad(x_tail, AC.boom_len, 10. * AC.tail_f + m_empenage * 9.81, I_tail,
                                               AC.tail.boom_E, c_tail)

    # plt.figure(1)
    # plt.plot(x_tail, y_tail, label='deflection of tail'); plt.legend()
    # plt.show()

    # Temporary variables to set the x and y displacements
    AC.temp_x_wing = x
    AC.temp_y_wing = y
    AC.temp_y_tail = y_tail

    return max(abs(sigma)), max(abs(y)), max(abs(sigma_tail)), max(abs(y_tail))
