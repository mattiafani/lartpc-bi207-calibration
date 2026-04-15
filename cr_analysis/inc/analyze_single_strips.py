#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 12 15:47:32 2023

@author: Mattia Fanì (Los Alamos National Laboratory, US) - mattia.fani@cern.ch

"""

import matplotlib.pyplot as plt

from inc.find_peaks_50l import find_blips_50l
from inc.find_charge_cluster import find_charge_cluster
from inc.single_evt_display import nicer_single_evt_display
from inc.settings import NC, NCC, NI1, get_blips_parameters
from inc.store_info import store_evts
from itertools import product

from inc.utils.utils import debug_print

plt.rcParams.update({'font.size': 20})


def find_charge_per_strip(year, k1, charge_per_strip, chn_c, peak_charge):

    if year == '2023':
        if k1 < 3:
            charge_per_strip[0][chn_c].append(peak_charge)
        else:
            charge_per_strip[1][chn_c].append(peak_charge)
    elif year == '2022':
        charge_per_strip[0][chn_c].append(peak_charge)
    else:
        raise NotImplementedError

    debug_print(f"Appending peak_charge={round(peak_charge, 1)}")

    return charge_per_strip


def analyze_single_strips(year, cnt, terminal_bool, plot_dir, txt_filename, raw_data_folder_name, run_time, evt_title,
                          save_file_name, event_id, adc, is_event_ok,
                          binary_file_id, binary_event_id, converted_file_id, converted_event_id, input_chndisplay_bool,
                          h1d_charge_per_strip, h1d_peaks, h1d_charge, list_evts_per_strip):

    # Peak analysis: detecting peaks, ranges; computing integrals ######################################################

    s = [[] for _ in range(NC)]
    r = [[] for _ in range(NC)]

    peak_width, blip_heights_per_plane, blip_distance = get_blips_parameters(year)

    for chn in range(NC):
        if chn < NCC:
            blip_height = blip_heights_per_plane[0]
        elif NCC <= chn < NCC + NI1:
            blip_height = blip_heights_per_plane[1]
        else:
            blip_height = blip_heights_per_plane[2]

        # storing peak_ranges for all strips
        # peak_ranges is: t_peak_start[i_peak],t_peak_top[i_peak],t_peak_end[i_peak],integral[i_peak]
        s[chn], r[chn] = find_blips_50l(adc[:, chn], chn, blip_height, peak_width, distance=blip_distance)

    for chn in range(NC):

        if len(r[chn]):
            for i_event in range(len(r[chn][0][0])):

                current_charge = r[chn][0][3][i_event]

                # charge_cluster = find_charge_cluster(adc, chn, current_charge, r, s, i_event)

                # store_evts(txt_filename, cnt, binary_file_id, binary_event_id, converted_file_id, converted_event_id, chn, r[chn][0][0][i_event], r[chn][0][1][i_event], r[chn][0][2][i_event], r[chn][0][3][i_event], charge_cluster)

    # Show traces on single strips #####################################################################################

    if input_chndisplay_bool:

        for chn in range(NCC):
            strip_ranges = r[chn]
            charge = strip_ranges[0][3] if len(strip_ranges) > 0 else []
            nicer_single_evt_display(chn, adc[:, chn], s[chn], save_file_name[:-4], evt_title, True, strip_ranges,
                                     charge, terminal_bool)

        for chn in range(NCC, NC):
            zero_i = []
            if len(s[chn]) > 0:
                zero_i = r[chn][0][2]
            nicer_single_evt_display(chn, adc[:, chn], zero_i, save_file_name[:-4], evt_title, True, r[chn], 0,
                                     terminal_bool)

    # Fill summary histograms ######################################################################################
    for chn in range(NCC):
        if len(r[chn]) > 0:
            for charge_detected_index in range(len(r[chn][0][3])):
                h1d_peaks.append(adc[r[chn][0][1], chn][charge_detected_index])
                h1d_charge.append(r[chn][0][3][charge_detected_index])

    # Fill single strip histograms #################################################################################

    # Charge collected per collection strip
    for chn in range(NCC):
        if len(r[chn]) > 0:
            for charge_detected in r[chn][0][3]:
                h1d_charge_per_strip[chn].append(charge_detected)

    # Number of particles detected per strip
    for chn in range(NC):
        if len(r[chn]) > 0:
            list_evts_per_strip[chn] += len(r[chn][0][2])

    return r, s
