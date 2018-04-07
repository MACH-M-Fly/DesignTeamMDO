from Propulsion.APCdat_parser import createKriging
import numpy as np
import math



diameter = 11.0
pitch = 6.0

power_model = createKriging([8, 13], [5, 9], [1000, 13000], 'power')
spherical_model = createKriging([8, 13], [5, 9], [1000, 13000], 'spherical')
g_model = createKriging([8, 13], [5, 9], [1000, 13000], 'exponential')

total_voltage = 4.0 * .65 * 3.0

RPM = 1000.0 * total_voltage

print(RPM)

# Power model
maxThrust, ss = power_model[0]['max'].execute('points', diameter, pitch, RPM)
maxVel, ss = power_model[0]['vel'].execute('points', diameter, pitch, RPM)
thrust14, ss = power_model[0]['14'].execute('points', diameter, pitch, RPM)
thrust24, ss = power_model[0]['24'].execute('points', diameter, pitch, RPM)
thrust34, ss = power_model[0]['34'].execute('points', diameter, pitch, RPM)

# X = [0, (maxVel / 4.0), (maxVel / 2.0), (maxVel * 3.0 / 4.0), maxVel]
# Y = [maxThrust, thrust14, thrust24, thrust34, 0.0]
# thrust_Curve = np.polyfit(X, Y, 4)
# print(thrust_Curve)
#
# # Spherical model
# maxThrust, ss = spherical_model[0]['max'].execute('points', diameter, pitch, RPM)
# maxVel, ss = spherical_model[0]['vel'].execute('points', diameter, pitch, RPM)
# thrust14, ss = spherical_model[0]['14'].execute('points', diameter, pitch, RPM)
# thrust24, ss = spherical_model[0]['24'].execute('points', diameter, pitch, RPM)
# thrust34, ss = spherical_model[0]['34'].execute('points', diameter, pitch, RPM)
#
# X = [0, (maxVel / 4.0), (maxVel / 2.0), (maxVel * 3.0 / 4.0), maxVel]
# Y = [maxThrust, thrust14, thrust24, thrust34, 0.0]
# thrust_Curve = np.polyfit(X, Y, 4)
# print(thrust_Curve)
#
# # Gaussian model
# maxThrust, ss = g_model[0]['max'].execute('points', diameter, pitch, RPM)
# maxVel, ss = g_model[0]['vel'].execute('points', diameter, pitch, RPM)
# thrust14, ss = g_model[0]['14'].execute('points', diameter, pitch, RPM)
# thrust24, ss = g_model[0]['24'].execute('points', diameter, pitch, RPM)
# thrust34, ss = g_model[0]['34'].execute('points', diameter, pitch, RPM)
#
# X = [0, (maxVel / 4.0), (maxVel / 2.0), (maxVel * 3.0 / 4.0), maxVel]
# Y = [maxThrust, thrust14, thrust24, thrust34, 0.0]
# thrust_Curve = np.polyfit(X, Y, 4)
# print(thrust_Curve)

# New thrust prediction

# Determine the wake velocity
rho = 1.105 # assume sea level
A = (diameter*0.0254/2.0)**2*3.14
Vw = math.sqrt(2*maxThrust/(rho*A))
print(A)
print(maxThrust)
print(Vw)


