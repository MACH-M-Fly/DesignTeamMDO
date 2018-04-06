## Design team MDO for MACH and M-Fly

[See our documentation site](https://mach-m-fly.github.io/DesignTeamMDO/ "Documentation Site!")

Purpose: The Joint Design Team MDO is used for both the AIAA DBF Team (MACH) and the SAE Aero Design Team (M-Fly) at U of M. 
This MDO allows for both teams to work together on an MDO to suit needs of both teams.



Contributors:  
MACH  

- Josh Anibal 
- Kohki
- Miles
M-Fly   


- Chris Reynolds 
- Beldon Lin
- Ian 


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
	- **Update with airfoil estimation code for cl/cd for velocity estimate when available**
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

Version 3:
- Make it work in OpenMDAO 2.1
- Airfoil design variables
- Stability (non-AVL)
- AUVSI Endurance mission
	- Battery model
- OpenMPI/Parallel
- Component weights scale with aircraft size



