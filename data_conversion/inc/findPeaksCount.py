# /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 23 11:20:08 2023

@author: Mattia Fanì (Los Alamos National Laboratory, US) - mattia.fani@cern.ch

"""

#import matplotlib.pyplot as plt

from scipy.signal import find_peaks
import inc.settings


def findPeaksCount(data, chn, height, width, sourcePosFinder, sourcePosFinderAll):

    inc.settings.settings()

    baselineValues = data.mean()
    withOutBaseline = data-baselineValues
    pe, _ = find_peaks(withOutBaseline, height=height, width=width)

    if len(pe) > 0:
        sourcePosFinder.append(inc.settings.chanPhy[chn])

    sourcePosFinderAll[inc.settings.chanPhy[chn]] += len(pe)

    return pe
