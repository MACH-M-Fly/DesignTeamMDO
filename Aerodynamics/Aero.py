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

 
