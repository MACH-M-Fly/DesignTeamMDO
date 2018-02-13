# python stantdard libraries
from __future__ import division

import copy

# open MDAO libraries
from openmdao.api import Component

# Import self-created components
from Input import updateAircraft, AC


class createAC(Component):
    """
    OpenMDAO component for updating the aircaft (AC) after each iteration of MDO

    Inputs
    -------
    Aircraft_Class  :   class
                        in_aircraft class
    design variables: 	many variables
                        Variables for modification


    Outputs
    -------
    Aircraft_Class  :   class
                        out_aircraft class

    """

    def __init__(self, ac):
        super(createAC, self).__init__()

        if ac is None:
            ac = copy.deepcopy(AC)

        # Input instance of aircraft - before modification
        self.add_param('def_aircraft', val=ac, desc='Aircraft Class')

        # Parameter(s) of aicraft to be modified within this component
        # - I.e. design variables
        # - Uncomment the variables to be used
        self.add_param('b_wing', val=ac.wing.b_wing, desc='wing span')
        # self.add_param('dihedral',val = 0.0, desc='wing dihedral')
        self.add_param('sweep', val=ac.wing.sweep, desc='wing sweep')
        self.add_param('chord', val=ac.wing.chord, desc='wing chord')
        self.add_param('dist_LG',val=ac.dist_LG, desc = 'Distance b/w LG and CG')
        self.add_param('boom_len', val=ac.tail.boom_len, desc='Length of Tailboom')
        # self.add_param('camber',val = np.array([0.0 , 0.0, 0.0,0.0]), desc='Wing Camber')
        # self.add_param('max_camber',val = np.array([0.0 , 0.0, 0.0,0.0]), desc='Percent chord of max camber')
        # self.add_param('thickness',val = np.array([0.0 , 0.0, 0.0,0.0]), desc='wing thickness')
        # self.add_param('max_thickness',val = np.array([0.0 , 0.0, 0.0,0.0]), desc='Percent chord of max thickness')	# Vertical Tail Span
        # self.add_param('Ainc',val = p.array([0.0 , 0.0, 0.0,0.0]), desc = 'Angle of Incidence')
        self.add_param('htail_chord', val=ac.tail.htail_chord, desc='Horiz. tail chord')
        self.add_param('vtail_chord', val=ac.tail.vtail_chord, desc='Vert. tail chord')
        self.add_param('b_htail', val=ac.tail.b_htail, desc='Horiz. tail span')
        self.add_param('b_vtail', val=ac.tail.b_vtail, desc='Vert. tail span')

        self.add_param('motor_KV', val=ac.propulsion.motorKV, desc='Motor KV')
        self.add_param('prop_diam', val=ac.propulsion.diameter, desc='Propeller Diameter')
        self.add_param('prop_pitch', val=ac.propulsion.pitch, desc='Propeller Pitch')

        self.add_param('m_payload', val=ac.m_payload, desc='Mass Payload')

        # Output instance of aircaft - after modification
        self.add_output('aircraft', val=ac, desc='Output Aircraft')

        # Output the tail volume coefficients (for constraints)
        self.add_output('cHT', val=0.0, desc='Horizontal Tail Volume Coefficient')
        self.add_output('cVT', val=0.0, desc='Vertical Tail Volume Coefficient')

        # Output the Relative Boom-Length
        self.add_output('delta_boom_len', val=0.0, desc='Delta Boom Length - Positive if Wing and Tail Don\'t Intersect')

    def solve_nonlinear(self, params, unknowns, resids):
        # Used passed in instance of aircraft
        # ac = params['def_aircraft']
        ac = copy.deepcopy(params['def_aircraft'])

        ac.m_payload = params['m_payload']

        # Uncomment to reveal more design variables for use in the MDO
        ac.wing.b_wing = params['b_wing']
        # AC.wing.dihedral = params['dihedral']
        ac.wing.sweep = params['sweep']
        ac.wing.chord = params['chord']
        ac.dist_LG = params['dist_LG']
        ac.boom_len = params['boom_len']
        # AC.camber = params['camber']
        # AC.max_camber = params['max_camber']
        # AC.thickness = params['thickness']
        # AC.max_thickness = params['max_thickness']
        # AC.wing.Ainc = params['Ainc']
        ac.tail.htail_chord = params['htail_chord']
        ac.tail.vtail_chord = params['vtail_chord']
        ac.tail.b_htail = params['b_htail']
        ac.tail.b_vtail = params['b_vtail']

        ac.propulsion.motorKV = params['motor_KV']
        ac.propulsion.diameter = params['prop_diam']
        ac.propulsion.pitch = params['prop_pitch']

        # Update aircraft before analysis
        updateAircraft(ac)

        # Set output to updated instance of aircraft
        unknowns['aircraft'] = ac

        # Calculate Volume Coefficients
        unknowns['cHT'] = ac.boom_len * ac.tail.calcSrefHTail() / (ac.wing.calcMAC() * ac.wing.calcSrefWing())
        unknowns['cVT'] = ac.boom_len * ac.tail.calcSrefVTail() / (ac.wing.b_wing * ac.wing.calcSrefWing())

        # Calculate delta-boom-length
        unknowns['delta_boom_len'] = ac.boom_len - 0.75 * ac.wing.chord[0] - 0.25 * ac.tail.htail_chord[0]
