from Input_Files.Input import *
from Post_Process.lib_plot import *
import matplotlib.pyplot as plt
import numpy as np

print(AC.num_Sections)
#my_surface = Surface(4, 1, 3, \
#	0, 1, [1,1,1,1], 1, 1, 1, [], 0)


print("Xle",AC.wing.Xle)
print("Yle",AC.wing.Yle)
print("Chord", AC.wing.chord_vals)

print("xo", AC.wing.Xo)
print("Xle_ht", AC.tail.Xle_ht)
print("Yle_ht", AC.tail.Yle_ht)
print("Tail Chords", AC.tail.htail_chord_vals)
tail = np.asarray(AC.tail.htail_chord_vals)
print("LOL", tail)
print("srsly", [0,0,0,0])
arr = np.array([0,0,0,0])
print("srsly", arr)
print("Convert", arr.tolist())

plot = plot_geo_final(AC.wing.Xle.tolist(), AC.wing.Yle.tolist(), AC.wing.chord_vals.tolist(), \
	AC.tail.Xle_ht.tolist(), AC.tail.Yle_ht.tolist(), AC.tail.htail_chord_vals.tolist(), 0.9, 1.5, 0)
#plot = plot_geo_final([0,0,0,0,0], [0,1,1.1,1.25,1.5], [1/4,1/5,1/6,1/7,1/8], \
#	[2, 2, 2, 2, 2], [0, 0.1, 0.2, 0.3, 0.4], [1,1,1,1,1], 1/8, 1/7, 1234)
plt.show()
