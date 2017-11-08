#python stantdard libraries
from __future__ import print_function

import Aerodynamics.aeroAnalysis as aeroAnalysis
import Performance.objPerformance as objPerformance

geo_filename = 'Aerodynamics/aircraft_mx2.txt'
mass_filename = 'Aerodynamics/aircraft_mx2.mass'

print('Running AVL Analysis')

alpha, CL, CD, CM, NP, sec_CL, sec_Yle, sec_Chord, velocity = aeroAnalysis.getAeroCoef(geo_filename=geo_filename, mass_filename=mass_filename)

sref_wing = 1.904512
sref_tail = 0.20028347
weight = 12.23337624 * 9.81
boom_len = 1.392426984
dist_LG = 0.12827
MAC = 0.496824
Iyy = 0.3350

# Mark Drela's Supra
geo_filename = 'Aerodynamics/aircraft_supra.txt'
mass_filename = 'Aerodynamics/aircraft_supra.mass'

alpha, CL, CD, CM, NP, sec_CL, sec_Yle, sec_Chord, velocity = aeroAnalysis.getAeroCoef(geo_filename=geo_filename, mass_filename=mass_filename)

sref_wing = 0.6787083
sref_tail = 0.0535483
weight = 1.81437 * 9.81
boom_len = 1.0668
dist_LG = 0.20193
MAC = 0.20193
Iyy = 0.1008

print('Running Takeoff Sim')

sum_y, dist, vel, ang, ang_vel, time = objPerformance.runwaySim_small(CL, CD, CM, sref_wing, sref_tail, weight, boom_len, dist_LG, MAC, Iyy)

print('Takeoff Distance %0.1f m, %0.1f ft' % (dist, dist * 3.28084))
print('Takeoff Time %0.2f s' % time)
print('Takeoff Velocity %0.2f m/s' % vel)
