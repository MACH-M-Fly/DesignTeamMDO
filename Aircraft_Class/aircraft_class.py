import numpy as np
import math
import scipy.integrate as integrate
import scipy.special as special

# aircraft_Class.py
# - Creates aircraft from input file parameters
#    - Aircraft (Mass, Inertias)
#    - Surfaces (Wing, horizontal tail, vertical tail)
#    - Fuselage (body volume)


class Aircraft(object):
# Aircraft class deals with all full aircraft parameters 
#   -  Convert units
#   -  Calculate aircraft mass
#   -  Calculate inertias
	def __init__(self):

										 # Wing= defult_wing, Tail_Horz=defult_tail_horz, Tail_Vert=defult_tail_vert,\
										 # X_cg=0.0, Y_cg=0.0, Z_cg=0.0, CD_p=0.0):


		self.CD_p = 0.0					# Parasitic drag coefficient
		# self.weight = 55.0				# Weight in N
		# self.CG = ([0.2, 0.0, 0.0])					# Cg, m. behind root LE of wing
		self.I = ([0.195995656591, 1.5429026885, 1.73889834509, 0.0, 0.0, 0.0])

		self.Iyy = self.calcI()


	def calcMass(self):
		pass
		return

	# Calculate aircraft Iyy, NOT the spar or tailboom I
	def calcI(self):
		self.Iyy = 5.0
		return self.Iyy




class Wing(object):
# Wing class fully defines wing surface(s).
	def __init__(self, num_sections, is_linear, b_wing, sweep, chord, Xo, Yo, Zo, dihedral, camber,max_camber, thickness, max_thickness, \
	 Afiles=[], ainc=np.array([])):

		# Assign Inputs to aircraft object
		self.num_sections = num_sections 		# Number of sections per half-wing
		self.is_linear = is_linear				# 0 for non-linear cubic varying chord, 1 for linearly varying wing/tail values
		self.b_wing = b_wing					# Wing span (not half-span)
		self.sweep = sweep						# Wing sweep (quarter chord in degrees)
		self.chord = chord 						# Chord as a function of half-span (b_wing/2)
		self.Xo = Xo 							# Root chord, leading edge, X position
		self.Yo = Yo							# Root chord, leading edge, X position
		self.Zo = Zo 							# Root chord, leading edge, X position
		self.dihedral = dihedral				# Wing dihedral angle (degrees)
		self.camber = camber 					# Camber as a cubic function of span
		self.max_camber = max_camber 			# Max camber position as a cubic function of span
		self.thickness = thickness 				# Thickness as a cubic function of span
		self.max_thickness = max_thickness		# Max thickness position as a cubic function of span
		# self.boom_len = boom_len				# Tailboom length
		self.Afiles = Afiles					# File for initial airfoil input
		self.ainc = ainc						# Angle of incidence as a function of half-span (b_wing/2)
		self.sec_span = self.b_wing/2.0/(self.num_sections-1) 			# Span of each section of wing
		
		# Check for linearly varying input
		if self.is_linear == 1:
			self.chord[0] = 0
			self.chord[1] = 0
			self.chord[2] = 0
			self.sweep[0] = 0
			self.sweep[1] = 0
			self.sweep[2] = 0

		# If no starting airfoil given, default airfoil to start is NACA2412
		if Afiles == []:
			self.Afiles = ['NACA2412']*self.num_sections

		# If no starting inclination angle given, default is zero
		if not(ainc.any()):
			self.ainc=np.zeros(self.num_sections)

		# Calculate wing chord values at each section
		self.chord_vals = self.getChord()
		# print("Chord Vals",self.chord_vals)

		# Calculate sweep values at each section
		self.sweep_vals = self.getSweep(self.sweep)
		# print("Sweep Vals", self.sweep_vals)

		# Calculate leading edge coordinates
		[self.Xle, self.Yle, self.Zle] = self.calcLeading_Edge()
		# print("Leading Edge: X, Y, Z", self.Xle, self.Yle, self.Zle)

		# Calulate wing surface reference area
		self.sref = self.calcSrefWing()
		# print("Wing Sref", self.Sref)

		# Calculate the mean aerodynamic chord
		self.MAC = self.calcMAC()
		# print("Wing MAC", self.MAC)

		# Calculate the CG of the aircraft
		self.CG = np.array([self.chord_vals[0]/4, 0.0, 0.0])

		# Get cmaber values at spanwise locations
		self.camber_vals = self.getCamber()

		# Get cmaber values at spanwise locations
		self.max_camber_vals = self.getMaxCamber()

		# Get cmaber values at spanwise locations
		self.thickness_vals = self.getThickness()

		# Get cmaber values at spanwise locations
		self.max_thickness_vals = self.getMaxThickness()

	# Function: Calculate sweep values at sectional chord locations
	def getSweep(self, sweep):
		self.sweep_vals = np.zeros(self.num_sections)
		for i in range(self.num_sections):
			span = (i+1)*self.sec_span
			self.sweep_vals[i] =  sweep[0]*span**3 + sweep[1]*span**2 + \
			sweep[2]*span + sweep[3] 
		return self.sweep_vals

	# Function: Calculate chord at spanwise locations
	def getChord(self):
		self.chord_vals = np.zeros(self.num_sections)
		# for i in range(self.num_sections):
		# 	span = (i+1)*self.sec_span
		# 	self.chord_vals[i] =  self.chord[0]*span**3 + self.chord[0]*span**2 + \
		# 	self.chord[2]*span + self.chord[3] 
		spans = np.arange(1,self.num_sections+1)*self.sec_span
		self.chord_vals = self.chord[0]*spans**2 + self.chord[1]*spans**2 + self.chord[2]*spans + self.chord[3]
		return self.chord_vals

	# Function: Calculate camber at spanwise locations
	def getCamber(self):
		self.camber_vals = np.zeros(self.num_sections)
		spans = np.arange(1,self.num_sections+1)*self.sec_span
		self.camber_vals = self.camber[0]*spans**2 + self.camber[1]*spans**2 + self.camber[2]*spans + self.camber[3]
		return self.camber_vals

	# Function: Calculate max camber position at spanwise locations
	def getMaxCamber(self):
		self.max_camber_vals = np.zeros(self.num_sections)
		spans = np.arange(1,self.num_sections+1)*self.sec_span
		self.max_camber_vals = self.max_camber[0]*spans**2 + self.max_camber[1]*spans**2 + self.max_camber[2]*spans + self.max_camber[3]
		return self.max_camber_vals

	# Function: Calculate thickness at spanwise locations
	def getThickness(self):
		self.thickness_vals = np.zeros(self.num_sections)
		spans = np.arange(1,self.num_sections+1)*self.sec_span
		self.thickness_vals = self.thickness[0]*spans**2 + self.thickness[1]*spans**2 + self.thickness[2]*spans + self.thickness[3]
		return self.thickness_vals

	# Function: Calculate max thickness at spanwise locations
	def getMaxThickness(self):
		self.max_thickness_vals = np.zeros(self.num_sections)
		spans = np.arange(1,self.num_sections+1)*self.sec_span
		self.max_thickness_vals = self.max_thickness[0]*spans**2 + self.max_thickness[1]*spans**2 + self.max_thickness[2]*spans + self.max_thickness[3]
		return self.max_thickness_vals

	# Calculate wing leading edge coordinates
	def calcLeading_Edge(self):
		# Build leading edge coordinates
		self.Xle = np.zeros(self.num_sections)
		self.Yle = np.zeros(self.num_sections)
		self.Zle = np.zeros(self.num_sections)
		self.Xle[0] = self.Xo
		self.Yle[0] = self.Yo
		self.Zle[0] = self.Zo
		Xo_quar = self.Xo-self.chord_vals[0]/4
		# print(range(self.num_sections))
		for i in range(1, self.num_sections):
			# print("i",i)
			angle = self.sweep_vals[i]*math.pi/180
			self.Xle[i] = self.sec_span*i*math.tan(angle) 
			self.Yle[i] = self.sec_span*i
			self.Zle[i] = self.Zo + self.sec_span*i*math.tan(self.dihedral*math.pi/180)
		return np.array([self.Xle,
						 self.Yle,
						 self.Zle])

	# Function: Calculate reference area for surface
	# Sref = integral (chord) dy (from 0 to bwing/2)
	def calcSrefWing(self):
		self.sref = 0
		self.sref = integrate.quad(lambda y: (self.chord[0]*y**3 + self.chord[1]*y**2 + \
			self.chord[2]*y + self.chord[3] ), 0, self.b_wing/2)
		self.sref = self.sref[0]*2
		return self.sref

	# Function: Calculate mean aerodynaic chord for surface
	# MAC = 2/Sref * integral chord^2 dy (from 0 to b_wing/2)
	def calcMAC(self):
		self.MAC = 0
		self.MAC = integrate.quad(lambda y: (self.chord[0]*y**3 + self.chord[1]*y**2 + \
			self.chord[2]*y + self.chord[3] )**2, 0, self.b_wing/2)
		self.MAC = self.MAC[0]*2.0/self.sref
		return self.MAC

	def addControlSurface(self, secStart, secEnd, hvec, name):

		self.control_surf = name
		self.control_secstart = secStart
		self.control_secend = secEnd
		self.control_hvec = hvec
		return

	def addSpar(self):
		pass

	def updateAircraft(self):
		self.b_wing = 5.0
		# Calculate wing chord values at each section
		
		self.getChord()
		# print("Chord Vals",self.chord_vals)

		# Calculate sweep values at each section
		self.getSweep(self.sweep)
		# print("Sweep Vals", self.sweep_vals)

		# Calculate leading edge coordinates
		self.calcLeading_Edge()
		# print("Leading Edge: X, Y, Z", self.Xle, self.Yle, self.Zle)

		# Calulate wing surface reference area
		self.calcSrefWing()
		# print("Wing Sref", self.Sref)

		# Calculate the mean aerodynamic chord
		self.calcMAC()
		# print("Wing MAC", self.MAC)

		# Calculate the CG of the aircraft
		self.CG = np.array([self.chord_vals[0]/4, 0.0, 0.0])

		# Get cmaber values at spanwise locations
		self.getCamber()

		# Get cmaber values at spanwise locations
		self.getMaxCamber()

		# Get cmaber values at spanwise locations
		self.getThickness()

		# Get cmaber values at spanwise locations
		self.getMaxThickness()




class Tail():
# Tail class fully deines tail surface(s).
	def __init__(self, num_sections, is_linear, b_htail, htail_chord, b_vtail, vtail_chord, Xo, Yo, Zo, boom_len):

		# Assign Inputs to aircraft object
		self.num_sections = num_sections 		# Number of sections per half-wing
		self.is_linear = is_linear				# 0 for non-linear cubic varying chord, 1 for linearly varying wing/tail values
		self.b_htail = b_htail					# Span of horizontal tail
		self.htail_chord = htail_chord			# Horizontail tail chord
		self.b_vtail = b_vtail					# Span of vertical tail (height)
		self.vtail_chord = vtail_chord			# Vertical tail chord
		self.Xo = Xo 							# Root chord, leading edge, X position
		self.Yo = Yo							# Root chord, leading edge, X position
		self.Zo = Zo 							# Root chord, leading edge, X position
		self.boom_len = boom_len				# Tailboom length
		self.sec_span_htail = self.b_htail/2.0/self.num_sections 		# Span of each section of horiz. tail
		self.sec_span_vtail = self.b_vtail/self.num_sections 		# Span of each section of vert. tail

		# Check for linearly varying input
		if self.is_linear == 1:
			self.htail_chord[0] = 0
			self.htail_chord[1] = 0
			self.htail_chord[2] = 0
			self.vtail_chord[0] = 0
			self.vtail_chord[1] = 0
			self.vtail_chord[2] = 0

		# Calculate horiz. tail chord values at each section
		self.htail_chord_vals = self.getHTailChord(self.htail_chord, self.sec_span_htail)
		# print("Htail Chord Vals",self.htail_chord_vals)

		# Calculate horiz. tail chord values at each section
		self.vtail_chord_vals = self.getVTailChord(self.vtail_chord, self.sec_span_vtail)
		# print("Htail Chord Vals",self.htail_chord_vals)

		# Calulate wing surface reference area
		self.sref_ht = self.calcSrefHTail()
		# print("Tail Sref", self.Sref)

		# Calulate wing surface reference area
		self.sref_vt = self.calcSrefVTail()
		# print("Tail Sref", self.Sref)


		# Calculate the mean aerodynamic chord
		self.MAC_ht = self.calcMAC_ht()
		# print("Wing MAC", self.MAC)

		# Calculate the mean aerodynamic chord
		self.MAC_vt = self.calcMAC_vt()
		# print("Wing MAC", self.MAC)

		# Calculate vert. tail chord values at each section
		# self.vtail_chord_vals = self.getVTailChord(self.vtail_chord, self.sec_span_vtail)
		# print("Vtail hord Vals",self.vtail_chord_vals)

		# Calculate leading edge coordinates
		[self.Xle_ht, self.Yle_ht, self.Zle_ht] = self.calcHorizLeading_Edge()
		[self.Xle_vt, self.Yle_vt, self.Zle_vt] = self.calcVertLeading_Edge()
		# print("Tail Leading Edge: X, Y, Z", self.Xle_ht, self.Yle_ht, self.Zle_ht)

	# sref = integral (chord) dy (from 0 to bwing/2)
	def calcSrefHTail(self):
		self.sref = 0
		self.sref = integrate.quad(lambda y: (self.htail_chord[0]*y**3 + self.htail_chord[1]*y**2 + \
			self.htail_chord[2]*y + self.htail_chord[3] ), 0., self.b_htail/2.)
		self.sref = self.sref[0]*2.
		return self.sref

	# sref = integral (chord) dy (from 0 to bwing/2)
	def calcSrefVTail(self):
		self.sref = 0
		self.sref = integrate.quad(lambda y: (self.vtail_chord[0]*y**3 + self.vtail_chord[1]*y**2 + \
			self.vtail_chord[2]*y + self.vtail_chord[3] ), 0., self.b_vtail)
		self.sref = self.sref[0]
		return self.sref

	# Function: Calculate horiz. tail chord at sectional chord locations
	def getHTailChord(self, htail_chord, sec_span_htail):
		self.htail_chord_vals = np.zeros(self.num_sections)
		for i in range(self.num_sections):
			span = (i+1)*sec_span_htail
			self.htail_chord_vals[i] = htail_chord[0]*span**3 + htail_chord[1]*span**2 + \
			htail_chord[2]*span + htail_chord[3]
		return self.htail_chord_vals

	# Function: Calculate vertical tail chord at sectional chord locations
	def getVTailChord(self, vtail_chord, sec_span_vtail):
		self.vtail_chord_vals = np.zeros(self.num_sections)
		for i in range(self.num_sections):
			span = (i+1)*sec_span_vtail
			self.vtail_chord_vals[i] = vtail_chord[0]*span**3 + vtail_chord[1]*span**2 + \
			vtail_chord[2]*span + vtail_chord[3]
		return self.vtail_chord_vals

		# Calculate horiz. tail leading edge coordinates
	def calcHorizLeading_Edge(self):
		# Build leading edge coordinates
		self.Xle_ht = np.zeros(self.num_sections)
		self.Yle_ht = np.zeros(self.num_sections)
		self.Zle_ht = np.zeros(self.num_sections)
		self.Xle_ht[0] = self.Xo + self.boom_len + self.htail_chord_vals[0]
		# print("Xle_ht HERE", self.Xle_ht)
		self.Yle_ht[0] = self.Yo
		self.Zle_ht[0] = self.Zo
		Xo_quar_ht = self.Xle_ht[0]-self.htail_chord_vals[0]/4
		# print(range(self.num_sections))
		angle = 0								# No sweep
		for i in range(1, self.num_sections):
			# print("i",i)
			self.Xle_ht[i] = self.Xle_ht[0] - self.sec_span_htail*i*math.tan(angle)
			self.Yle_ht[i] = self.sec_span_htail*i
			self.Zle_ht[i] = self.Zo + self.sec_span_htail*i
		# print("YLE of Htail", self.Yle_ht)
		return np.array([self.Xle_ht,
						 self.Yle_ht,
						 self.Zle_ht])
		# Calculate vert. tail leading edge coordinates
	def calcVertLeading_Edge(self):
		# Build leading edge coordinates
		self.Xle_vt = np.zeros(self.num_sections)
		self.Yle_vt = np.zeros(self.num_sections)
		self.Zle_vt = np.zeros(self.num_sections)
		self.Xle_vt[0] = self.Xo + self.boom_len + self.vtail_chord_vals[0]
		# print("Xle_ht HERE", self.Xle_ht)
		self.Yle_vt[0] = self.Yo
		self.Zle_vt[0] = self.Zo
		Xo_quar_vt = self.Xle_vt[0]-self.vtail_chord_vals[0]/4
		# print(range(self.num_sections))
		angle = 0								# No sweep
		for i in range(1, self.num_sections):
			# print("i",i)
			self.Xle_vt[i] = self.Xle_vt[0] - self.sec_span_vtail*i*math.tan(angle)
			self.Yle_vt[i] = self.sec_span_vtail*i
			self.Zle_vt[i] = self.Zo + self.sec_span_vtail*i
		# print("ZLE of Vtail", self.Zle_vt)
		return np.array([self.Xle_vt,
						 self.Yle_vt,
						 self.Zle_vt])

	# Function: Calculate mean aerodynaic chord for tail
	# MAC = 2/Sref * integral chord^2 dy (from 0 to b_wing/2)
	def calcMAC_ht(self):
		self.MAC_ht = 0
		self.MAC_ht = integrate.quad(lambda y: (self.htail_chord[0]*y**3 + self.htail_chord[1]*y**2 + \
			self.htail_chord[2]*y + self.htail_chord[3] )**2, 0, self.b_htail/2.)
		self.MAC_ht = self.MAC_ht[0]*2.0/self.sref_ht
		return self.MAC_ht

	# Function: Calculate mean aerodynaic chord for tail
	# MAC = 2/Sref * integral chord^2 dy (from 0 to b_wing/2)
	def calcMAC_vt(self):
		self.MAC_vt = 0
		self.MAC_vt = integrate.quad(lambda y: (self.vtail_chord[0]*y**3 + self.vtail_chord[1]*y**2 + \
			self.vtail_chord[2]*y + self.vtail_chord[3] )**2, 0, self.b_vtail)
		self.MAC_vt = self.MAC_vt[0]/self.sref_vt
		return self.MAC_vt

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


