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
from Propulsion.propulsionAnalysis import propulsionAnalysis
# from Post_Process.postProcess import postProcess
from Input import AC, updateAircraft
# from Post_Process.lib_plot import *
from Post_Process.postProcess import *

import CreateProblem


# Animation Setup
# FFMpegWriter = animation.writers['ffmpeg']
# metadata = dict(title='MACH MDO', artist='MACH',comment='MDO Animation') 
# writer = FFMpegWriter(fps=15, metadata=metadata)


# ==================================== Initailize plots for animation ===================================== #
# - Can only use on a non-CAEN linux

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

prob0 = CreateProblem.CreateRunOnceProblem()
prob0.run()
in_ac = copy.deepcopy(prob0['my_comp.aircraft'])

prob = CreateProblem.CreateOptimizationProblem()
prob.run()

# Animation settings
# with writer.saving(fig, "OPT_#.mp4", 100):
# 	prob.run()

# lib_plot(prob)

# Specify the output aircraft (final AC) from the MDO
out_ac = prob['my_comp.aircraft']

# ============================================== Post-Processing ============================================ #
postProcess_Main(in_ac, out_ac)

# plotGeoFinal(out_ac.wing.Xle.tolist(), out_ac.wing.Yle.tolist(), out_ac.wing.chord_vals.tolist(), \
# 				out_ac.tail.Xle_ht.tolist(), out_ac.tail.Yle_ht.tolist(), out_ac.tail.htail_chord_vals.tolist(), \
# 				out_ac.CG[0], out_ac.NP, out_ac.score, out_ac.mount_len)
