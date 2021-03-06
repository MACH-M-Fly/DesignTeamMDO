from __future__ import division

#from scipy.optimize import *
#import numpy as np
import matplotlib.pyplot as plt
#import matplotlib.animation as animation
# plt.rcParams['animation.ffmpeg_path'] = './.local/lib/python2.7/site-packages'
from mpl_toolkits.axes_grid.anchored_artists import AnchoredText

import numpy as np
#import os
import string

from openmdao.api import Component


class Plot(Component):
    """
    OpenMDAO component for post-processing
        * Movie writing DOES NOT work on CAEN linux
        * Plots aircraft:
            * During each iteration and at the end (plotGeoFinal)
            * Plots wing (blue) and tail (red)
            * Plots CG (black) and NP (light blue - cyan)
            * Includes configuration number (fig)


    :Inputs:
    -------
    Aircraft_Class:	class
                    in_aircraft class (now has data from upstream components)


    :Outputs:
    -------
    Plots
    """

    # Plots each iteration configuration
    def __init__(self, ac, writer):
        super(Plot, self).__init__()

        # Plotting Setup
        fig = plt.figure(figsize=[12, 8])
        self.fig = fig

        geo1 = plt.subplot2grid((5, 5), (0, 0), colspan=3, rowspan=4)
        geo2 = plt.subplot2grid((5, 5), (4, 0), colspan=3, rowspan=1)
        geo1.set_xlim([-2, 2])
        geo1.set_ylim([-0.5, 2])
        geo2.set_xlim([-2, 2])
        geo2.set_ylim([-0.5, 0.5])

        A = list()
        A.append(plt.subplot2grid((5, 5), (0, 3), colspan=2))
        A.append(plt.subplot2grid((5, 5), (1, 3), colspan=2))
        A.append(plt.subplot2grid((5, 5), (2, 3), colspan=2))
        A.append(plt.subplot2grid((5, 5), (3, 3), colspan=2))
        A.append(plt.subplot2grid((5, 5), (4, 3), colspan=2))

        for i in range(0, 5):
            A[i].set_xlim([0, 0.7])
            A[i].set_ylim([-0.1, 0.2])

        self.geo1 = geo1
        self.geo2 = geo2
        self.A = A

        self.fig = fig
        self.writer = writer

        # Input instance of aircraft - before modification
        self.add_param('in_aircraft', val=ac, desc='Input Aircraft Class')

    def solve_nonlinear(self, params, unknowns, resids):
        # Used passed in instance of aircraft
        AC = params['in_aircraft']

        # Pull variables from AC needed for plotting
        Xle = AC.wing.Xle
        Yle = AC.wing.Yle
        C = AC.wing.chord_vals
        Xle_ht = AC.tail.Xle_ht
        Yle_ht = AC.tail.Yle_ht
        C_t = AC.tail.htail_chord_vals
        x_cg = AC.x_cg
        NP = AC.NP
        score = AC.score

        wing_edge = Xle + [sum(x) for x in zip(Xle, C)][::-1] + [sum(x) for x in zip(Xle, C)] + [1 * x for x in
                                                                                                 Xle[::-1]]
        wing_pos = Yle + Yle[::-1] + [-1 * x for x in Yle] + [-1 * x for x in Yle[::-1]]
        wing_zpos = [0.0 * abs(x) for x in wing_pos]

        tail_edge = Xle_ht + [sum(x) for x in zip(Xle_ht, C_t)][::-1] + [sum(x) for x in zip(Xle_ht, C_t)] + [1 * x for
                                                                                                              x in
                                                                                                              Xle_ht[
                                                                                                              ::-1]]
        tail_pos = Yle_ht + Yle_ht[::-1] + [-1 * x for x in Yle_ht] + [-1 * x for x in Yle_ht[::-1]]
        tail_zpos = [0.0 * abs(x) for x in tail_pos]

        self.geo1.plot(wing_pos, wing_edge, 'b-', tail_pos, tail_edge, 'r-', [0, 0], [C[0], Xle_ht[0]], 'g-')
        self.geo1.plot([Yle[0], Yle[0]], [Xle[0], Xle[0] + C[0]], 'm--')
        self.geo1.plot([Yle[1], Yle[1]], [Xle[1], Xle[1] + C[1]], 'm--')
        self.geo1.plot([Yle[2], Yle[2]], [Xle[2], Xle[2] + C[2]], 'm--')
        self.geo1.plot([Yle[3], Yle[3]], [Xle[3], Xle[3] + C[3]], 'm--')
        self.geo1.plot([Yle[4], Yle[4]], [Xle[4], Xle[4] + C[4]], 'm--')
        self.geo1.plot(0, x_cg, 'ko', 0, NP, 'co')
        self.geo1.set_xlim([-2, 2])
        self.geo1.set_ylim([-0.5, 2])

        at = AnchoredText(str(score), prop=dict(size=17), frameon=True, loc=2)
        at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
        self.geo1.add_artist(at)

        self.geo2.plot(wing_pos, wing_zpos, 'b-', tail_pos, tail_zpos, 'r-')
        self.geo2.set_xlim([-2, 2])
        self.geo2.set_ylim([-0.5, 0.5])

        for i in range(1, len(self.A) + 1):
            f = open('./Aerodynamics/airfoils/A_' + str(i) + '.dat', 'r')
            flines = f.readlines()

            X = []
            Y = []
            for j in range(1, len(flines)):
                words = string.split(flines[j])
                X.append(float(words[0]))
                Y.append(float(words[1]))

            self.A[i - 1].set_xlim([0, max(C)])
            self.A[i - 1].set_ylim([(max(C) * min(Y) - 0.02), (max(C) * max(Y) + 0.02)])

            X = [C[i - 1] * x for x in X]
            Y = [C[i - 1] * x for x in Y]
            X = [x + Xle[i - 1] for x in X]

            # print(X,Y)

            self.A[i - 1].plot(X, Y, 'm-')

        self.writer.grab_frame()

        at.remove()
        self.geo1.lines = []
        self.geo2.lines = []
        self.A[0].lines = []
        self.A[1].lines = []
        self.A[2].lines = []
        self.A[3].lines = []
        self.A[4].lines = []


def plotGeoFinal(Xle, Yle, C, Xle_ht, Yle_ht, C_t, x_cg, NP, score, mount_len):
    """
    Plots the final optimized geometry

    :Inputs:
    -------
    Xle : ndarray
        Wing leading edge at each section (x coord.)
    Yle : ndarray
        Wing leading edge at each section (y coord.)
    C : ndarray
        Chord at each section
        Xle_ht: Tail leading edge at each section (x coord.)
        Yle_ht: Tail leading edge at each section (y coord.)
        C_t: Tail chord at each section
        x_cg: CG position
        NP : float?
        Neutral point position
    score : float
        Objective function score
    mount_len : float
        Motor mount length to plot the motor


    :Outputs:
    -------
    Single plot
    """
    wing_edge = Xle + [sum(x) for x in zip(Xle, C)][::-1] + [sum(x) for x in zip(Xle, C)] + [1 * x for x in Xle[::-1]]
    wing_pos = Yle + Yle[::-1] + [-1 * x for x in Yle] + [-1 * x for x in Yle[::-1]]
    wing_zpos = [0.0 * abs(x) for x in wing_pos]

    tail_edge = Xle_ht + [sum(x) for x in zip(Xle_ht, C_t)][::-1] + [sum(x) for x in zip(Xle_ht, C_t)] + [1 * x for x in
                                                                                                          Xle_ht[::-1]]
    tail_pos = Yle_ht + Yle_ht[::-1] + [-1 * x for x in Yle_ht] + [-1 * x for x in Yle_ht[::-1]]
    tail_zpos = [0.0 * abs(x) for x in tail_pos]

    plt.close('all')
    fig = plt.figure(figsize=[12, 8])

    A = []

    geo1 = plt.subplot2grid((5, 5), (0, 0), colspan=3, rowspan=4)
    geo2 = plt.subplot2grid((5, 5), (4, 0), colspan=3, rowspan=1)

    A.append(plt.subplot2grid((5, 5), (0, 3), colspan=2))
    A.append(plt.subplot2grid((5, 5), (1, 3), colspan=2))
    A.append(plt.subplot2grid((5, 5), (2, 3), colspan=2))
    A.append(plt.subplot2grid((5, 5), (3, 3), colspan=2))
    A.append(plt.subplot2grid((5, 5), (4, 3), colspan=2))

    geo1.plot(wing_pos, wing_edge, 'b-', tail_pos, tail_edge, 'r-', [0, 0], [C[0], Xle_ht[0]], 'g-')
    geo1.plot([Yle[0], Yle[0]], [Xle[0], Xle[0] + C[0]], 'm--')
    geo1.plot([Yle[1], Yle[1]], [Xle[1], Xle[1] + C[1]], 'm--')
    geo1.plot([Yle[2], Yle[2]], [Xle[2], Xle[2] + C[2]], 'm--')
    geo1.plot([Yle[3], Yle[3]], [Xle[3], Xle[3] + C[3]], 'm--')
    geo1.plot([Yle[4], Yle[4]], [Xle[4], Xle[4] + C[4]], 'm--')
    # print("Mount Length = %f"% mount_len)
    geo1.plot(0, x_cg, 'ko', 0, NP, 'cd', 0, mount_len, 'bs')
    # Automatic axis scaling
    # geo1.set_xlim([-max(Yle)*1.2, max(Yle)*1.2])
    geo1.axis('equal')
    geo1.set_ylim([0.0, (max(Xle_ht) + max(C_t)) * 1.2])

    at = AnchoredText(str(score), prop=dict(size=17), frameon=True, loc=2)
    at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
    geo1.add_artist(at)

    geo2.plot(wing_pos, wing_zpos, 'b-', tail_pos, tail_zpos, 'r-')
    geo2.set_xlim([-max(Yle) * 1.2, max(Yle) * 1.2])
    # Automatic axis scaling
    geo2.set_ylim([-1, max(Xle_ht) * 2.0])

    # Use other subplots in window for plotting sectional airfoils
    for i in range(1, len(A) + 1):
        f = open('./airfoils/A_' + str(i) + '.dat', 'r')
        flines = f.readlines()

        X = []
        Y = []
        for j in range(1, len(flines)):
            words = str.split(flines[j])
            X.append(float(words[0]))
            Y.append(float(words[1]))

        A[i - 1].set_xlim([0, max(C)])
        A[i - 1].set_ylim([(max(C) * min(Y) - 0.02), (max(C) * max(Y) + 0.02)])

        X = [C[i - 1] * x for x in X]
        Y = [C[i - 1] * x for x in Y]
        # X = [x + Xle[i -1] for x in X]

        # print(X,Y)

        A[i - 1].plot(X, Y, 'm-')

    plt.tight_layout()
    plt.show()


def plotGeoFinalDuo(in_AC, out_AC):
    """
    Plots the final geometry compared to the input geometry

    :Inputs:
    -------
    in_AC : Aircraft
        input, or starting, aircraft to compare against. Note: in_AC can be None
    out_AC : Aircraft
        final aircraft

    :Outputs:
    -------
    Single plot
    """
    plt.close('all')
    fig = plt.figure(figsize=[12, 8])

    A = []

    geo1 = plt.subplot2grid((5, 5), (0, 0), colspan=3, rowspan=4)
    geo2 = plt.subplot2grid((5, 5), (4, 0), colspan=3, rowspan=1)

    A.append(plt.subplot2grid((5, 5), (0, 3), colspan=2))
    A.append(plt.subplot2grid((5, 5), (1, 3), colspan=2))
    A.append(plt.subplot2grid((5, 5), (2, 3), colspan=2))
    A.append(plt.subplot2grid((5, 5), (3, 3), colspan=2))
    A.append(plt.subplot2grid((5, 5), (4, 3), colspan=2))

    geo1_xlim = []
    geo1_ylim = []
    geo2_xlim = []
    geo2_ylim = []

    if in_AC is None and out_AC is None:
        raise ValueError('Both in_AC and out_AC are None in lib_plot.py')

    for n in range(2):
        if n == 0:
            AC = in_AC
            c1 = 'k-'
            c2 = 'k-'
            c3 = 'k-'
            c4 = 'k--'
            c5 = 'k-'
            c6 = 'k--'
        elif n == 1:
            AC = out_AC
            c1 = 'b-'
            c2 = 'r-'
            c3 = 'g-'
            c4 = 'm--'
            c5 = 'm-'
            c6 = 'b--'
        else:
            raise ValueError('Invalid aircraft presented in lib_plot')

        # Continue if AC is None
        if AC is None:
            continue

        Xle = AC.wing.Xle.tolist()
        Yle = AC.wing.Yle.tolist()
        C = AC.wing.chord_vals.tolist()
        Xle_ht = AC.tail.Xle_ht.tolist()
        Yle_ht = AC.tail.Yle_ht.tolist()
        C_t = AC.tail.htail_chord_vals.tolist()
        x_cg = AC.CG[0]
        NP = AC.NP
        score = AC.score
        mount_len = AC.mount_len

        # Plot aircraft geometry
        wing_edge = Xle + [sum(x) for x in zip(Xle, C)][::-1] + [sum(x) for x in zip(Xle, C)] + [1 * x for x in
                                                                                                 Xle[::-1]]
        wing_pos = Yle + Yle[::-1] + [-1 * x for x in Yle] + [-1 * x for x in Yle[::-1]]
        wing_zpos = [0.0 * abs(x) for x in wing_pos]

        tail_edge = Xle_ht + [sum(x) for x in zip(Xle_ht, C_t)][::-1] + [sum(x) for x in zip(Xle_ht, C_t)] + [1 * x for
                                                                                                              x in
                                                                                                              Xle_ht[
                                                                                                              ::-1]]
        tail_pos = Yle_ht + Yle_ht[::-1] + [-1 * x for x in Yle_ht] + [-1 * x for x in Yle_ht[::-1]]
        tail_zpos = [0.0 * abs(x) for x in tail_pos]

        geo1.plot(wing_pos, wing_edge, c1, tail_pos, tail_edge, c2, [0, 0], [C[0], Xle_ht[0]], c3)
        geo1.plot([Yle[0], Yle[0]], [Xle[0], Xle[0] + C[0]], c4)
        geo1.plot([Yle[1], Yle[1]], [Xle[1], Xle[1] + C[1]], c4)
        geo1.plot([Yle[2], Yle[2]], [Xle[2], Xle[2] + C[2]], c4)
        geo1.plot([Yle[3], Yle[3]], [Xle[3], Xle[3] + C[3]], c4)
        geo1.plot([Yle[4], Yle[4]], [Xle[4], Xle[4] + C[4]], c4)

        if n == 1:
            geo1.plot(0, x_cg, 'ko', 0, NP, 'cd', 0, mount_len, 'bs')

        # Automatic axis scaling
        geo1_xlim.append([-max(Yle) * 1.2, max(Yle) * 1.2])
        geo1_ylim.append([0.0, (max(Xle_ht) + max(C_t) * 1.2)])

        # Show score to plot
        if n == 1:
            at = AnchoredText(str(score), prop=dict(size=17), frameon=True, loc=2)
            at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
            geo1.add_artist(at)

        if n == 1:
            # Plot list distribution (use AOA closest to the cruise AOA)
            alpha = AC.alpha
            cruise_alpha = AC.ang
            sec_CL = AC.sec_CL
            sec_L = AC.sec_L
            sec_Yle = AC.sec_Yle

            temp = [abs(x - cruise_alpha) for x in alpha]
            plt_ind = temp.index(min(temp))
            plt_secCL = sec_CL[plt_ind]
            plt_secL = sec_L[plt_ind]
            plt_Yle = sec_Yle[plt_ind]

            # geo2.plot(  plt_Yle, plt_secCL, c1 )
            geo2.plot(plt_Yle, plt_secL, c1)

            # Elliptical list distribution
            a = plt_Yle[-1] - plt_Yle[0]
            b = plt_secL[0]
            plt_ellipCL = [b * np.sqrt(1 - (x / a) ** 2) for x in (plt_Yle - plt_Yle[0])]
            geo2.plot(plt_Yle, plt_ellipCL, c6)

            # Automatic axis scaling
            geo2_xlim.append([0.0, max(plt_Yle) * 1.1])
            geo2_ylim.append([min(plt_secL) * 1.2, max(plt_secL) * 1.2])

        # Use other subplots in window for plotting sectional airfoils
        for i in range(1, len(A) + 1):
            f = open('Aerodynamics/airfoils/A_{:s}.dat'.format(str(i)), 'r')
            flines = f.readlines()

            X = []
            Y = []
            for j in range(1, len(flines)):
                words = str.split(flines[j])
                X.append(float(words[0]))
                Y.append(float(words[1]))

            A[i - 1].set_xlim([0, max(C)])
            A[i - 1].set_ylim([(max(C) * min(Y) - 0.02), (max(C) * max(Y) + 0.02)])

            X = [C[i - 1] * x for x in X]
            Y = [C[i - 1] * x for x in Y]
            # X = [x + Xle[i -1] for x in X]

            # print(X,Y)

            A[i - 1].plot(X, Y, c5)

    # Automatic axis scaling
    geo1_xlim = np.array(geo1_xlim)
    geo1_ylim = np.array(geo2_xlim)

    geo1.set_xlim(min(geo1_xlim[:, 0]), max(geo1_xlim[:, 1]))
    geo1.axis('equal')
    geo1.set_ylim(min(geo1_ylim[:, 0]), max(geo1_ylim[:, 1]))

    # geo2.set_xlim(min(geo2_xlim[0][0], geo2_xlim[1][0]), max(geo2_xlim[0][1], geo2_xlim[1][1]))
    # geo2.set_ylim(min(geo2_ylim[0][0], geo2_ylim[1][0]), max(geo2_ylim[0][1], geo2_ylim[1][1]))

    name = out_AC.AC_name

    plt.tight_layout()
    plt.savefig(('OPT_%s.pdf' % name), bbox_inches='tight')
    plt.show()
