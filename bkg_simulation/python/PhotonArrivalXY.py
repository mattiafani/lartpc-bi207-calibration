#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import inc.GV

inc.GV.globalVariables()
r = 4*inc.GV.source_radius+1
plot_frame = 1.0

# Set the size of the figure
figsize = (8, 6)  
fig, ax = plt.subplots(figsize=figsize) 

df = pd.read_csv("Output/allParticles.csv")
particle_string_list = ['i','d','x1','y1','z1','i1','Energy','ComptE','rr']
data0 = df[df.iloc[:,1] != 0.0]

###############################################################################
# Plotting arrival position
###############################################################################

plt.hist2d(data0.iloc[:, 2],data0.iloc[:, 3], bins=40, cmap=plt.cm.jet)

cb = plt.colorbar()
cb.set_label('Counts')

plt.xlabel('x [mm]')
plt.ylabel('y [mm]')
plt.title('Photon Arrival position')

# Set the limits of the plot
plot_frame = 1.0
plt.xlim(-1*plot_frame*r, plot_frame*r)
plt.ylim(-1*plot_frame*r, plot_frame*r)

# Set the ticks and labels on the x axis
x_ticks = np.linspace(-plot_frame*r+1, plot_frame*r-1, 9)
x_ticklabels = ['{:0.0f}'.format(x) for x in x_ticks]
plt.xticks(x_ticks, x_ticklabels)

# Set the ticks and labels on the y axis
y_ticks = np.linspace(-plot_frame*r+1, plot_frame*r-1, 9)
y_ticklabels = ['{:0.0f}'.format(y) for y in y_ticks]
plt.yticks(y_ticks, y_ticklabels)

# set grid
plt.grid(color='grey', linestyle='-', linewidth=0.5)

# save and show plot
plt.savefig("./Output/h2d_PhotonArrivalXY.pdf")
plt.show()

###############################################################################
