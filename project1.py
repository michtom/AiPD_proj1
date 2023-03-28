import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import Frame
import wave
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)


class GUI:

    def __init__(self):
        self.times = None
        self.audio_normalised = None
        self.volume = None
        self.window = tk.Tk()
        self.window.title("Sound analysing app")
        self.window.geometry("900x600+50+50")
        ttk.Label(self.window, text="Upload a .wav file").grid(row=0, column=0)
        button = ttk.Button(self.window, text="Open", command=self.open_file)
        button.grid(row=1, column=0, padx=5, pady=5)
        self.plot_basic()
        self.plot_volume()
        self.window.mainloop()

    def analyze(self, file):
        frames = file.getnframes()
        audio = file.readframes(frames)
        rate = file.getframerate()
        duration = frames / rate
        self.times = np.linspace(0, frames / rate, num=frames)
        audio_as_np_int16 = np.frombuffer(audio, dtype=np.int16)
        audio_as_np_float32 = audio_as_np_int16.astype(np.float32)
        # Normalise float32 array so that values are between -1.0 and +1.0
        max_int16 = 2 ** 15
        self.audio_normalised = audio_as_np_float32 / max_int16
        ttk.Label(self.window, text="Length: " + str(duration) + "s").grid(row=2, column=0, pady=5, padx=2)
        channel_num = file.getnchannels()
        if channel_num > 1:
            ttk.Label(self.window, text="Choosing channel 1").grid(row=4, column=0, pady=5, padx=2)
            self.audio_normalised = self.audio_normalised[1::channel_num]
        ttk.Label(self.window, text="No. of channels: " + str(channel_num)).grid(row=3, column=0, pady=5, padx=2)
        self.volume = [0 for i in range(0, frames - 4, 256)]
        j = 0
        for i in range(0, frames - 255, 256):
            self.volume[j] = np.sqrt(0.2 * sum(self.audio_normalised[i:i + 255] ** 2))
            j += 1
        self.plot_basic()
        self.plot_volume()

    def plot_basic(self):
        fig = Figure(figsize=(8, 3), dpi=100)
        plot1 = fig.add_subplot(111)
        if self.times is not None and self.audio_normalised is not None:
            plot1.plot(self.times, self.audio_normalised)
        plot1.set_ylabel("Amplitude")
        plot1.set_xlabel("Time (s)")
        canvas = FigureCanvasTkAgg(fig, master=self.window)
        canvas.draw()
        canvas.get_tk_widget().grid(row=1, column=1, rowspan=8, columnspan=3, padx=10, pady=10)
        toolbar_frame = Frame(master=self.window)
        toolbar_frame.grid(row=9, column=1)
        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
        toolbar.update()
        canvas.get_tk_widget().grid(row=1, column=1)

    def plot_volume(self):
        fig = Figure(figsize=(8, 3), dpi=100)
        plot1 = fig.add_subplot(111)
        if self.volume is not None:
            plot1.plot(self.volume)
        plot1.set_ylabel("volume")
        plot1.set_xlabel("time")
        canvas = FigureCanvasTkAgg(fig, master=self.window)
        canvas.draw()
        canvas.get_tk_widget().grid(row=10, column=1, rowspan=8, columnspan=3, pady=10, padx=10)
        toolbar_frame = Frame(master=self.window)
        toolbar_frame.grid(row=18, column=1)
        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
        toolbar.update()
        canvas.get_tk_widget().grid(row=10, column=1)

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
