#Input  Python Libraries
from __future__ import division

from openmdao.api import Component
import numpy as np

import math

from Aircraft_Class.gen_files import genMass, genGeo

import time

weight_run_times = []

class calcWeight(Component):
    """
    OpenMDAO component for weights estimation
    - Parametric based on data from both teams

    Inputs
    -------
    Aircraft_Class  :   class
                        in_aircraft class


    Outputs
    -------
    Aircraft_Class  :   class
                        out_aircraft class
    stress_wing     :   float
                        stress in wing spar
    stress_tail     :   float
                        stress in tail boom


    Version 2 Implementation

        Payload prediction will refine the size of the fuselage. The current fuselage length is determined strictly
        by satisfying the static margin criteria in the input file. The payload prediction weight will define the
        upper bound length of the fuselage.

        upper_Fuselage_Length = AC.payload;
    """

    # set up interface to the framework
    def __init__(self):
        super(calcWeight, self).__init__()

        # Import the starting aircraft
        from Input import AC

        # Input instance of aircraft - before modification
        self.add_param('in_aircraft',val=AC, desc='Input Aircraft Class')

        # Output instance of aircraft - after modification
        self.add_output('out_aircraft',val=AC, desc='Output Aircraft Class')

        # Output for Mass
        self.add_output('ac_mass', val=0.0, desc='Output Mass of the AC')


    def solve_nonlinear(self, params, unknowns, resids):
        # make all input variables local for ease
        AC = params['in_aircraft']

        start_time = time.time()

        unknowns['out_aircraft'] = calcWeight_process(AC)

        unknowns['ac_mass'] = AC.mass

        weight_run_times.append(time.time() - start_time)

def getWing_mass(AC):
    """
    Calculate wing mass


    Inputs
    ----------
    AC              :   Class
                        Class containing all aircraft data


    Outputs
    ----------
    num_ribs        :   int
                        Number of ribs in the wing
    m_wing          :   float
                        Mass of wing
    """
    sref_wing = AC.wing.sref                # m^2 | reference area of wing
    b_wing = AC.wing.b_wing                 # m | wing span
    MAC = AC.wing.MAC                       # m | mean aerodynamic chord of wing

    linden_LE = AC.LE_lindens               # kg/m | Main Wing Leading edge mass
    linden_TE = AC.TE_lindens               # kg/m | Main Wing Trailing edge mass
    linden_spar = AC.spar_lindens           # kg/m | Main Wing Spar mass
    k_ribs = AC.k_ribs                      # kg/m | mass of rib per 0.05 meter of rib

    den_spar = AC.spar_den                  # kg/m^3 | density of aluminum
    outer_r = AC.wing.spar_dim[0]           # m | outer radius of wing alum. spar
    inner_r = AC.wing.spar_dim[1]           # m | inner radius of wing alum. spar

    ultrakote_den = AC.ultrakote_Density    # kg/m^2 | density of ultrakote

    # Calculate number of ribs along the wing
    num_ribs = math.ceil(b_wing * AC.rib_lindens)
    print('Number of Ribs: %d' % num_ribs)

    # Calculate mass of components in wing
    m_ribs = k_ribs * num_ribs * MAC 				# kg | total mass of ribs
    m_LE = linden_LE * b_wing                       # kg | mass of leading edge
    m_TE = linden_TE * b_wing                       # kg | mass of trailing edge
    m_spar = linden_spar * b_wing                   # kg | mass of spar

    # TODO - FIX THIS!!!
    # kg | mass of aluminum spar of wing (asssum its length is half of wing span, hollow circular shape)
    m_wing_alum_spar = 0.5*b_wing * np.pi*(outer_r**2 - inner_r**2) * den_spar

    # Calculate mass of ultrakote
    wet_area_w = 2.1*sref_wing
    m_ult = wet_area_w * ultrakote_den

    # Get total mass of wing
    m_wing = m_ribs + m_LE + m_TE + m_spar + m_wing_alum_spar + m_ult

    print("Wing Mass = %f kg"% m_wing)
    # print("	Wing Rib Mass        = %f kg"% m_ribs)
    # print("	Wing LE Mass         = %f kg"% m_LE)
    # print("	Wing TE Mass         = %f kg"% m_TE)
    # print("	Wing Spar Mass       = %f kg"% m_spar)
    # print("	Wing ultrakote Mass  = %f kg"% m_ult)
    # print("	Wing Alum. Spar Mass = %f kg"% m_wing_alum_spar)
    # print("	Wing Rib Number 	 = %d"% num_ribs)
    print("	Wing Sref = %f m^2" % sref_wing)
    print("	MAC of wing = %f m" % MAC)
    print("	Wing span = %f m" % b_wing)
    print("	Wing chord = " + ', '.join("%f" % n for n in AC.wing.chord))
    print("	Wing chord vals = " + ', '.join("%f" % n for n in AC.wing.chord_vals))
    print("	Wing sweep = " + ', '.join("%f" % n for n in AC.wing.sweep))
    print("	Wing sweep vals = " + ', '.join("%f" % n for n in AC.wing.sweep_vals))

    return num_ribs, m_wing

def getTail_mass(AC):
    """
    Calculate tail mass


    Inputs
    ----------
    AC              :   Class
                        Class containing all aircraft data


    Outputs
    ----------
    m_tail          :   float
                        Mass of tail
    """
    # Get variables from AC
    b_htail = AC.tail.b_htail               # m | span of vertical tail
    b_vtail = AC.tail.b_vtail               # m | span of vertical tail
    MAC_ht = AC.tail.MAC_ht                 # m | MAC of horizontal tail
    MAC_vt = AC.tail.MAC_vt                 # m | MAC of vertical tail

    linden_spar_t = AC.spar_lindens_t       # kg/m | tail spar
    linden_LE_t = AC.LE_lindens_t           # kg/m | leading edge tail
    linden_TE_t = AC.TE_lindens_t           # kg/m | trailing edge tail

    C_t = AC.tail.htail_chord_vals
    ultrakote_den = AC.ultrakote_Density    # kg/m^2 | density of ultrakote

    # Calculate number of ribs along wing
    num_ribs_ht = math.ceil(b_htail * AC.rib_lindens_t)
    num_ribs_vt = math.ceil(b_vtail * AC.rib_lindens_t)

    # Calculate mass of components in tail
    m_ribs_ht = AC.k_ribs_t * num_ribs_ht * MAC_ht
    m_ribs_vt = AC.k_ribs_t * num_ribs_vt * MAC_vt
    m_ribs_t = m_ribs_ht + m_ribs_vt

    m_LE_t = linden_LE_t * (b_htail + b_vtail)
    m_TE_t = linden_TE_t * (b_htail + b_vtail)
    m_spar_t = linden_spar_t * (b_htail + b_vtail)

    # Calculate mass of ultrakote
    wet_area_t = 2*(b_htail + b_vtail) * C_t[0]
    m_ult = wet_area_t * ultrakote_den

    # Get total mass of tail
    m_tail = m_ribs_t + m_LE_t + m_TE_t + m_spar_t + m_ult

    print("Tail Mass = %f kg" % m_tail)
    print("	Mass of Tail Ribs = %f kg"% m_ribs_t)
    print("	Mass of LE        = %f kg"% m_LE_t)
    print("	Mass of TE        = %f kg"% m_TE_t)
    print("	Mass of Tail Spar = %f kg"% m_spar_t)
    print("	Mass of Tail ultrakote = %f kg"% m_ult)

    print("H_Tail")
    print("	b_htail = %f m"% b_htail)
    print("	Sref of HT = %f m^2"% AC.tail.sref_ht)
    print("	MAC of HT = %f"% MAC_ht)
    print("	H_Tail chord = " + ', '.join("%f" % n for n in AC.tail.htail_chord))
    print("	H_Tail chord_val = " + ', '.join("%f" % n for n in C_t))
    print("	Number of Ribs in HTail = %f"% num_ribs_ht)

    print("V_Tail")
    print("	b_vtail = %f"% b_vtail)
    print("	Sref of VT = %f m^2"% AC.tail.sref_vt)
    print("	MAC of VT = %f"% MAC_vt)
    print("	V_Tail chord = " + ', '.join("%f" % n for n in AC.tail.vtail_chord))
    print("	V_Tail chord_val = " + ', '.join("%f" % n for n in AC.tail.vtail_chord_vals))
    print("	Number of Ribs in VTail = %f"% num_ribs_vt)
    print("	Kg per rib = %f"% AC.k_ribs_t)

    return m_tail

def getStruct_mass(AC):
    """
    Calculate mass of spars, tailbooms, and mounts


    Inputs
    ----------
    AC              :   Class
                        Class containing all aircraft data


    Outputs
    ----------
    m_boom          :   float
                        tailboom mass
    m_landgear      :   float
                        landing gear mass
    m_ballast       :   float
                        ballast mass
    """

    boom_len = AC.boom_len

    # Calculate mass of tailboom
    den_boom = AC.boom_den              # kg/m^3 | density of aluminum
    outer_r = AC.tail.boom_Dim[0]       # m | outer radius of alum. tailboom
    inner_r = AC.tail.boom_Dim[1]       # m | inner radius of alum. tailboom

    m_boom = boom_len * np.pi*(outer_r**2 - inner_r**2) * den_boom

    # Calculate mass of landing gears
    dist_LG = AC.dist_LG                # m | distance between LE of wing and landing gear

    height_LG = np.sin(10 * np.pi / 180) * (boom_len - dist_LG)
    m_landgear_rear = 1.29 * height_LG * 2
    m_landgear_front = 0.27

    m_landgear = 0.25#m_landgear_rear + m_landgear_front

    # Calculate mass of ballast
    m_ballast = 0.					# kg | ballast mass (assume constant for now)

    print("Boom Mass = %f kg"% m_boom)
    print("	Boom Length = %f m"% boom_len)
    print("Landing Gear Mass = %f kg"% m_landgear)
    print("	Front LG Mass = %f kg"% m_landgear_front)
    print("	Rear LG Mass  = %f kg"% m_landgear_rear)
    print("	Height of LG = %f m"% height_LG)

    return m_boom, m_landgear, m_ballast

def massPostProcess(AC, m_wing, m_tail, m_boom, m_landgear, m_ballast):
    """
    Calculate center of gravity and moment of inertia


    Inputs
    ----------
    AC              :   Class
                        Class containing all aircraft data


    Outputs
    ----------
    cg              :   ndarray ([x_cg, y_cg, z_cg])
                        center of gravity
    Is              :   ndarray ([Ixx, Iyy, Izz])
                        Moment of inertias
    m_total         :   float
                        total aircraft mass
    mount_len       :   float
                        motor mount length
    """
    m_motor = 10**4.0499*AC.propulsion.motorKV**-0.5329/1000.0                              # kg | motor mass
    m_prop = (0.1178*AC.propulsion.diameter**2+(-0.3887)*AC.propulsion.diameter) / 1000.0   # kg | propeller mass, assume plastic propeller
    m_battery = (0.026373*AC.propulsion.cellNum+2.0499e-5)*(AC.propulsion.escCur/1.3/30)    # kg | battery mass, assume 30C, 5min max amp
    m_electronics = 0.8431*AC.propulsion.escCur/1000.0                                      # kg | electronics mass

    m_fuselage = 0.25                   # kg | fuselage mass (assume constant for now)
    m_payload = AC.m_payload

    MAC = AC.wing.MAC                   # m | mean aerodynamic chord of wing
    b_wing = AC.wing.b_wing             # m | wing span
    s_wing = AC.wing.calcSrefWing()
    boom_len = AC.boom_len              # m | tailboom length
    C = AC.wing.chord_vals              # m | chord values of wing
    C_t = AC.tail.htail_chord_vals      # m | chord values of horitontal tail
    dist_LG = AC.dist_LG                # m | distance between LE of wing and landing gear
    mount_len = -0.22                   # m | position of prop relative to LE of wing

    # Calculate total mass
    m_total = m_wing + m_tail + m_boom + m_landgear + m_motor + m_prop + m_battery + m_electronics + m_fuselage + m_payload + m_ballast

    # Calculate CG
    x_wing = m_wing * 0.25 * MAC
    x_tail = m_tail * ( C[0] + boom_len + C_t[0]/4. )
    x_boom = m_boom * ( C[0] + boom_len/2. )
    x_landgear = m_landgear * dist_LG
    x_motor = m_motor * mount_len
    x_elec = ( m_battery + m_electronics ) * mount_len/4.
    #x_structs = ( m_fuselage + m_payload ) * C[0]/4.
    x_structs = AC.x_struct
    x_ballast = m_ballast * mount_len/2.

    x_cg = ( x_wing + x_tail + x_boom + x_landgear + x_motor + x_elec + x_structs + x_ballast ) / m_total
    y_cg = 0.
    z_cg = 0.

    # Calculate moment of inertia
    Ixx = m_total*(.245*b_wing/2.)**2
    Iyy = m_total*(.35*(C[0] + boom_len + C_t[0])/2.)**2
    Izz = m_total*(.393*(b_wing + C[0] + boom_len + C_t[0])/2.)**2

    # Create array for output
    cg = ([x_cg, y_cg, z_cg])
    Is = ([Ixx, Iyy, Izz])

    print("Total Mass = %f kg" % m_total)
    print(" Empty Mass = %f kg" % (m_total - m_payload))
    print("	Empenage Mass = %f kg" % (m_tail + m_boom))
    print("	Payload Mass = %f kg" % m_payload)
    print("	Fuselage Mass = %f kg" % m_fuselage)
    print("	X CG = %f m from LE of wing" % x_cg)
    print("	Wing loading = %f N/m^2" % (9.81 * m_total / s_wing))
    print(" Motor Weight = %f kg" % m_motor)
    print(" Ballast Mass = %f kg" % m_ballast)
    # print("	Wing root chord = %f m"% C[0])
    # print("	Tail root chord = %f m"% C_t[0])

    return cg, Is, m_total, mount_len

def calcWeight_process(AC):
    """
    Post-process the weight calculations and assign to AC


    Inputs
    ----------
    AC              :   Class
                        Class containing all aircraft data


    Outputs
    ----------
    Modified AC for "out_aircraft"
    """

    # Calculate wing mass
    num_ribs, m_wing = getWing_mass(AC)
    AC.num_ribs = num_ribs

    # Calculate tail mass
    m_tail = getTail_mass(AC)

    # Calculate tailboom mass
    m_boom, m_landgear, m_ballast = getStruct_mass(AC)

    # Calculate CG, I, and total mass
    cg, Is, m_total, mount_len = massPostProcess(AC, m_wing, m_tail, m_boom, m_landgear, m_ballast)

    AC.x_cg = cg[0]
    AC.y_cg = cg[1]
    AC.z_cg = cg[2]
    AC.CG = cg

    AC.Ixx = Is[0]
    AC.Iyy = Is[1]
    AC.Izz = Is[2]

    AC.mass = m_total
    AC.mass_wing = m_wing
    AC.mass_tail = m_tail
    AC.mass_boom = m_boom
    AC.weight = m_total*9.81
    AC.mount_len = mount_len
    AC.mass_empty = AC.mass - AC.m_payload

    # Create AVL geometry file
    genMass(AC)
    genGeo(AC)

    return AC
