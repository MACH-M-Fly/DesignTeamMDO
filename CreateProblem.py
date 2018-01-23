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
# from Post_Process.lib_plot import *
from Post_Process.postProcess import *

from Input import AC

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

        ac = AC

        # Mass Payload
        self.add_design_variable('m_payload', AC.m_payload)

        # Wingspan (m)
        self.add_design_variable('b_wing', AC.wing.b_wing)

        # Chord (cubic constants: chord = ax^3+bx^2+c*x+d, x = half-span position)
        self.add_design_variable('chord', AC.wing.chord)

        # Motor parameters
        self.add_design_variable('motor_KV', AC.propulsion.motorKV)
        self.add_design_variable('prop_diam', AC.propulsion.diameter)
        self.add_design_variable('prop_pitch', AC.propulsion.pitch)

        # Length of tailboom (m)
        self.add_design_variable('boom_len', AC.tail.boom_len)

        # Length of tailboom (m)
        # self.add('boom_len',IndepVarComp('boom_len', 1.60))
        # self.add('b_htail',IndepVarComp('b_htail',1.30))

        # Horizontal tail span (m)
        self.add_design_variable('b_htail', AC.tail.b_htail)

        # Horiz. Tail Chord (cubic constants: chord = ax^3+bx^2+c*x+d, x = half-span position)
        self.add_design_variable('htail_chord', AC.tail.htail_chord)

        # Vertical Tail Values
        self.add_design_variable('b_vtail', AC.tail.b_vtail)

        # Vert. Tail Chord (cubic constants: chord = ax^3+bx^2+c*x+d, x = half-span position)
        self.add_design_variable('vtail_chord', AC.tail.vtail_chord)

        # Distance from the CG to the landing gear
        self.add_design_variable('dist_LG', AC.dist_LG)

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

        # Ainc
        # self.add('Ainc',IndepVarComp('Ainc',np.array([1.0 , 1.0, 1.0,1.0])))

        # Adding components
        connections = ('chord', 'b_wing', 'motor_KV', 'prop_diam',
                       'prop_pitch', 'boom_len', 'b_htail', 'htail_chord',
                       'b_vtail', 'vtail_chord', 'm_payload', 'dist_LG')
        CreateAddModules(self, connections)

    def add_design_variable(self, var, init_val):
        """Adds an independent design variable to the current model"""
        self.add(var, IndepVarComp(var, init_val))


def CreateAddModules(item, connections=()):
    """
    CreateAddModules creates modules for each and adds them to the problem
    - Additional items can be connected later

    Inputs:
        item - MUST be an OpenMDAO group
    """
    # Create modules
    item.add('createAC', createAC())
    item.add('calcWeight', calcWeight())
    item.add('aeroAnalysis', aeroAnalysis())
    item.add('structAnalysis', structAnalysis())
    item.add('objPerformance', objPerformance())
    item.add('getBuildTime', getBuildTime())
    item.add('propulsionAnalysis', propulsionAnalysis())

    # Connect different variables, as per the format in constrainedMDO
    for connect in connections:
        item.connect('{0:s}.{0:s}'.format(connect), 'createAC.{:s}'.format(connect))

    # Setting up the MDO run by connecting all modules
    item.connect('createAC.aircraft', 'calcWeight.in_aircraft')
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
    prob.root.deriv_options['type'] = 'fd'
    prob.root.deriv_options['form'] = 'central'
    prob.root.deriv_options['step_size'] = 1.0e-3

    # ===================================== Add design Varibles and Bounds ==================================== #
    # - Uncomment any bounds as you add more design variables
    # - Must also uncomment the param in createAC.py

    prob.driver.add_desvar('m_payload.m_payload',
                           lower=0.0,
                           upper=4.53592)

    prob.driver.add_desvar('b_wing.b_wing',
                           lower=0.25,
                           upper=1.2192)

    # prob.driver.add_desvar('sweep.sweep',
    #                        lower = np.array([-5., -5., -5., -20.0 ]),
    #                        upper = np.array([5., 5., 5., 30.0 ]))

    prob.driver.add_desvar('chord.chord',
                           lower=np.array([-0.4, -0.4, -0.4, 0.01]),
                           upper=np.array([0.3, 0.3, 0.3, 2.0]))

    prob.driver.add_desvar('boom_len.boom_len',
                           lower=0.1,
                           upper=10.)

    prob.driver.add_desvar('motor_KV.motor_KV',
                           lower=300.,
                           upper=900.)

    prob.driver.add_desvar('prop_diam.prop_diam',
                           lower=8.,
                           upper=11.)

    prob.driver.add_desvar('prop_pitch.prop_pitch',
                           lower=5.,
                           upper=9.)

    prob.driver.add_desvar('b_htail.b_htail',
                           lower=0.2,
                           upper=4.0)

    prob.driver.add_desvar('htail_chord.htail_chord',
                           lower=np.array([-0.05, -0.3, -0.4, 0.01]),
                           upper=np.array([0.1, 0.2, 0.2, 3.0]) )

    prob.driver.add_desvar('b_vtail.b_vtail',
                           lower=0.2,
                           upper=1.2)

    prob.driver.add_desvar('vtail_chord.vtail_chord',
                           lower=np.array([0.25, 0.25, 0.25, 0.25, 0.25 ]),
                           upper=np.array([0.45, 0.45, 0.45, 0.45, 0.45 ]) )

    prob.driver.add_desvar('dist_LG.dist_LG',
                           lower=0.0,
                           upper=3.0)

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
    prob.driver.add_constraint('objPerformance.sum_y', lower = 0.0)
    prob.driver.add_constraint('objPerformance.chord_vals', lower=np.ones((AC.wing.num_sections, 1)) * 0.1)
    # prob.driver.add_constraint('objPerformance.htail_chord_vals', lower = np.ones((AC.tail.num_sections,1))*0.01  )
    prob.driver.add_constraint('aeroAnalysis.SM', lower=0.05, upper=0.4)
    # prob.driver.add_constraint('structAnalysis.stress_wing', lower = 0.00, upper = 60000.)
    # prob.driver.add_constraint('structAnalysis.stress_tail', lower = 0.00, upper = 60000.)

    prob.driver.add_constraint('objPerformance.takeoff_distance', upper=AC.runway_length)

    prob.driver.add_constraint('calcWeight.ac_mass', lower=0.0, upper=4.53592)

    # ======================================== Post-Processing ============================================== #
    prob.setup()

    return prob

