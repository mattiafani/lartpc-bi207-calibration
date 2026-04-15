# /usr/bin/env python3
# -*- coding: utf-8 -*-


from scipy.signal import find_peaks
import inc.settings


def findPeaks(data, chn, height, width):

    inc.settings.settings()

    baselineValues = data.mean()
    withOutBaseline = data-baselineValues
    pe, prop = find_peaks(withOutBaseline, height=height, width=width)

    return pe, prop
