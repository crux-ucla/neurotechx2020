#all code
import pandas as pd
import numpy as np
from scipy import signal
from scipy.integrate import simps
import time
import requests

alow, ahigh = 8, 12
blow, bhigh = 12.5, 30

def compute_periodogram(eegdata):
  #Find the power spectral density of the data
  p_freqs, p_psd = signal.periodogram(eegdata, srate)
  #Frequency resolution (bin size)
  p_freq_res = p_freqs[1] - p_freqs[0]
  #Find intersecting values in frequency vector
  p_idx_alpha = np.logical_and(p_freqs >= alow, p_freqs <= ahigh)
  p_idx_beta = np.logical_and(p_freqs >= blow, p_freqs <= bhigh)
  
  # Compute the absolute power by approximating the area under the curve
  p_alpha_power = simps(p_psd[p_idx_alpha], dx=p_freq_res)
  
  p_beta_power = simps(p_psd[p_idx_beta], dx=p_freq_res)

	# Relative power (expressed as a percentage of total power)
  p_total_power = simps(p_psd, dx=p_freq_res)

  p_alpha_rel_power = p_alpha_power / p_total_power

  p_beta_rel_power = p_beta_power / p_total_power
  
  return(pd.DataFrame([p_alpha_rel_power,p_beta_rel_power]))
  
def compute_Welch(data):
  #Length of Fourier Transform
  winlength = 1 * srate 
  #noverlap is number of points of overlap
  nOverlap = np.round(srate/2)
  #Calculated power spectral density
  w_freqs, w_psd = signal.welch(data, srate, nperseg=winlength, noverlap=nOverlap)
  #if not specified, noverlap = 50%

  # Find intersecting values in frequency vector
  w_idx_alpha = np.logical_and(w_freqs >= alow, w_freqs <= ahigh)
  w_idx_beta = np.logical_and(w_freqs >= blow, w_freqs <= bhigh)

  #Frequency resolution
  w_freq_res = w_freqs[1] - w_freqs[0]

  # Compute the absolute power by approximating the area under the curve
  w_alpha_power = simps(w_psd[w_idx_alpha], dx=w_freq_res)
  w_beta_power = simps(w_psd[w_idx_beta], dx=w_freq_res)

  # Relative delta power (expressed as a percentage of total power)
  w_total_power = simps(w_psd, dx=w_freq_res)

  w_alpha_rel_power = w_alpha_power / w_total_power

  w_beta_rel_power = w_beta_power / w_total_power
  return(pd.DataFrame([w_alpha_rel_power,w_beta_rel_power]))

data = pd.read_csv('/Users/eugen/Desktop/Sample_Muse_Data.csv', sep = ',', header = 1, usecols = [0,1,2,3,4], skip_blank_lines = True, names = ['Time','EEG1','EEG2','EEG3','EEG4'])
data = data.dropna()
#data['Time'] = data['Time'] - data['Time'][0]
srate = 256

#Calculating Welch's method over first 1 minute to get baseline alpha/beta values
eegdata2 = data.iloc[0:srate*60,2]
eegdata3 = data.iloc[0:srate*60,3]

w_rel_power2 = pd.DataFrame.transpose(compute_Welch(eegdata2))
w_rel_power3 = pd.DataFrame.transpose(compute_Welch(eegdata3))
  
w_rel_power2.columns = ["Alpha_Rel","Beta_Rel"]
w_rel_power3.columns = ["Alpha_Rel","Beta_Rel"]

powers_eeg2= pd.DataFrame()
powers_eeg3= pd.DataFrame() 
#iterate such that 50% overlap, so start at 256 data points after the previous starting point (i.e. 1 second after)
#look at 2nd minute's worth of data, starting at 60 seconds and 50% overlap till last interval

#we could find length of time in seconds: len(data) / srate -> number of iterations for the for loop  (seconds - 1)

for starting_sec in range(60,119) :
  start = starting_sec * srate #start of each 2 seconds worth of data
  end = (starting_sec * srate) + (srate * 2) #end, srate*2 = 2 seconds worth of data
  
  #in case we don't get enough data points for the last iteration
  if(end > len(data)):
    eeg2 = data.iloc[start:len(data), 2]
    eeg3 = data.iloc[start:len(data), 3]
  else:
    eeg2 = data.iloc[start:end, 2]
    eeg3 = data.iloc[start:end, 3]
  
  #get the powers from periodogram
  eeg2_powers = pd.DataFrame.transpose(compute_periodogram(eeg2))
  eeg3_powers = pd.DataFrame.transpose(compute_periodogram(eeg3))
  
  #add the values to dataframe for future calculations/reference
  powers_eeg2 = pd.concat([powers_eeg2,eeg2_powers], ignore_index = True)
  powers_eeg3 = pd.concat([powers_eeg3,eeg3_powers], ignore_index = True)

#relative alpha and beta powers separated by electrode
powers_eeg2.columns = ["Alpha_Rel","Beta_Rel"]
powers_eeg3.columns = ["Alpha_Rel","Beta_Rel"]

#combined relative alpha and beta powers
alpha = (powers_eeg2.iloc[:, 0].values + powers_eeg3.iloc[:, 0].values)/2
beta = (powers_eeg2.iloc[:, 1].values + powers_eeg3.iloc[:, 1].values)/2

w2alpha = w_rel_power2.iat[0,0]
w2beta = w_rel_power2.iat[0,1]
w3alpha = w_rel_power3.iat[0,0]
w3beta = w_rel_power3.iat[0,1]

#average baseline alpha and beta powers
alpha_total = (w2alpha + w3alpha)/2
beta_total = (w2beta + w3beta)/2


baselined_alpha = pd.DataFrame(((alpha - alpha_total)/alpha_total)*100)
baselined_beta = pd.DataFrame(((beta - beta_total)/beta_total)*100)

#alpha asymmetry, eeg2 is left and eeg 3 is right electrode, taking natural log
alpha_asym = np.log(powers_eeg2.iloc[:,0]) - np.log(powers_eeg3.iloc[:,0])

#To simulate streaming, we update our database periodically with the values
#given in the sequences
request_url = "http://localhost:8010/proxy/test/"
 
alpha_percent_change = baselined_alpha.values[:, 0]
beta_percent_change = baselined_beta.values[:, 0]
alpha_asymmetry = alpha_asym.values

for i in range(len(alpha_percent_change)): 
    requests.put(request_url + "alpha", json={'value': round(alpha_percent_change[i], 3)})
    requests.put(request_url + "beta", json={'value': round(beta_percent_change[i], 3)})
    requests.put(request_url + "alphaAsymmetry", json={'value': round(alpha_asymmetry[i], 3)})
    time.sleep(2)
