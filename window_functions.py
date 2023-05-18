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
