import sys
import pathlib
path_of_the_current_file = str(pathlib.Path().absolute())
sys.path.append('/afs/ipp/aug/ads-diags/common/python/lib')
sys.path.append(path_of_the_current_file+'/modules')
import ECI_Load_osam as ECI
import TDI_Load_osam as TDI
import IDA_Load_osam as IDA
import my_funcs_class as my_funcs
import matplotlib.pyplot as plt
import numpy as np
import importlib
import dd_20190506 as dd
importlib.reload(TDI)
importlib.reload(ECI)
importlib.reload(my_funcs)
importlib.reload(IDA)

# mf=my_funcs.my_funcs()
# mf.find_nearest_idx(array, value)

# EI=ECI.ECI()
# EI.Load(25781)
# EI.Load_FakeRz()
# EI.ECEId




dd_load = dd.shotfile("ECI", 25781, 'AUGD')

N_LOS, N_R = 16, 8
ECEId = np.zeros([N_LOS,len(time),N_R])
for i_LOS in range(N_LOS):
    ECEId[i_LOS,:,:] = dd_load.getObjectData(b'LOS%i'%(i_LOS+1)).T
    # ECEId[i_LOS,:,:] = dd_load.getSignalGroup(b'LOS%i'%(i_LOS+1))
    print("LOS loaded: %g/%g"%(i_LOS+1,N_LOS))

ECEId = np.swapaxes(ECEId,0,1)

LOS5 = dd_load.getObjectData(b'LOS5').T
len(LOS5[0, :])
len(LOS5[:, 0])
LOS5[0, ::-1]
# TD=TDI.TDI()
# TD.Load(37203)

# TD.ECEId

# mf=my_funcs.my_funcs()
# mf.CutDataECEI(EI.time,EI.ECEId, tBegin = 2.00, tEnd = 2.01)
# mf.relECEI(mf.ECEId_C)
# mf.ECEId_C
# mf.time_C


# removeLOS_ch = [1,13,15,16]
# removeLOS_ch = np.array(removeLOS_ch).astype(int) - 1
# ch_zz = np.arange(16)
# ch_zz = np.delete(ch_zz, removeLOS_ch)
# plt.contourf(EI.RR_fake[ch_zz,:],EI.zz_fake[ch_zz,:],mf.ECEId_rel[21,ch_zz,:] )
# plt.show()
# def Fourier_analysis_ECEI(self, time, ECEId, noise_level, f_cut):

# def SavGol_filter_ECEI(self, ECEI_data, win_len, pol_ord):
# dd_load = dd.shotfile('TDI', 37203, 'AUGD')

# Sig1 = dd_load.getSignalGroup(b'Sig1')
# Sig1_ed = dd_load.getObjectData(b'Sig1')
# time = dd_load.getTimeBase(b't1')
# Sig1.shape
# Sig1_ed.shape
# Sig1_ed[:, 3243242]
