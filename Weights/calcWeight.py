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

from Aircraft_Class.gen_files import gen_mass, gen_geo
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
        
        
        
        The 
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
        sref_Wing = AC.wing.Sref
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
        rib_dens = AC.k_ribs          # ribs/ meter wing
        rib_dens_t = AC.k_ribs_t        # ribs/meter tail
        
        linden_LE = AC.LE_lindens           # kg/m | leading edge
        linden_TE = AC.TE_lindens           # kg/m | Main Wing Trailing edge mass
        linden_spar = AC.spar_lindens         # kg/m | Main Wing Spar 
        k_ribs = 0.0065             # kg | Main Wing Ribs        linden_LE_t = 0.075  # kg/m | leading edge tail
        linden_spar_t = 0.25        # kg/m | tail spar
        k_ribs_t = 0.003            # kg | mass of ribs in the tail
        static_margin = 0.15        # Static margin 
        payload_max_dimension = 0.07  # m | masimum dimension of payload, width depth height, that fuselage will build around 
        linden_boom = 0.107         # kg/m
        m_motor = AC.m_motor         # kg
        m_battery = AC.m_battery        # kg
        m_prop = AC.m_propeller               # kg 
        m_electronics = AC.m_electronics      # kg
        payload_diameter = 0.1      # m side lenght or maximum diamter of a payload
        payload_depth = 0.00635     # m , quarter of an inch thick payload
        max_payloadnum = 12         # Number of maximum payloads
        
        m_payload = 2.26796         # kg
        balsa_Density = 1600        # kg/m^3
        fuselage_thickness = 0.003175  # m
        fuselage_area = (payload_diameter + fuselage_thickness) * 4
        volume_payload = fuselage_area * payload_depth
        mass_fuselage_payload = volume_payload * balsa_Density
        
        ###############################################
        num_ribs = math.ceil(b_wing * rib_dens)
        m_ribs = k_ribs * num_ribs * (MAC / 0.5)
        m_LE = linden_LE * b_wing
        m_TE = linden_TE * b_wing
        m_spar = linden_spar * b_wing
        
        m_wing = m_ribs + m_LE + m_TE + m_spar
        # calc mass of the tail
        num_ribs_t = math.ceil((b_htail + b_vtail) * rib_dens_t) 
        m_ribs_t = k_ribs_t * num_ribs_t
        m_LE_t = linden_LE * (b_htail + b_vtail)
        m_TE_t = linden_TE * (b_htail + b_vtail)
        m_spar_t = linden_spar_t * (b_htail + b_vtail)
        ultrakote_Density = .1318 #kg/m^2
        m_tail = m_ribs_t + m_LE_t + m_TE_t + m_spar_t

        wet_area_w = 2*(sref_Wing)
        wet_area_t = 2*(b_htail+b_vtail)*C_t[0]
        m_wing = m_wing + wet_area_w*ultrakote_Density
        m_tail = m_tail + wet_area_t*ultrakote_Density
        # mass boom
        m_boom = boom_len * linden_boom 
        
        # mass landing gear
        height_LG = np.sin(10 * np.pi / 180) * (boom_len - dist_LG)
        m_landgear_rear = 0.69 * height_LG * 2
        m_landgear = m_landgear_rear + 0.163
        
        #########
        m_x = m_wing * 0.25 * MAC + m_landgear * dist_LG + m_tail * boom_len + m_boom * boom_len / 2
        m_total = m_wing + m_tail + m_landgear + m_boom + m_motor + m_battery + m_electronics
        def x_CG_loc(mount_len):
            
            cg = (m_x + mount_len * m_motor + mount_len / 2 * m_battery) / m_total
        
            return (cg - MAC / 4)
        
        # adjust the motor mount length until the CG is at c/4
        mount_len = fsolve(x_CG_loc, np.array([1]))[0]
        
        
        Ixx = (m_motor + m_prop) * mount_len ** 2 + m_battery * (mount_len / 2) ** 2 + m_landgear * dist_LG ** 2 + m_tail * boom_len ** 2 + 1 / 3 * m_boom * boom_len ** 2
        Iyy = 1 / 12 * (m_wing * b_wing ** 2 + m_tail * b_htail ** 2)
        Izz = Ixx + Iyy

        # x_cg = MAC/4
        z_cg = 0
        
        
            # DETERMINE THE FUSELAGE LENGTH
                    
        # These variables need to be inputs in the input file
        SM = 0.15

        # Neutral point estimation
        NP = 0.25*MAC
        
        
        
        # Add payload plates until static margin requirement is fulfilled. Defines the minimum fuselage length for achieving static stability.
        payload_num = 0
        payload_counter = 0

        x_cg = x_CG_loc(mount_len)
        LHS = SM * MAC + NP - x_cg
        m_total = m_wing + m_tail + m_landgear + m_boom + m_motor + m_battery + m_electronics + mass_fuselage_payload
        for i in range(1, 100):
                
                # Start fuselage iteration with x-axis increment of payload plate
                payload_counter = i
                fuselage_length = payload_depth * payload_counter;
                fuselage_mass = fuselage_length * (mass_fuselage_payload)
                
                m_total = m_wing + m_tail + m_landgear + m_boom + m_motor + m_battery + m_electronics + m_payload*(i) + fuselage_mass
                x_cg_fuselage = payload_depth*(i) * (mass_fuselage_payload + m_payload) / m_total
                
                if max_payloadnum > i:
                    m_total = m_wing + m_tail + m_landgear + m_boom + m_motor + m_battery + m_electronics + m_payload*(max_payloadnum) + fuselage_mass
                    x_cg_fuselage = (payload_depth*(i) * (mass_fuselage_payload) + m_payload*(max_payloadnum)) / m_total
                    if x_cg_fuselage >= LHS: 
                        break
                elif x_cg_fuselage >= LHS: 
                    break
                
        fuselage_length = payload_depth * payload_counter;
        fuselage_mass = fuselage_length * (mass_fuselage_payload)
        
        
        
        # # total mass
        
        m_total = m_wing + m_tail + m_landgear + m_boom + m_motor + m_battery + m_electronics + fuselage_mass
        total_payload_mass = payload_counter*m_payload
        
        AC.Ixx = Ixx
        AC.Iyy = Iyy
        AC.Izz = Izz
        AC.x_cg = x_cg
        AC.z_cg = z_cg
        AC.mass= m_total
        AC.weight = m_total*9.81
        AC.CG = ([AC.x_cg, 0.0, AC.z_cg])

        
        
        
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
#         print('Sref_Wing: ' + str(sref_Wing))
#         print('Mount length: ' + str(mount_len))
#         print('MAC: ' + str(MAC))
#         print('Xle: ' + str(Xle))
#         print('x_cg: ' + str(x_cg) + '  z_cg: ' + str(z_cg))
#         print('Total Mass: ' +str(m_total))
#         print('Total Payload Mass: ' +str(total_payload_mass))
              
        # Create AVL geometry file
        gen_mass(AC)
        gen_geo(AC)
        
        
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
                    
