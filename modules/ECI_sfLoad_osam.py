"""
to use these functions inside other python programs, paste the following:
import modules.ECI_sfLoad_osam as ECI
then use as
EI=ECI.ECI()
EI.Load(Shot)
"""
import numpy as np
import aug_sfutils as sf

class ECIhelp:
    status = False

class ECI:
    def __init__( self ,  Experiment = 'AUGD', Diagnostic = 'ECI', Shotnumber = None ):

        if Shotnumber != None :
            self.Load( Shotnumber )

    def Load( self ,  Shotnumber, Experiment='AUGD', Diagnostic='ECI', Edition = 0):
        sfload = sf.SFREAD(Diagnostic, Shotnumber, experiment=Experiment, edition=Edition)

        self.Shotnumber = Shotnumber

        time = sfload.gettimebase('time')
        print("Loading %s: tBegin = %g, tEnd = %g s"%(Diagnostic,time[0],time[-1]))
        N_LOS, N_R = 16, 8
        ECEId = np.zeros([N_LOS,len(time),N_R])
        for i_LOS in range(N_LOS):
            ECEId[i_LOS,:,::-1] = sfload.getobject('LOS%i'%(i_LOS+1)) #revers R array #revers R array
            for i_R in range(N_R):
                ECEId[i_LOS,:,i_R] -= np.mean(ECEId[i_LOS,:100,i_R]) # remove offset
            print("LOS loaded: %g/%g"%(i_LOS+1,N_LOS))

        ECEId = np.swapaxes(ECEId,0,1)
        self.ECEId = ECEId
        self.time = time

    def find_nearest_idx(self,array, value):
        "find nearest idx in array for the value"
        idx = (np.abs(array - value)).argmin()
        return idx


    def Load_FakeRz(self):
        """
        Calculate fake ECEI window position
        (Ray tracing should be a proper way)
        """
        from scipy.constants import e, m_e 
        N_LOS, N_R = 16, 8
        path_to_eceilog = '/shares/departments/AUG/users/osam/LOG_ECEI/'
        with open(path_to_eceilog+"%d.log"%(self.Shotnumber), 'r') as f:
            ECEI_LOG = f.read()
        Bt = float(ECEI_LOG.split(" ")[0].split("=")[1])
        f_LO = float(ECEI_LOG.split(" ")[1].split("=")[1])
        self.Bt = Bt
        self.f_LO = f_LO 
        f_0 = 3.7 # [GHz]
        ch_spacing = 800 # MHz
        R0 = 1.65 # [m] AUG main radius
        f_array  = np.zeros(N_R)
        z_array  = np.zeros(N_LOS)
        dz = 0.0322 # [m] - fake dz between LOSs
        z_up = 0.3165 # [m] - fake LOS1 z position
        # z_up = 0.5165 # [m] - fake LOS1 z position


        f_array[0] = f_LO + f_0  # [GHz]
        for i in range(N_R-1):
            f_array[i+1] = f_array[0]+ch_spacing*1e-3*(1+i) # [GHz]

        z_array[0] = z_up
        for i in range(N_LOS-1):
            z_array[i+1] = z_array[0] - dz*(i+1)

        R_array = 2*e*np.abs(Bt)*R0/(2*np.pi*m_e*f_array*1.e9)
        R_array = R_array[::-1]
        RR_array, zz_array = np.meshgrid(R_array,z_array)

        self.R_fake = R_array
        self.z_fake = z_array
        self.RR_fake = RR_array
        self.zz_fake = zz_array
        self.N_LOS = N_LOS
        self.N_R = N_R
        print("FakeRz has been loaded")
        
    def Load_RZO(self):
        sfload_RZO = sf.SFREAD("RZO", self.Shotnumber, experiment="OSAM", edition=int(0))
        
        self.R = sfload_RZO.getobject('R')[:,:,::-1] #revers R array #revers R array
        self.z = sfload_RZO.getobject('z')[:,:,::-1] #revers R array #revers R array
        self.rhop = sfload_RZO.getobject('rho')[:,:,::-1] #revers R array #revers R array
        self.time_rzo = sfload_RZO.getobject('time')
        print("RZO has been loaded")
