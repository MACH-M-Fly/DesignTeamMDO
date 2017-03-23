# NOTE: This file assumes that there is a constant airfoil being used
#       for the moment, this can be changed in the future

import math

# Wing Parameters
numRibs = 24
wingspanMeters = 3.2
avgChordMeters = 0.65532
isCarbonFiber = True

# Airfoil Parameters
airfoilTC = 0.16

# Taper Parameters
taperRatio = 0.61  # Starting parameter for the wing taper ratio
taperStart = 0.47  # Starting parameter for the wing taper start ratio

# Tail Parameters
numRibs_HSt = 16

width_HSt   = 1.23    # Width of Horizontal Stabilizer
chord_HSt   = 0.325

numRibs_VSt = 5
height_VSt  = 0.32
chord_VSt   = 0.325

# Constants for defining wing build hours
hoursPerRib = 4
airfoilTC_Threshold = 0.2

hoursPerSparMeter = 5
hoursPerTeMeter = 16
hoursPerLeMeter = 16

hoursPerCarbonCureCycle = 16
hoursPerCarbonCyclePeron = 3
personPerLeMeter = 1.6

hoursPerMonokoteMeter2 = 5

# Constants for definining tail build hours
hoursPerVertSurfaceMeter2 = 5^2
hoursPerHorzSurfaceMeter2 = 5^2

# Number of people will vary
# 16 hours cure + 3 for prep, 3 * Number of people
# Spar Constant

if isCarbonFiber:
    hoursPerLeMeter = 3
    hoursPerSparMeter = 1

# Constants for defining fuselage build hours

# My Variables (REMOVABLE)


# Estimator Function to get Wing Build Hours
def getWingBuildHours():
    # Estimate roughly 1/2 hour per rib of the aircraft
    airfoilHours = numRibs * hoursPerRib

    # Increase the time rquried for creating an airfoil if the
    # thickness is less than a certian threshold
    #
    #  -> Should look into not straight multiplication, but perhaps a log?
    if airfoilTC < airfoilTC_Threshold:
        airfoilHours = airfoilHours * airfoilTC_Threshold / airfoilTC


    # Get an estimate for the spar hours
    #  -> assumes constants spar, no taper/bend
    sparHours = wingspanMeters * hoursPerSparMeter


    # Trailing Edge hours
    teHours = wingspanMeters * hoursPerTeMeter

    # Leading Edge hours
    if isCarbonFiber:
        leHours = hoursPerCarbonCureCycle + hoursPerCarbonCyclePeron * math.ceil(personPerLeMeter * wingspanMeters)
    else:
        leHours = wingspanMeters * hoursPerLeMeter

    # -> Need something to delineate taper...

    # Monokote Hours for estimated wetted area of the wing
    monokoteHours = 2*wingspanMeters*avgChordMeters*hoursPerMonokoteMeter2

    # Return the sum of all hours calculated above
    return airfoilHours + sparHours + teHours + leHours + monokoteHours

# Estimator Function to get Fuselage Build Hours
def getFuselageBuildHours():
    return 50 # Currently just an estimated constant 50 hours

# Estimator Function to get Tail Build Hours
def getTailBuildHours():
    vsArea = height_VSt * chord_VSt
    hzArea = width_HSt * chord_HSt

    leteHours = (hoursPerLeMeter + hoursPerTeMeter) * (height_VSt + width_HSt)
    
    return leteHours + vsArea * hoursPerVertSurfaceMeter2 * 2 + hzArea * hoursPerHorzSurfaceMeter2 * 2

def getAircraftBuildHours():
    totalHours = getWingBuildHours()
    totalHours = totalHours + getFuselageBuildHours()
    totalHours = totalHours + getTailBuildHours()
    return totalHours

print(getAircraftBuildHours())
