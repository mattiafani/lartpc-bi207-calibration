#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import inc.GV

inc.GV.globalVariables()
r = inc.GV.source_radius
plot_frame = 1.0

# Set the size of the figure
figsize = (8, 6)  
fig, ax = plt.subplots(figsize=figsize) 

df = pd.read_csv("Output/allParticles.csv")
particle_string_list = ['i','d','x1','y1','z1','i1','Energy','ComptE','rr']
data0 = df[df.iloc[:,1] == 0.0]

###############################################################################
# Plotting collection wire histogram
###############################################################################

hist_color = 'gold'
plot_title = 'h1d_ElectronsChn'
n, bins, patches = ax.hist(data0.iloc[:, 5]-0.5, bins=8, range=[0.5,8.5],\
                           color=hist_color, label='Electrons')
label_text = f"Electrons\nTotal Entries: {len(data0.iloc[:, 5])}"
ylegend = 0.82

ax.set_xlabel('Channel', fontsize=14) 
ax.set_ylabel('Entries [#]', fontsize=14)  

# ax.set_xticks([i/10 for i in range(1, 129, 10)])  

ax.grid(axis='y')  

bbox_props = dict(boxstyle='square', facecolor='white', alpha=0.5, \
          edgecolor='black', linewidth=1)
ax.text(0.98, ylegend, label_text, transform=ax.transAxes,\
        bbox=bbox_props,ha='right')

# Add a legend to the plot
ax.legend(fontsize=12)
ax.set_title('Electron arrival Chn')

plt.savefig(f"Output/{plot_title}.pdf")
plt.show()
