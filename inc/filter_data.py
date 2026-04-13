#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 28 12:39:50 2023

@author: Mattia Fanì (Los Alamos National Laboratory, US) - mattia.fani@cern.ch

"""

import numpy as np
from inc.findPeaks import findPeaks
from inc.show_event import show_event
from inc.settings import NC, NCC, NTT, output_align
from inc.utils.utils import most_frequent


def prepare_data(filter_cosmics, data, evt_title, saveFileName, isbatchbool, jFileNr, jEvtNr):

    is_event_ok = False

    # Check sample size
    is_data_dimension_incorrect = False
    adc = np.empty((NTT, NC))
    for strip_index in range(NC):
        channel = 'chn' + str(strip_index)
        if len(data[channel]) != NTT:
            print(
                f'{output_align}!! Event {jEvtNr}: strip {strip_index} has dimension {len(np.array(data[channel]))} '
                f'instead of {NTT}.')
            is_data_dimension_incorrect = True

            break

        else:
            adc[:, strip_index] = np.array(data[channel])

    ####

    is_event_cosmic_or_shower = False
    if filter_cosmics and not is_data_dimension_incorrect:

        adc = np.empty((NTT, NC))
        mostFreqADC = 0

        peak_width = 5
        peak_height = 24  # 24

        event_channels_w_peaks = []

        for strip_index in range(NCC):
            channel = 'chn' + str(strip_index)
            mostFreqADC = most_frequent(data[channel])

            adc[:, strip_index] = np.array(data[channel]) - mostFreqADC
            peaks, prop, peak_ranges = findPeaks(adc[:, strip_index], strip_index, peak_height, peak_width)
            if len(peaks) > 0:
                event_channels_w_peaks.append(len(peaks))
        if len(event_channels_w_peaks) > 20:
            is_event_cosmic_or_shower = True
            print(f"{output_align}! Non-source event detected. Event ({jFileNr}, {jEvtNr}).")
            # show_event(data,evt_title,saveFileName,isbatchbool)

    ####

    if not is_event_cosmic_or_shower and not is_data_dimension_incorrect:
        is_event_ok = True

    return adc, is_event_ok
