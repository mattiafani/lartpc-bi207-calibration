#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 18:48:06 2023

@author: Mattia Fanì (Los Alamos National Laboratory, US) - mattia.fani@cern.ch

"""

import os
import sys
import numpy as np
from pathlib import Path

from inc.settings import NCC, NC, output_align
from inc.read_data import read_data
from inc.find_run_time import find_time_now
from inc.utils.utils import parse_args
from inc.store_info import txt_file_initialize
from inc.draw_summary_plots import draw_summary_plots

DEFAULTS = {
    # 'raw_data_folder_name': '20220511',
    # 'raw_data_folder_name': '20230623',
    'raw_data_folder_name': '20220511_dev01',
    # 'raw_data_folder_name': '20230722',
    'input_evtdisplay_bool': False,
    'input_chndisplay_bool': False,
    'input_equalize_bool': True,
    'input_filter_bool': True
}


def main(raw_data_folder_name, input_evtdisplay_bool, input_chndisplay_bool,
         input_equalize_bool, input_filter_bool, terminal_bool):

    # Call analysis ####################################################################################################

    if input_equalize_bool:
        print(f"{output_align}: Charge equalization is active")
        print(
            f"{output_align}: Noisy channels defined for {raw_data_folder_name[:4]} data will be excluded from analysis")

    # Reading data

    h1d_charge_per_strip = [[] for _ in range(NCC)]
    h1d_peaks = []
    h1d_charge = []

    list_evts_per_strip = np.zeros(NC)

    path_to_folder_plots = f"./Plots/{raw_data_folder_name}"
    Path(path_to_folder_plots).mkdir(parents=True, exist_ok=True)

    txt_filename = txt_file_initialize(path_to_folder_plots, raw_data_folder_name)

    evt_counter = 0
    evt_counter = read_data(terminal_bool, evt_counter, raw_data_folder_name, path_to_folder_plots, txt_filename,
                            input_evtdisplay_bool, input_chndisplay_bool, input_equalize_bool, input_filter_bool,
                            h1d_charge_per_strip, h1d_peaks, h1d_charge, list_evts_per_strip)

    print(f"\n [{find_time_now()}] - Read data ends: {evt_counter} events found\n")

    # Summary plots ####################################################################################################

    draw_summary_plots(terminal_bool, h1d_charge_per_strip, path_to_folder_plots, raw_data_folder_name,
                       h1d_peaks, evt_counter, h1d_charge, list_evts_per_strip)

    ####################################################################################################################


# ENABLING INPUT FROM TERMINAL
if __name__ == "__main__":
    raw_data_folder_name_, input_evtdisplay_bool_, input_chndisplay_bool_, input_equalize_bool_, input_filter_bool_, terminal_bool_ = parse_args(
        sys.argv, DEFAULTS)
    main(raw_data_folder_name_, input_evtdisplay_bool_,
         input_chndisplay_bool_, input_equalize_bool_, input_filter_bool_, terminal_bool_)
