'''
pyAVL

pyAVL is a wrapper for Mark Drela's Xfoil code. The purpose of this
class is to provide an easy to use wrapper for avl for intergration
into other projects.

Developers:
-----------
- Josh Anibal (JLA)

History
-------
	v. 1.0 - Initial Class Creation (JLA, 08 2016)
'''

__version__ = 1.0

# =============================================================================
# Standard Python modules
# =============================================================================

import os, sys, string, copy, pdb, time
from multiprocessing import Queue, Process
from enum import Enum

# =============================================================================
# External Python modules
# =============================================================================

import numpy as np

# =============================================================================
# Extension modules
# =============================================================================

import pyavl as avl

# =============================================================================
# AVL Trim and Constraint Options
# =============================================================================

avl_const_options = {'alpha':['A', 'A '],
                    'beta':['B', 'B '],
                    'roll rate':['R', 'R '],
                    'pitch rate':['P', 'P '],
                    'yaw rate':['Y', 'Y'],
                    'elevator':['D1', 'PM '],
                    'rudder': ['D2', 'YM '],
                    'aileron': ['D3', 'RM ']}

def set_constraint_cond(variable, value):
    avl.conset(avl_const_options[variable][0],(avl_const_options[variable][1] +  str(value) + ' \n'))

avl_trim_options = {'bankAng':['B'],
                    'CL':['C'],
                    'velocity':['V'],
                    'mass':['M'],
                    'dens':['D'],
                    'G':['G'],
                    'X_cg': ['X'],
                    'Y_cg': ['Y'],
                    'Z_cg': ['Z']}

def set_trim_cond(variable, value):
    avl.trmset('C1','1 ', options[variable][0], (str(value) +'  \n'))

avl_queue = Queue()

# =============================================================================
# Multiprocessing AVL Run Function
# =============================================================================

class SequenceType(Enum):
    ALFA = 'alpha'
    CL = 'CL'

def run_avl_with_params(queue, sequence_key, sequence):
    # Get the AVL analysis object
    avl_analysis = queue.get()

    # Setup the AVL run file
    avl.avl()
    avl.loadgeo(avl_analysis.geo_file)
    avl.loadmass(avl_analysis.mass_file)

    # Add in constraints
    for key in avl_analysis.constraints:
        constraint = avl_analysis.constraints[key]
        variable = constraint[0]
        value = constraint[1]
        set_constraint_cond(variable, value)

    # Add in trim conditions
    for key in avl_analysis.trim_conds:
        trims = avl_analysis.trim_conds[key]
        variable = trims[0]
        value = trim[1]
        set_trim_cond(variable, value)

    # Put in a default sequence Length
    if sequence is None:
        sequence = (None,)

    # Default length 1, but loop over all items in a sequence
    for value in sequence:
        if sequence_key == SequenceType.ALFA:
            set_constraint_cond(sequence_key.value, value)
        elif sequence_key == SequenceType.CL:
            set_trim_cond(sequence_key.value, value)
        elif sequence_key == None:
            pass
        else:
            raise RuntimeError('Invalid type for sequence %s' % sequence_key)

        # Attempt to run the operation
        avl.oper()

        # Set the executable flag to true
        avl_analysis.__exe = True

        # If success, append data items
        avl_analysis.alpha.append(float(avl.case_r.alfa))  # *(180.0/np.pi) # returend in radians)
        avl_analysis.CL.append(float(avl.case_r.cltot))
        avl_analysis.CD.append(float(avl.case_r.cdtot))   # append(avl.case_r.cdvtot)  for total viscous)
        avl_analysis.CM.append(float(avl.case_r.cmtot))
        avl_analysis.span_eff.append(float(avl.case_r.spanef))

        avl_analysis.elev_def.append(float(avl.case_r.delcon[0]))
        avl_analysis.rud_def.append(float(avl.case_r.delcon[1]))

        avl_analysis.velocity.append(np.asarray(avl.case_r.vinf))

        # get section properties
        NS = avl.surf_i.nj[0]
        avl_analysis.sec_CL.append(np.asarray(avl.strp_r.clstrp[:NS]))
        avl_analysis.sec_CD.append(np.asarray(avl.strp_r.cdstrp[:NS]))
        avl_analysis.sec_Chord.append(np.asarray(avl.strp_r.chord[:NS]))
        avl_analysis.sec_Yle.append(np.asarray(avl.strp_r.rle[1][:NS]))

        # Calculate the neutral point
        avl.calcst()
        avl_analysis.NP = avl.case_r.xnp

    # Put avl_analysis back into queue
    queue.put(avl_analysis)

# =============================================================================
# AVL Data File
# =============================================================================

class avlAnalysis():
    def __init__(self, geo_file=None, mass_file=None,  aircraft_object=None):
        self.clearVals()

        self.geo_file = geo_file
        self.mass_file = mass_file

        if not(geo_file == None):
            files_exist = os.path.exists(geo_file)
            if not(mass_file is None):
                files_exist = files_exist and os.path.exists(mass_file)

            if not files_exist:
                raise RuntimeError('ERROR:  There was an error opening the file %s' % file)



        elif not(aircraft_object == None):
            raise ValueError('avlAnalysis does not yet support aircraft object inputs')

        else:
            raise ValueError('ERROR: in avlAnalysis, neither a geometry file or aircraft object was given')


    def clearVals(self):
        """Resets pertinant values that can be obtained from AVL"""
        self.__exe = False

        self.NP = None

        self.alpha =[]
        self.CL = []
        self.CD = []
        self.CM = []
        self.span_eff = []

        self.elev_def = []
        self.rud_def = []

        self.velocity = []

        self.sec_CL = []
        self.sec_CD = []
        self.sec_Chord = []
        self.sec_Yle = []

        self.constraints = dict()
        self.trim_conds  = dict()


    def addConstraint(self, variable, val):
        self.__exe = False

        if variable not in avl_const_options:
            raise ValueError('ERROR:  constraint varible not a valid option')
        else:
            self.constraints[variable] = (variable, val)


    def addTrimCondition(self, variable, val):
        self.__exe = False

        if variable not in avl_trim_options:
            raise ValueError('ERROR:  constraint varible not a valid option')
        else:
            self.trim_conds[variable] = (variable, val)


    def executeRun(self, sequence_key=None, sequence=(None,)):
        queue = Queue()
        queue.put(self)

        t = Process(target=run_avl_with_params, args=(queue, sequence_key, sequence))
        t.start()
        t.join(5)

        if t.is_alive():
            t.terminate()
            t.join()
            raise RuntimeError('Oper Times Out')
        else:
            self.__dict__ = queue.get().__dict__


    def calcNP(self):
        # executeRun must be run first
        if not self.__exe:
            raise RuntimeError('ERROR:  executeRun most be called first')


    def alphaSweep(self, start_alpha, end_alpha, increment=1):
        alphas = np.arange(start_alpha, end_alpha+increment, increment)
        self.executeRun(SequenceType.ALFA, tuple(alphas))


    def CLSweep(self, start_CL, end_CL, increment=0.1):
        CLs = np.arange(start_CL, end_CL+increment, increment)
        self.executeRun(Sequencetype.CL, tuple(alphas))



    # def calcSectionalCPDist(self):

    #     for N in [1, avl.case_i.nsurf]:

    #         J1 = avl.surf_i.jfrst(N)
    #         JN = J1 + avl.surf_i.nj - 1
    #         JINC = 1

    #         CPSCL = avl.   cpfac*  avl.case_r.cref


    #         for


    #     return



#### fortran code

#       DO N = 1, NSURF

#         J1 = JFRST(N)
#         JN = JFRST(N) + NJ(N)-1
#         JINC = 1



#            CPSCL = CPFAC*CREF


#          IP = 0
#          DO J = J1, JN, JINC
#            I1 = IJFRST(J)
#            NV = NVSTRP(J)
#            DO II = 1, NV
#              IV = I1 + II-1
#              XAVE = RV(1,IV)
#              YAVE = RV(2,IV)
#              ZAVE = RV(3,IV)
#              DELYZ = DCP(IV) * CPSCL
#              XLOAD = XAVE
#              YLOAD = YAVE + DELYZ*ENSY(J)
#              ZLOAD = ZAVE + DELYZ*ENSZ(J)

# c             XLOAD = XAVE + DELYZ*ENC(1,IV)
# c             YLOAD = YAVE + DELYZ*ENC(2,IV)
# c             ZLOAD = ZAVE + DELYZ*ENC(3,IV)

#              IF(II.GT.1) THEN
#                IP = IP+1
#                PTS_LINES(1,1,IP) = XLOADOLD
#                PTS_LINES(2,1,IP) = YLOADOLD
#                PTS_LINES(3,1,IP) = ZLOADOLD
#                PTS_LINES(1,2,IP) = XLOAD
#                PTS_LINES(2,2,IP) = YLOAD
#                PTS_LINES(3,2,IP) = ZLOAD
#                ID_LINES(IP) = 0
#              ENDIF
#              XLOADOLD = XLOAD
#              YLOADOLD = YLOAD
#              ZLOADOLD = ZLOAD
#            END DO
#          END DO
#          NLINES = IP
#          NPROJ = 2*NLINES
#          CALL VIEWPROJ(PTS_LINES,NPROJ,PTS_LPROJ)
#          CALL PLOTLINES(NLINES,PTS_LPROJ,ID_LINES)
#          CALL NEWCOLOR(ICOL)
#          CALL NEWPEN(IPN)
#         ENDIF
# C
