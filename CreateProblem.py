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
from Propulsion.propulsionAnalysis import propulsionAnalysis
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

        # Wingspan (m)
        self.add('b_wing', IndepVarComp('b_wing', 3.2))

        # Quarter Chord Sweep in degrees (cubic)
        # self.add('sweep',IndepVarComp('sweep', np.array([0.0, 0.0, 0.0, 0.0])))

        self.add('chord', IndepVarComp('chord', np.array(
            [0.0, 0.0, 0.0, 0.72])))  # Chord (cubic constants: chord = ax^3+bx^2+c*x+d, x = half-span position)

        # Length of tailboom (m)
        # self.add('boom_len',IndepVarComp('boom_len', 1.60))
        # self.add('b_htail',IndepVarComp('b_htail',1.30))

        # Horiz. Tail Chord (cubic constants: chord = ax^3+bx^2+c*x+d, x = half-span position)
        # self.add('htail_chord',IndepVarComp('htail_chord',np.array([0.0 , 0.0, 0.0,0.325])))
        # self.add('b_vtail',IndepVarComp('b_vtail',0.37))
        # self.add('vtail_chord',IndepVarComp('vtail_chord',np.array([0.0 , 0.0, 0.0,0.325])))

        # Wing dihedral angle (degrees)
        # self.add('dihedral',IndepVarComp('dihedral',1.0))

        # Distance between CG and landing gear (m)
        # self.add('dist_LG',IndepVarComp('dist_LG', 1.0))

        # Wing camber (cubic constants: camber = c_ax^3+c_bx^2+c_c*x + c_d, x = half-span position)
        # self.add('camber',IndepVarComp('camber',np.array([1.0 , 1.0, 1.0,1.0])))

        # Horizontail Tail Span
        # self.add('max_camber',IndepVarComp('max_camber',np.array([1.0 , 1.0, 1.0,1.0])))

        # Tail Root airfoil Cord
        # self.add('thickness',IndepVarComp('thickness',np.array([1.0 , 1.0, 1.0,1.0])))

        # Vertical Tail Span
        # self.add('max_thickness',IndepVarComp('max_thickness',np.array([1.0 , 1.0, 1.0,1.0])))

        # Boom Length
        # self.add('Ainc',IndepVarComp('Ainc',np.array([1.0 , 1.0, 1.0,1.0])))

        # Adding components
        # - First component to add is AC itself
        self.add('my_comp', createAC())
        self.add('calcWeight', calcWeight())
        self.add('aeroAnalysis', aeroAnalysis())
        self.add('structAnalysis', structAnalysis())
        self.add('objPerformance', objPerformance())
        self.add('getBuildTime', getBuildTime())
        self.add('propulsionAnalysis', propulsionAnalysis())

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
        self.connect('getBuildTime.out_aircraft', 'propulsionAnalysis.in_aircraft')


def CreateAddModules(item):
    """
    CreateAddModules creates modules for each and adds them to the problem
    - Additional items can be connected later

    Inputs:
        item - MUST be an OpenMDAO group
    """
    # Create modules
    item.add('my_comp', createAC())
    item.add('calcWeight', calcWeight())
    item.add('aeroAnalysis', aeroAnalysis())
    item.add('structAnalysis', structAnalysis())
    item.add('objPerformance', objPerformance())
    item.add('getBuildTime', getBuildTime())
    item.add('propulsionAnalysis', propulsionAnalysis())

    # Setting up the MDO run by connecting all modules
    item.connect('my_comp.aircraft', 'calcWeight.in_aircraft')
    item.connect('calcWeight.out_aircraft', 'aeroAnalysis.in_aircraft')
    item.connect('aeroAnalysis.out_aircraft', 'structAnalysis.in_aircraft')
    item.connect('structAnalysis.out_aircraft', 'objPerformance.in_aircraft')
    item.connect('objPerformance.out_aircraft', 'getBuildTime.in_aircraft')
    item.connect('getBuildTime.out_aircraft', 'propulsionAnalysis.in_aircraft')


def CreateRoot():
    """
    CreateRoot creates the linked problem set that is used to define a problem
    """
    # Create the root group and add all modules
    root = Group()
    CreateAddModules(root)

    # Return the root
    return root


def CreateRunOnceProblem():
    """
    CreateRunOnceProblem Creates the Initial Run-Once Problem to connect everything together
    - Sets up the problem, but DOES NOT RUN
    """
    # Define the problem
    root = CreateRoot()

    # Setup the problem (but do not run)
    prob0 = Problem(root)
    prob0.setup()

    # Return the problem
    return prob0


def CreateOptimizationProblem():
    """
    CreateOptimizationProblem creates the problem that can be used for optimization
    - Setsup the problem, but DOES NOT RUN
    """
    # ============================================== Create Problem ============================================ #
    prob = Problem()
    prob.root = constrainedMDO()

    # ================================================ Add Driver ============================================== #
    # Gradient-Free Method: Not currently working
    # prob.driver = pyOptSparseDriver()
    # prob.driver.options['optimizer'] = 'ALPSO'
    # prob.driver.opt_settings = {'SwarmSize': 40, 'maxOuterIter': 30,\
    # 				'maxInnerIter': 7, 'minInnerIter' : 7,  'seed': 2.0}

    # Gradient-based method
    prob.driver = ScipyOptimizer()
    prob.driver.options['optimizer'] = 'SLSQP'
    prob.driver.options['tol'] = 1.0e-5
    prob.root.fd_options['force_fd'] = True
    prob.root.fd_options['form'] = 'central'
    prob.root.fd_options['step_size'] = 1.0e-6

    # ===================================== Add design Varibles and Bounds ==================================== #
    # - Uncomment any bounds as you add more design variables
    # - Must also uncomment the param in createAC.py
    prob.driver.add_desvar('b_wing.b_wing', lower=0.25, upper=6.)
    # prob.driver.add_desvar('sweep.sweep',   				lower = np.array([-5., -5., -5., -20.0 ]),\
    # upper = np.array([5., 5., 5., 30.0 ]) )
    prob.driver.add_desvar('chord.chord',
                           lower=np.array([-0.4, -0.4, -0.4, 0.01]),
                           upper=np.array([0.3, 0.3, 0.3, 2.0]))
    # prob.driver.add_desvar('boom_len.boom_len', 			lower = 0.1,  upper = 10)
    # prob.driver.add_desvar('b_htail.b_htail', 				lower = 0.2,  upper = 4.0)
    # prob.driver.add_desvar('htail_chord.htail_chord', 	 	lower = np.array([-0.05, -0.3, -0.4, 0.01]),\
    # upper = np.array([0.1, 0.2, 0.2, 3.0]) )
    # prob.driver.add_desvar('b_vtail.b_vtail', 				lower = 0.2,  upper = 1.2)
    # prob.driver.add_desvar('vtail_chord.vtail_chord', 		lower = np.array([0.25, 0.25, 0.25, 0.25, 0.25 ]),\
    # 													  	upper = np.array([0.45, 0.45, 0.45, 0.45, 0.45 ]) )

    # prob.driver.add_desvar('dihedral.dihedral',   			lower = 1,    upper = 3 )
    # prob.driver.add_desvar('dist_LG.dist_LG', 				lower = 0.05, upper = 0.1)
    # prob.driver.add_desvar('camber.camber',         		lower = np.array([0.10, 0.10, 0.10, 0.10, 0.10 ]),\
    # 										        		upper = np.array([0.15, 0.14, 0.14, 0.14, 0.14 ]))
    # prob.driver.add_desvar('max_camber.max_camber', 		lower = np.array([0.35, 0.35, 0.35, 0.35, 0.35 ]),\
    # 														upper = np.array([0.50, 0.50, 0.50, 0.50, 0.50 ]))
    # prob.driver.add_desvar('thickness.thickness',   		lower = np.array([0.10, 0.10, 0.10, 0.10, 0.10 ]),\
    # 											    		upper = np.array([0.15, 0.15, 0.15, 0.15, 0.15 ]) )
    # prob.driver.add_desvar('max_thickness.max_thickness', 	lower = np.array([0.25, 0.25, 0.25, 0.25, 0.25 ]),\
    # 													  	upper = np.array([0.45, 0.45, 0.45, 0.45, 0.45 ]) )
    # prob.driver.add_desvar('Ainc.Ainc', 	  				lower = 0.15, upper = 0.3)
    # ------------------------ Propulsion System Design Variables---------------------------------------
    # KV
    # Prop Radius
    #

    # ======================================== Add Objective Function and Constraints========================== #
    prob.driver.add_objective('objPerformance.score')
    # prob.driver.add_constraint('objPerformance.sum_y', lower = 0.0)
    prob.driver.add_constraint('objPerformance.chord_vals', lower=np.ones((AC.wing.num_sections, 1)) * 0.1)
    # prob.driver.add_constraint('objPerformance.htail_chord_vals', lower = np.ones((AC.tail.num_sections,1))*0.01  )
    prob.driver.add_constraint('aeroAnalysis.SM', lower=0.05, upper=0.4)
    # prob.driver.add_constraint('structAnalysis.stress_wing', lower = 0.00, upper = 60000.)
    # prob.driver.add_constraint('structAnalysis.stress_tail', lower = 0.00, upper = 60000.)

    # ======================================== Post-Processing ============================================== #
    prob.setup()

