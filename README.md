# Joint_MDO_v1
Design team MDO for MACH and M-Fly

Creators:
- Chris Reynolds (CLR)
- Josh Anibal (JLA)
- Beldon Lin (BCL)

Purpose: The Joint Design Team MDO is used for both the AIAA DBF Team (MACH) and the SAE Aero Design Team (M-Fly) at U of M. 
This MDO allows for both teams to work together on an MDO to suit needs of both teams.

Version 1:
- Aerodynamic optimization only 

Modules:
- input_file.py: Input file, well documented, the only code a user needs to modify to run.
- aircraft_class.py: Processes input file, creates a class for passing around aircraft attributes.
- pyAVL.py: Aerodynamic analysis
- To be added: Weights.py: Weights analysis (mass properties).
- To be added: Performance.py: Lap time and payload esimation



Version 2:

- Move away from classed based model for moving information around 
	- easier to implement derivaties some components
- Compare take off simulations
- Make the misson segments more modular 
- Improve post processing
- Aero structural optimization 
	- pros cons of switching to openaerostruct 
- Parasitic drag calculation 
- Resize the tail based on tail volume coefficients 
- Dynamic Stability requirements 

- Change objective functions ( MACH and Mfly )

- Airfoil Optimization 

- Machine Learning with Motocalc
- Clean up what is printed to the terminal 
