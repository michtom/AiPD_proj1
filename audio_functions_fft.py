import math
import wave
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gmean

def get_frames(signal_array, window_len, overlap_len):
    overlap_len = int(overlap_len)
    signal_array = list(signal_array)
    signal_array.extend([0 for _ in range(overlap_len-(len(signal_array)%overlap_len))])
    signal_array = np.array(signal_array)
    frames = []
    for i in range(0, len(signal_array)-overlap_len, overlap_len):
        frames.append(signal_array[i:i+window_len])

    return frames

def create_spectrum(data, fs, **kwargs):
    magnitudes = np.abs(np.fft.rfft(data))
    length = len(data)
    freqs = np.abs(np.fft.fftfreq(length, 1.0/fs)[:length//2+1])
    
    return magnitudes, freqs

def get_f_volume(spectrum):
    vol = []
    for x in spectrum:
        vol.append(sum(x[0]**2)/len(x[0]))

    return vol

def get_f_centroid(spectrum):
    centroid = []
    for x in spectrum:
        centroid.append(sum(x[0]*x[1])/sum(x[0]))

    return centroid

def get_effective_bandwidth(spectrum, fc):
    bw = []
    for i in range(len(spectrum)):
        bw.append(sum((spectrum[i][1]-fc[i])**2*spectrum[i][0]**2)/sum(spectrum[i][0]**2))

    return bw

def get_band_energy(spectrum, f0, f1):
    be = []
    for x in spectrum:
        idxs = np.where((x[1]>f0)&(x[1]<f1))
        be.append(np.mean(x[0][idxs]))

    return be

def get_band_energy_ratio(spectrum, f0, f1):
    be = get_band_energy(spectrum, f0, f1)
    vol = get_f_volume(spectrum)
    return [i/j for i, j in zip(be,vol)]

def get_sfm(spectrum, lb, hb):
    sfm = []
    for x in spectrum:
        idxs = np.where((x[1]>lb)&(x[1]<hb))
        sfm.append(gmean(x[0][idxs])/np.mean(x[0][idxs]**2))

    return sfm

def get_scf(spectrum, lb, hb):
    scf = []
    for x in spectrum:
        idxs = np.where((x[1]>lb)&(x[1]<hb))
        scf.append(max(x[0]**2)/np.mean(x[0][idxs]**2))

    return scf

def plot_frames(data, title):
    plt.plot(data)
    plt.xlabel("n")
    plt.title(title)

def plot_spectrum(signal, start, end, framerate):
    start_index = int((start/1000)*framerate)
    end_index = int((end/1000)*framerate)
    signal = signal[start_index:end_index]
    spectrum = create_spectrum(signal, framerate)
    plt.plot(spectrum[1], spectrum[0])
    plt.title("Spectrum")
    plt.xlabel("freq")
    plt.ylabel("magnitude")
