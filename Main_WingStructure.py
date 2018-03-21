import Structures.structAnalysis as struct_anal

import math
import numpy as np

from Input import AC
from Weights.calcWeight import getWing_mass


# Define wing parameters
wing_type = 'I'
flange_w = 0.9652  / 100
flange_h = 0.6858 / 100
web_w = 0.3302 / 100
web_h = 2.3876 / 100
spar_dim = (flange_w, flange_h, web_w, web_h)

flange_A = 2 * flange_w * flange_h
web_A = web_w * web_h
total_A = flange_A + web_A

v_spruce = flange_A / total_A
v_balsa = web_A / total_A

spar_E = 21.4e9 + 3.71e9
print(spar_E / 1e9)

internal_dist = 0.76
measure_dist = 0.575
spar_len = 0.76

# Define loaded masses
masses_1 = [0.452, 0.908, 1.361, 1.819, 2.269, 2.727]
masses_2 = [0.454, 0.906, 1.356, 1.810, 2.266, 2.717]
masses_3 = [0.456, 0.907, 1.365, 1.817, 2.271, 2.723, 2.271, 1.818, 1.366, 0.908, 0.458, 0.002]
masses_4 = [0.450, 0.902, 1.360, 1.812, 2.268, 2.722, 2.267, 1.811, 1.359, 0.902, 0.450, 0.001]

masses = [masses_1, masses_2, masses_3, masses_4]

for i in range(len(masses)):
    print('Trial ' + str(i+1) + ' [cm]')

    for m in masses[i]:
        P = m * 9.81
        x_spar = np.linspace(0, spar_len, 11)
        c_spar, I_spar = struct_anal.calcI(wing_type, spar_dim)
        y_spar = struct_anal.calcPointLoadSimplySupported(x_spar, measure_dist, internal_dist,
                                                          P, I_spar, spar_E)

        slope_last = (y_spar[-1] - y_spar[-2]) / (x_spar[-1] - x_spar[-2])

        y_max = y_spar[-1] + slope_last * (spar_len - measure_dist)

        print('{:.6e}'.format(np.max(y_max) * 100.)) # Centimeters

    print('')


# Calc Mass

# Add 20 grams for servos, 20 for wires, and 20 for servo attachements
# Add 10% fudge factor for glue, etc...
mass_w = (getWing_mass(AC)[1])*1.1 + 0.020*3
print('Mass: {:.4f} kg'.format(mass_w))

# TODO - Calc Mass


