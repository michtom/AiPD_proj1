import math
import wave
import numpy as np
import matplotlib.pyplot as plt


def cut_file(file, start_time, end_time):
    """
    Prepares signal array of normalised amplitudes
    """
    file.rewind()
    start = math.ceil((start_time/1000)*file.getframerate())
    end = math.ceil((end_time/1000)*file.getframerate())
    file.readframes(start)
    signal_array = np.frombuffer(file.readframes(end-start), dtype=np.int16)
    signal_array = signal_array/2**15
    return signal_array, end-start

def get_window_len(file):
    """
    As frame length should be between 10ms and 40ms
    window_len should be between 10ms*framerate and 40ms*framerate
    We choose maximum possible frame width to satisfy
    """
    result = int(40/1000*file.getframerate())
    if result%2==1: result-=1

    return result

def get_zcr(signal_array, window_len, overlap_len):
    """
    Returns zcr array
    """

    zcr = []
    for i in range(0, len(signal_array)-overlap_len, overlap_len):
        s = signal_array[i:i+window_len]
        s = np.where(s>0, 1,
            np.where(s==0, 0, -1))
        result =  sum(abs(s[1:]-s[:-1]))/(2*window_len)
        zcr.append(result)

    return np.array(zcr)

def get_ste(signal_array, window_len, overlap_len):
    """
    Returns ste array
    """
    ste = []
    for i in range(0, len(signal_array)-overlap_len, overlap_len):
        ste.append(sum(signal_array[i:i+window_len]**2)/window_len)

    return np.array(ste)

def get_volume(signal_array, window_len, overlap_len):
    """
    Return volume array
    """
    return (get_ste(signal_array, window_len, overlap_len)**(1/2))

def get_frame_length(window_len, framerate):
    return window_len*1000/framerate

def cut_signal_array(signal, start, end, framerate):

    """
    Cuts a fragment of a signal array, takes times as arguments
    """

    start_index = int((start/1000)*framerate)
    end_index = int((end/1000)*framerate)
    return signal[start_index:end_index]

def get_silence_frames(signal, silence, window_len, overlap_len, vol, zcr):

    """
    Returns array indicating which frames are classified as silence (0 is silence, 1 is not)
    """

    zcr_silence = get_zcr(silence, window_len, overlap_len)
    vol_silence = get_volume(silence, window_len, overlap_len)

    zcr_threshold = max(zcr_silence)
    vol_threshold = max(vol_silence)

    silence = []
    for i in range(len(vol)):
        if vol[i]<=vol_threshold and zcr[i]<=zcr_threshold:
            silence.append(0)
        else:
            silence.append(1)

    return np.array(silence)

def plot_signal(signal, zcr, vol, silence, voiced, framerate):


    duration = len(signal)/framerate
    times = np.linspace(0, duration, len(signal))
    times2 = np.linspace(0, duration, len(zcr))
    plt.figure(figsize=(40, 8))
    plt.plot(times, signal)
    plt.plot(times2, zcr/max(zcr))
    plt.plot(times2, vol/max(vol))
    plt.plot(times2, silence)
    #plt.plot(times2, voiced)

def get_vdr(vol):
    return (max(vol)-min(vol))/max(vol)

def get_lster(signal, ste, framerate):
    onesec_window_width = int(len(ste)/(len(signal)/framerate))
    onesec_window_width_ceil = int(np.ceil(len(ste)/(len(signal)/framerate)))
    lster = []
    for i in range(0, len(ste)-onesec_window_width, onesec_window_width):
        result = sum(np.array(list(map(lambda x: sgn(x), ste[i:i+onesec_window_width_ceil] - 0.5*np.mean(ste[i:i+onesec_window_width_ceil]))))+1)/(2*onesec_window_width_ceil)
        lster.append(result)
        lster.append(result)

    return lster

def sgn(x):
    if x > 0:
        return 1
    elif x == 0:
        return 0
    else:
        return -1

