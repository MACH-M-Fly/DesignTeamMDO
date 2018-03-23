from __future__ import print_function
import numpy as np
import math

# Kriging Library
from pykrige.ok3d import OrdinaryKriging3D


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
    for key in perfDict:
        # Convert MPH to m/s
        vel = perfDict[key][0] * 0.44704
        # Convert lbf to N
        T = perfDict[key][1] * 4.44822
        # Convert in-lbf to N-m
        Q = perfDict[key][2] * .112985
        # Polyfit
        coeff = np.polyfit(vel, T, 4)
        coeffQ = np.polyfit(vel, Q, 4)
        coeffDictThrust[key] = coeff
        coeffDictTorque[key] = coeffQ

    # print(coeffDict)
    return [data, perfDict, coeffDictThrust, coeffDictTorque]


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
    for i in range(5):
        dataDict[str(i)] = []
        dataDictQ[str(i)] = []
    for d in range(rangeD[0], rangeD[1] + 1):
        for p in range(rangeP[0], rangeP[1] + 1):
            filestring = 'PER3_' + str(d) + 'x' + str(p) + '.dat'
            print('Reading in ' + filestring)
            output = propDataParse(filestring)
            coeffDictT = output[2]
            coeffDictQ = output[3]
            print('Success reading in ' + filestring)
            # Only keep the values within the RPM range
            for rpm in range(rangeRPM[0], rangeRPM[1] + 1000, 1000):
                # Split into different coefficients
                for i in range(5):
                    # print(str(rpm))
                    dataDict[str(i)].append([float(d), float(p), float(rpm), float(coeffDictT[str(rpm)][i])])
                    dataDictQ[str(i)].append([float(d), float(p), float(rpm), float(coeffDictQ[str(rpm)][i])])

    # ======================
    # Create Kriging models
    # ======================
    krigingDict = {}
    # Coeff 1
    data = np.array(dataDict[str(0)])
    ok3d1 = OrdinaryKriging3D(data[:, 0], data[:, 1], data[:, 2], data[:, 3],
                              variogram_model=vario)
    k3d1, ss3d1 = ok3d1.execute('grid', x, y, z)
    krigingDict['coeff1'] = [ok3d1, k3d1, ss3d1]

    # Coeff 2
    data = np.array(dataDict[str(1)])
    ok3d2 = OrdinaryKriging3D(data[:, 0], data[:, 1], data[:, 2], data[:, 3],
                              variogram_model=vario)
    k3d2, ss3d2 = ok3d2.execute('grid', x, y, z)
    krigingDict['coeff2'] = [ok3d2, k3d2, ss3d2]

    # Coeff 3
    data = np.array(dataDict[str(2)])
    ok3d3 = OrdinaryKriging3D(data[:, 0], data[:, 1], data[:, 2], data[:, 3],
                              variogram_model=vario)
    k3d3, ss3d3 = ok3d3.execute('grid', x, y, z)
    krigingDict['coeff3'] = [ok3d3, k3d3, ss3d3]

    # Coeff 4
    data = np.array(dataDict[str(3)])
    ok3d4 = OrdinaryKriging3D(data[:, 0], data[:, 1], data[:, 2], data[:, 3],
                              variogram_model=vario)
    k3d4, ss3d4 = ok3d4.execute('grid', x, y, z)
    krigingDict['coeff4'] = [ok3d4, k3d4, ss3d4]

    # Coeff 5
    data = np.array(dataDict[str(4)])
    ok3d5 = OrdinaryKriging3D(data[:, 0], data[:, 1], data[:, 2], data[:, 3],
                              variogram_model=vario)
    k3d5, ss3d5 = ok3d5.execute('grid', x, y, z)
    krigingDict['coeff5'] = [ok3d5, k3d5, ss3d5]

    print('Success creating Kriging Model for Propulsion Component: Thrust')

    # =============
    # Torque
    # =============
    data = np.array(dataDictQ[str(0)])
    ok3d1 = OrdinaryKriging3D(data[:, 0], data[:, 1], data[:, 2], data[:, 3],
                              variogram_model=vario)
    k3d1, ss3d1 = ok3d1.execute('grid', x, y, z)
    krigingDict['coeff1Q'] = [ok3d1, k3d1, ss3d1]

    # Coeff 2
    data = np.array(dataDictQ[str(1)])
    ok3d2 = OrdinaryKriging3D(data[:, 0], data[:, 1], data[:, 2], data[:, 3],
                              variogram_model=vario)
    k3d2, ss3d2 = ok3d2.execute('grid', x, y, z)
    krigingDict['coeff2Q'] = [ok3d2, k3d2, ss3d2]

    # Coeff 3
    data = np.array(dataDictQ[str(2)])
    ok3d3 = OrdinaryKriging3D(data[:, 0], data[:, 1], data[:, 2], data[:, 3],
                              variogram_model=vario)
    k3d3, ss3d3 = ok3d3.execute('grid', x, y, z)
    krigingDict['coeff3Q'] = [ok3d3, k3d3, ss3d3]

    # Coeff 4
    data = np.array(dataDictQ[str(3)])
    ok3d4 = OrdinaryKriging3D(data[:, 0], data[:, 1], data[:, 2], data[:, 3],
                              variogram_model=vario)
    k3d4, ss3d4 = ok3d4.execute('grid', x, y, z)
    krigingDict['coeff4Q'] = [ok3d4, k3d4, ss3d4]

    # Coeff 5
    data = np.array(dataDictQ[str(4)])
    ok3d5 = OrdinaryKriging3D(data[:, 0], data[:, 1], data[:, 2], data[:, 3],
                              variogram_model=vario)
    k3d5, ss3d5 = ok3d5.execute('grid', x, y, z)
    krigingDict['coeff5Q'] = [ok3d5, k3d5, ss3d5]

    print('Success creating Kriging Model for Propulsion Component: Torque')

    return krigingDict

# Plotting (NOT DONE YET, DO NOT USE)
# def plotKrigGrid(krigingDict, rangeD, rangeP, rangeRPM):

#	predictFig = mlab.figure(figure='predict')
#  Axis
#	x = np.arange(float(rangeD[0]), float(rangeD[1]), 1.0) # diameter
#	y = np.arange(float(rangeP[0]), float(rangeP[1]), 1.0) # pitch
#	z = np.arange(float(rangeRPM[0]), float(rangeRPM[1]), 1000.0) # RPM

#	plot = mlab.contour3d(krigingDict['coeff1'][1], contours=15, transparent=True, figure=predictFig)
#	mlab.show()


# ---------------------------------
# Testing functions
# ---------------------------------


# Test function
# propDataParse('PER3_10x4.dat')

# Test Kriging model creation function

# KG = createKriging([8,10],[5,8],[1000, 10000])
# plotKrigGrid(KG,[8,10],[5,8],[1000, 10000])
