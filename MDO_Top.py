# python standard libraries
from __future__ import print_function

# addition python libraries
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import copy

from Post_Process.postProcess import postProcess_Main, Plot

import CreateProblem

import argparse

from Input import AC

# ================================= Interperate cmd line options =================================
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--movie',
                    action='store_true',
                    help='toggle movie generation')
parser.add_argument('--once',
                    action='store_true',
                    help='only run the optimization once')
args = parser.parse_args()


# ==================================== Initailize plots for animation ===================================== #
if args.movie:
    # Animation Setup
    FFMpegWriter = animation.writers['ffmpeg']
    metadata = dict(title='MACH MDO', artist='MACH', comment='MDO Animation')
    writer = FFMpegWriter(fps=15, metadata=metadata)
else:
    writer = None

# ============================================== Create Problem ============================================ #

if __name__ == '__main__':
    # Create the run-once problem
    prob0 = CreateProblem.CreateRunOnceProblem(AC)
    prob0.run()
    in_ac = copy.deepcopy(prob0['createAC.aircraft'])

    # Create the constrained problem, if applicable
    if not args.once:
        prob = CreateProblem.CreateOptimizationProblem(ac=AC, writer=writer)

        # Run the optimization problem, adding a movie if applicable
        if args.movie:
            with writer.saving(prob.driver.root.Plot.fig, 'opt_run.mp4', 100):
                prob.run()
        else:
            prob.run()

        # Specify the output aircraft (final AC) from the MDO
        out_ac = prob['createAC.aircraft']

        # Extract the createAC object from the problem root
        createAC = prob.root.createAC
    else:
        out_ac = in_ac
        in_ac = None

    # Post-Process Results
    postProcess_Main(in_ac, out_ac)
