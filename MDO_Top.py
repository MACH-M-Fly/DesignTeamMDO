# python standard libraries
from __future__ import print_function

# addition python libraries
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import copy

from Post_Process.postProcess import postProcess_Main, Plot

import CreateProblem

import argparse

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
    # Plotting Setup

    fig = plt.figure(figsize=[12,8])

    geo1 = plt.subplot2grid((5, 5), (0, 0), colspan=3, rowspan=4)
    geo2 = plt.subplot2grid((5, 5), (4, 0), colspan=3, rowspan=1)
    geo1.set_xlim([-2, 2])
    geo1.set_ylim([-0.5, 2])
    geo2.set_xlim([-2, 2])
    geo2.set_ylim([-0.5,0.5])

    A = list()
    A.append(plt.subplot2grid((5, 5), ( 0, 3), colspan=2))
    A.append(plt.subplot2grid((5, 5), ( 1, 3), colspan=2))
    A.append(plt.subplot2grid((5, 5), ( 2, 3), colspan=2))
    A.append(plt.subplot2grid((5, 5), ( 3, 3), colspan=2))
    A.append(plt.subplot2grid((5, 5), ( 4, 3), colspan=2))

    for i in range(0,5):
        A[i].set_xlim([0, 0.7])
        A[i].set_ylim([-0.1, 0.2])

    plt.tight_layout()

    # Animation Setup
    FFMpegWriter = animation.writers['ffmpeg']
    metadata = dict(title='MACH MDO', artist='MACH', comment='MDO Animation')
    writer = FFMpegWriter(fps=15, metadata=metadata)

    # Create the plot object
    plot_obj = Plot(geo1, geo2, A, writer, fig)
else:
    fig = None
    writer = None
    plot_obj = None

# ============================================== Create Problem ============================================ #

if __name__ == '__main__':
    # Create the run-once problem
    prob0 = CreateProblem.CreateRunOnceProblem()
    prob0.run()
    in_ac = copy.deepcopy(prob0['createAC.aircraft'])

    # Create the constrained problem, if applicable
    if not args.once:
        prob = CreateProblem.CreateOptimizationProblem(plot_obj=plot_obj)

        # Run the optimization problem
        if args.movie:
            with writer.saving(fig, 'opt_run.mp4', 100):
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
