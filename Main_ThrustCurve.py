import numpy as np

import CreateProblem

prob0 = CreateProblem.CreateRunOnceProblem()
prob0.run()
ac = prob0['createAC.aircraft']

thrustCurve = ac.propulsion.getThrustCurve()

vel_vals = np.linspace(0, 18, 100)
t_vals = np.polyval(thrustCurve, vel_vals)

v_str = ''
t_str = ''

for v in vel_vals:
    v_str += '{:.3f}, '.format(v)

v_str = v_str[:-2]

for t in t_vals:
    t_str += '{:.5f}, '.format(t)

t_str = t_str[:-2]

print('[{:s}]'.format(v_str))
print('[{:s}]'.format(t_str))
