'''
# ObjPerformance.py
# - Evaluate aircraft performance based on objective
# Obj 1) M-Fly: Maximum payload, limited runway
# Obj 2) MACH: Minimum lap time, given lap perimiter

Inputs:
- Aircraft_Class
- Data from Aero(CL, CD, neutral point)

Outputs:
- Objective Function (1: Payload or 2: lap time)
- Takeoff distance (constraint)
- Climb rate (constraint)

'''

import numpy as np 
import math
