import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import Frame
import wave
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.colors import ListedColormap
import audio_functions
from audio_functions import *
import pandas as pd


class Toolbar(NavigationToolbar2Tk):
    """
    override NavigationToolbar2Tk class from matplotlib to set off displaying coordinates on a plot
    """
    def set_message(self, s):
        pass


class GUI:

    def __init__(self):
        self.channel_label = None
        self.length_label = None
        self.hzcr = None
        self.lster = None
        self.voiced = None
        self.ste = None
        self.silence = None
        self.duration = None
        self.zcr = None
        self.times = None
        self.audio_normalised = None
        self.volume = None
        self.window = tk.Tk()
        self.window.title("Sound analysing app")
        self.window.geometry("1200x500+50+50")
        # a button to open and load a desired .wav file
        ttk.Label(self.window, text="Upload a .wav file").grid(row=0, column=0)
        button = ttk.Button(self.window, text="Open", command=self.open_file)
        button.grid(row=1, column=0, padx=5, pady=5)
        # a button to choose a plot to be displayed
        ttk.Label(self.window, text="Select plot to be shown").grid(row=0, column=4)
        self.var_plot = tk.IntVar()
        self.var_plot.set(1)
        ttk.Radiobutton(self.window, text="basic plot",
                        variable=self.var_plot, value=1, command=self.choose_plot).grid(row=1, column=4, sticky="we")
        ttk.Radiobutton(self.window, text="volume plot",
                        variable=self.var_plot, value=2, command=self.choose_plot).grid(row=2, column=4, sticky="we")
        ttk.Radiobutton(self.window, text="ZCR plot",
                        variable=self.var_plot, value=3, command=self.choose_plot).grid(row=3, column=4, sticky="we")
        ttk.Radiobutton(self.window, text="STE plot",
                        variable=self.var_plot, value=4, command=self.choose_plot).grid(row=4, column=4, sticky="we")
        ttk.Radiobutton(self.window, text="LSTER plot",
                        variable=self.var_plot, value=5, command=self.choose_plot).grid(row=5, column=4, sticky="we")
        ttk.Radiobutton(self.window, text="HZCR plot",
                        variable=self.var_plot, value=6, command=self.choose_plot).grid(row=6, column=4, sticky="we")
        self.choose_plot()
        # a button to choose which parameter should be marked as red background on a plot
        self.value_red = tk.IntVar()
        self.value_red.set(1)
        ttk.Label(self.window, text="Select value to be displayed in red").grid(row=7, column=4)
        ttk.Radiobutton(self.window, text="silence",
                        variable=self.value_red, value=1, command=self.choose_plot).grid(row=8, column=4, sticky="we")
        ttk.Radiobutton(self.window, text="voiced frames",
                        variable=self.value_red, value=2, command=self.choose_plot).grid(row=9, column=4, sticky="we")
        self.window.mainloop()

    def open_file(self):
        filename = fd.askopenfilename(
            title="Open a file",
            initialdir='/',
            filetypes=[('wave file', '*.wav')]
        )
        file = wave.open(filename, 'r')
        self.analyze(file)

    def analyze(self, file):
        """
        a function that extracts parameters from .wav file
        """
        frames = file.getnframes()
        rate = file.getframerate()
        self.duration = frames / rate
        self.times = np.linspace(0, frames / rate, num=frames)
        window_len = audio_functions.get_window_len(file)
        overlap_len = int(window_len / 2)
        self.audio_normalised, something = audio_functions.cut_file(file, 0, frames)
        channel_num = file.getnchannels()
        if self.length_label is None:
            self.length_label = ttk.Label(self.window, text="Length: " + str(self.duration) + "s")
            self.length_label.grid(row=2, column=0, pady=5, padx=2)
            self.channel_label = ttk.Label(self.window, text="No. of channels: " + str(channel_num))
            self.channel_label.grid(row=3, column=0, pady=5, padx=2)
            if channel_num > 1:
                ttk.Label(self.window, text="Choosing channel 1").grid(row=4, column=0, pady=5, padx=2)
                self.audio_normalised = self.audio_normalised[1::channel_num]
        else:
            self.length_label.config(text="Length: " + str(self.duration) + "s")
            self.channel_label.config(text="No. of channels: " + str(channel_num))
        self.zcr = audio_functions.get_zcr(self.audio_normalised, window_len, overlap_len)
        self.volume = audio_functions.get_volume(self.audio_normalised, window_len, overlap_len)
        self.ste = audio_functions.get_ste(self.audio_normalised, window_len, overlap_len)
        self.voiced = audio_functions.get_voiced_frames(self.volume, self.zcr)
        self.lster = audio_functions.get_lster(self.audio_normalised, self.ste, rate)
        self.hzcr = audio_functions.get_hzcr(self.audio_normalised, self.zcr, rate)
        vol_treshold = 10e-3
        zcr_treshold = 0.1
        self.silence = audio_functions.get_silence_frames(self.volume, self.zcr, vol_treshold, zcr_treshold)
        self.choose_plot()

    def choose_plot(self):
        """
        a function that calls a correct plotting function, based on a choice from a button
        """
        value = self.var_plot.get()
        if value == 1:
            self.plot_basic()
        elif value == 2:
            self.plot_volume()
        elif value == 3:
            self.plot_zcr()
        elif value == 4:
            self.plot_ste()
        elif value == 5:
            self.plot_lster()
        elif value == 6:
            self.plot_hzcr()
        return

    def plot_basic(self):
        """
        a function that plots amplitudes of a .wav file
        """
        fig = Figure(figsize=(8, 4), dpi=100)
        plot1 = fig.add_subplot(111)
        if self.times is not None and self.audio_normalised is not None:
            plot1.plot(self.times, self.audio_normalised)
            plot1.set_xlim([0, max(self.times)])
        # choose parameter displayed as red background, based on choice from a button (used in every plotting function)
        cmap = ListedColormap(['white', 'red'])
        if self.silence is not None and self.value_red.get() == 1:
            plot1.pcolorfast(plot1.get_xlim(), plot1.get_ylim(), pd.DataFrame(self.silence).values[np.newaxis],
                             cmap=cmap, alpha=0.4)
        if self.voiced is not None and self.value_red.get() == 2:
            plot1.pcolorfast(plot1.get_xlim(), plot1.get_ylim(), pd.DataFrame(self.voiced).values[np.newaxis],
                             cmap=cmap, alpha=0.4)
        plot1.set_ylabel("Amplitude")
        plot1.set_xlabel("Time (s)")
        #        if self.duration is not None:
        #            plot1.set_xticks(np.linspace(0, self.duration, 10).astype(int).tolist())
        canvas = FigureCanvasTkAgg(fig, master=self.window)
        canvas.draw()
        canvas.get_tk_widget().grid(row=1, column=1, rowspan=8, columnspan=3, padx=10, pady=10, sticky="nsew")
        toolbar_frame = Frame(master=self.window)
        toolbar_frame.grid(row=9, column=1)
        toolbar = Toolbar(canvas, toolbar_frame)
        toolbar.update()
        canvas.get_tk_widget().grid(row=1, column=1)

    def plot_volume(self):
        """
        a function that plots volume of a sound
        """
        fig = Figure(figsize=(8, 4), dpi=100)
        plot1 = fig.add_subplot(111)
        if self.volume is not None:
            xaxis = np.linspace(0, self.duration, num=len(self.volume))
            plot1.plot(xaxis, self.volume)
            plot1.set_xlim([0, max(xaxis)])
        cmap = ListedColormap(['white', 'red'])
        if self.silence is not None and self.value_red.get() == 1:
            plot1.pcolorfast(plot1.get_xlim(), plot1.get_ylim(), pd.DataFrame(self.silence).values[np.newaxis],
                             cmap=cmap, alpha=0.4)
        if self.voiced is not None and self.value_red.get() == 2:
            plot1.pcolorfast(plot1.get_xlim(), plot1.get_ylim(), pd.DataFrame(self.voiced).values[np.newaxis],
                             cmap=cmap, alpha=0.4)
        plot1.set_ylabel("Volume")
        plot1.set_xlabel("Time (s)")
        canvas = FigureCanvasTkAgg(fig, master=self.window)
        canvas.draw()
        canvas.get_tk_widget().grid(row=1, column=1, rowspan=8, columnspan=3, pady=10, padx=10, sticky="nsew")
        toolbar_frame = Frame(master=self.window)
        toolbar_frame.grid(row=9, column=1)
        toolbar = Toolbar(canvas, toolbar_frame)
        toolbar.update()
        canvas.get_tk_widget().grid(row=1, column=1)

    def plot_zcr(self):
        """
        a function that plots Zero-crossing rate of a sound
        """
        fig = Figure(figsize=(8, 4), dpi=100)
        plot1 = fig.add_subplot(111)
        if self.zcr is not None:
            xaxis = np.linspace(0, self.duration, num=len(self.zcr))
            plot1.plot(xaxis, self.zcr)
            plot1.set_xlim([0, max(xaxis)])
        cmap = ListedColormap(['white', 'red'])
        if self.silence is not None and self.value_red.get() == 1:
            plot1.pcolorfast(plot1.get_xlim(), plot1.get_ylim(), pd.DataFrame(self.silence).values[np.newaxis],
                             cmap=cmap, alpha=0.4)
        if self.voiced is not None and self.value_red.get() == 2:
            plot1.pcolorfast(plot1.get_xlim(), plot1.get_ylim(), pd.DataFrame(self.voiced).values[np.newaxis],
                             cmap=cmap, alpha=0.4)
        plot1.set_ylabel("Zero-crossing rate")
        plot1.set_xlabel("Time (s)")
        canvas = FigureCanvasTkAgg(fig, master=self.window)
        canvas.draw()
        canvas.get_tk_widget().grid(row=1, column=1, rowspan=8, columnspan=3, pady=10, padx=10)
        toolbar_frame = Frame(master=self.window)
        toolbar_frame.grid(row=9, column=1)
        toolbar = Toolbar(canvas, toolbar_frame)
        toolbar.update()
        canvas.get_tk_widget().grid(row=1, column=1)

    def plot_ste(self):
        """
        a function that plots short-time energy of a sound
        """
        fig = Figure(figsize=(8, 4), dpi=100)
        plot1 = fig.add_subplot(111)
        if self.ste is not None:
            plot1.plot(np.linspace(0, self.duration, num=len(self.ste)), self.ste)
        cmap = ListedColormap(['white', 'red'])
        if self.silence is not None and self.value_red.get() == 1:
            plot1.pcolorfast(plot1.get_xlim(), plot1.get_ylim(), pd.DataFrame(self.silence).values[np.newaxis],
                             cmap=cmap, alpha=0.4)
        if self.voiced is not None and self.value_red.get() == 2:
            plot1.pcolorfast(plot1.get_xlim(), plot1.get_ylim(), pd.DataFrame(self.voiced).values[np.newaxis],
                             cmap=cmap, alpha=0.4)
        plot1.set_ylabel("Short-time energy")
        plot1.set_xlabel("Time (s)")
        canvas = FigureCanvasTkAgg(fig, master=self.window)
        canvas.draw()
        canvas.get_tk_widget().grid(row=1, column=1, rowspan=8, columnspan=3, pady=10, padx=10)
        toolbar_frame = Frame(master=self.window)
        toolbar_frame.grid(row=9, column=1)
        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
        toolbar.update()
        canvas.get_tk_widget().grid(row=1, column=1)

    def plot_lster(self):
        """
        a function that plots low short-time energy rate of a sound
        """
        fig = Figure(figsize=(8, 4), dpi=100)
        plot1 = fig.add_subplot(111)
        if self.lster is not None:

            lster_linspace = audio_functions.get_lster_linspace(self.lster, self.duration)
            plot1.plot(lster_linspace, np.array([[x, x] for x in self.lster]).flatten())
        cmap = ListedColormap(['white', 'red'])
        if self.silence is not None and self.value_red.get() == 1:
            plot1.pcolorfast(plot1.get_xlim(), plot1.get_ylim(), pd.DataFrame(self.silence).values[np.newaxis],
                             cmap=cmap, alpha=0.4)
        if self.voiced is not None and self.value_red.get() == 2:
            plot1.pcolorfast(plot1.get_xlim(), plot1.get_ylim(), pd.DataFrame(self.voiced).values[np.newaxis],
                             cmap=cmap, alpha=0.4)
        plot1.set_ylabel("Low Short-time energy ratio")
        plot1.set_xlabel("Time (s)")
        canvas = FigureCanvasTkAgg(fig, master=self.window)
        canvas.draw()
        canvas.get_tk_widget().grid(row=1, column=1, rowspan=8, columnspan=3, pady=10, padx=10)
        toolbar_frame = Frame(master=self.window)
        toolbar_frame.grid(row=9, column=1)
        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
        toolbar.update()
        canvas.get_tk_widget().grid(row=1, column=1)

    def plot_hzcr(self):
        """
        a function that plots low short-time energy rate of a sound
        """
        fig = Figure(figsize=(8, 4), dpi=100)
        plot1 = fig.add_subplot(111)
        if self.hzcr is not None:
            hzcr_linspace = audio_functions.get_lster_linspace(self.hzcr, self.duration)
            plot1.plot(hzcr_linspace, np.array([[x, x] for x in self.hzcr]).flatten())
        cmap = ListedColormap(['white', 'red'])
        if self.silence is not None and self.value_red.get() == 1:
            plot1.pcolorfast(plot1.get_xlim(), plot1.get_ylim(), pd.DataFrame(self.silence).values[np.newaxis],
                             cmap=cmap, alpha=0.4)
        if self.voiced is not None and self.value_red.get() == 2:
            plot1.pcolorfast(plot1.get_xlim(), plot1.get_ylim(), pd.DataFrame(self.voiced).values[np.newaxis],
                             cmap=cmap, alpha=0.4)
        plot1.set_ylabel("High zero crossing rate")
        plot1.set_xlabel("Time (s)")
        canvas = FigureCanvasTkAgg(fig, master=self.window)
        canvas.draw()
        canvas.get_tk_widget().grid(row=1, column=1, rowspan=8, columnspan=3, pady=10, padx=10)
        toolbar_frame = Frame(master=self.window)
        toolbar_frame.grid(row=9, column=1)
        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
        toolbar.update()
        canvas.get_tk_widget().grid(row=1, column=1)


def main():
    GUI()


if __name__ == '__main__':
    main()
