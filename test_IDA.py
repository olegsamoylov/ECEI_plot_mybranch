import numpy as np
import aug_sfutils as sf
import modules.IDA_sfLoad_osam as IDA


Diagnostic = "IDA"
Experiment = "AUGD"
Shotnumber = int(25781)
Edition = int(0)
# tBegin = 2.1
# tEnd = 2.6

ID=IDA.IDA()
ID.Load(Shotnumber)
ID.Load(Shotnumber, tBegin=1., tEnd=4.)

"""
sfload = sf.SFREAD(Diagnostic, Shotnumber, experiment=Experiment, edition=Edition)


time = sfload.gettimebase('time')

N_LOS, N_R = 16, 8
ECEId = np.zeros([N_LOS,len(time),N_R])

for i_LOS in range(N_LOS):
    ECEId[i_LOS,:,::-1] = sfload.getobject('LOS%i'%(i_LOS+1)) #revers R array
    for i_R in range(N_R):
        ECEId[i_LOS,:,i_R] -= np.mean(ECEId[i_LOS,:100,i_R]) # remove offset
    print("LOS loaded: %g/%g"%(i_LOS+1,N_LOS))
    
        ECEId = np.swapaxes(ECEId,0,1)
        self.ECEId = ECEId
        self.time = time
"""
