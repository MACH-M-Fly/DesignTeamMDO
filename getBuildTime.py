# python stantdard libraries
from __future__ import division
from time import localtime, strftime, time

# addition python libraries
import numpy as np
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import math

# open MDAO libraries
from openmdao.api import IndepVarComp, Component, Problem, Group
from openmdao.api import ScipyOptimizer, ExecComp, SqliteRecorder
# from openmdao.drivers.pyoptsparse_driver import pyOptSparseDriver
from openmdao.drivers.latinhypercube_driver import OptimizedLatinHypercubeDriver
from scipy.optimize import *
# from sympy import Symbol, nsolve

# Import self-created components
from Input import AC


class getBuildTime(Component):
    """
    OpenMDAO component for estimating build time
    - Based on historical values for both teamse

    Inputs
    -------
    Aircraft_Class  :   class
                        in_aircraft class


    Outputs
    -------
    Aircraft_Class  :   class
                        out_aircraft class
    build_time 		:	float
                        Estimated build time in people hours

    """

    def __init__(self):
        super(getBuildTime, self).__init__()

        # Input instance of aircraft - before modification
        self.add_param('in_aircraft', val=AC, desc='Input Aircraft Class')

        # Output instance of aircaft - after modification
        self.add_output('out_aircraft', val=AC, desc='Output Aircraft Class')

    def solve_nonlinear(self, params, unknowns, resids):
        # Used passed in instance of aircraft
        AC = params['in_aircraft']

        # Wing Parameters
        numRibs = AC.num_ribs
        wingspanMeters = AC.wing.b_wing
        avgChordMeters = AC.wing.MAC
        isCarbonFiber = True

        # Airfoil Parameters
        airfoilTC = 0.16

        # Taper Parameters
        taperRatio = 0.61  # Starting parameter for the wing taper ratio
        taperStart = 0.47  # Starting parameter for the wing taper start ratio

        # Tail Parameters
        numRibs_HSt = 16

        width_HSt = 1.23  # Width of Horizontal Stabilizer
        chord_HSt = 0.325

        numRibs_VSt = 5
        height_VSt = 0.32
        chord_VSt = 0.325

        # Constants for defining wing build hours
        hoursPerRib = 4
        airfoilTC_Threshold = 0.2

        hoursPerSparMeter = 5
        hoursPerTeMeter = 16
        hoursPerLeMeter = 16

        hoursPerCarbonCureCycle = 16
        hoursPerCarbonCyclePeron = 3
        personPerLeMeter = 1.6

        hoursPerMonokoteMeter2 = 5

        # Constants for definining tail build hours
        hoursPerVertSurfaceMeter2 = 5 ** 2
        hoursPerHorzSurfaceMeter2 = 5 ** 2

        # Number of people will vary
        # 16 hours cure + 3 for prep, 3 * Number of people
        # Spar Constant

        if isCarbonFiber:
            hoursPerLeMeter = 3
            hoursPerSparMeter = 1

        # Constants for defining fuselage build hours

        # My Variables (REMOVABLE)

        # Estimator Function to get Wing Build Hours
        def getWingBuildHours():
            # Estimate roughly 1/2 hour per rib of the aircraft
            airfoilHours = numRibs * hoursPerRib

            # Increase the time rquried for creating an airfoil if the
            # thickness is less than a certian threshold
            #
            #  -> Should look into not straight multiplication, but perhaps a log?
            if airfoilTC < airfoilTC_Threshold:
                airfoilHours = airfoilHours * airfoilTC_Threshold / airfoilTC

            # Get an estimate for the spar hours
            #  -> assumes constants spar, no taper/bend
            sparHours = wingspanMeters * hoursPerSparMeter

            # Trailing Edge hours
            teHours = wingspanMeters * hoursPerTeMeter

            # Leading Edge hours
            if isCarbonFiber:
                leHours = hoursPerCarbonCureCycle + hoursPerCarbonCyclePeron * math.ceil(
                    personPerLeMeter * wingspanMeters)
            else:
                leHours = wingspanMeters * hoursPerLeMeter

            # -> Need something to delineate taper...

            # Monokote Hours for estimated wetted area of the wing
            monokoteHours = 2 * wingspanMeters * avgChordMeters * hoursPerMonokoteMeter2

            # Return the sum of all hours calculated above
            return airfoilHours + sparHours + teHours + leHours + monokoteHours

        # Estimator Function to get Fuselage Build Hours
        def getFuselageBuildHours():
            return 50  # Currently just an estimated constant 50 hours

        # Estimator Function to get Tail Build Hours
        def getTailBuildHours():
            vsArea = height_VSt * chord_VSt
            hzArea = width_HSt * chord_HSt

            leteHours = (hoursPerLeMeter + hoursPerTeMeter) * (height_VSt + width_HSt)

            return leteHours + vsArea * hoursPerVertSurfaceMeter2 * 2 + hzArea * hoursPerHorzSurfaceMeter2 * 2

        def getAircraftBuildHours():
            totalHours = getWingBuildHours()
            totalHours = totalHours + getFuselageBuildHours()
            totalHours = totalHours + getTailBuildHours()
            return totalHours

        # Run build time estimation
        AC.total_hours = getAircraftBuildHours()
        print("Current Iteration Total Hours", AC.total_hours)

        # Set output to updated instance of aircraft
        unknowns['out_aircraft'] = AC
