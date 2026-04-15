#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 28 12:39:50 2023

@author: Mattia Fanì (Los Alamos National Laboratory, US) - mattia.fani@cern.ch

"""

import numpy as np
from inc.settings import NC, NCC, NTT, output_align, ch_eq_year, get_cosmic_rejection_parameters
from inc.find_peaks_50l import find_peaks_50l
from inc.utils.utils import most_frequent


def prepare_data(equalize_bool, filter_bool, noisy_channels, data, evt_title, save_file_name, run_time, isbatchbool,
                 j_file_nr, j_evt_nr, first_time=True):
    is_event_ok = False
    is_data_dimension_incorrect = False

    adc = np.empty((NTT, NC))

    for chn in range(NC):

        channel = f'chn{chn}'

        # Check trace dimension
        if len(data[channel]) != NTT:
            if first_time:
                print(f'{output_align}!! Event {j_evt_nr}: strip {chn} has dimension {len(data[channel])} '
                      f'instead of {NTT}.')
            is_data_dimension_incorrect = True
            break
        else:

            # Baseline subtraction
            most_freq_adc = most_frequent(data[channel])
            adc[:, chn] = np.array(data[channel]) - most_freq_adc

            # Equalization (quick & dirty - to be refined)
            if equalize_bool:

                ch_eq = ch_eq_year(evt_title[:4])

                adc[:, chn] = np.round(adc[:, chn] * ch_eq[chn], decimals=1)

                # Noise increases when rising the threshold. Need to remove overly noisy channels
                if len(noisy_channels) > 0:
                    for noisy_channel in noisy_channels:
                        if chn == noisy_channel:
                            adc[:, chn] = 0

    ####

    is_event_cosmic_or_shower = False
    if filter_bool and not is_data_dimension_incorrect:

        peak_width, peak_height, n_strips_w_peaks = get_cosmic_rejection_parameters(evt_title[:4])
        event_channels_w_peaks = []

        for chn in range(NCC):

            peaks, prop, peak_ranges = find_peaks_50l(adc[:, chn], chn, peak_height, peak_width)
            if len(peaks) > 0:
                event_channels_w_peaks.append(len(peaks))

        # 2022: 10 peaks above 24 ADC should be okay.
        # 2023: I think events will be much dirtier there

        if len(event_channels_w_peaks) > n_strips_w_peaks:
            is_event_cosmic_or_shower = True
            if first_time:
                print(f"{output_align}! Non-source event detected. Event ({j_file_nr}, {j_evt_nr}).")
            # show_event(adc, run_time, evt_title, save_file_name, isbatchbool)

    ####

    if not is_event_cosmic_or_shower and not is_data_dimension_incorrect:
        is_event_ok = True

    return adc, is_event_ok
