import sys
import os
sys.path.append('/afs/ipp/aug/ads-diags/common/python/lib')
import numpy as np
import matplotlib.pyplot as plt
import pathlib
import importlib
path_of_the_current_file = str(os.path.dirname(os.path.realpath(__file__)))
os.chdir(path_of_the_current_file)
sys.path.append(path_of_the_current_file + '/modules')
import my_funcs_class as my_funcs
import ECI_Load_osam as ECI
importlib.reload(ECI)
importlib.reload(my_funcs)
from scipy.signal import savgol_filter

Shot = 26063
tB = 1.3064
tE = 1.3074

if 1 == 1:
    EC = ECI.ECI()
    EC.Load(Shot)
ECEId = EC.ECEId.copy()
ECEId_time = EC.time.copy()


mf = my_funcs.my_funcs()
idx_B = mf.find_nearest_idx(ECEId_time, tB)
idx_E = mf.find_nearest_idx(ECEId_time, tE)

# ECEId[idx_B:idx_E,2,:]
mf.SavGol_filter_ECEI(ECEId[idx_B:idx_E,:,:], 11, 3)

# N_LOS = ECEId.shape[1]
# N_R = ECEId.shape[2]
# for NL in range(N_LOS):
    # for NR in range(N_R):
        # print("NL = %g, NR = %g" %(NL,NR))
        # savgol_filter(ECEId[idx_B:idx_E,NL,NR], 11, 3)
        # savgol_filter(ECEId[:,NL,NR], 11, 3)

# ECEId[:,0,3]

