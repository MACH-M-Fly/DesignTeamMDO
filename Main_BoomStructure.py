import Structures.structAnalysis as struct_anal

import numpy as np


# Define tail boom parameters
boom_type = 'R'
width_o = 0.0254
width_i = 0.022225
boom_dim = (width_o, width_o, width_i, width_i)
boom_E = 68.9e9
boom_len = 0.9144

# Define loaded masses
masses_1 = [0.451, 0.901, 1.356, 1.810, 2.264, 2.715, 3.167, 3.625, 4.083, 4.538]
masses_2 = [0.450, 0.901, 1.359, 1.814, 2.269, 2.727, 3.178, 3.630, 4.084, 4.537]
masses_3 = [0.451, 0.901, 1.356, 1.810, 2.264, 2.715, 3.167, 3.625, 4.083, 4.538]

masses = [masses_1, masses_2, masses_3]

for i in range(len(masses)):
    print('Trial ' + str(i+1))

    for m in masses[i]:
        P = m * 9.807
        x_tail = np.linspace(0, boom_len, 1001)
        c_tail, I_tail = struct_anal.calcI(boom_type, boom_dim)
        M_tail, y_tail, sigma_tail = struct_anal.calcPointLoadSimplySupported(x_tail, 0.3048, boom_len, P, I_tail, boom_E, c_tail)
        print('{:.6e}'.format(np.max(y_tail)*100.)) # Centimeters

    print('')


# Calc Mass

den_boom = 2700.0
outer_a = boom_dim[0] * boom_dim[1]
inner_a = boom_dim[2] * boom_dim[3]

m_boom = boom_len * (outer_a - inner_a) * den_boom

print('Mass of Boom: {:.3f} kg'.format(m_boom))
