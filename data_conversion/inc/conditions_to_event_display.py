#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from inc.findPeaks import findPeaks
import inc.settings


def conditions_to_event_display(adc):

    inc.settings.settings()
    condition = False
    strips_with_single_lone_peak = 0
    for chn in range(48):
        peaks, properties = findPeaks(adc[:, chn], chn, inc.settings.peak_height, inc.settings.peak_width)
        if len(peaks) == 1:
            strips_with_single_lone_peak += 1
    if strips_with_single_lone_peak > 35:
        condition = True

    return condition
