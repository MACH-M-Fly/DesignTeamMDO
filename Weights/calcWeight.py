#Input  Python Libraries
from __future__ import division

from openmdao.api import IndepVarComp, Component, Problem, Group
from openmdao.api import ScipyOptimizer, ExecComp, SqliteRecorder
from openmdao.drivers.pyoptsparse_driver import pyOptSparseDriver
from openmdao.drivers.latinhypercube_driver import OptimizedLatinHypercubeDriver

from scipy.optimize import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os

import math

from Aircraft_Class.gen_files import genMass, genGeo
from Input import AC

class calcWeight(Component):
    """
        Weight: Uses current iteration of the aircraft and inputs to calculate and 
        estimate the total weight and payloads of the aircraft
        Inputs:
            - Aircraft_Class: Input aircraft instance
            - Design variables: These will be modified based on new MDO iteration
        Outputs:
            - Aircraft_Class: Output and modified aircraft instance 
        Version 2 Implementation
        
        Payload prediction will refine the size of the fuselage. The current fuselage length is determined strictly 
        by satisfying the static margin criteria in the input file. The payload prediction weight will define the 
        upper bound length of the fuselage.
        
        upper_Fuselage_Length = AC.payload;
        
    """
     
# set up interface to the framework
    def __init__(self): 
        super(calcWeight, self).__init__()
        
        # Input instance of aircraft - before modification
        self.add_param('in_aircraft',val=AC, desc='Input Aircraft Class')

        # Output instance of aircraft - after modification
        self.add_output('out_aircraft',val=AC, desc='Output Aircraft Class')
    

    def solve_nonlinear(self, params, unknowns, resids):
        # make all input variables local for ease
        AC = params['in_aircraft']
        
        boom_len = AC.boom_len
        dist_LG = AC.dist_LG
          
          
        C = AC.wing.chord_vals
        b_wing = AC.wing.b_wing

        Xle = AC.wing.Xo
            
        Yle = AC.wing.Yo
        sref_Wing = AC.wing.sref
        b_vtail = AC.tail.b_vtail
        b_htail = AC.tail.b_htail
        Xle_t = AC.tail.Xo
        Yle_t = AC.tail.Yo
        C_t = AC.tail.htail_chord_vals
        
        CDp = 0.0116
        
        def shape_func(y, A, B):
            # print('yes')
            return (A ** 2 * y - A * (A - B) / (b_wing / 4) * y ** 2 + (A - B) ** 2 / (3 * (b_wing / 4) ** 2) * y ** 3)
        
        MAC = AC.wing.MAC
        
        # calc mass of the Wing
        # current stats are based off of M-9
        rib_dens = 10.               # ribs/ meter wing
        rib_dens_t = 10.            # ribs/meter tail

        den_boom = AC.spar_den             # kg/m^3 | density of aluminum
        
        linden_LE = AC.LE_lindens           # kg/m | leading edge
        linden_TE = AC.TE_lindens           # kg/m | Main Wing Trailing edge mass
        linden_spar = AC.spar_lindens       # kg/m | Main Wing Spar 
        linden_spar_t = AC.spar_lindens_t    # kg/m | tail spar
        linden_LE_t = AC.LE_lindens_t       # kg/m | leading edge tail
        linden_TE_t = AC.TE_lindens_t       # trailing edge tail kg/m    
        SM = 0.15                           # Static margin 
        payload_max_dimension = 0.07        # m | masimum dimension of payload, width depth height, that fuselage will build around 
        linden_boom = 1.0471                  # kg/m
        m_motor = AC.m_motor                # kg
        m_battery = AC.m_battery            # kg
        m_prop = AC.m_propeller             # kg 
        m_electronics = AC.m_electronics    # kg
        payload_diameter = 0.1              # m side lenght or maximum diamter of a payload
        payload_depth = 0.00635             # m , quarter of an inch thick payload
        max_payloadnum = 12                 # Number of maximum payloads
        m_payload = 2.26796                 # kg
        balsa_Density = 1600                # kg/m^3
        fuselage_thickness = 0.003175       # m
        fuselage_area = (payload_diameter + fuselage_thickness) * 4
        volume_payload = fuselage_area * payload_depth
        mass_fuselage_payload = volume_payload * balsa_Density
        
        ###############################################
        num_ribs = math.ceil(b_wing * rib_dens)
        AC.num_ribs = num_ribs
        m_ribs = AC.k_ribs * num_ribs* (MAC / 0.05)
        m_LE = linden_LE * b_wing
        m_TE = linden_TE * b_wing
        m_spar = linden_spar * b_wing

        m_wing_alum_spar = b_wing*.5 * np.pi*(AC.wing.spar_dim[0]**2 - AC.wing.spar_dim[1]**2) * den_boom
        
        m_wing = m_ribs + m_LE + m_TE + m_spar + m_wing_alum_spar

        # calc mass of the tail
        num_ribs_ht = math.ceil(b_htail*rib_dens_t)
        num_ribs_vt = math.ceil(b_vtail*rib_dens_t)
        m_ribs_ht = AC.k_ribs_t*num_ribs_ht*(AC.tail.MAC_ht)/0.1
        m_ribs_vt = AC.k_ribs_t*num_ribs_vt*(AC.tail.MAC_vt)/0.1
        m_ribs_t = m_ribs_ht + m_ribs_vt
        # num_ribs_t = math.ceil((b_htail + b_vtail) * rib_dens_t) 
        # m_ribs_t = AC.k_ribs_t * num_ribs_t
        m_LE_t = linden_LE_t * (b_htail + b_vtail)
        m_TE_t = linden_TE_t * (b_htail + b_vtail)
        m_spar_t = linden_spar_t * (b_htail + b_vtail)
        print("b_htail", b_htail)
        print("b_vtail", b_vtail)
        print("Number of Ribs in HTail", num_ribs_ht)
        print("Number of Ribs in VTail", num_ribs_vt)
        print("Kg per rib", AC.k_ribs_t)
        print("Mass of Tail Ribs", m_ribs_t)
        print("Mass of LE", m_LE_t)
        print("Mass of TE", m_TE_t)
        print("Mass of Tail Spar", m_spar_t)

        ultrakote_Density = .1318                                   #kg/m^2
        m_tail = m_ribs_t + m_LE_t + m_TE_t + m_spar_t
        wet_area_w = 2*(sref_Wing)
        wet_area_t = 2*(b_htail+b_vtail)*C_t[0]
        m_wing = m_wing + wet_area_w*ultrakote_Density
        m_tail = m_tail + wet_area_t*ultrakote_Density
        
        # mass boom
        AC.tail.boom_Dim
        # m_boom = boom_len * linden_boom 
        m_boom = boom_len * np.pi*(AC.tail.boom_Dim[0]**2 - AC.tail.boom_Dim[1]**2) * den_boom
        
        # mass landing gear
        height_LG = np.sin(10 * np.pi / 180) * (boom_len - dist_LG)
        m_landgear_rear = 0.69 * height_LG * 2
        m_landgear = m_landgear_rear + 0.163
        #########
        m_total = m_wing + m_tail + m_landgear + m_boom + m_motor + m_battery + m_electronics
        
        # def x_CG_loc(mount_len):
            
        #     cg = (m_x + mount_len * m_motor + mount_len / 2 * (m_battery+m_electronics)) / m_total
        
        #     return (cg - MAC / 4)
        
        # # adjust the motor mount length until the CG is at c/4
        # mount_len = fsolve(x_CG_loc, np.array([1]))[0]  

        #x_cg = MAC/4

        # x_cg = MAC/4
        z_cg = 0
        
        # DETERMINE THE FUSELAGE LENGTH
                    
        # These variables need to be inputs in the input file
        if hasattr(AC , 'SM'):
            SM = AC.SM
        else:
            SM = 0.15
    
        # Neutral point retrieval from aircraft class
        if hasattr(AC , 'NP'):
            NP = AC.NP
        else:
             NP = 0.25*MAC

        fuselage_mass = 1.0 #kg

        
        # # Add payload plates until static margin requirement is fulfilled. Defines the minimum fuselage length for achieving static stability.
        # payload_num = 0
        # payload_counter = 0

        # RHS = (x_cg-NP)/MAC
        # m_total = m_wing + m_tail + m_landgear + m_boom + m_motor + m_battery + m_electronics + mass_fuselage_payload
        
        # for i in range(1, 100):
                
        #     # Start fuselage iteration with x-axis increment of payload plate
        #     payload_counter = i
        #     fuselage_length = payload_depth * payload_counter;
        #     fuselage_mass = fuselage_length * (mass_fuselage_payload)
                
        #     m_total = m_wing + m_tail + m_landgear + m_boom + m_motor + m_battery + m_electronics + m_payload*(i) + fuselage_mass
        #     x_cg_fuselage = fuselage_length/2 * (mass_fuselage_payload*payload_counter + m_payload*payload_counter) / m_total
        #     if x_cg >= (RHS*MAC + NP):
        #         break
            
        #     elif max_payloadnum > i:
        #         m_total = m_wing + m_tail + m_landgear + m_boom + m_motor + m_battery + m_electronics + m_payload*(payload_counter) + fuselage_mass
        #         x_cg_fuselage = fuselage_length/2 * (mass_fuselage_payload*payload_counter + m_payload*payload_counter) / m_total
        #         x_cg = x_cg + x_cg_fuselage
        #         RHS = (x_cg-NP)/MAC
        #         if x_cg >= (RHS*MAC + NP):: 
        #             break

        #     elif max_payloadnum <= i:
        #         m_total = m_wing + m_tail + m_landgear + m_boom + m_motor + m_battery + m_electronics + m_payload*(max_payloadnum) + fuselage_mass*payload_counter
        #         x_cg_fuselage = fuselage_length/2 * (mass_fuselage_payload*payload_counter + m_payload*max_payloadnum) / m_total
        #         x_cg = x_cg + x_cg_fuselage
        #         break
                            
        # fuselage_length = payload_depth * payload_counter;
        # fuselage_mass = fuselage_length * (mass_fuselage_payload)

    
        payload_counter = 0
  
        # # total mass
        total_payload_mass = 0.5
        m_x = m_wing * 0.25 * MAC + m_landgear * dist_LG + m_tail * (C[0]+ boom_len + C_t[0]/4.) + m_boom * (C[0]+(boom_len / 2.))
        m_total = m_wing + m_tail + m_landgear + m_boom + m_motor + m_battery + m_electronics + fuselage_mass + total_payload_mass
        
        mount_len = - 0.15 
        total_payload_mass = 0.5
        x_cg = (m_x + mount_len * m_motor + mount_len / 4. * (m_battery+m_electronics) + (fuselage_mass+total_payload_mass)*(C[0]/4.))/ m_total

        Ixx = (m_total/9.81)*(.245*b_wing/2)**2 
        Iyy = (m_total/9.81)*(.35*(C[0]+boom_len+C_t[0])/2)**2 
        Izz = (m_total/9.81)*(.393*(b_wing + C[0] + boom_len + C_t[0] )/2)**2
        
        AC.Ixx = Ixx
        AC.Iyy = Iyy
        AC.Izz = Izz
        AC.x_cg = x_cg
        # AC.x_cg = 0.25*MAC
        AC.y_cg = 0.0
        AC.z_cg = z_cg
        AC.mass = m_total
        AC.mass_tail = m_tail
        AC.weight = m_total*9.81
        AC.CG = ([AC.x_cg, AC.y_cg, AC.z_cg])
        AC.mount_len = mount_len
#         print('============== input =================')
#         print('b_wing= ' + str(b_wing))
#         print('C= ' + str(C))
#         print('b_htail= ' + str(b_htail))
#         print('C_t= ' + str(C_t))        
#         print('dist_LG= ' + str(dist_LG))
#         print('boom_len= ' + str(boom_len))
#         print(' ')
#         
#         print('============== output =================')
#         print('sref_Wing: ' + str(sref_Wing))
#         print('Mount length: ' + str(mount_len))
#         print('MAC: ' + str(MAC))
#         print('Xle: ' + str(Xle))
        # print('x_cg: ' + str(x_cg) + '  z_cg: ' + str(z_cg))
        print('Total Mass: ' + str(m_total))
        print('Total Payload Mass: ' + str(total_payload_mass))
        print('X Cg:  ' + str(x_cg))
        print('Chord:  ' + str(C[0]))    
        print('Tail Chord:  ' + str(C_t[0])) 
        print('Fuselage Mass:  ' + str(fuselage_mass)) 
        print('Tail Mass:  ' + str(m_tail)) 
        print('Wing Mass:  ' + str(m_wing))   
        print('Boom Mass:  ' + str(m_boom))
        print('Boom Lenght:  ' + str(boom_len)) 
        print('Rib Mass:  ' + str(m_ribs)) #_tail = m_ribs_t + m_LE_t + m_TE_t + m_spar_t
        print('LE Mass:  ' + str(m_LE))
        print('TE Mass:  ' + str(m_TE)) 
        print('Spar Mass:  ' + str(m_spar))        
        # Create AVL geometry file
        genMass(AC)
        genGeo(AC)
        
        
        # # ========================== PLOT ===============================
        # wing_edge = Xle + [sum(x) for x in zip(Xle, C)][::-1] + [sum(x) for x in zip(Xle, C)] + [1 * x for x in Xle[::-1]]
        # wing_pos = Yle + Yle[::-1] + [-1 * x for x in Yle] + [-1 * x for x in Yle[::-1]]
        
        # tail_edge = Xle_t + [sum(x) for x in zip(Xle_t, C_t)][::-1] + [sum(x) for x in zip(Xle_t, C_t)] + [1 * x for x in Xle_t[::-1]]
        # tail_pos = Yle_t + Yle_t[::-1] + [-1 * x for x in Yle_t] + [-1 * x for x in Yle_t[::-1]]
        
        # print("calcWeight Mass", m_total)
        # print("Wing Mass", m_wing)
        # print("Tail Mass", m_tail)
        
        unknowns['out_aircraft'] = AC
        # -- END OF FILE --        

def getWing_mass(AC):

def getTail_mass(AC):