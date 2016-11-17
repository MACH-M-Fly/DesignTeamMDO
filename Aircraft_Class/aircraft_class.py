import numpy as np
import math
import scipy.integrate as integrate
import scipy.special as special

# aircraft_Class.py
# - Creates aircraft from input file parameters
#    - Aircraft (Mass, Inertias)
#    - Surfaces (Wing, horizontal tail, vertical tail)
#    - Fuselage (body volume)


class Aircraft():
# Aircraft class deals with all full aircraft parameters 
#   -  Convert units
#   -  Calculate aircraft mass
#   -  Calculate inertias
	def __init__(self):

										 # Wing= defult_wing, Tail_Horz=defult_tail_horz, Tail_Vert=defult_tail_vert,\
										 # X_cg=0.0, Y_cg=0.0, Z_cg=0.0, CD_p=0.0):
		self.CD_p = 0.0

		# self.Wing = Wing
		# self.Tail_Horz = Tail_Horz                
		# self.Tail_Vert = Tail_Vert

	def  convertUints(self):
		pass
		return

	def calcMass(self):
		pass
		return

	def calcI(self):
		pass
		return

class Surface():
# Surface class fully defines all surfaces.
	def __init__(self, num_Sections, is_linear, b_wing, sweep, chord, Xo, Yo, Zo, Afiles = [], Ainc = np.array([])):

		# Assign Inputs to aircraft object
		self.num_Sections = num_Sections-1 		# Number of sections per half-wing
		self.is_linear = is_linear				# 0 for non-linear cubic varying chord, 1 for linearly varying wing values
		self.b_wing = b_wing					# Wing span (not half-span)
		self.sweep = sweep						# Wing sweep (quarter chord)
		self.chord = chord 						# Chord as a function of half-span (b_wing/2)
		self.Xo = Xo 							# Root chord, leading edge, X position
		self.Yo = Yo							# Root chord, leading edge, X position
		self.Zo = Zo 							# Root chord, leading edge, X position
		self.Afiles = Afiles					# File for initial airfoil input
		self.Ainc = Ainc						# Angle of incidence as a function of half-span (b_wing/2)
		self.sec_span = self.b_wing/2/self.num_Sections 	# Span of each section of wing

		# If no starting airfoil given, default airfoil to start is NACA2412
		if Afiles == []:
			self.Afiles = ['NACA2412']*self.num_Sections
		# If no starting inclination angle given, default is zero
		if not(Ainc.any()):
			self.Ainc=np.zeros(self.num_Sections)

		# Calculate chord values at each section
		self.chord_vals = self.getChord(self.chord,self.sec_span)
		print("Chord Vals",self.chord_vals)

		# Calculate leading edge coordinates
		[self.Xle, self.Yle, self.Zle] = self.calcLeading_Edge()

		# Calulate wing surface reference area
		self.Sref_wing = self.calcSrefWing()

		# Calculate the mean aerodynamic chord
		self.MAC = self.calcMAC()

	# Function: Calculate chord at specified half-span position
	def getChord(self,chord,sec_span):
		self.chord_vals = np.zeros(self.num_Sections)
		for i in range(self.num_Sections):
			span = (i+1)*sec_span
			self.chord_vals[i] =  chord[0]*span**3 + chord[0]*span**2 + \
			chord[2]*span + chord[3] 
		return self.chord_vals

	# Function: Build Aircraft back 100 inches and up 100 inches
	#   - Avoid building parts in negative X or negative Z
	def calcLeading_Edge(self):
		# Build leading edge coordinates
		self.Xle = np.zeros(self.num_Sections)
		self.Yle = np.zeros(self.num_Sections)
		self.Zle = np.zeros(self.num_Sections)
		self.Xle[0] = self.Xo
		self.Yle[0] = self.Yo
		self.Zle[0] = self.Zo
		Xo_quar = self.Zo-self.chord_vals[0]/4
		for i in range(self.num_Sections):
			angle = self.sweep[i]*math.pi/180
			self.Xle[i] = Xo_quar - self.sec_span*i*math.tan(angle) 
			self.Yle[i] = self.sec_span*i
			self.Zle[i] = self.Zo # No dihedral right now
		return np.array([self.Xle,
						 self.Yle,
						 self.Zle])

	# Function: Calculate reference area for surface
	# Sref = integral (chord) dy (from 0 to bwing/2)
	def calcSrefWing(self):
		self.Sref = 0
		self.Sref = integrate.quad(lambda y: (self.chord[0]*y**3 + self.chord[0]*y**2 + \
			self.chord[2]*y + self.chord[3] ), 0, self.b_wing/2)
		print("Sref",self.Sref[0])
		self.Sref = self.Sref[0]*2
		print("Sref",self.Sref)
		return self.Sref

	# Function: Calculate mean aerodynaic chord for surface
	# MAC = 2/Sref * integral chord^2 dy (from 0 to b_wing/2)
	def calcMAC(self):
		self.MAC = 0
		self.MAC = integrate.quad(lambda y: (self.chord[0]*y**3 + self.chord[0]*y**2 + \
			self.chord[2]*y + self.chord[3] )**2, 0, self.b_wing/2)
		self.MAC = self.MAC[0]*2/self.Sref_wing
		print("chordvals",self.chord_vals)
		print("secspan",self.sec_span)
		print("sref",self.Sref_wing)
		

		print("MAC",self.MAC)
		return self.MAC

	def addControlSurface(self, secStart, secEnd, hvec, name):

		self.controlSurf = name
		self.control_secStart = secStart
		self.control_secEnd = secEnd
		self.control_hvec = hvec
		return

	def addSpar(self):
		pass

class Body():
	# Body class obtains the interior volume of the aircraft
	def __init__(self, Bfile, translate = [0, 0, 0], scale = [1, 1, 1] ):
		self.Bfile
		self.translate
		self.scale

	# Calculate interior volume
	def getVolume(self):
		pass 
		return

# defult_wing = Surface( Sref=0.5, MAC=0.5, Bref=1.0, Chord=np.array([0.6, 0.4]) )
# defult_tail_horz = Surface( Sref=0.125, MAC=0.25, Bref=0.5, Chord=np.array([0.3, 0.2]), Xle=np.array([1.0, 1.0]) )
# defult_tail_horz = Surface( Sref=0.125, MAC=0.25, Bref=0.5, Chord=np.array([0.3, 0.2]), Xle=np.array([1.0, 1.0]), Yle=np.array([0.0, 0.0]), Zle=np.array([0.0, 0.25]) )


# print(defult_wing.Yle)


