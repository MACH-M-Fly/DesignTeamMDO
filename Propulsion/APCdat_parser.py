from __future__ import print_function
import numpy as np
import math

# Kriging Library
from pykrige.ok3d import OrdinaryKriging3D
from pykrige.uk3d import UniversalKriging3D


# Plotting
# from mpl_toolkits.mplot3d import axes3d
# import mayavi.mlab as mlab


# Helper function that determines whether a string can be converted or not
def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


# Reads APC .dat files
def propDataParse(filename):
    '''Reads in APC data files and outputs coefficients '''
    data = open('Propulsion/Data/' + filename).read().split()
    # data = open('Data/' + filename).read().split()
    # print data

    # Clean up -NaN clumping
    dataClean = []
    for element in data:
        a = element.split('-')
        for j in a:
            if j:
                dataClean.append(j)
    data = dataClean

    lengthFile = len(data)
    perfDict = {}
    perfArray = []
    velArray = []
    thrustArray = []
    torqueArray = []
    dataMode = 0
    dataIndex = 0
    dictKey = ''
    vel = 0;
    j = 0

    # Split into dictionary
    for i in range(lengthFile):

        if not dataMode:
            # Take in RPM
            if data[i] == 'RPM' and data[i + 1] == '=':
                dictKey = data[i + 2]

            # (Lbf) anchor
            if data[i] == '(Lbf)':
                dataMode = 1
                dataIndex = 0

        else:
            # Reached end of the thrust curve
            if not isfloat(data[i]):
                dataMode = 0
                # Put into dictionary
                perfDict[dictKey] = [np.array(velArray), np.array(thrustArray), np.array(torqueArray)]
                velArray = []
                thrustArray = []
                torqueArray = []

            else:
                # Read in velocity
                if dataIndex == 0:
                    velArray.append(float(data[i]))
                    dataIndex = dataIndex + 1

                elif dataIndex == 6:
                    torqueArray.append(float(data[i]))
                    dataIndex = dataIndex + 1
                # Read in Thrust and put into array
                elif dataIndex == 7:
                    thrustArray.append(float(data[i]))
                    dataIndex = 0
                # Ignore the data and continue moving along
                else:
                    dataIndex = dataIndex + 1

    # Clean up all NaN
    for key in perfDict:
        velNan = []
        tNan = []
        qNan = []
        for num in range(perfDict[key][0].size):
            if math.isnan(perfDict[key][0][num]) or math.isnan(perfDict[key][1][num]):
                velNan.append(num)
                tNan.append(num)
                qNan.append(num)
        newVel = np.delete(perfDict[key][0], velNan)
        newT = np.delete(perfDict[key][1], tNan)
        newQ = np.delete(perfDict[key][2], qNan)
        perfDict[key] = [newVel, newT, newQ]

    # Iterate through each thrust curve and interpolate 4 degree polynomial
    coeffDictThrust = {}
    coeffDictTorque = {}
    maxThrust = {}
    maxTorque = {}
    maxVel = {}
    maxTorqueVel = {}
    thrust14 = {}
    thrust24 = {}
    thrust34 = {}
    torque14 = {}
    torque24 = {}
    torque34 = {}
    for key in perfDict:
        # Convert MPH to m/s
        vel = perfDict[key][0] * 0.44704
        # Convert lbf to N
        T = perfDict[key][1] * 4.44822
        # Convert in-lbf to N-m
        Q = perfDict[key][2] * .112985

        # Polyfit
        # coeff = np.polyfit(vel, T, 4)
        # coeffQ = np.polyfit(vel, Q, 4)

        maxThrust[key] = T[0]
        maxTorque[key] = np.amax(Q)
        maxVel[key] = vel[-1]
        thrustLength = len(T)
        thrust14[key] = T[int(thrustLength/4.0)]
        thrust24[key] = T[int(thrustLength/2.0)]
        thrust34[key] = T[int(thrustLength*3.0/4.0)]


        # coeffDictThrust[key] = coeff
        # coeffDictTorque[key] = coeffQ

    thrust = {}
    thrust['14'] = thrust14
    thrust['24'] = thrust24
    thrust['34'] = thrust34
    thrust['max'] = maxThrust
    thrust['vel'] = maxVel

    torque = {}

    torque['max'] = maxTorque




    # print(coeffDict)
    return [data, perfDict, coeffDictThrust, coeffDictTorque, thrust, torque]


# Creates a Kriging model
def createKriging(rangeD, rangeP, rangeRPM, vario):
    ''' Creates the Kriging model with diameter, pitch, and rpm as inputs (3D) '''
    # rangeD = [min diameter, max diameter]
    # rangeP = [min pitch, max diameter]

    # Axis
    x = np.arange(float(rangeD[0]), float(rangeD[1]), 1.0)  # diameter
    y = np.arange(float(rangeP[0]), float(rangeP[1]), 1.0)  # pitch
    z = np.arange(float(rangeRPM[0]), float(rangeRPM[1]), 1000.0)  # RPM

    # ================
    # Collect Data
    # ================
    dataDict = {}
    dataDictQ = {}
    thrustDict = []
    torqueDict = []
    for i in range(5):
        dataDict[str(i)] = []
        dataDictQ[str(i)] = []
    for d in range(rangeD[0], rangeD[1] + 1):
        for p in range(rangeP[0], rangeP[1] + 1):
            filestring = 'PER3_' + str(d) + 'x' + str(p) + '.dat'
            print('Reading in ' + filestring)
            output = propDataParse(filestring)
            thrust = output[4]
            torque = output[5]
            print('Success reading in ' + filestring)
            # Only keep the values within the RPM range
            for rpm in range(rangeRPM[0], rangeRPM[1] + 1000, 1000):
                # Split into different coefficients
                # for i in range(5):
                #     # print(str(rpm))
                #     dataDict[str(i)].append([float(d), float(p), float(rpm), float(coeffDictT[str(rpm)][i])])
                #     dataDictQ[str(i)].append([float(d), float(p), float(rpm), float(coeffDictQ[str(rpm)][i])])
                thrustDict.append([float(d), float(p), float(rpm), float(thrust['14'][str(rpm)]),
                                           float(thrust['24'][str(rpm)]), float(thrust['34'][str(rpm)]),
                                           float(thrust['max'][str(rpm)]), float(thrust['vel'][str(rpm)])])
                torqueDict.append([float(d), float(p), float(rpm), float(torque['max'][str(rpm)])])

    # ======================
    # Create Kriging models
    # ======================
    # krigingDict = {}
    # # Coeff 1
    # data = np.array(dataDict[str(0)])
    # ok3d1 = OrdinaryKriging3D(data[:, 0], data[:, 1], data[:, 2], data[:, 3],
    #                           variogram_model=vario)
    # k3d1, ss3d1 = ok3d1.execute('grid', x, y, z)
    # krigingDict['coeff1'] = [ok3d1, k3d1, ss3d1]
    #
    # # Coeff 2
    # data = np.array(dataDict[str(1)])
    # ok3d2 = OrdinaryKriging3D(data[:, 0], data[:, 1], data[:, 2], data[:, 3],
    #                           variogram_model=vario)
    # k3d2, ss3d2 = ok3d2.execute('grid', x, y, z)
    # krigingDict['coeff2'] = [ok3d2, k3d2, ss3d2]
    #
    # # Coeff 3
    # data = np.array(dataDict[str(2)])
    # ok3d3 = OrdinaryKriging3D(data[:, 0], data[:, 1], data[:, 2], data[:, 3],
    #                           variogram_model=vario)
    # k3d3, ss3d3 = ok3d3.execute('grid', x, y, z)
    # krigingDict['coeff3'] = [ok3d3, k3d3, ss3d3]
    #
    # # Coeff 4
    # data = np.array(dataDict[str(3)])
    # ok3d4 = OrdinaryKriging3D(data[:, 0], data[:, 1], data[:, 2], data[:, 3],
    #                           variogram_model=vario)
    # k3d4, ss3d4 = ok3d4.execute('grid', x, y, z)
    # krigingDict['coeff4'] = [ok3d4, k3d4, ss3d4]
    #
    # # Coeff 5
    # data = np.array(dataDict[str(4)])
    # ok3d5 = OrdinaryKriging3D(data[:, 0], data[:, 1], data[:, 2], data[:, 3],
    #                           variogram_model=vario)
    # k3d5, ss3d5 = ok3d5.execute('grid', x, y, z)
    # krigingDict['coeff5'] = [ok3d5, k3d5, ss3d5]
    #
    thrustKrigingDict = {}
    # Max Thrust
    thrustDict = np.array(thrustDict)
    maxThrustok3d = OrdinaryKriging3D(thrustDict[:,0], thrustDict[:,1],thrustDict[:,2],thrustDict[:,6],
                               variogram_model=vario)
    maxVelok3d = OrdinaryKriging3D(thrustDict[:, 0], thrustDict[:, 1], thrustDict[:, 2], thrustDict[:, 7],
                               variogram_model=vario)
    thrust14ok3d = OrdinaryKriging3D(thrustDict[:, 0], thrustDict[:, 1], thrustDict[:, 2], thrustDict[:, 3],
                               variogram_model=vario)
    thrust24ok3d = OrdinaryKriging3D(thrustDict[:, 0], thrustDict[:, 1], thrustDict[:, 2], thrustDict[:, 4],
                               variogram_model=vario)
    thrust34ok3d = OrdinaryKriging3D(thrustDict[:, 0], thrustDict[:, 1], thrustDict[:, 2], thrustDict[:, 5],
                               variogram_model=vario)
    thrustKrigingDict['max'] = maxThrustok3d
    thrustKrigingDict['vel'] = maxVelok3d
    thrustKrigingDict['14']= thrust14ok3d
    thrustKrigingDict['24']= thrust24ok3d
    thrustKrigingDict['34'] = thrust34ok3d

    print('Success creating Kriging Model for Propulsion Component: Thrust')
    #
    # # =============
    # # Torque
    # # =============
    # data = np.array(dataDictQ[str(0)])
    # ok3d1 = OrdinaryKriging3D(data[:, 0], data[:, 1], data[:, 2], data[:, 3],
    #                           variogram_model=vario)
    # k3d1, ss3d1 = ok3d1.execute('grid', x, y, z)
    # krigingDict['coeff1Q'] = [ok3d1, k3d1, ss3d1]
    #
    # # Coeff 2
    # data = np.array(dataDictQ[str(1)])
    # ok3d2 = OrdinaryKriging3D(data[:, 0], data[:, 1], data[:, 2], data[:, 3],
    #                           variogram_model=vario)
    # k3d2, ss3d2 = ok3d2.execute('grid', x, y, z)
    # krigingDict['coeff2Q'] = [ok3d2, k3d2, ss3d2]
    #
    # # Coeff 3
    # data = np.array(dataDictQ[str(2)])
    # ok3d3 = OrdinaryKriging3D(data[:, 0], data[:, 1], data[:, 2], data[:, 3],
    #                           variogram_model=vario)
    # k3d3, ss3d3 = ok3d3.execute('grid', x, y, z)
    # krigingDict['coeff3Q'] = [ok3d3, k3d3, ss3d3]
    #
    # # Coeff 4
    # data = np.array(dataDictQ[str(3)])
    # ok3d4 = OrdinaryKriging3D(data[:, 0], data[:, 1], data[:, 2], data[:, 3],
    #                           variogram_model=vario)
    # k3d4, ss3d4 = ok3d4.execute('grid', x, y, z)
    # krigingDict['coeff4Q'] = [ok3d4, k3d4, ss3d4]
    #
    # # Coeff 5
    # data = np.array(dataDictQ[str(4)])
    # ok3d5 = OrdinaryKriging3D(data[:, 0], data[:, 1], data[:, 2], data[:, 3],
    #                           variogram_model=vario)
    # k3d5, ss3d5 = ok3d5.execute('grid', x, y, z)
    # krigingDict['coeff5Q'] = [ok3d5, k3d5, ss3d5]
    torqueKrigingDict = {}
    # Max Thrust
    torqueDict = np.array(torqueDict)
    maxTorqueok3d = OrdinaryKriging3D(torqueDict[:,0], torqueDict[:,1],torqueDict[:,2],torqueDict[:,3],
                               variogram_model=vario)
    torqueKrigingDict['max'] = maxTorqueok3d


    print('Success creating Kriging Model for Propulsion Component: Torque')
    krigingDict = [thrustKrigingDict, torqueKrigingDict]

    return krigingDict




# ---------------------------------
# Testing functions
# ---------------------------------


# Test function
# propDataParse('PER3_10x4.dat')

# Test Kriging model creation function

KG = createKriging([8,10],[5,8],[1000, 10000], 'linear')
# plotKrigGrid(KG,[8,10],[5,8],[1000, 10000])
