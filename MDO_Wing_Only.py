from InputWing import AC, updateAircraft

#from Aerodynamics.aeroAnalysis import aeroAnalysis
from Structures.structAnalysis import structAnalysis
from Propulsion.propulsionAnalysis import propulsionAnalysis
from Weights.calcWeight import calcWeight

# Update structures components?

# Update the aircraft
updateAircraft(AC)

comps = [propulsionAnalysis(), calcWeight(), structAnalysis()]

for comp in comps:
    AC.wing_f = 4.44822*8
    AC.tail_f = 10
    in_dict = {'in_aircraft' : AC}
    out_dict = dict()
    comp.solve_nonlinear(in_dict, out_dict, None)
    AC = out_dict['out_aircraft']

print('Wing Mass %0.3f kg' % AC.mass_wing)
print('Maximum Deflection Wing %0.5f m' % AC.y_max)
print('Maximum Stress Wing %0.5f Pa' % AC.sig_max)
