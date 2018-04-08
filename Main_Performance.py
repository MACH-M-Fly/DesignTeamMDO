from Input import AC
import Performance.objPerformance as perf
import Aerodynamics.aeroAnalysis as aero
import Weights.calcWeight as weight
import Constants as constants
import math



def calcPerformance(AC, cgLE, cgLG, Iyy, wind):

    #==========================================================
    # Calculate Weights
    #==========================================================

    AC = weight.calcWeight_process(AC)
    print(AC.CG)
    AC.CG = [cgLE, 0, 0]
    AC.dist_LG = cgLG
    AC.Iyy = Iyy


    #==========================================================
    # Calculate Aero Analysis
    #==========================================================
    try:
        AC.alpha, AC.CL, AC.CD, AC.CM, AC.NP, AC.sec_CL, AC.sec_Yle, sec_Chord, velocity = aero.getAeroCoef()
    except RuntimeError as e:
        print('TRIM FAILED')
        print(e)
        AC.alpha = [ 0 ]
        AC.CL = lambda x: 0
        AC.CD = lambda x: 0
        AC.CM = lambda x: 0
        AC.NP = 0
        AC.sec_CL = [ [ 0 ] ]
        AC.sec_Yle = [ [ 0 ] ]
        sec_Chord = [ [ 0 ] ]
        velocity = [ [ 0 ] ]
        #return False # TODO - FIX THIS TO PROPERLY ACCOUNT FOR NO-TRIM

    # Static Margine calculation
    SM = (AC.NP - AC.CG[0]) / AC.wing.MAC
    AC.SM = SM

    # Calculate cruise velocity
    AC.vel, AC.ang = aero.calcVelCruise(AC.CL, AC.CD, AC.weight, AC.wing.sref, AC.tail.sref_ht, AC)

    # Get gross lift
    flapped = False
    AC.gross_F, AC.wing_f, AC.tail_f = aero.grossLift(AC.vel, AC.ang, AC.wing.sref, AC.tail.sref_ht, flapped, AC.CL, AC)

    AC.sec_L = aero.calcSecLift(velocity, AC.sec_CL, sec_Chord)

    # print('Wing Lift = %f' % AC.wing_f)
    # print('Tail Lift = %f' % AC.tail_f)

    # print("Cruise Velocity = %f m/s" % AC.vel)
    # print("Cruise AOA = %f degrees" % AC.ang)
    # print("CL of aircraft = %f" % AC.CL(AC.ang))
    # print("CD of aircraft = %f" % AC.CD(AC.ang))
    # print("SM = %f" % AC.SM)

    #==========================================================
    # Calculate Takeoff Performance
    #==========================================================

    sum_y, dist, vel, ang, ang_vel, time = perf.runwaySim_small_wind(AC.CL, AC.CD, AC.CM, AC.wing.sref, AC.tail.sref_ht, AC.weight, AC.boom_len,
                                              AC.dist_LG, AC.wing.MAC, AC.Iyy, AC, wind)

    # print('############')
    # print('Performance')
    # print('############')
    # print('Takeoff Dist:  %.3f m' % dist)
    # print('Takeoff Time:  %.3f s' % time)
    # print('Takeoff Velo:  %.3f m/s' % vel)
    # print('Sum Y: %.3f ' % sum_y)

    return dist, vel


#====================================
# Main loop
#====================================

# Flight data
rhoList = [1.272698989, 1.274389765, 1.251931086, 1.255450418]
payloadList = [0.916, 0.916, 0.916, 1.574]
cgLGList = [0.046482, 0.046482, 0.046482, 0.06527]
cgLEList = [0.077978, 0.077978, 0.077978, 0.059182]
IyyList = [4.27,4.27,4.27,5.71]
windList = [0, 0, 0, 0]

distList = []
velList = []

for i in range(4):
    # Modify aircraft
    constants.Rho = rhoList[i]
    AC.m_payload = payloadList[i]

    dist, vel = calcPerformance(AC, cgLGList[i], cgLEList[i], IyyList[i], windList[i])
    distList.append(dist)
    velList.append(vel)
    print('Flight '+str(i+1)+' Takeoff Distance:')
    print(dist)

print(distList)
print(velList)

