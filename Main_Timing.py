import CreateProblem
from Aerodynamics.aeroAnalysis import run_times as aero_time_s
from Performance.objPerformance import run_times as perf_time_s
from Structures.structAnalysis import run_time as struct_time_s
from Propulsion.propulsionAnalysis import run_times as prop_time_s
from Weights.calcWeight import run_times as weight_time_s
from datetime import datetime


# Define an averaging function
def avg(x):
    s = 0
    for v in x:
        s += v.microseconds * 1e-6
    return s / len(x)

# Define the number of run cases to average
num_runs = 1
total_s = []

# Run the cases
for i in range(num_runs):
    prob0 = CreateProblem.CreateRunOnceProblem()
    start = datetime.now()
    prob0.run()
    total_s.append(datetime.now() - start)
    ac = prob0['createAC.aircraft']

# Find the resulting averages for each
aero_avg = avg(aero_time_s)
perf_avg = avg(perf_time_s)
prop_avg = avg(prop_time_s)
struct_avg = avg(struct_time_s)
weight_avg = avg(weight_time_s)
total_avg = avg(total_s)

# Print Results
print('Aero Time: %.3f s' % aero_avg)
print('Perf Time: %.3f s' % perf_avg)
print('Prop Time: %.3f s' % prop_avg)
print('Str. Time: %.3f s' % struct_avg)
print('Wgt. Time: %.3f s' % weight_avg)
print('Tot. Time: %.3f s' % total_avg)
