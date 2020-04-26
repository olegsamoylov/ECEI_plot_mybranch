import matplotlib.pyplot as plt
import numpy as np

import sys
import pathlib
path_of_the_current_file = str(pathlib.Path().absolute())
sys.path.append(path_of_the_current_file+'/modules')
import my_funcs_class as my_funcs
import importlib
importlib.reload(my_funcs)


x = np.linspace(0.0,6.28, 10000)
y = np.sin(x) + 5*np.cos(100.00*x) + 2.0*np.sin(5.0*x) + np.random.normal(0,1,len(x))


mf=my_funcs.my_funcs()
freq_fft, y_fft, offset = mf.fft_analysis(x,y)
noise_level_value = np.max(np.abs(y_fft))*1.0

f_cut_lp = 400.0/(2*np.pi)
f_cut_hp = 50.0/(2*np.pi)

# NN_len = len(freq_fft)
# idx_freq = mf.find_nearest_idx(freq_fft[:int(NN_len/2)], f_cut) 
# freq_fft[idx_freq]
# Y2 = y_fft.copy()
# idx_cut = (np.abs(y_fft[idx_freq:NN_len-idx_freq]) < noise_level_value) 
# idx_cut1 = (np.abs(y_fft[:idx_freq]) <= noise_level_value)
# idx_cut2 = (np.abs(y_fft[NN_len-idx_freq:]) <= noise_level_value)

# Y2[:idx_freq][idx_cut1] = 0.0
# Y2[NN_len-idx_freq:][idx_cut2] = 0.0

y_fft_f_lp = mf.set_to_0_below_level_within_range_lowpass(freq_fft, y_fft, noise_level_value, f_cut_lp)
y_fft_f_hp = mf.set_to_0_below_level_within_range_highpass(freq_fft, y_fft_f_lp, noise_level_value, f_cut_hp)


y_fft_f_ifft = mf.inverse_fft(y_fft_f_hp,offset)



plt.plot(x,y, "b")
plt.plot(x,y_fft_f_ifft, "r")
plt.show()


# plt.plot(2*np.pi*freq_fft,np.abs(y_fft), "b")
# plt.plot(2*np.pi*freq_fft,np.abs(y_fft_f_hp), "r")
# plt.plot(2*np.pi*freq_fft,np.abs(Y2), "r")
# plt.plot(2*np.pi*freq_fft,np.abs(Y2), "r")

# plt.show()





