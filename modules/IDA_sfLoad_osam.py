"""
to use these functions inside other python programs, paste the following:
import modules.IDA_sfLoad_osam as IDA
then use as
ID=IDA.IDA()
ID.Load(Shot)
ID.Load(Shot, tBegin=0., tEnd=4.)
"""
import numpy as np
import aug_sfutils as sf

class IDAhelp:
    status = False

class IDA:
    def __init__( self ,  Experiment = 'AUGD', Diagnostic = 'IDA', Shotnumber = None ):

        if Shotnumber != None :
            self.Load( Shotnumber )

    def Load( self ,  Shotnumber, Experiment='AUGD', Diagnostic='IDA', Edition = 0, tBegin=-1.0, tEnd=12.0):
        sfload = sf.SFREAD(Diagnostic, Shotnumber, experiment=Experiment, edition=Edition)
        self.Shotnumber = Shotnumber
        self.tBegin = tBegin 
        self.tEnd = tEnd
        print("Reading Te,ne,pe,rhop,time (%g-%g s)"%(tBegin,tEnd))
        self.Te = sfload.getobject('Te', tbeg=tBegin, tend=tEnd)
        self.ne = sfload.getobject('ne', tbeg=tBegin, tend=tEnd)
        self.pe = sfload.getobject('pe', tbeg=tBegin, tend=tEnd) 
        self.rhop = sfload.getobject('rhop', tbeg=tBegin, tend=tEnd)
        self.time = sfload.getobject('time', tbeg=tBegin, tend=tEnd)
        print("IDA Loaded")

    def getData_for_t(self, time_point):
        idx_t = self.find_nearest_idx(self.time,time_point)
        self.Te_t = self.Te[idx_t]
        self.ne_t = self.ne[idx_t]
        self.pe_t = self.pe[idx_t]
        self.rhop_t = self.rhop[idx_t]
        self.time_t = self.time[idx_t]
        print("received data for t = %g s" %(self.time_t))

    def find_nearest_idx(self,array, value):
        "find nearest idx in array for the value"
        idx = (np.abs(array - value)).argmin()
        return idx


