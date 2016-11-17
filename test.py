from Input import Inputs
import math
import numpy as np

from aircraft_Class import *

ac1 = Inputs("M6")
print(ac1.b_wing)
print(ac1.bank_angle)

print(np.ones(5))

for i in range(ac1.num_Sections):
	print(i)

print(ac1.num_Sections)

my_surface = Surface(ac1.num_Sections, ac1.is_linear, ac1.b_wing, \
	ac1.sweep, ac1.c_r, ac1.taper, ac1.Xo, ac1.Yo, ac1.Zo, [], ac1.Ainc)

