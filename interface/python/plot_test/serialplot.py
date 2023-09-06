#!/usr/bin/python
# -*- coding: utf-8 -*-

# gui toolkit
import tkinter as tk
from tkinter import font

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

    DataLong    = 1024
    DataIdx     = 0
    PlotUpd     = True
    SerThdRun   = True

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

        # Graph Frame
        self.graphfrm = tk.Frame()

        # Graph Data
        self.X = np.arange(0, self.DataLong, 1)
        self.Y = np.zeros(self.DataLong, dtype='i2')

        # Example Figure Plot
        self.fig = Figure(figsize=(8, 6), dpi=100,facecolor='white')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('white')
        self.ax.grid(True,which='both',ls='-')
        self.ax.set_ylim(1500,2500)
        self.line, = self.ax.plot(self.X, self.Y)

        style.use('ggplot')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graphfrm)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.LEFT)

        # Graph Pack
        self.graphfrm.pack(side=tk.BOTTOM,expand=True)

        # Serial Port
        self.serPort = serial.Serial(port=sys.argv[1],baudrate=115200,timeout=0)

        # start graph animation
        self.aniplot = plotani.FuncAnimation(self.fig, self.graphupdate, interval=0.00005, repeat=False, cache_frame_data=False)
        self.aniplot._start()

        # serial thread
        self.serThd = thd(target=self.serial_read).start()

        # window loop
        self.window.protocol("WM_DELETE_WINDOW",self.wnd_closing)
        self.window.mainloop()

    def array_value(self,val_Y):
        self.Y[self.DataIdx] = val_Y

        self.DataIdx = self.DataIdx + 1
        if self.DataIdx == self.DataLong:
            self.DataIdx = 0

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
            self.line.set_data(self.X,self.Y)

if __name__ == "__main__":
    serplot = SerialPlotTest()
