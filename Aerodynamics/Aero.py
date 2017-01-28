'''
 Aero.py
 - Obtain aerodynamic parameters for aircraft (cl, cd, L/D, etc.)
 - Run AVL for whole vehicle
 - Modify airfoils in AVL

Inputs:
- Aircraft_Class
 
Outputs:
- Aero data (CL, CD, neutral point)
- Loads data

'''

import numpy as np 
import math

 
class aerodynamics(Component):
	'''
	Obtain aerodynamic data from AVL
	'''

	def __init__(self ): 
		super(aerodynamics,self).__init__()

		self.add_param('b_wing',val=3.33,desc='Wing Span [m]')