"""File to determine the wetted area multiplier for a given airfoil"""


# Open the airfoil data file
with open('Aerodynamics/airfoils/A_1.dat', 'r') as f:
    data = str(f.read())

# Split the lines
lines = data.split('\n')

# Create a list for point
points = []

# Iterate over all lines except first (name)
for l in lines[1:]:
    # Split lines into x/y components
    p = l.split()

    # Ignore empty lines
    if len(p) == 0:
        continue
    # Throw error if line isn't empty and doesn't contain 2 values (x, y)
    elif len(p) != 2:
        raise ValueError('invalid length for line %s' % l)

    # Extract x and y parts
    x = float(p[0])
    y = float(p[1])

    # Append point tuple
    points.append((x, y))

# Initialize the swet multiplier
swet_multiplier = 0

# Iterate over all points to determine the distance between
for i in range(len(points)):
    # Find the next point
    i_next = i + 1

    # If next point is beyond list (last point), set to first point
    if i_next == len(points):
        i_next = 0

    # Extract point 1 and point 2
    p1 = points[i]
    p2 = points[i_next]

    # Determine triangle distance between points
    dist = ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5

    # Add distance to multiplier
    swet_multiplier += dist

# Print results
print('Airfoil: {:s}'.format(lines[0]))
print('S_wet Multiplier: {:.3f}'.format(swet_multiplier))
