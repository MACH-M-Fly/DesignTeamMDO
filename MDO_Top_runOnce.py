# python stantdard libraries
from __future__ import print_function

import copy
from Post_Process.postProcess import postProcess_Main
import CreateProblem

# ============================================== Create Problem ============================================ #

prob0 = CreateProblem.CreateRunOnceProblem()
prob0.run()
in_ac = copy.deepcopy(prob0['my_comp.aircraft'])

# ============================================== Post-Processing ============================================ #

postProcess_Main(None, in_ac)

