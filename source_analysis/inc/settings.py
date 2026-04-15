# /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 18:48:06 2023

@author: Mattia Fanì (Los Alamos National Laboratory, US) - mattia.fani@cern.ch

"""

IGNORED_FOLDER_PREFIX = "."
N_EXPECTED_EVTS_PER_RAW_FILE = 25
COLLECTION_BIAS_VOLTAGE = 900  # Volts
CATHODE_HV = 27200  # Volts
N_EVTS_PER_CONV_FILE = 10  # Evt Nr for each .JSON file
NTT = 645  # n_time_ticks
NC = 128  # Overall number of channels
NCC = 48  # Number of channels on collection plane
NI1 = 40  # Number of channels on induction 1 plane
NI2 = 40  # Number of channels on induction 2 plane
output_align = ' ' * 19  # only for cosmetics
debug = False  # debug option for print
default_coincidence_strip = False


def get_noisy_chns(year):
    # Defining noisy channels
    noisy_channels_2022 = [89, 94, 95, 96, 128]
    noisy_channels_2023 = [89, 128]
    noisy_channels = locals()[f"noisy_channels_{year}"]
    # we think in human units, work in machine units
    noisy_channels = [strip - 1 for strip in noisy_channels]

    return noisy_channels


def ch_eq_year(year):

    if year == '2022':
        ch_eq = [1] * int(NCC/2) + [1.8] * int(NCC/2) + [1.8] * int(NI1) + [1] * int(NI2)
    elif year == '2023':
        ch_eq = [1] * int(NCC/2) + [1.8] * int(NCC/2) + [1.8] * int(NI1) + [1] * int(NI2)

    return ch_eq


def get_cosmic_rejection_parameters(year):
    if year == '2022':
        peak_width = 5
        peak_height = 18
        n_strips_w_peaks = 10
        return peak_width, peak_height, n_strips_w_peaks
        # return 1, 1, 50
    elif year == '2023':
        peak_width = 5
        peak_height = 18
        n_strips_w_peaks = 20
        return peak_width, peak_height, n_strips_w_peaks
    raise NotImplementedError


def get_blips_parameters(year):

    if year == '2022':
        peak_width = 5
        blip_heights_per_plane = [32, 36, 20]  # [40, 35, 24]  # [30, 35, 20]  # C, I1, I2
        blip_distance = 20  # 20
    elif year == '2023':
        peak_width = 5
        blip_heights_per_plane = [32, 36, 20]  # [40, 35, 24]  # [30, 35, 20]  # C, I1, I2
        blip_distance = 20  # 20
    else:
        raise NotImplementedError

    return peak_width, blip_heights_per_plane, blip_distance
