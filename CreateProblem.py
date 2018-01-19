# python stantdard libraries
from __future__ import print_function
from time import localtime, strftime, time

# addition python libraries
import numpy as np
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import copy

# open MDAO libraries
from openmdao.api import IndepVarComp, Component, Problem, Group
from openmdao.api import ScipyOptimizer, ExecComp, SqliteRecorder
# from openmdao.drivers.pyoptsparse_driver import pyOptSparseDriver

# Import self-created components
from CreateAC import createAC
from Weights.calcWeight import calcWeight
from Aerodynamics.aeroAnalysis import aeroAnalysis
from Structures.structAnalysis import structAnalysis
from Performance.objPerformance import objPerformance
from getBuildTime import getBuildTime
# from Post_Process.postProcess import postProcess
from Input import AC, updateAircraft
# from Post_Process.lib_plot import *
from Post_Process.postProcess import *


# Animation Setup
# FFMpegWriter = animation.writers['ffmpeg']
# metadata = dict(title='MACH MDO', artist='MACH',comment='MDO Animation')
# writer = FFMpegWriter(fps=15, metadata=metadata)

class constrainedMDO(Group):
    """
    OpenMDAO group for Version 1.0 of the constrained MDO for the joint design team
    - Developed by Chris Reynolds in partnership with Joint Design Team MDO group
    - Top level OpenMDAO setup script for constrained MDO
        on the Joint MDO design team project
    """

    def __init__(self):
        super(constrainedMDO, self).__init__()

        # ====================================== Params =============================================== #
        # - Uncomment a param to add it as a design variable
        # - Must also uncomment the param in createAC.py
        self.add('b_wing', IndepVarComp('b_wing', 3.2))  # Wingspan (m)
        # self.add('sweep',IndepVarComp('sweep', np.array([0.0, 0.0, 0.0, 0.0])))		# Quarter Chord Sweep in degrees (cubic)
        self.add('chord', IndepVarComp('chord', np.array(
            [0.0, 0.0, 0.0, 0.72])))  # Chord (cubic constants: chord = ax^3+bx^2+c*x+d, x = half-span position)
        # self.add('boom_len',IndepVarComp('boom_len', 1.60))							# Length of tailboom (m)
        # self.add('b_htail',IndepVarComp('b_htail',1.30))
        # self.add('htail_chord',IndepVarComp('htail_chord',np.array([0.0 , 0.0, 0.0,0.325]))) # Horiz. Tail Chord (cubic constants: chord = ax^3+bx^2+c*x+d, x = half-span position)
        # self.add('b_vtail',IndepVarComp('b_vtail',0.37))
        # self.add('vtail_chord',IndepVarComp('vtail_chord',np.array([0.0 , 0.0, 0.0,0.325])))

        # self.add('dihedral',IndepVarComp('dihedral',1.0))							# Wing dihedral angle (degrees)
        # self.add('dist_LG',IndepVarComp('dist_LG', 1.0))							# Distance between CG and landing gear (m)
        # self.add('camber',IndepVarComp('camber',np.array([1.0 , 1.0, 1.0,1.0])))# Wing camber (cubic constants: camber = c_ax^3+c_bx^2+c_c*x + c_d, x = half-span position)
        # self.add('max_camber',IndepVarComp('max_camber',np.array([1.0 , 1.0, 1.0,1.0])))		# Horizontail Tail Span
        # self.add('thickness',IndepVarComp('thickness',np.array([1.0 , 1.0, 1.0,1.0])))		# Tail Root airfoil Cord
        # self.add('max_thickness',IndepVarComp('max_thickness',np.array([1.0 , 1.0, 1.0,1.0])))	# Vertical Tail Span
        # self.add('Ainc',IndepVarComp('Ainc',np.array([1.0 , 1.0, 1.0,1.0])))	# Boom Length

        # Adding components
        # - First component to add is AC itself
        self.add('my_comp', createAC())
        self.add('calcWeight', calcWeight())
        self.add('aeroAnalysis', aeroAnalysis())
        self.add('structAnalysis', structAnalysis())
        self.add('objPerformance', objPerformance())
        self.add('getBuildTime', getBuildTime())

        # ====================================== Connections ============================================ #
        # - Uncomment a connection to add that param as a design variable
        # - Must also uncomment the param in createAC.py
        self.connect('b_wing.b_wing', 'my_comp.b_wing')
        # self.connect('sweep.sweep', 'my_comp.sweep')
        self.connect('chord.chord', 'my_comp.chord')
        # self.connect('boom_len.boom_len', 'my_comp.boom_len')
        # self.connect('b_htail.b_htail', 'my_comp.b_htail')
        # self.connect('htail_chord.htail_chord', 'my_comp.htail_chord')
        # self.connect('b_vtail.b_vtail', 'my_comp.b_vtail')
        # self.connect('vtail_chord.vtail_chord', 'my_comp.vtail_chord')

        # self.connect('dihedral.dihedral', 'my_comp.dihedral')
        # self.connect('dist_LG.dist_LG', 'my_comp.dist_LG')
        # self.connect('camber.camber', 'my_comp.camber')
        # self.connect('max_camber.max_camber', 'my_comp.max_camber')
        # self.connect('thickness.thickness', 'my_comp.thickness')
        # self.connect('max_thickness.max_thickness', 'my_comp.max_thickness')
        # self.connect('Ainc.Ainc', 'my_comp.Ainc')

        # Connections for components
        # - This is where you can connect additional components
        self.connect('my_comp.aircraft', 'calcWeight.in_aircraft')
        self.connect('calcWeight.out_aircraft', 'aeroAnalysis.in_aircraft')
        self.connect('aeroAnalysis.out_aircraft', 'structAnalysis.in_aircraft')
        self.connect('structAnalysis.out_aircraft', 'objPerformance.in_aircraft')
        self.connect('objPerformance.out_aircraft', 'getBuildTime.in_aircraft')


def CreateProb0():
    """
    CreateProb0 Creates the Initial Run-Once Problem to connect everything together
    """