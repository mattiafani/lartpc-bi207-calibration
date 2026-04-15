#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 23 14:56:36 2023

@author: Mattia Fanì (Los Alamos National Laboratory, US) - mattia.fani@cern.ch

"""

import os
from inc.settings import get_blips_parameters, get_cosmic_rejection_parameters


def hist_to_csv(filename, values, bin_size, n_entries):
    filename = filename + ".csv"

    if not os.path.exists(filename):
        header = "n_entries,bin_size,hist_values\n"
        with open(filename, "w") as f:
            f.write(header)
            f.close()

    with open(filename, "a") as f:
        f.write(f"{n_entries},{bin_size},{values}\n".replace('\n', '').replace(' ', ''))

    f.close()


def txt_file_initialize(path_to_folder_plots, raw_data_folder_name):

    peak_width, blip_heights_per_plane, blip_distance = get_blips_parameters(raw_data_folder_name[:4])
    peak_width, peak_height, n_strips_w_peaks = get_cosmic_rejection_parameters(raw_data_folder_name[:4])

    txt_filename = f"{path_to_folder_plots}/{raw_data_folder_name}_CR_{peak_width}_{peak_height}_{n_strips_w_peaks}_BH_{blip_heights_per_plane[0]}_{blip_heights_per_plane[1]}_{blip_heights_per_plane[2]}"

    filename = txt_filename + ".csv"

    if os.path.exists(filename):
        os.remove(filename)

    if not os.path.exists(filename):
        header = "evt_nr,raw_file_nr,raw_evt_nr,json_file_nr,json_evt_nr,strip_nr,evt_st_t,evt_pk_t,evt_en_t,charge,charge_cluster\n"
        with open(filename, "w") as ft:
            ft.write(header)
            ft.close()

    return txt_filename


def store_evts(filename, evt_nr, raw_file_nr, raw_evt_nr, json_file_nr, json_evt_nr, strip_nr, evt_st_t, evt_pk_t, evt_en_t, charge, charge_cluster):
    filename = filename + ".csv"

    with open(filename, "a") as ft:
        ft.write(f"{evt_nr},{raw_file_nr},{raw_evt_nr},{json_file_nr},{json_evt_nr},{strip_nr},{evt_st_t},{evt_pk_t},{evt_en_t},{charge},{charge_cluster}\n")

    ft.close()
