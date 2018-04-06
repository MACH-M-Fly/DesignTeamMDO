.. DesignTeamMDO documentation getting_started file

===============
Getting Started
===============

This brief tutorial will get the DesignTeamMDO code installed on your computer and all the other Python dependancies required installed. This assumes that Python is already installed. At the moment, the code requires Python 2 to function properly. These dependancies include:

* pip
* matplotlib
* numpy
* OpenMDAO 1.7.3
* scipy
* sympy
* pykrige


Clone The Directory
-------------------

To get a copy of the code on your local computer you can run the following command in your terminal or use a GUI git tool (the terminal is easiest in my opinion).::

    git https://github.com/MACH-M-Fly/DesignTeamMDO.git

Get Dependences
---------------

First before we can run the code we need to install all of the packages used. Thanks to Ian, this is quite simple. 99.9 % of the time all that needs to be done is run the setup.sh script in the top-level directory. To run the script simply type the following command into the terminal.::

    sh setup.sh

Usually, with Python, to install a package one just needs to use shell `pip install thePackageName'. The script just automates this process for each of the packages in the `setup.sh` file.
