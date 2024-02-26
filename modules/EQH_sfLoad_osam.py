"""
to use these functions inside other python programs, paste the following:
import sys
sys.path.append("/afs/ipp-garching.mpg.de/home/o/osam/workspace/python3_projects/modules_osam")
import EQH_sfLoad_osam as EQH
import importlib
importlib.reload(EQH)
then use as
EQ=EQH.EQH()
EQ.Load(Shot)
EQ.Load(Shot, tBegin = 2.0, tEnd = 4.0)
"""
import numpy as np
from scipy.interpolate import interp1d
import aug_sfutils as sf

class EQHhelp:
    status = False

class EQH:
    def __init__( self ,  Experiment = 'AUGD', Diagnostic = 'EQH', Shotnumber = None ):

        if Shotnumber != None :
            self.Load( Shotnumber )

    def Load( self ,  Shotnumber, Experiment='AUGD', Diagnostic='EQH', Edition = 0, tBegin=-1.0, tEnd=12.0):
        sfload = sf.SFREAD(Diagnostic, Shotnumber,
                       experiment=Experiment, edition=Edition)

        self.Shotnumber = Shotnumber
        self.tBegin = tBegin 
        self.tEnd = tEnd

        self.Nz = sfload.getparset("PARMV")["N"] + 1
        self.NR = sfload.getparset("PARMV")["M"] + 1
        Ntime = sfload.getparset("PARMV")["NTIME"]
        time0 = sfload.getobject("time")[0:Ntime]
        idxTime = np.where( (time0>=tBegin) & (time0<=tEnd) )[0]
        self.time = time0[idxTime]
        
        
        self.R = (sfload.getobject("Ri").T)[0:Ntime,0:self.NR][idxTime]
        self.z = (sfload.getobject("Zj").T)[0:Ntime,0:self.Nz][idxTime]

        self.PsiOrigin = (sfload.getobject("PFM").T)[0:Ntime,0:self.Nz,0:self.NR][idxTime]
        ###magnetic axis,sxm
        self.PsiSpecial = (sfload.getobject("PFxx").T)[0:Ntime][idxTime]   
        ##time, R, z
        self.Psi = np.swapaxes(self.PsiOrigin,1,2)
        self.PsiAxis = self.PsiSpecial[:,0]
        self.PsiSep = self.PsiSpecial[:,1]

        self.rhopM = np.sqrt(np.abs((self.Psi.T-self.PsiAxis)/(self.PsiSep-self.PsiAxis))).T
        self.rhopM = np.swapaxes(self.rhopM,1,2)

        # get the axis and sepratrix positions
        sfload = sf.SFREAD("GQH", Shotnumber,
                       experiment=Experiment, edition=Edition)
        self.Rmag = sfload.getobject("Rmag")[idxTime]
        self.zmag = sfload.getobject("Zmag")[idxTime]
        self.Raus = sfload.getobject("Raus")[idxTime]
        self.zaus = self.zmag


    def getrRhop_forTime(self, time_point):
        """
        linear interpolation of rhopM for
        a given time point
        """
        rhopM_t = np.zeros([self.Nz,self.NR])
        idx_B = np.searchsorted(self.time, time_point, side='right') -1
        idx_E = np.searchsorted(self.time, time_point, side='right')
        for i_Nz in range(self.Nz):
            linfit = interp1d([self.time[idx_B],self.time[idx_E]], np.vstack([self.rhopM[idx_B,i_Nz,:], self.rhopM[idx_E,i_Nz,:]]), axis=0)
            rhopM_t[i_Nz,:] = linfit(time_point)
        self.rhopM_t = rhopM_t
        # R and z are constant in time (no interp needed)
        self.R_t = self.R[idx_B]
        self.z_t = self.z[idx_B]
        RR_t, zz_t = np.meshgrid(self.R_t,self.z_t)
        self.RR_t = RR_t
        self.zz_t = zz_t
        self.t_point = time_point
        print("rhopM lin interp for t=%g s, between tB=%g s,tE=%g s" %(time_point,self.time[idx_B],self.time[idx_E]))

