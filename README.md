# Joint_MDO_v1
Design team MDO for MACH and M-Fly

**NOTE** This is specifically for the 405 MDO validation project with SAE Micro class aircraft

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


- Change objective functions
	- MACH (Kohki)
	- Mfly (Nick)
- Compare take off simulations (Ian)
	- Use MFly Data
- Parasitic drag calculation (Nick)
- Airfoil DVs (camber, thickness, camber max loc, thickness max loc) (Josh)
- Clean up what is printed to the terminal 
- Improve post processing
	- Movie (Josh)
- Fuselage Shaping
- Resize the tail based on tail volume coefficients (when not a DV)
- Machine Learning with Motocalc to create a model to use in optimzation (Beldon)
- Move away from classed based model for moving information around 
	- easier to implement derivaties some components
- Make the misson segments more modular 
- Dynamic Stability requirements 
- Aero structural optimization 
	- pros cons of switching to openaerostruct 
- OpenMPI integration for parallel computing 
- integrate PyoptSparse for gradient free optimizers 




