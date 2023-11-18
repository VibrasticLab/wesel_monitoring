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
import matplotlib.pyplot as plt

# additional
import os
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
    PrintY      = True
    SavName     = ''
    BaudRate    = 115200

    # calibration values
    # gain of least significant bit (LSB) value is user-defined by reading and converting ADC output data, resulting in zero values of g (in silent/no input condition)
    # default values is 1 (section Finding the ADC Offset Error Example)
    # https://www.allaboutcircuits.com/technical-articles/adc-offset-and-gain-error-specifications/
    GainLsbCalib = 1.015

    # LSB basically is ratio between full scale output voltage of ADC and number of bit combination (2^N)
    Lsb = (2.5/4095)

    # Since the FSO range from +- 1.25, so the output voltage need to be normalized as hown in Figure 1
    # https://e2e.ti.com/blogs_/archives/b/precisionhub/posts/it-s-in-the-math-how-to-convert-adc-code-to-a-voltage-part-1
    VoltageOffset = 1.25

    # Sensitivity of accelerometer sensor 830m1-0025 (in V/g)
    # https://www.ttieurope.com/content/dam/tti-europe/manufacturers/te-connectivity/resources/product-CAT-EAC0023.datasheet.pdf
    Sensitivity = 50/1000


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

        # Show Image of All Data Button
        self.savimgbtn = tk.Button(self.buttonfrm, text="Show All", command=self.plot_all_data)
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
        self.fs = 500
        self.nfft = int(pow(2, np.ceil(np.log2(len(self.Y)))))
        self.win = np.hamming(self.nfft)
        self.freq = (self.fs / 2) * np.arange(0, 1, 1/(self.nfft/2+1))
        self.ampFFT = np.zeros(int(self.nfft/2+1), dtype='i2')
        self.nOverlap = int(self.DataLong / 2)
        self.YFFT = np.zeros(self.DataLong)

        # Live Monitoring Figure Plot
        self.fig = Figure(figsize=(11, 9), dpi=100,facecolor='white', tight_layout=True)

        # Time domain Plot
        self.ax1 = self.fig.add_subplot(211)
        self.ax1.set_facecolor('white')
        self.ax1.grid(True,which='both',ls='-')
        self.ax1.set_ylim(-1,1)
        self.ax1.set_title("Vibration in Time domain")
        self.ax1.set_xlabel("Data point")
        self.ax1.set_ylabel("Amplitude (g)")
        self.line1, = self.ax1.plot(self.X, self.Y)
        self.ax1.relim()
        self.ax1.autoscale_view()

        # Spectrum domain Plot
        self.ax2 = self.fig.add_subplot(212)
        self.ax2.set_facecolor('white')
        self.ax2.grid(True,which='both',ls='-')
        self.ax2.set_ylim(0,1)
        self.ax2.set_title("Vibration in Spectrum domain")
        self.ax2.set_xlabel("FFT point")
        self.ax2.set_ylabel("Magnitude")
        self.line2, = self.ax2.plot(self.freq, self.ampFFT)

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
        self.SerThdRun = False
        # write CSV/MAT
        self.SavDataName = str(filedlg.asksaveasfilename(
            initialfile = 'data.csv',
            defaultextension=".csv",
            filetypes=[("CSV Data","*.csv")]))

        self.vibData = np.round(np.asarray([self.timeData, self.ampData]), 2).T
        np.savetxt(self.SavDataName, self.vibData, delimiter=",")

        self.PlotUpd = True
        self.SerThdRun = True

    def plot_all_data(self):
        fig, axs = plt.subplots(2)

        # Plot of All Data
        axs[0].set_facecolor('white')
        axs[0].grid(True,which='both',ls='-')
        axs[0].set_ylim(-1,1)
        axs[0].set_title("Vibration in Time domain")
        axs[0].set_xlabel("Time (s)")
        axs[0].set_ylabel("Amplitude (g)")
        axs[0].plot(self.timeData, self.ampData)
        axs[0].relim()
        axs[0].autoscale_view()

        # Spectrum domain Plot
        axs[1].set_facecolor('white')
        axs[1].set_title("Vibration in Spectrum domain")
        axs[1].set_xlabel("FFT point")
        axs[1].set_ylabel("Magnitude")

        pad_end_size = self.nfft
        total_segments = int(np.ceil(len(self.ampData) / self.nOverlap))
        inner_pad = np.zeros(self.nfft)

        proc = np.concatenate((self.ampData, np.zeros(pad_end_size)))
        tft_result = np.empty((self.total_segments, self.nfft), dtype=np.float32)

        for i in range(self.total_segments):
            idx_hop = self.nOverlap * i
            segment = proc[idx_hop:idx_hop + self.nfft]
            windowed = segment * self.win
            padded = np.append(windowed, inner_pad)
            spectrum = np.fft.fft(padded) / self.nfft
            autopower = np.abs(spectrum * np.conj(spectrum))
            stft_result[i, :] = autopower[:self.nfft]

        stft_result = 20 * np.log10(self.stft_result)
        stft_result = np.clip(self.stft_result, -40, 200)

        axs[1].imshow(self.stft_result, origin='lower', cmap='jet', interpolation='nearest', aspect='auto')

        plt.show()

    def plot_save(self):
        self.SavPlotName = str(filedlg.asksaveasfilename(
            initialfile = 'plot.png',
            defaultextension=".png",
            filetypes=[("PNG Image","*.png")]))
        self.fig.savefig(self.SavPlotName,format='png')

    def plot_pause(self):
        if self.PlotUpd:
            self.PlotUpd = False
            self.SerThdRun = False
        else:
            self.PlotUpd = True
            self.SerThdRun = True

    def array_value(self,val_Y):
        lsb = self.GainLsbCalib * self.Lsb
        val_Y_mV = (val_Y * lsb) - self.VoltageOffset
        val_Y_g = val_Y_mV / self.Sensitivity
        self.Y[self.DataIdx] = val_Y_g

        # storage Y data for overlapping during FFT computation
        if self.DataIdx+self.nOverlap-2 == len(self.YFFT)-1:
            self.YFFT[self.DataIdx+self.nOverlap-2] = val_Y_g
            self.YFFT[0:self.nOverlap-1] = self.YFFT[self.nOverlap:-1]
        elif self.DataIdx+self.nOverlap-2 < len(self.YFFT)-1:
            self.YFFT[self.DataIdx+self.nOverlap-2] = val_Y_g
        else:
            self.YFFT[self.DataIdx] = val_Y_g

        if self.PrintY:
            print(val_Y_g)

        if self.DataIdx == self.DataLong-1:
            self.DataIdx = 0
            self.Y = self.Y - np.mean(self.Y) + np.mean(self.Y)

            # save x (time) and y (amplitude) data to their array
            self.ampData = np.append(self.ampData, self.Y)
            self.timeData = np.linspace(0, len(self.ampData)-1, len(self.ampData)) / self.fs

        if self.DataIdx == self.nOverlap:
            self.Y_offset = self.YFFT - np.mean(self.YFFT)

            # TODO: need to add overlap on FFT calculation
            self.ampFFT = (2/len(self.Y_offset)) * np.abs(np.fft.fft(self.win * self.Y_offset))[0:int(self.nfft/2+1)]

        self.DataIdx = self.DataIdx + 1

    def wnd_closing(self):
        self.SerThdRun = False
        if self.serPort.is_open:
            self.serPort.close()

        plt.close('all')
        self.window.destroy()

    def port_read(self):
        try:
            dataIn = self.serPort.readline()
        except serial.SerialException as e:
            print(e)
            return None
        except TypeError as e:
            #Disconnect of USB->UART occured
            print(e)
            self.SerPort.close()
            return None
        else:
            return dataIn

    def serial_read(self):
        while self.SerThdRun:
            serVal = self.port_read()
            if len(serVal)>5: # %4i and CR/LF
                valY = int(serVal)
                self.array_value(valY)

            if os.name == 'posix':
                sleep(0.0001)

    def graphupdate(self,args):
        if self.PlotUpd:
            self.line1.set_data(self.X,self.Y)
            self.line2.set_data(self.freq,self.ampFFT)

if __name__ == "__main__":
    serplot = SerialPlotTest()
