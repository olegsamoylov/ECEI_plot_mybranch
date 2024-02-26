"""
to use these functions inside other python programs, paste the following:
import sys
sys.path.append("/afs/ipp-garching.mpg.de/home/o/osam/PythonLibraries")
import ECE_sfLoad_osam as ECE
import importlib
importlib.reload(ECE)
then use as
EC=ECE.ECE()
EC.Load(Shot, Diagnostic='CEC')
"""
import numpy as np
from scipy import interpolate
import aug_sfutils as sf

class ECE:
    def __init__( self ,  Experiment = 'AUGD', Diagnostic = 'CEC', Shotnumber = None ):
        
        if Shotnumber != None :
            self.Load( Shotnumber )

    def Load(self, eqm,  Shotnumber, Experiment='AUGD', Diagnostic='CEC', Edition=0, tBegin=-1.0, tEnd=12.0, eqExp='AUGD', interp_rz=False, RMCbinning=100.0):
        self.Shotnumber = Shotnumber
        self.Experiment = Experiment
        self.Diagnostic = Diagnostic
        self.Edition = Edition
        self.tBegin = tBegin
        self.tEnd = tEnd
        self.eqm = eqm
        print("Reading %s.." % (Diagnostic))
        if (Diagnostic != "RMC"):
            print("Reading Te")
            sfload = sf.SFREAD(Diagnostic, Shotnumber,
                           experiment=Experiment, edition=Edition)
            self.Te = sfload.getobject("Trad-A", cal=True, tbeg=tBegin, tend=tEnd)
            print("Reading time")
            self.time = np.asarray(sfload.gettimebase(
                "time-A", tbeg=tBegin, tend=tEnd))
        if (Diagnostic == "RMC"):
            sfRMC = sf.SFREAD("RMC", Shotnumber,
                              experiment=Experiment, edition=Edition)
            print("Reading Te")
            self.Te = np.concatenate(
                (sfRMC.getobject("Trad-A1", cal=True, tbeg=tBegin, tend=tEnd),
                 sfRMC.getobject("Trad-A2", cal=True, tbeg=tBegin, tend=tEnd)),
                axis=1
            )
            print("Reading time")
            self.time = np.asarray(sfRMC.gettimebase(
                "Trad-A1", tbeg=tBegin, tend=tEnd))

            sfload = sf.SFREAD("RMD", Shotnumber,
                           experiment=Experiment, edition=Edition)
            print("Reading RMD for the calibration coefs")
            if sfload.diag == "RMD":
                # calibration
                Multi00 = np.concatenate(
                    (sfload.getparset("eCAL-A1")["MULTIA00"],
                     sfload.getparset("eCAL-A2")["MULTIA00"]),
                    axis=0
                )
                Shift00 = np.concatenate(
                    (sfload.getparset("eCAL-A1")["SHIFTB00"],
                     sfload.getparset("eCAL-A2")["SHIFTB00"]),
                    axis=0
                )
                self.Te = np.multiply(Multi00, self.Te, dtype=np.float64)
                self.Te = np.add(Shift00, self.Te, dtype=np.float64)
                print("RMC is calibrated succesfully.")
                self.dataBinning(RMCbinning)
            else:
                print("!!! Coud NOT load RMD.")
                print("!!! RMC data is NOT calibrated !!!")

        print("Reading R, z, rztime")
        if (interp_rz == True):
            R = np.asarray(sfload.getobject("R-A", tbeg=tBegin, tend=tEnd))
            z = np.asarray(sfload.getobject("z-A", tbeg=tBegin, tend=tEnd))
            rztime = np.asarray(sfload.getobject(
                "rztime", tbeg=tBegin, tend=tEnd))
            print("Interpolating (linear) R, z on the %s time.." % (Diagnostic))
            R_int, z_int = np.zeros_like(self.Te), np.zeros_like(self.Te)
            for i_ch in range(R.shape[1]):
                f_R = interpolate.interp1d(
                    rztime, R[:, i_ch], kind='linear', bounds_error=False, fill_value="extrapolate")
                f_z = interpolate.interp1d(
                    rztime, z[:, i_ch], kind='linear', bounds_error=False, fill_value="extrapolate")
                R_int[:, i_ch] = f_R(self.time)
                z_int[:, i_ch] = f_z(self.time)
            self.R = R_int
            self.z = z_int
            self.rztime = self.time.copy()
        else:
            self.R = np.asarray(sfload.getobject("R-A", tbeg=tBegin, tend=tEnd))
            self.z = np.asarray(sfload.getobject("z-A", tbeg=tBegin, tend=tEnd))
            print("Reading rztime")
            self.rztime = np.asarray(sfload.getobject(
                "rztime", tbeg=tBegin, tend=tEnd))
        print("Reading freq")
        self.freq = np.asarray(sfload.getparset("parms-A")["f"])
        self.chs_numbers = np.arange(1, len(self.freq)+1)
        self.freq = np.asarray(sfload.getparset("parms-A")["f"])
        self.chs_numbers = np.arange(1, len(self.freq)+1)
        print("Loaded")
        # sorting
        idx_sort = np.argsort(self.freq, axis=0)[::-1]
        self.Te = self.Te[:, idx_sort]
        self.R = self.R[:, idx_sort]
        self.z = self.z[:, idx_sort]
        self.freq = self.freq[idx_sort]
        self.chs_numbers = self.chs_numbers[idx_sort]
        print("sorted by freqs in descending order")
        self.remove0chs()
        print("Zero channels (switched off) are removed")


    def dataBinning(self, samplefreq = 1.0 ):			
        print("binning with ", samplefreq," kHz")
        time = self.time
        data = self.Te
        ntimes= np.size(time)
        samplingrate = 1.0/np.mean(np.diff(time))
        dataShape = np.array(np.shape(data))  
        #get the time index
        idxOfTime = np.squeeze(np.where(dataShape == ntimes))
        # if more index with the number of times exists, take the first one
        if np.size(idxOfTime) > 1:
            idxOfTime = idxOfTime[0]

        bins = int(ntimes*(float(samplefreq)*1.0e3/samplingrate))

        slices = np.linspace(0, ntimes, bins+1, True).astype(int)
        counts = np.diff(slices)

        #calculate new timebase
        newTime = np.add.reduceat(time, slices[:-1]) / counts
        newNtimes = np.size(newTime)

        #create new shape
        newDataShape = dataShape
        #replace old shape
        np.put(newDataShape, idxOfTime, newNtimes)
        #create new Data array
        newData = np.zeros( (newDataShape)  )

        #simplify array such as the first index is always the timebase
        newData = np.swapaxes(newData,0,idxOfTime)
        data = np.swapaxes( data,0,idxOfTime )

        storeShape = np.shape( newData )

        # rehape data to two dimensions
        data = np.reshape(data,(ntimes,int(float(np.size(data))/float(ntimes))))
        newData = np.reshape(newData,(newNtimes,int(float(np.size(newData))/float(newNtimes))))

        for i in range(np.shape(data)[1]):
            newData[:,i] = np.add.reduceat(data[:,i], slices[:-1]) / counts

        #shape back
        newData = np.reshape(newData,(storeShape))
        #swap back to original shape
        newData = np.swapaxes(newData,0,idxOfTime)
        self.time = newTime
        self.Te = newData

    def LoadAllRhop(self):
        "load rhop from tBegin until tEnd (EQI or EQH)"
        # self.eqm = sf.EQU(self.Shotnumber, diag=eqm_diag)
        # self.eqm_diag = eqm_diag
        rhop = sf.rz2rho(self.eqm, self.R, self.z, t_in=self.rztime,
                         coord_out='rho_pol', extrapolate=True
                         )
        self.rhop = rhop
        print("rhop is loaded")

    def Load_Rzrhop_LFS(self):
        "Load R_LFS, z_LFS, rhop_LFS, Te_LFS from tBegin until tEnd in LFS"
        sfmag = sf.SFREAD('GQH', self.Shotnumber,
                          experiment=self.Experiment, edition=self.Edition)
        Rmag = np.asarray(sfmag.getobject(
            "Rmag", tbeg=self.tBegin, tend=self.tEnd))
        R_core = np.mean(Rmag)
        idx_LFS = np.where(np.mean(self.R, axis=0) > R_core)[0]
        self.Te_LFS = self.Te[:, idx_LFS]
        self.R_LFS = self.R[:, idx_LFS]
        self.z_LFS = self.z[:, idx_LFS]
        self.freq_LFS = self.freq[idx_LFS]
        self.chs_numbers_LFS = self.chs_numbers[idx_LFS]
        if not hasattr(self, 'rhop'):
            self.LoadAllRhop()
        self.rhop_LFS = self.rhop[:, idx_LFS]
        print("R_LFS, z_LFS, rhop_LFS, Te_LFS are loaded")

    def Load_Rzrhop_cut(self, rhop_min= 0.0, rhop_max = 0.99):
        "Load R_cut, z_cut, rhop_cut, Te_cut from tBegin until tEnd in LFS"
        if not hasattr(self, 'rhop_LFS'):
            self.Load_Rzrhop_LFS()
        else:
            idx_cut = np.where(np.logical_and(
                (np.mean(self.rhop_LFS, axis=0) > rhop_min),
                (np.mean(self.rhop_LFS, axis=0) < rhop_max)
            ))[0]
            self.Te_cut = self.Te_LFS[:, idx_cut]
            self.R_cut = self.R_LFS[:, idx_cut]
            self.z_cut = self.z_LFS[:, idx_cut]
            self.freq_cut = self.freq_LFS[idx_cut]
            self.chs_numbers_cut = self.chs_numbers_LFS[idx_cut]
            self.rhop_cut = self.rhop_LFS[:, idx_cut]
            print("R_cut, z_cut, rhop_cut, Te_cut are loaded")


    def remove0chs(self):
        "remove channels that are switched off"
        remove_ch = np.where(np.mean(self.Te, axis=0) == 0.)[0]
        ch = np.arange(self.R.shape[1])
        ch = np.delete(ch, remove_ch)
        self.Te = self.Te[:, ch]
        self.R = self.R[:, ch]
        self.z = self.z[:, ch]
        self.freq = self.freq[ch]
        self.chs_numbers = self.chs_numbers[ch]
        print("the following channels are removed:")
        print(remove_ch)

    def remove_chs_NN(self, chs_to_del):
        "remove given channels"
        idxs = self.find_idxs_of_el_in_arr(self.chs_numbers, chs_to_del)
        deleted_channels = self.chs_numbers[idxs]  # double check
        self.chs_numbers = np.delete(self.chs_numbers, idxs)
        self.Te = np.delete(self.Te, idxs, axis=1)
        self.R = np.delete(self.R, idxs, axis=1)
        self.z = np.delete(self.z, idxs, axis=1)
        self.freq = np.delete(self.freq, idxs)
        if hasattr(self, 'rhop'):
            self.rhop = np.delete(self.rhop, idxs, axis=1)
        if hasattr(self, 'chs_numbers_LFS'):
            idxs = self.find_idxs_of_el_in_arr(
                self.chs_numbers_LFS, chs_to_del)
            self.chs_numbers_LFS = np.delete(self.chs_numbers_LFS, idxs)
            self.Te_LFS = np.delete(self.Te_LFS, idxs, axis=1)
            self.R_LFS = np.delete(self.R_LFS, idxs, axis=1)
            self.z_LFS = np.delete(self.z_LFS, idxs, axis=1)
            self.freq_LFS = np.delete(self.freq_LFS, idxs)
            self.rhop_LFS = np.delete(self.rhop_LFS, idxs, axis=1)
        if hasattr(self, 'chs_numbers_cut'):
            idxs = self.find_idxs_of_el_in_arr(
                self.chs_numbers_cut, chs_to_del)
            self.chs_numbers_cut = np.delete(self.chs_numbers_cut, idxs)
            self.Te_cut = np.delete(self.Te_cut, idxs, axis=1)
            self.R_cut = np.delete(self.R_cut, idxs, axis=1)
            self.z_cut = np.delete(self.z_cut, idxs, axis=1)
            self.freq_cut = np.delete(self.freq_cut, idxs)
            self.rhop_cut = np.delete(self.rhop_cut, idxs, axis=1)

        print("The following channels are deleted:")
        print(deleted_channels)

    def find_idxs_of_el_in_arr(self, array, elements):
        "find indexes of elements in an array"
        idxs = []
        for i in elements:
            if i in array:
                idx_i = list(array).index(i)
                idxs.append(idx_i)
        return idxs

    def find_nearest_idx(self, array, value):
        "find nearest idx in array for the value"
        idx = (np.abs(array - value)).argmin()
        return idx

    def find_indexes_btw_arrays(self, arr_search, arr_find_in):
        " Find the indexes in arr_find_in to each value in array_search."
        indexes = np.zeros_like(arr_search)

        for i, elem in enumerate(arr_search):
            matches = np.where(arr_find_in == elem)
            if matches[0].size > 0:
                indexes[i] = matches[0][0]

        return indexes


    def get_theta_star_for_t(self, t_in):
        # if (not hasattr(self, 'eqm')):
        #     if (self.eqm_diag != equ_diag):
        #         self.eqm = sf.EQU(self.Shotnumber, diag=equ_diag)
        Nrho, Ntheta = int(400), int(400)
        rgrid, zgrid, theta_star_grid = sf.mag_theta_star(
            self.eqm, t_in=t_in, n_rho=Nrho, n_theta=Ntheta, rz_grid=True)
        f = interpolate.interp2d(rgrid, zgrid, theta_star_grid, kind='cubic')
        idx_rztime = self.find_nearest_idx(self.rztime, t_in)
        self.theta_star = np.zeros_like(self.chs_numbers).astype(np.float)
        for i_ch, elem in enumerate(self.chs_numbers):
            self.theta_star[i_ch] = f(self.R[idx_rztime,i_ch], self.z[idx_rztime,i_ch])
        if hasattr(self, 'chs_numbers_LFS'):
            idxs = self.find_indexes_btw_arrays(self.chs_numbers_LFS, self.chs_numbers)
            self.theta_star_LFS = self.theta_star[idxs]
        if hasattr(self, 'chs_numbers_cut'):
            idxs = self.find_indexes_btw_arrays(self.chs_numbers_cut, self.chs_numbers)
            self.theta_star_cut = self.theta_star[idxs]
        print("theta_star for the time point t = %g s is loaded"%(t_in)) 
