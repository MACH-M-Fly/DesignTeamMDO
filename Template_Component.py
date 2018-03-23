# python stantdard libraries
from __future__ import division

# addition python libraries
import numpy as np

# open MDAO libraries
from openmdao.api import Component


# Change the name of your componenet here
class exampleComponent(Component):
    """
        exampleComponent: Uses the current iteration of the aircraft, performances
        "input analysis name" analysis
        Inputs:
            - Aircraft_Class: Input aircraft instance
            - Design variables: These will be modified based on new MDO iteration
        Outputs:
            - Aircraft_Class: Output and modified aircraft instance
    """

    def __init__(self, ac):
        super(exampleComponent, self).__init__()

        # Input instance of aircraft - before modification
        self.add_param('in_aircraft', val=ac, desc='Input Aircraft Class')

        # Output instance of aircaft - after modification
        self.add_output('out_aircraft', val=ac, desc='Output Aircraft Class')

    def solve_nonlinear(self, params, unknowns, resids):
        # Used passed in instance of aircraft
        AC = params['in_aircraft']

        # Insert component analysis functions here - This is an example from the aeroAnalysis component
        # Add attributes to AC
        AC.CL, AC.CD, AC.CM, AC.NP = getAeroCoef()

        # Set output to updated instance of aircraft
        unknowns['out_aircraft'] = AC
