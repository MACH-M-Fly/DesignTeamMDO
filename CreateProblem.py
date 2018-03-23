"""
Creates the design problem for the
"""

# python stantdard libraries
from __future__ import print_function

# addition python libraries
import copy

# open MDAO libraries
from openmdao.api import IndepVarComp, Component, Problem, Group

import numpy as np

from openmdao.api import ScipyOptimizer, ExecComp, SqliteRecorder
# from openmdao.drivers.pyoptsparse_driver import pyOptSparseDriver

# Import self-created components
from CreateAC import createAC
from Weights.calcWeight import calcWeight
from Aerodynamics.aeroAnalysis import aeroAnalysis
from Structures.structAnalysis import structAnalysis
from Performance.objPerformance import objPerformance
from Propulsion.propulsionAnalysis import propulsionAnalysis
from Build_Time.BuildTime import BuildTime
from Post_Process.lib_plot import Plot

# Animation Setup
# FFMpegWriter = animation.writers['ffmpeg']
# metadata = dict(title='MACH MDO', artist='MACH',comment='MDO Animation')
# writer = FFMpegWriter(fps=15, metadata=metadata)


class ConstrainedMDO(Group):
    """
    Return evenly spaced numbers over a specified interval.
    Returns `num` evenly spaced samples, calculated over the
    interval [`start`, `stop`].
    The endpoint of the interval can optionally be excluded.

    :Parameters:
    ----------
    start : scalar
        The starting value of the sequence.
    stop : scalar
        The end value of the sequence, unless `endpoint` is set to False.
        In that case, the sequence consists of all but the last of ``num + 1``
        evenly spaced samples, so that `stop` is excluded.  Note that the step
        size changes when `endpoint` is False.
    num : int, optional
        Number of samples to generate. Default is 50. Must be non-negative.
    endpoint : bool, optional
        If True, `stop` is the last sample. Otherwise, it is not included.
        Default is True.
    retstep : bool, optional
        If True, return (`samples`, `step`), where `step` is the spacing
        between samples.
    dtype : dtype, optional
        The type of the output array.  If `dtype` is not given, infer the data
        type from the other input arguments.
        .. versionadded:: 1.9.0

    :Returns:
    -------
    samples : ndarray
        There are `num` equally spaced samples in the closed interval
        ``[start, stop]`` or the half-open interval ``[start, stop)``
        (depending on whether `endpoint` is True or False).
    step : float, optional
        Only returned if `retstep` is True
        Size of spacing between samples.
    """

    def __init__(self, ac, writer):
        super(ConstrainedMDO, self).__init__()

        # ====================================== Params =============================================== #
        # - Uncomment a param to add it as a design variable
        # - Must also uncomment the parameter in createAC.py

        ac = copy.deepcopy(ac)
        self.ac = ac

        # Mass Payload
        self.add_design_variable('m_payload', ac.m_payload)

        # Wingspan (m)
        self.add_design_variable('b_wing', ac.wing.b_wing)

        # Chord (cubic constants: chord = ax^3+bx^2+c*x+d, x = half-span position)
        self.add_design_variable('chord', ac.wing.chord)

        # Motor parameters
        self.add_design_variable('motor_KV', ac.propulsion.motorKV)
        self.add_design_variable('prop_diam', ac.propulsion.diameter)
        self.add_design_variable('prop_pitch', ac.propulsion.pitch)

        # Length of tailboom (m)
        self.add_design_variable('boom_len', ac.tail.boom_len)

        # Length of tailboom (m)
        # self.add('boom_len',IndepVarComp('boom_len', 1.60))
        # self.add('b_htail',IndepVarComp('b_htail',1.30))

        # Horizontal tail span (m)
        self.add_design_variable('b_htail', ac.tail.b_htail)

        # Horiz. Tail Chord (cubic constants: chord = ax^3+bx^2+c*x+d, x = half-span position)
        self.add_design_variable('htail_chord', ac.tail.htail_chord)

        # Vertical Tail Values
        self.add_design_variable('b_vtail', ac.tail.b_vtail)

        # Vert. Tail Chord (cubic constants: chord = ax^3+bx^2+c*x+d, x = half-span position)
        self.add_design_variable('vtail_chord', ac.tail.vtail_chord)

        # Distance from the CG to the landing gear
        self.add_design_variable('dist_LG', ac.dist_LG)

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
        CreateAddModules(self, ac, connections, writer)

    def add_design_variable(self, var, init_val):
        """Adds an independent design variable to the current model"""
        self.add(var, IndepVarComp(var, init_val))


def CreateAddModules(item, ac, connections=(), writer=None):
    """
    CreateAddModules creates modules for each and adds them to the problem
    - Additional items can be connected later

    Inputs:
        item - MUST be an OpenMDAO group
    """
    # Create modules
    item.add('createAC', createAC(ac))
    item.add('calcWeight', calcWeight(ac))
    item.add('aeroAnalysis', aeroAnalysis(ac))
    item.add('structAnalysis', structAnalysis(ac))
    item.add('objPerformance', objPerformance(ac))
    item.add('getBuildTime', BuildTime(ac))
    item.add('propulsionAnalysis', propulsionAnalysis(ac))

    # Add plot object, if applicable
    if writer is not None:
        item.add('Plot', Plot(ac, writer))

    # Connect different variables, as per the format in constrainedMDO
    for connect in connections:
        item.connect('{0:s}.{0:s}'.format(connect), 'createAC.{:s}'.format(connect))

    # Setting up the MDO run by connecting all modules
    item.connect('createAC.aircraft', 'propulsionAnalysis.in_aircraft')
    item.connect('propulsionAnalysis.out_aircraft', 'calcWeight.in_aircraft')
    item.connect('calcWeight.out_aircraft', 'aeroAnalysis.in_aircraft')
    item.connect('aeroAnalysis.out_aircraft', 'structAnalysis.in_aircraft')
    item.connect('structAnalysis.out_aircraft', 'objPerformance.in_aircraft')
    item.connect('objPerformance.out_aircraft', 'getBuildTime.in_aircraft')

    # Connect movie plotting if applicable
    if writer is not None:
        item.connect('getBuildTime.out_aircraft', 'Plot.in_aircraft')


def CreateRoot(ac):
    """
    CreateRoot creates the linked problem set that is used to define a problem
    """
    # Create the root group and add all modules
    root = Group()
    CreateAddModules(root, ac)

    # Return the root
    return root


def CreateRunOnceProblem(ac):
    """
    CreateRunOnceProblem Creates the Initial Run-Once Problem to connect everything together
    - Sets up the problem, but DOES NOT RUN
    """
    # Define the problem
    root = CreateRoot(ac)

    # Setup the problem (but do not run)
    prob0 = Problem(root)
    prob0.setup()

    # Return the problem
    return prob0


def CreateOptimizationProblem(ac, writer=None):
    """
    CreateOptimizationProblem creates the problem that can be used for optimization
    - Sets up the problem, but DOES NOT RUN
    """
    # ============================================== Create Problem ============================================ #
    prob = Problem()
    prob.root = ConstrainedMDO(ac=ac, writer=writer)

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
                           upper=4.53592/2)

    prob.driver.add_desvar('b_wing.b_wing',
                           lower=1.0,
                           upper=1.2192)

    # prob.driver.add_desvar('sweep.sweep',
    #                        lower = np.array([-5., -5., -5., -20.0 ]),
    #                        upper = np.array([5., 5., 5., 30.0 ]))

    prob.driver.add_desvar('chord.chord',
                           lower=np.array([0.0, 0.0, 0.0, 0.20]),
                           upper=np.array([0.0, 0.0, 0.0, 2.0]))

    prob.driver.add_desvar('boom_len.boom_len',
                           lower=0.5,
                           upper=10.)

    prob.driver.add_desvar('motor_KV.motor_KV',
                           lower=600.,
                           upper=900.)

    prob.driver.add_desvar('prop_diam.prop_diam',
                           lower=9.,
                           upper=12.)

    prob.driver.add_desvar('prop_pitch.prop_pitch',
                           lower=5.,
                           upper=8.)

    prob.driver.add_desvar('b_htail.b_htail',
                           lower=0.2,
                           upper=0.40)

    prob.driver.add_desvar('htail_chord.htail_chord',
                           lower=np.array([0.0, 0.0, 0.0, 0.1]),
                           upper=np.array([0.0, 0.0, 0.0, 3.0]) )

    prob.driver.add_desvar('b_vtail.b_vtail',
                           lower=0.2,
                           upper=1.2)

    prob.driver.add_desvar('vtail_chord.vtail_chord',
                           lower=np.array([0., 0., 0., 0.1 ]),
                           upper=np.array([0., 0., 0., 0.45 ]) )

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
    prob.driver.add_constraint('objPerformance.sum_y', lower=0.0)
    prob.driver.add_constraint('objPerformance.chord_vals', lower=np.ones((ac.wing.num_sections, 1)) * 0.1)
    # prob.driver.add_constraint('objPerformance.htail_chord_vals', lower = np.ones((AC.tail.num_sections,1))*0.01  )
    prob.driver.add_constraint('aeroAnalysis.SM', lower=0.05, upper=0.4)
    # prob.driver.add_constraint('structAnalysis.stress_wing', lower = 0.00, upper = 60000.)
    # prob.driver.add_constraint('structAnalysis.stress_tail', lower = 0.00, upper = 60000.)

    prob.driver.add_constraint('createAC.cVT', lower=0.03)
    prob.driver.add_constraint('createAC.cHT', lower=0.5)

    #prob.driver.add_constraint('objPerformance.takeoff_distance', upper=AC.runway_length)
    prob.driver.add_constraint('calcWeight.ac_mass', lower=0.0, upper=4.53592)

    prob.driver.add_constraint('aeroAnalysis.cruise_AoA', upper=10.)

    # ======================================== Post-Processing ============================================== #
    prob.setup()

    return prob
