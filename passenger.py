import numpy as np

ball_weight = np.array([0.4, 0.67, 1.12, 1.85, 2.39])  # oz
ball_percent = np.array([0.15, 0.2, 0.3, 0.2, 0.15])
ball_diameter = np.array([27,32, 38, 45, 49])

average_weight = np.sum(ball_weight*ball_percent)
average_diameter = np.sum(ball_weight*ball_diameter)
print average_weight
# print average_diameter

std = np.sqrt(sum((ball_weight - average_weight)**2*ball_percent))

def ballWeight(N):

	std_N = std/np.sqrt(N)

	# print std_N

	# print (ball_percent[-1]**N)

	return (average_weight + 1.5 *std_N)*N, average_weight + 1.5 *std_N

print('15         ', ballWeight(15))
print('14         ', ballWeight(14))
print('10         ', ballWeight(10))
print('5         ', ballWeight(5))


