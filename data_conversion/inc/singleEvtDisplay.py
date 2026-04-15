#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 20 16:01:46 2023

@author: Mattia Fanì (Los Alamos National Laboratory, US) - mattia.fani@cern.ch
"""

import matplotlib.pyplot as plt
import inc.settings
import numpy as np

def singleEvtDisplay(chn,y,peaks,source_blips,blips):
    
    plt.plot(y, \
             label='Chn_'+str(chn)+', Strip '+str(inc.settings.chanPhy[chn]))
    plt.plot(peaks, y[peaks], "x")
    plt.plot(source_blips, y[source_blips], "o")
    plt.plot(blips, y[blips], "*")
    plt.ylabel('ADC (bl sub.)')
    plt.xlabel('time ticks')
    plt.legend()
    plt.grid()
    plt.xticks(np.arange(0, 641, 100))
    plt.show()
    
