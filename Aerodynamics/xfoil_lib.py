import time
import subprocess as sp
import os
import shutil
import sys
import string
from time import localtime, strftime

# Specify path
xfoilpath = '/home/josh/xfoil'


def xfoilAlt(name, camber, max_camb_pos, thickness, max_thick_pos, Re, alpha ):
    """Alters an airfoil from an existing airfoil

    Parameters
    ----------
    name        :   string
                    airfoil name
    camber      :   float
                    camber of new airfoil
    max_camb_pos:   float
                    % chord of maximum camber
    thickness   :   float
                    t/c of new airfoil
    max_thick_pos:  float
                    % chord of maximum thickness
    Re:             float
                    Reynolds number
    alpha:          float
                    angle of attack

    Outputs
    -------
    Saves airfoil to airfoils directory

    """
    
    def Cmd(cmd):
        ps.stdin.write(cmd+'\n')

    # Alter name if needed
    try:
        os.remove(name+'_data.dat')
    except :
        pass

    # Open xfoil
    ps = sp.Popen( xfoilpath ,stdin=sp.PIPE,stderr=sp.PIPE,stdout=sp.PIPE)
    ps.stderr.close()

    # Setup
    Cmd('PLOP')
    Cmd('G')
    Cmd(' ')

    # Load geometry to alter
    Cmd('load E420.dat')

    # Alter geometry
    Cmd('GDES')
    Cmd('TSET')
    Cmd(str(thickness))
    Cmd(str(camber))
    Cmd('HIGH')
    Cmd(str(max_thick_pos))
    Cmd(str(max_camb_pos))   
    Cmd('x')
    Cmd(' ')
    Cmd(' ')

    # Increase paneling 
    # Cmd('PANE')
    Cmd('PPAR')
    Cmd('N')
    Cmd('150')
    Cmd(' ')
    Cmd(' ')

    # Calculate data
    Cmd('OPER')
    Cmd('ITER 100')
    Cmd('visc '+str(Re))
    Cmd('PACC')
    Cmd(name+'_data.dat')  # output file
    Cmd(' ')          # no dump file
    Cmd('a '+str(alpha))
    Cmd('PACC')
    Cmd('PDEL 0')
    Cmd(' ')
    Cmd(' ')
    Cmd('SAVE')
    Cmd('./airfoils/'+name+'.dat')
    Cmd(' ')
    Cmd(' ')          
          
    Cmd('quit')  # exit

    ps.stdout.close()
    ps.stdin.close()
    ps.wait()

def xfoilRunFlap(name, Re, alpha_start, alpha_end ):
    """Runs xfoil with a flap (elevator deflection)

    Parameters
    ----------
    name        :   string
                    airfoil name
    Re:             float
                    Reynolds number
    alpha_start:    float
                    angle of attack to start collecting data
    alpha_end:      float
                    angle of attack to end collecting data

    Outputs
    -------
    Saves all data to a .dat file
    
    """

    def Cmd(cmd):
        ps.stdin.write(cmd+'\n')

    # Modify name if needed
    try:
        os.remove('elev_data_flap.dat')
    except :
        pass
    # Modify name if needed
    try:
        os.remove('elev_data.dat')
    except :
        pass

    # Open xfoil
    ps = sp.Popen(xfoilpath,stdin=sp.PIPE,stderr=sp.PIPE,stdout=sp.PIPE)
    ps.stderr.close()


    Cmd(name)

    Cmd('GDES')
    Cmd('FLAP')
    Cmd('0.5')
    Cmd('0')
    Cmd('-20')   
    Cmd('x')
    Cmd(' ')
    Cmd(' ')

    # Increase paneling 
    Cmd('PPAR')
    Cmd('N')
    Cmd('250')
    Cmd(' ')
    Cmd(' ')
    Cmd(' ')

    # Calculate data
    Cmd('OPER')
    Cmd('ITER 200')
    Cmd('visc '+str(Re))
    Cmd('PACC')
    Cmd('elev_data_flap.dat')  # output file
    Cmd(' ')          # no dump file
    Cmd('aseq '+str(alpha_start)+' ' + str(alpha_end) + ' 1')


    # time.sleep(5)
    Cmd('PACC')
    Cmd('PDEL 0')

    Cmd(' ')
    Cmd(' ')  

    Cmd(name)
    # Increase paneling 
    Cmd('GDES')
    Cmd(' ')


    # calculate data
    Cmd('OPER')
    Cmd('PACC')
    Cmd('elev_data.dat')  # output file
    Cmd(' ')          # no dump file
    Cmd('aseq '+str(alpha_start)+' ' + str(alpha_end) + ' 1')
    Cmd('PACC')
    Cmd('PDEL 0')

    Cmd(' ')
           

    Cmd('quit')  # exit

    ps.stdout.close()
    ps.stdin.close()
    ps.wait()

def xfoilRun(name, Re, alpha_start, alpha_end ):
    """Runs xfoil, no deflections

    Parameters
    ----------
    name        :   string
                    airfoil name
    Re:             float
                    Reynolds number
    alpha_start:    float
                    angle of attack to start collecting data
    alpha_end:      float
                    angle of attack to end collecting data

    Outputs
    -------
    Saves all data to a .dat file
    
    """

    def Cmd(cmd):
        ps.stdin.write(cmd+'\n')

    # Modify name if needed
    try:
        os.remove(name+'_data.dat')
    except :
        pass

    # Open xfoil
    ps = sp.Popen(xfoilpath,stdin=sp.PIPE,stderr=sp.PIPE,stdout=sp.PIPE)
    ps.stderr.close()

    # Load airfoil
    Cmd('load '+name+'.dat')

    
    # Increase paneling 
    Cmd('PANE')
    Cmd('PPAR')
    Cmd('N')
    Cmd('250')
    Cmd(' ')
    Cmd(' ')

    # Calculate data
    Cmd('OPER')
    Cmd('ITER 200')
    Cmd('visc '+str(Re))
    Cmd('PACC')
    Cmd(name+'_data.dat')  # output file
    Cmd(' ')          # no dump file
    Cmd('aseq '+str(alpha_start)+' ' + str(alpha_end) + ' 1')
    Cmd('PACC')
    Cmd('PDEL')

    Cmd(' ')
    Cmd(' ')          
          
    Cmd('quit')  # exit

    ps.stdout.close()
    ps.stdin.close()
    ps.wait()

def xfoilFinal(name, camber, max_camb_pos, thickness, max_thick_pos):
    """Alters an airfoil from an existing airfoil

    Parameters
    ----------
    name        :   string
                    airfoil name
    camber      :   float
                    camber of new airfoil
    max_camb_pos:   float
                    % chord of maximum camber
    thickness   :   float
                    t/c of new airfoil
    max_thick_pos:  float
                    % chord of maximum thickness


    Outputs
    -------
    Saves airfoil to airfoils directory

    """

    def Cmd(cmd):
        ps.stdin.write(cmd+'\n')

    # Modify name if needed
    try:
        os.remove(name+'_data.dat')

    except :
        pass

    ps = sp.Popen( xfoilpath ,stdin=sp.PIPE,stderr=sp.PIPE,stdout=sp.PIPE)
    ps.stderr.close()

    Cmd('PLOP')
    Cmd('G')
    Cmd(' ')

    # Load base airfoil
    # Cmd('load ./airfoils/'+name+'.dat')
    Cmd('load E420.dat')

    # Alter geometry
    Cmd('GDES')
    Cmd('TSET')
    Cmd(str(thickness))
    Cmd(str(camber))
    Cmd('HIGH')
    Cmd(str(max_thick_pos))
    Cmd(str(max_camb_pos))   
    Cmd('x')
    Cmd(' ')
    Cmd(' ')

    # Save new geometry
    Cmd('SAVE')
    Cmd('./airfoils/'+name+'.dat')
    Cmd(' ')
    Cmd(' ')          
          
    Cmd('quit')  # exit

    ps.stdout.close()
    ps.stdin.close()
    ps.wait()




def getDataXfoil(filename):
    """Reads in previously run xfoil data

    Parameters
    ----------
    filename    :   string
                    name of xfoil run file


    Outputs
    -------
    alphas:     :   ndarray
                    Angles of attack run
    Cls:        :   ndarray
                    Cl's from run
    Cds:        :   ndarray
                    Cd's from run   
    Cms:        :   ndarray
                    Cm's from run
    LtoDs:      :   ndarray
                    L/D's (Ratios) from run                 
    """    

    # Open file and read in
    f = open(filename, 'r')
    flines = f.readlines()

    # Initialize
    alphas = []
    Cls = []
    Cds = []
    Cms =  []
   
    # Read data
    for i in range(12,len(flines)): 
        words = string.split(flines[i]) 
        alphas.append(float(words[ 0]))
        Cls.append(float(words[ 1]))
        Cds.append(float(words[ 2]))
        Cms.append(float(words[ 4]))

    # Calculate lift-to-drag ratio
    LtoDs = [a/b for a,b in zip(Cls,Cds)]

    return (alphas, Cls, Cds, Cms, LtoDs)

# def getLDmax(name):
#     filename = name+"_data.dat"
#     f = open(filename, 'r')
#     flines = f.readlines()
#     LDmax = 0
#     for i in range(12,len(flines)):
#         #print flines[i]
#         words = string.split(flines[i]) 
#         LD = float(words[1])/float(words[2])
#         if(LD>LDmax):
#             LDmax = LD
#     return LDmax