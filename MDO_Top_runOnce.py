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
from Post_Process.lib_plot import *
from Post_Process.postProcess import *


# Animation Setup
# FFMpegWriter = animation.writers['ffmpeg']
# metadata = dict(title='MACH MDO', artist='MACH',comment='MDO Animation') 
# writer = FFMpegWriter(fps=15, metadata=metadata)

class constrainedMDO(Group):
    """
    WARNING: Only used for testing to "run once", i.e. no optimization
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
        # self.add('dihedral',IndepVarComp('dihedral',1.0))						# Wing dihedral angle (degrees)
        self.add('sweep',
                 IndepVarComp('sweep', np.array([0.0, 0.0, 0.0, 0.0])))  # Quarter Chord Sweep in degrees (cubic)
        self.add('chord', IndepVarComp('chord', np.array(
            [0.0, 0.0, 0.0, 0.72])))  # Chord (cubic constants: chord = ax^3+bx^2+c*x+d, x = half-span position)
        # self.add('dist_LG',IndepVarComp('dist_LG', 1.0))						# Distance between CG and landing gear (m)
        self.add('boom_len', IndepVarComp('boom_len', 1.60))  # Length of tailboom (m)
        # self.add('camber',IndepVarComp('camber',np.array([1.0 , 1.0, 1.0,1.0])))# Wing camber (cubic constants: camber = c_ax^3+c_bx^2+c_c*x + c_d, x = half-span position)
        # self.add('max_camber',IndepVarComp('max_camber',np.array([1.0 , 1.0, 1.0,1.0])))		# Horizontail Tail Span
        # self.add('thickness',IndepVarComp('thickness',np.array([1.0 , 1.0, 1.0,1.0])))		# Tail Root airfoil Cord
        # self.add('max_thickness',IndepVarComp('max_thickness',np.array([1.0 , 1.0, 1.0,1.0])))	# Vertical Tail Span
        # self.add('Ainc',IndepVarComp('Ainc',np.array([1.0 , 1.0, 1.0,1.0])))	# Boom Length
        self.add('htail_chord', IndepVarComp('htail_chord', np.array([0.0, 0.0, 0.0,
                                                                      0.325])))  # Horiz. Tail Chord (cubic constants: chord = ax^3+bx^2+c*x+d, x = half-span position)
        self.add('vtail_chord', IndepVarComp('vtail_chord', np.array([0.0, 0.0, 0.0, 0.325])))
        self.add('b_htail', IndepVarComp('b_htail', 1.30))
        self.add('b_vtail', IndepVarComp('b_vtail', 0.37))

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
        # self.connect('b_wing.b_wing',['createAC.b_wing'])
        # self.connect('dihedral.dihedral',['createAC.dihedral'])
        # self.connect('sweep.sweep',['createAC.sweep'])
        # self.connect('chord.chord',['createAC.chord'])
        # self.connect('dist_LG.dist_LG',['createAC.dist_LG'])
        # self.connect('boom_len.boom_len',['createAC.boom_len'])
        # self.connect('camber.camber',['createAC.camber'])
        # self.connect('max_camber.max_camber',['createAC.max_camber'])
        # self.connect('thickness.thickness',['createAC.thickness'])
        # self.connect('max_thickness.max_thickness',['createAC.max_thickness'])
        # self.connect('Ainc.Ainc',['createAC.Ainc'])
        # self.connect('c_r_ht.c_r_ht',['createAC.c_r_ht'])
        # self.connect('c_r_vt.c_r_vt',['createAC.c_r_vt'])
        # self.connect('b_htail.b_htail','my_comp.b_htail')
        # self.connect('b_vtail.b_vtail','my_comp.b_vtail')

        self.connect('chord.chord', 'my_comp.chord')
        self.connect('sweep.sweep', 'my_comp.sweep')
        self.connect('boom_len.boom_len', ['my_comp.boom_len'])
        self.connect('htail_chord.htail_chord', 'my_comp.htail_chord')
        self.connect('vtail_chord.vtail_chord', 'my_comp.vtail_chord')
        self.connect('b_wing.b_wing', 'my_comp.b_wing')
        self.connect('b_htail.b_htail', 'my_comp.b_htail')
        self.connect('b_vtail.b_vtail', 'my_comp.b_vtail')

        # Connections for components
        # - This is where you can connect additional components
        self.connect('my_comp.aircraft', 'calcWeight.in_aircraft')
        self.connect('calcWeight.out_aircraft', 'aeroAnalysis.in_aircraft')
        # self.connect('my_comp.aircraft','aeroAnalysis.in_aircraft')
        self.connect('aeroAnalysis.out_aircraft', 'structAnalysis.in_aircraft')
        self.connect('structAnalysis.out_aircraft', 'objPerformance.in_aircraft')
        self.connect('objPerformance.out_aircraft', 'getBuildTime.in_aircraft')
    # self.connect('objPerformance.out_aircraft','Plot.in_aircraft')


# ==================================== Initailize plots for animation ===================================== #

# fig = plt.figure(figsize=[12,8])

# geo1 = plt.subplot2grid((5, 5), (0, 0), colspan=3, rowspan=4)
# geo2 = plt.subplot2grid((5, 5), (4, 0), colspan=3, rowspan=1)
# geo1.set_xlim([-2, 2])
# geo1.set_ylim([-0.5, 2])
# geo2.set_xlim([-2, 2])
# geo2.set_ylim([-0.5,0.5])

# A = []
# A.append(plt.subplot2grid((5, 5), ( 0, 3), colspan=2))
# A.append(plt.subplot2grid((5, 5), ( 1, 3), colspan=2))
# A.append(plt.subplot2grid((5, 5), ( 2, 3), colspan=2))
# A.append(plt.subplot2grid((5, 5), ( 3, 3), colspan=2))
# A.append(plt.subplot2grid((5, 5), ( 4, 3), colspan=2))
# for i in range(0,5):
# 	A[i].set_xlim([0, 0.7])
# 	A[i].set_ylim([-0.1, 0.2])

# plt.tight_layout()

# ============================================== Create Problem ============================================ #
# prob = Problem()
# prob.root = constrainedMDO()


# # ================================================ Add Driver ============================================== #
# prob.driver = pyOptSparseDriver()
# prob.driver.options['optimizer'] = 'ALPSO'
# prob.driver.opt_settings = {'SwarmSize': 40, 'maxOuterIter': 30,\
# 				'maxInnerIter': 7, 'minInnerIter' : 7,  'seed': 2.0}

# prob.driver = ScipyOptimizer()
# prob.driver.options['optimizer'] = 'SLSQP'
# prob.driver.options['tol'] = 1.0e-4
# prob.root.fd_options['force_fd'] = True	
# prob.root.fd_options['form'] = 'central'
# prob.root.fd_options['step_size'] = 1.0e-6

# prob.driver = ScipyOptimizer()
# prob.driver.options['optimizer'] = 'SNOPT'
# prob.driver.options['tol'] = 1.0e-2
# prob.root.fd_options['force_fd'] = True	
# prob.root.fd_options['form'] = 'central'
# prob.root.fd_options['step_size'] = 1.0e-4


# ===================================== Add design Varibles and Bounds ==================================== #
# prob.driver.add_desvar('b_wing.b_wing',   				lower = 1,    upper = 3 )
# prob.driver.add_desvar('dihedral.dihedral',   			lower = 1,    upper = 3 )
# prob.driver.add_desvar('sweep.sweep',   				lower = np.array([0.25, 0.25, 0.25, 0.25, 0.25 ]),\
# 													  	upper = np.array([0.45, 0.45, 0.45, 0.45, 0.45 ]) )
# prob.driver.add_desvar('chord.chord',        			lower = np.array([0.0, 0.0, 0.0, 0.0, 0.0 ]),\
# 													  	upper = np.array([15.0, 15.0, 15.0, 15.0, 15.0 ]) )
# prob.driver.add_desvar('t2.t2',           				lower = 0.6,  upper = 1.0)
# prob.driver.add_desvar('t3.t3', 		  				lower = 0.6,  upper = 1.0)
# prob.driver.add_desvar('t4.t4',			  				lower = 0.6,  upper = 1.0)
# prob.driver.add_desvar('t5.t5',			  				lower = 0.6,  upper = 1.0)
# prob.driver.add_desvar('dist_LG.dist_LG', 				lower = 0.05, upper = 0.1)
# prob.driver.add_desvar('boom_len.boom_len', 			lower = 0.5,  upper = 1.5)
# prob.driver.add_desvar('camber.camber',         		lower = np.array([0.10, 0.10, 0.10, 0.10, 0.10 ]),\
# 										        		upper = np.array([0.15, 0.14, 0.14, 0.14, 0.14 ]))
# prob.driver.add_desvar('max_camber.max_camber', 		lower = np.array([0.35, 0.35, 0.35, 0.35, 0.35 ]),\
# 														upper = np.array([0.50, 0.50, 0.50, 0.50, 0.50 ]))
# prob.driver.add_desvar('thickness.thickness',   		lower = np.array([0.10, 0.10, 0.10, 0.10, 0.10 ]),\
# 											    		upper = np.array([0.15, 0.15, 0.15, 0.15, 0.15 ]) )
# prob.driver.add_desvar('max_thickness.max_thickness', 	lower = np.array([0.25, 0.25, 0.25, 0.25, 0.25 ]),\
# 													  	upper = np.array([0.45, 0.45, 0.45, 0.45, 0.45 ]) )
# prob.driver.add_desvar('Ainc.Ainc', 	  				lower = 0.15, upper = 0.3)
# prob.driver.add_desvar('c_r_ht.c_r_ht', 	  			lower = np.array([0.25, 0.25, 0.25, 0.25, 0.25 ]),\
# 													  	upper = np.array([0.45, 0.45, 0.45, 0.45, 0.45 ]) )
# prob.driver.add_desvar('c_r_vt.c_r_vt', 	  			lower = np.array([0.25, 0.25, 0.25, 0.25, 0.25 ]),\
# 													  	upper = np.array([0.45, 0.45, 0.45, 0.45, 0.45 ]) )
# prob.driver.add_desvar('b_htail.b_htail', 				lower = 0.6,  upper = 1.2)
# prob.driver.add_desvar('b_vtail.b_vtail', 				lower = 0.6,  upper = 1.2)


# ======================================== Post-Processing ============================================== #
# Setting up the first iteration run, where nothing is modified
root = Group()
# root.add('indep_var', IndepVarComp('chord', np.array([0.0, 0.0, 0.0, 0.15])))
# root.add('indep_var2', IndepVarComp('b_wing', 2.0))
root.add('my_comp', createAC())
root.add('calcWeight', calcWeight())
root.add('aeroAnalysis', aeroAnalysis())
root.add('structAnalysis', structAnalysis())
root.add('objPerformance', objPerformance())
root.add('getBuildTime', getBuildTime())
# root.add('Plot', Plot(geo1, geo2, A, writer, fig))


# root.connect('indep_var.chord', 'my_comp.chord')
# root.connect('indep_var2.b_wing', 'my_comp.b_wing')
root.connect('my_comp.aircraft', 'calcWeight.in_aircraft')
root.connect('calcWeight.out_aircraft', 'aeroAnalysis.in_aircraft')
# root.connect('my_comp.aircraft','aeroAnalysis.in_aircraft')
root.connect('aeroAnalysis.out_aircraft', 'structAnalysis.in_aircraft')
root.connect('structAnalysis.out_aircraft', 'objPerformance.in_aircraft')
root.connect('objPerformance.out_aircraft', 'getBuildTime.in_aircraft')
# root.connect('objPerformance.out_aircraft','Plot.in_aircraft')

prob = Problem(root)
prob.setup()
in_ac = copy.deepcopy(prob['my_comp.aircraft'])

prob.run()

# with writer.saving(fig, "OPT_#.mp4", 100):
# 	prob.run()

# lib_plot(prob)

out_ac = prob['my_comp.aircraft']
# print('================  Final Results ===================')
# print(out_ac.wing.chord_vals)
# print('Wing Span', out_ac.wing.b_wing)
# # print("CL", out_ac.CL)
# # print("CD", out_ac.CD)
# # print("CM", out_ac.CM)
# print("CL", out_ac.CL(out_ac.ang))
# print("CD", out_ac.CD(out_ac.ang))
# print("NP", out_ac.NP)
# print("SM", out_ac.SM)

# print('\n########    Performance Metrics  #######')
# print("Number of Laps", out_ac.N)

# print('\n########      Weight Breakdown   #######')
# print('Aircraft Mass %f kg' % out_ac.mass)
# print('Wing Mass %f kg' % out_ac.mass_wing)
# print('Tail Mass %f kg' % out_ac.mass_tail)

# print('\n########    Structural Analysis  #######')
# print('Gross Lift %f N (%f kg)' % (out_ac.gross_F, out_ac.gross_F/9.81))
# print("Wing Max Stress %.3f MPa" % (out_ac.sig_max/1.E6))
# print("Wing Max Deflection %.3f mm" % (out_ac.y_max*1.E3))
# print("Tail Max Stress %.3f MPa" % (out_ac.sig_max_tail/1.E6))
# print("Tail Max Deflection %.3f mm" % (out_ac.y_max_tail*1.E3))
# print("CG", out_ac.CG)

# print("\n#####\n")

# Output final geometry of aircraft
in_ac.score = 10
in_ac.CG = ([0.1, 0, 0])
in_ac.NP = 0.1
in_ac.mount_len = -0.15
in_ac.total_hours = 325
in_ac.N = 6
in_ac.tot_time = 35
out_ac.score = 12
out_ac.wing.Yle[-1] = 2.
out_ac.total_hours = 35

postProcess_Main(in_ac, out_ac)

# plotGeoFinal(out_ac.wing.Xle.tolist(), out_ac.wing.Yle.tolist(), out_ac.wing.chord_vals.tolist(), \
# 				out_ac.tail.Xle_ht.tolist(), out_ac.tail.Yle_ht.tolist(), out_ac.tail.htail_chord_vals.tolist(), \
# 				out_ac.CG[0], out_ac.NP, 5., out_ac.mount_len)


# Inputs:
#     	Xle: Wing leading edge at each section (x coord.)
#		Yle: Wing leading edge at each section (y coord.)
#  		C: Chord at each section
#   	Xle_ht: Tail leading edge at each section (x coord.)       
#   	Yle_ht: Tail leading edge at each section (y coord.)  
#  		C_t: Tail chord at each section  
#		x_cg: CG position
#		NP: Neutral point position
#		Score: Objective function score
