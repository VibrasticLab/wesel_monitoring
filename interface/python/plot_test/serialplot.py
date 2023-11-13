#!/usr/bin/python
# -*- coding: utf-8 -*-

# gui toolkit
import tkinter as tk
from tkinter import font
import tkinter.filedialog as filedlg

# plotting features
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import matplotlib.animation as plotani
from matplotlib.figure import Figure
from matplotlib import style

# additional
import sys
import serial
import numpy as np
from time import sleep
from threading import Thread as thd

class SerialPlotTest():

    DataLong    = 512
    DataIdx     = 0
    PlotUpd     = True
    SerThdRun   = True
    PrintY      = False
    SavName     = ''
    BaudRate    = 57600

    def __init__(self):
        super(SerialPlotTest, self).__init__()

        # main Window
        self.window = tk.Tk()
        self.window.geometry("800x600")
        self.window.resizable(False,False)
        self.window.title("Serial Plot Test")

        self.lbltitle = tk.Label(self.window, text="Serial Plot Test")
        self.lbltitle.pack(side=tk.TOP)

        # Window Font
        wndfont = font.Font(self.window, family="Liberation Mono", size=15)
        self.lbltitle.config(font=wndfont)

        # Info Frame
        self.infofrm = tk.Frame(self.window)
        self.infofrm.pack(side=tk.TOP)

        # Button Frame
        self.buttonfrm = tk.Frame(self.infofrm)
        self.buttonfrm.pack(side=tk.TOP)

        # Plot Button
        self.pausebtn = tk.Button(self.buttonfrm, text="Pause", command=self.plot_pause)
        self.pausebtn.config(font=wndfont)
        self.pausebtn.pack(side=tk.RIGHT)

        # Save Data Button
        self.savdatbtn = tk.Button(self.buttonfrm, text="Dump", command=self.csv_save)
        self.savdatbtn.config(font=wndfont)
        self.savdatbtn.pack(side=tk.LEFT)

        # Save Image Button
        self.savimgbtn = tk.Button(self.buttonfrm, text="Save", command=self.plot_save)
        self.savimgbtn.config(font=wndfont)
        self.savimgbtn.pack(side=tk.LEFT)

        # Graph Frame
        self.graphfrm = tk.Frame()

        # Graph Data
        self.X = np.arange(0, self.DataLong, 1)
        self.Y = np.zeros(self.DataLong, dtype='i2')

        # Main Data
        self.timeData = np.asarray([self.X])
        self.ampData = np.asarray([self.Y])

        # Graph FFT Data
        self.fs = 2000
        self.nfft = int(pow(2, np.ceil(np.log2(len(self.Y)))))
        self.win = np.hamming(self.nfft)
        self.freq = (self.fs / 2) * np.arange(0, 1, 1/(self.nfft/2+1))
        self.amp = np.zeros(int(self.nfft/2+1), dtype='i2')

        # Example Figure Plot
        self.fig = Figure(figsize=(11, 9), dpi=100,facecolor='white', tight_layout=True)

        # Time domain Plot
        self.ax1 = self.fig.add_subplot(211)
        self.ax1.set_facecolor('white')
        self.ax1.grid(True,which='both',ls='-')
        # self.ax1.set_ylim(1800,2200)
        self.ax1.set_ylim(-10,20)
        self.ax1.set_title("Vibration in Time domain")
        self.ax1.set_xlabel("Data point")
        self.ax1.set_ylabel("Amplitude")
        self.line1, = self.ax1.plot(self.X, self.Y)

        # Spectrum domain Plot
        self.ax2 = self.fig.add_subplot(212)
        self.ax2.set_facecolor('white')
        self.ax2.grid(True,which='both',ls='-')
        self.ax2.set_ylim(0,10000)
        self.ax2.set_title("Vibration in Spectrum domain")
        self.ax2.set_xlabel("FFT point")
        self.ax2.set_ylabel("Magnitude")
        self.line2, = self.ax2.plot(self.freq, self.amp)

        style.use('ggplot')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graphfrm)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.LEFT)

        # Graph Pack
        self.graphfrm.pack(side=tk.BOTTOM,expand=True)

        # Serial Port
        self.serPort = serial.Serial(port=sys.argv[1],baudrate=self.BaudRate,timeout=0)

        # start graph animation
        self.aniplot = plotani.FuncAnimation(self.fig, self.graphupdate, interval=0.00005, repeat=False, cache_frame_data=False)
        self.aniplot._start()

        # serial thread
        self.serThd = thd(target=self.serial_read).start()

        # window loop
        self.window.protocol("WM_DELETE_WINDOW",self.wnd_closing)
        self.window.mainloop()

    def csv_save(self):
        self.PlotUpd = False
        # write CSV/MAT
        self.SavDataName = str(filedlg.asksaveasfilename(
            initialfile = 'data.csv',
            defaultextension=".csv",
            filetypes=[("CSV Data","*.csv")]))

        self.vibData = np.asarray([self.timeData, self.ampData]).T
        np.savetxt(self.SavDataName, self.vibData, delimiter=",")

        self.PlotUpd = True

    def plot_save(self):
        self.SavPlotName = str(filedlg.asksaveasfilename(
            initialfile = 'plot.png',
            defaultextension=".png",
            filetypes=[("PNG Image","*.png")]))
        self.fig.savefig(self.SavPlotName,format='png')

    def plot_pause(self):
        if self.PlotUpd:
            self.PlotUpd = False
        else:
            self.PlotUpd = True

    def array_value(self,val_Y):
        val_Y_mV = (val_Y * (3.3/4095)) - 1.15
        val_Y_g = val_Y_mV / (50/1000)
        self.Y[self.DataIdx] = val_Y_g

        if self.PrintY:
            print(val_Y)

        self.DataIdx = self.DataIdx + 1
        if self.DataIdx == self.DataLong:
            self.DataIdx = 0
            # self.Y = self.Y - np.mean(self.Y)
            self.amp = (2/len(self.Y)) * np.abs(np.fft.fft(self.win * self.Y))[0:int(self.nfft/2+1)]

            # save x (time) and y (amplitude) data to their array
            self.timeData = np.append(self.timeData, self.X)
            self.ampData = np.append(self.ampData, self.Y)

    def wnd_closing(self):
        self.SerThdRun = False
        if self.serPort.is_open:
            self.serPort.close()

        self.window.destroy()

    def serial_read(self):
        while self.SerThdRun:
            serVal = self.serPort.readline()
            if len(serVal)>5: # %4i and CR/LF
                valY = int(serVal)
                self.array_value(valY)

            sleep(0.0001)

    def graphupdate(self,args):
        if self.PlotUpd:
            self.line1.set_data(self.X,self.Y)
            self.line2.set_data(self.freq,self.amp)


if __name__ == "__main__":
    serplot = SerialPlotTest()
