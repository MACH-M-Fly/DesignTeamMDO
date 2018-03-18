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
masses_1 = [0.458, 0.912, 1.367, 1.823, 2.274, 2.725, 3.175, 3.627, 4.080, 4.532]
masses_2 = [0.458, 0.913, 1.364, 1.816, 2.271, 2.723, 3.173, 3.626, 4.080, 4.534]
masses_3 = [0.457, 0.913, 1.363, 1.813, 2.264, 2.719, 3.170, 3.624, 4.076, 4.530]

masses = [masses_1, masses_2, masses_3]

for i in range(len(masses)):
    print('Trial ' + str(i+1))

    for m in masses[i]:
        P = m * 9.807
        x_tail = np.linspace(0, boom_len, 1001)
        c_tail, I_tail = struct_anal.calcI(boom_type, boom_dim)
        M_tail, y_tail, sigma_tail = struct_anal.calcPointLoad(x_tail, boom_len, P, I_tail, boom_E, c_tail)
        print('P = {:0.5f} N\tD = {:.6e}'.format(P, max(y_tail)*100.)) # Centimeters

    print()
