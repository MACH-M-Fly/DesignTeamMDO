# python stantdard libraries
from __future__ import print_function
from time import localtime, strftime, time

# addition python libraries
#import numpy as np
#import matplotlib.animation as animation
#import matplotlib.pyplot as plt
import copy

from Post_Process.postProcess import postProcess_Main

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

# prob0 = CreateProblem.CreateRunOnceProblem()
# prob0.run()
# in_ac = copy.deepcopy(prob0['createAC.aircraft'])

prob = CreateProblem.CreateOptimizationProblem()
prob.run()
# Specify the output aircraft (final AC) from the MDO
out_ac = prob['createAC.aircraft']


# Animation settings
# with writer.saving(fig, "OPT_M.mp4", 100):
# 	prob.run()

# lib_plot(prob)



# ============================================== Post-Processing ============================================ #
postProcess_Main(in_ac, out_ac)

# plotGeoFinal(out_ac.wing.Xle.tolist(), out_ac.wing.Yle.tolist(), out_ac.wing.chord_vals.tolist(), \
# 				out_ac.tail.Xle_ht.tolist(), out_ac.tail.Yle_ht.tolist(), out_ac.tail.htail_chord_vals.tolist(), \
# 				out_ac.CG[0], out_ac.NP, out_ac.score, out_ac.mount_len)
