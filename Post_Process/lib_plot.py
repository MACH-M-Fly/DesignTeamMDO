'''
 lib_plot.py
 Created by Josh Anibal (JLA), modified by Chris Reynolds (CLR)
 - Plots aircraft:
    - During each iteration and at the end (plot_geo_final)
    - Plots wing (blue) and tail (red)
 	- Plots CG (black) and NP (light blue - cyan)
    - Includes configuration number (fig)
'''

from __future__ import division

from scipy.optimize import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
plt.rcParams['animation.ffmpeg_path'] = './.local/lib/python2.7/site-packages'
from mpl_toolkits.axes_grid.anchored_artists import AnchoredText

import numpy as np
import os
import string	

from openmdao.api import IndepVarComp, Component, Problem, Group

from Input import AC



# Class for plotting each iteration and a final geometry plotter
class Plot(Component):
	
	# Plots each iteration configuration
	def __init__(self, geo1, geo2, A, writer, fig):
		super(Plot,self).__init__()

		self.geo1 = geo1
		self.geo2 = geo2
		self.A = A

		self.fig = fig
		self.writer = writer


		# Input instance of aircraft - before modification
		self.add_param('in_aircraft',val=AC, desc='Input Aircraft Class')


	def solve_nonlinear(self,params,unknowns,resids):
		# Used passed in instance of aircraft
		AC = params['in_aircraft']

		# Pull variables from AC needed for plotting
		Xle = AC.wing.Xle
		Yle = AC.wing.Yle
		C = AC.wing.chord_vals
		Xle_ht = AC.tail.Xle_ht
		Yle_ht = AC.tail.Yle
		C_t = AC.tail.htail_chord_vals
		x_cg = AC.x_cg
		NP = AC.NP
		score = AC.score

		wing_edge = Xle + [sum(x) for x in zip(Xle, C)][::-1] + [sum(x) for x in zip(Xle, C)] + [1*x for x in Xle[::-1]]
		wing_pos = Yle + Yle[::-1] + [-1*x for x in Yle] + [-1*x for x in Yle[::-1]]
		wing_zpos = [0.0*abs(x) for x in wing_pos]

		tail_edge = Xle_ht + [sum(x) for x in zip(Xle_ht, C_t)][::-1] + [sum(x) for x in zip(Xle_ht, C_t)] + [1*x for x in Xle_ht[::-1]]
		tail_pos = Yle_ht + Yle_ht[::-1] + [-1*x for x in Yle_ht] + [-1*x for x in Yle_ht[::-1]]
		tail_zpos = [0.0*abs(x) for x in tail_pos]

		self.geo1.plot(  wing_pos, wing_edge ,  'b-', tail_pos, tail_edge, 'r-',[0, 0], [C[0], Xle_ht[0]], 'g-')
		self.geo1.plot( [Yle[0], Yle[0]] , [Xle[0] ,Xle[0] + C[0]] ,  'm--')
		self.geo1.plot( [Yle[1], Yle[1]] , [Xle[1] ,Xle[1] + C[1]] ,  'm--')
		self.geo1.plot( [Yle[2], Yle[2]] , [Xle[2] ,Xle[2] + C[2]] ,  'm--')
		self.geo1.plot( [Yle[3], Yle[3]] , [Xle[3] ,Xle[3] + C[3]] ,  'm--')
		self.geo1.plot( [Yle[4], Yle[4]] , [Xle[4] ,Xle[4] + C[4]] ,  'm--')
		self.geo1.plot(0, x_cg, 'ko', 0, NP, 'co')
		self.geo1.set_xlim([-2, 2])
		self.geo1.set_ylim([-0.5,2])

		at = AnchoredText(str(score),prop=dict(size=17), frameon=True, loc=2 )
		at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
		self.geo1.add_artist(at)


		self.geo2.plot(  wing_pos, wing_zpos ,  'b-', tail_pos, tail_zpos, 'r-')
		self.geo2.set_xlim([-2, 2])
		self.geo2.set_ylim([-0.5,0.5])

		for i in range (1, len(self.A) +1):
			f = open('./airfoils/A_' + str(i) + '.dat', 'r')
			flines = f.readlines()

			X = []
			Y = []
			for j in range(1, len(flines)):
				words = string.split(flines[j]) 
				X.append(float(words[ 0]))
				Y.append(float(words[ 1]))

			self.A[i -1].set_xlim([0, max(C)])
			self.A[i -1].set_ylim([(max(C)*min(Y)-0.02),(max(C)*max(Y)+0.02)])

			X = [C[i - 1]*x for x in X]
			Y = [C[i - 1]*x for x in Y]
			X = [x + Xle[i -1] for x in X]

			# print(X,Y)


			self.A[i -1].plot(X, Y, 'm-')

		self.writer.grab_frame(figure = self.fig)

		at.remove()
		self.geo1.lines = []
		self.geo2.lines = []
		self.A[0].lines = []
		self.A[1].lines = []
		self.A[2].lines = []
		self.A[3].lines = []
		self.A[4].lines = []

# Function: Plots a final geometry with given inputs                                      
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
def plot_geo_final(Xle, Yle, C, Xle_ht, Yle_ht, C_t, x_cg, NP, score):
	wing_edge = Xle + [sum(x) for x in zip(Xle, C)][::-1] + [sum(x) for x in zip(Xle, C)] + [1*x for x in Xle[::-1]]
	wing_pos = Yle + Yle[::-1] + [-1*x for x in Yle] + [-1*x for x in Yle[::-1]]
	wing_zpos = [0.0*abs(x) for x in wing_pos]

	print(wing_edge)

	tail_edge = Xle_ht + [sum(x) for x in zip(Xle_ht, C_t)][::-1] + [sum(x) for x in zip(Xle_ht, C_t)] + [1*x for x in Xle_ht[::-1]]
	tail_pos = Yle_ht + Yle_ht[::-1] + [-1*x for x in Yle_ht] + [-1*x for x in Yle_ht[::-1]]
	tail_zpos = [0.0*abs(x) for x in tail_pos]

	plt.close('all')
	fig = plt.figure(figsize=[12,8])

	A = []

	geo1 = plt.subplot2grid((5, 5), (0, 0), colspan=3, rowspan=4)
	geo2 = plt.subplot2grid((5, 5), (4, 0), colspan=3, rowspan=1)

	A.append(plt.subplot2grid((5, 5), ( 0, 3), colspan=2))
	A.append(plt.subplot2grid((5, 5), ( 1, 3), colspan=2))
	A.append(plt.subplot2grid((5, 5), ( 2, 3), colspan=2))
	A.append(plt.subplot2grid((5, 5), ( 3, 3), colspan=2))
	A.append(plt.subplot2grid((5, 5), ( 4, 3), colspan=2))

	geo1.plot(  wing_pos, wing_edge ,  'b-', tail_pos, tail_edge, 'r-',[0, 0], [C[0], Xle_ht[0]], 'g-')
	geo1.plot( [Yle[0], Yle[0]] , [Xle[0] ,Xle[0] + C[0]] ,  'm--')
	geo1.plot( [Yle[1], Yle[1]] , [Xle[1] ,Xle[1] + C[1]] ,  'm--')
	geo1.plot( [Yle[2], Yle[2]] , [Xle[2] ,Xle[2] + C[2]] ,  'm--')
	geo1.plot( [Yle[3], Yle[3]] , [Xle[3] ,Xle[3] + C[3]] ,  'm--')
	geo1.plot( [Yle[4], Yle[4]] , [Xle[4] ,Xle[4] + C[4]] ,  'm--')
	geo1.plot(0, x_cg, 'ko', 0, NP, 'co')
	# Automatic axis scaling
	geo1.set_xlim([-max(Yle)*1.2, max(Yle)*1.2])
	geo1.set_ylim([-1, max(Xle_ht)*2.0])


	at = AnchoredText(str(score),prop=dict(size=17), frameon=True, loc=2 )
	at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
	geo1.add_artist(at)

	geo2.plot(  wing_pos, wing_zpos ,  'b-', tail_pos, tail_zpos, 'r-')
	geo2.set_xlim([-max(Yle)*1.2, max(Yle)*1.2])
	# Automatic axis scaling
	geo2.set_ylim([-1, max(Xle_ht)*2.0])
	
	# Use other subplots in window for plotting sectional airfoils
	for i in range (1, len(A) +1):
		f = open('./airfoils/A_' + str(i) + '.dat', 'r')
		flines = f.readlines()

		X = []
		Y = []
		for j in range(1, len(flines)):
			words = str.split(flines[j]) 
			X.append(float(words[ 0]))
			Y.append(float(words[ 1]))

		A[i -1].set_xlim([0, max(C)])
		A[i -1].set_ylim([(max(C)*min(Y)-0.02),(max(C)*max(Y)+0.02)])

		X = [C[i - 1]*x for x in X]
		Y = [C[i - 1]*x for x in Y]
		X = [x + Xle[i -1] for x in X]

		# print(X,Y)


		A[i -1].plot(X, Y, 'm-')


	plt.tight_layout()