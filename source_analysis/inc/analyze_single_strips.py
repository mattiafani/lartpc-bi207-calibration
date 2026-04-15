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

                charge_cluster = find_charge_cluster(adc, chn, current_charge, r, s, i_event)

                store_evts(txt_filename, cnt, binary_file_id, binary_event_id, converted_file_id, converted_event_id, chn,
                           r[chn][0][0][i_event], r[chn][0][1][i_event], r[chn][0][2][i_event], r[chn][0][3][i_event], charge_cluster)

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


# def source_analysis(year, p, r, s, i_evt, adc, charge_per_strip_coincidence, charge_per_strip_coincidence_cluster):

#     # Event selection ##################################################################################################

#     t_dist = 20  # 10 µs (20 ticks) seem appropriate for 20220511

#     i1_strips = []
#     i2_strips = []

#     if year == '2022':
#         i1_strips = [p[2] - 1, p[2], p[2] + 1]
#         i2_strips = [p[4] - 1, p[4], p[4] + 1]

#     if year == '2023':
#         i1_strips = [p[2] - 1, p[2], p[2] + 1,
#                      p[3] - 1, p[3], p[3] + 1]
#         i2_strips = [p[4] - 1, p[4], p[4] + 1,
#                      p[5] - 1, p[5], p[5] + 1]

#     for chn_c, k1, k2 in product(range(NCC), range(len(i1_strips)), range(len(i2_strips))):
#         if year == '2023':
#             if (k1 < 3 and k2 < 3) or (k1 >= 3 and k2 >= 3):
#                 continue
#             debug_print(f"collection strip = {chn_c} | i1 = {k1}, "
#                         f"strip {i1_strips[k1]} | i2 = {k2}, strip {i2_strips[k2]}")

#         if len(r[chn_c]) > 0 and len(r[i1_strips[k1]]) > 0 and len(r[i2_strips[k2]]) > 0:
#             debug_print(f"\ni_evt = {i_evt} - Evts found")
#             for candidate_event_C in range(len(r[chn_c][0][1])):
#                 debug_print(f"C = {chn_c}, t = {r[chn_c][0][1][candidate_event_C]}")
#                 flag = True
#                 for candidate_event_I1 in range(len(r[i1_strips[k1]][0][2])):
#                     for candidate_event_I2 in range(len(r[i2_strips[k2]][0][2])):
#                         dt_c_i1 = abs(r[chn_c][0][1][candidate_event_C] -
#                                       r[i1_strips[k1]][0][2][candidate_event_I1])
#                         dt_c_i2 = abs(r[chn_c][0][1][candidate_event_C] -
#                                       r[i2_strips[k2]][0][2][candidate_event_I2])
#                         debug_print(f"I1 = {i1_strips[k1]} ({candidate_event_I1}), t = "
#                                     f"{r[i1_strips[k1]][0][2][candidate_event_I1]}, tdiff = {dt_c_i1}")
#                         debug_print(f"I2 = {i2_strips[k2]} ({candidate_event_I2}), t = "
#                                     f"{r[i2_strips[k2]][0][2][candidate_event_I2]}, tdiff = {dt_c_i2}")

#                         if dt_c_i1 < t_dist and dt_c_i2 < t_dist:

#                             debug_print("Event times match")

#                             peak_charge = r[chn_c][0][3][candidate_event_C]
#                             peak_charge_cluster = find_charge_cluster(
#                                 adc, chn_c, peak_charge, r, s, candidate_event_C, candidate_event_I1,
#                                 candidate_event_I2)

#                             if flag:
#                                 charge_per_strip_coincidence = \
#                                     find_charge_per_strip(year, k1, charge_per_strip_coincidence, chn_c, peak_charge)
#                                 flag = False
#                                 debug_print("Flag=False")

#                             if peak_charge_cluster > 0:
#                                 charge_per_strip_coincidence_cluster = \
#                                     find_charge_per_strip(year, k1, charge_per_strip_coincidence_cluster, chn_c,
#                                                           peak_charge_cluster)
#                                 debug_print(f"Appending peak_charge_cluster={round(peak_charge_cluster, 1)}")

#                         else:
#                             debug_print("Event times don't match")
