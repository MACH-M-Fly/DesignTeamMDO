"""
File to define constants used throughout the MDO run cases

Note that all constants are defined in terms of SI units
"""

import math

# Physical Constants
g = 9.81

# Aerodynamic Constants
Rho = 1.225
mu_k = 0.005
inced_ang = math.radians(-5.0)

# Specify path of xfoil
xfoil_path = 'Aerodynamics/xfoil/elev_data'
airfoils_path = 'Aerodynamics/airfoils'
