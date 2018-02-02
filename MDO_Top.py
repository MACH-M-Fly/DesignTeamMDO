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




# ============================================== Create Problem ============================================ #

prob0 = CreateProblem.CreateRunOnceProblem()
prob0.run()
in_ac = copy.deepcopy(prob0['createAC.aircraft'])

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
