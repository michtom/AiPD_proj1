import numpy as np


def rectangular_window(frame):
    return np.ones(len(frame))


def triangular_window(frame):
    N = len(frame)
    n_list = np.array(range(N))
    return 1 - (2*np.abs(n_list-(N-1)/2))/(N-1)


def hanning_window(frame):
    N = len(frame)
    n_list = np.array(range(N))
    return (1-np.cos((2*np.pi*n_list)/(N-1)))/2


def hamming_window(frame):
    N = len(frame)
    n_list = np.array(range(N))
    return 0.54 - 0.46*np.cos((2*np.pi*n_list)/(N-1))


def blackman_window(frame):
    N = len(frame)
    n_list = np.array(range(N))
    return 0.42 - 0.5*np.cos((2*np.pi*n_list)/(N-1)) + 0.08*np.cos((4*np.pi*n_list)/(N-1))


def get_windowed_audio(audio, frame_length, window_type):
    if audio is None:
        return audio
    n = len(audio)
    audio_windowed = [0 for i in range(n)]
    if window_type == 2:
        for i in range(0, n, frame_length):
            audio_windowed[i:i+frame_length] = rectangular_window(audio[i:i+frame_length])*audio[i:i+frame_length]
    elif window_type == 3:
        for i in range(0, n, frame_length):
            audio_windowed[i:i+frame_length] = triangular_window(audio[i:i+frame_length])*audio[i:i+frame_length]
    elif window_type == 4:
        for i in range(0, n, frame_length):
            audio_windowed[i:i+frame_length] = hanning_window(audio[i:i+frame_length])*audio[i:i+frame_length]
    elif window_type == 5:
        for i in range(0, n, frame_length):
            audio_windowed[i:i+frame_length] = hamming_window(audio[i:i+frame_length])*audio[i:i+frame_length]
    elif window_type == 6:
        for i in range(0, n, frame_length):
            audio_windowed[i:i+frame_length] = blackman_window(audio[i:i+frame_length])*audio[i:i+frame_length]
    return audio_windowed
