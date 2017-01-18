from Input_Files.Input import *
from Post_Process.lib_plot import *
import matplotlib.pyplot as plt
import numpy as np

from Aerodynamics.Aero import *

from Aerodynamics.xfoil_lib import *

Re = 500000
alpha = 0
print(AC.max_camber)

xfoil_alt("E420", AC.camber, AC.max_camber, AC.thickness, AC.max_thickness, Re, alpha)