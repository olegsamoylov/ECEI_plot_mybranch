import sys
sys.path.append('/afs/ipp/aug/ads-diags/common/python/lib')
# import dd_20190506 as dd
import dd
# from ddww import dd
import numpy as np
import matplotlib.pyplot as plt

Shot = 25781
data = dd.shotfile('RZO', Shot, 'ECEI')
# R = data.getObjectData(b'R')
# R = data.getSignal(b'R')
# R = data.getSignal(b'R')
R = data.getSignalGroup('R')

# equ_data = equ.equ_map(Shot, 'EQH', 'AUGD')
# rho = equ_data.rz2rho([1.9,2.0],[0,0],[2.0,2.1],'rho_pol')
# rho = equ_data.rz2rho(R,z,rztime,'rho_pol')
# R_0, z_0 = equ_data.rho2rz(0,t_in = 2.0, coord_in='rho_pol',all_lines=False)
# # Te = data.getParameter(b'Trad-A')
# Te = data.getSignal(b'Trad-A')
# Te = data.getParameterSet(b'Trad-A', tBegin=1., tEnd=2. )
# Te = data.getObjectData(b'Trad-A')
# Te = data.getObjectData(b'time-A')
# Te = data.getObjectData(b'R-A')


# Te = data.getObjectData(b'R-A')
# R = data.getSignalGroup(b'R-A')
# z = data.getSignalGroup(b'z-A')
# data.getSignalGroup(b'Trad-A', tBegin=1., tEnd=3. )
# data.getSignal(b'time-A')
# data.getTimeBase(b'time-A')
# rztime = data.getTimeBase(b'rztime')
# not reliable
# data(b'R-A').data
# data(b'Trad-A', tBegin=1., tEnd=2. ).data
# data(b'Trad-A', tBegin=1., tEnd=2. ).time



