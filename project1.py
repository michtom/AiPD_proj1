import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
import wave
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)


class GUI:

    def analyze(self, file):
        frames = file.getnframes()
        audio = file.readframes(frames)
        rate = file.getframerate()
        duration = frames / rate
        times = np.linspace(0, frames / rate, num=frames)
        audio_as_np_int16 = np.frombuffer(audio, dtype=np.int16)
        audio_as_np_float32 = audio_as_np_int16.astype(np.float32)
        # Normalise float32 array so that values are between -1.0 and +1.0
        max_int16 = 2 ** 15
        audio_normalised = audio_as_np_float32 / max_int16
        ttk.Label(self.window, text="The file is " + str(duration) + " seconds long").pack()
        channel_num = file.getnchannels()
        string_3 = " channel"
        if channel_num > 1:
            string_3 += "s"
            ttk.Label(self.window, text="So far focusing only on first channel").pack()
            audio_normalised = audio_normalised[1::channel_num]
        ttk.Label(self.window, text="The sound has " + str(channel_num) + string_3).pack()
        self.plot_basic(audio_normalised, times)
        volume = [0 for i in range(0, frames - 4, 256)]
        j = 0
        for i in range(0, frames - 255, 256):
            volume[j] = np.sqrt(0.2 * sum(audio_normalised[i:i + 255] ** 2))
            j += 1
        self.plot_volume(volume)

        # self.plot_spectrogram(audio, rate)

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Sound analysing app")
        self.window.geometry("900x600+50+50")
        ttk.Label(self.window, text="Upload a .wav file").pack()
        ttk.Button(self.window, text="Open", command=self.open_file).pack()
        self.window.mainloop()

    def plot_spectrogram(self, audio, freq):
        # to be fixed
        fig = Figure()
        plot1 = fig.add_subplot(111)
        plot1.specgram(audio, Fs=freq, vmin=-20, vmax=50)
        plot1.set_xlabel("Time (s)")
        plot1.set_ylabel("Frequency (Hz)")
        plot1.set_title("Spectrogram")
        plot1.colorbar()
        canvas = FigureCanvasTkAgg(fig, master=self.window)
        canvas.draw()
        canvas.get_tk_widget().pack()
        toolbar = NavigationToolbar2Tk(canvas, self.window)
        toolbar.update()
        canvas.get_tk_widget().pack()

    def plot_basic(self, audio, times):
        fig = Figure()
        plot1 = fig.add_subplot(111)
        plot1.plot(times, audio)
        plot1.set_ylabel("Amplitude")
        plot1.set_xlabel("Time (s)")
        canvas = FigureCanvasTkAgg(fig, master=self.window)
        canvas.draw()
        canvas.get_tk_widget().pack()
        toolbar = NavigationToolbar2Tk(canvas, self.window)
        toolbar.update()
        canvas.get_tk_widget().pack()

    def plot_volume(self, volume):
        fig = Figure()
        plot1 = fig.add_subplot(111)
        plot1.plot(volume)
        plot1.set_ylabel("volume")
        plot1.set_xlabel("time")
        canvas = FigureCanvasTkAgg(fig, master=self.window)
        canvas.draw()
        canvas.get_tk_widget().pack()
        toolbar = NavigationToolbar2Tk(canvas, self.window)
        toolbar.update()
        canvas.get_tk_widget().pack()

    def open_file(self):
        filename = fd.askopenfilename(
            title="Open a file",
            initialdir='/',
            filetypes=[('wave file', '*.wav')]
        )
        file = wave.open(filename, 'r')
        self.analyze(file)


def main():
    GUI()


if __name__ == '__main__':
    main()
