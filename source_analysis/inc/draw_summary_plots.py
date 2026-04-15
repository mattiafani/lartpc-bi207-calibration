#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  4 19:40:34 2023

@author: Mattia Fanì (Los Alamos National Laboratory, US) - mattia.fani@cern.ch

"""

import numpy as np
import matplotlib.pyplot as plt
from inc.settings import NCC
from inc.basic_functions import plot_scatter_histo, plot_charge_strip_histogram, plot_histogram


def draw_summary_plots(terminal_bool, h1d_charge_per_strip, path_to_folder_plots, raw_data_folder_name, h1d_peaks, evt_counter, h1d_charge, list_evts_per_strip):

    colors = plt.cm.rainbow(np.linspace(0, 1, len(h1d_charge_per_strip)))

    plot_name_base = path_to_folder_plots + '/' + raw_data_folder_name

    # h1d: all charges detected
    plot_histogram(terminal_bool, h1d_peaks, plot_name_base + '_SummaryDistrPeaks.pdf',
                   raw_data_folder_name, 'Peak height [ADC]', 'Entries [#]', 'green', 10, 0, 500, evt_counter)

    # h1d: all peaks above threshold
    plot_histogram(terminal_bool, h1d_charge, plot_name_base + '_SummaryDistrCharge.pdf',
                   raw_data_folder_name, 'Charge [ADC*µs]', 'Entries [#]', 'red', 100, 0, 5000, evt_counter)

    # list: event counter per strip
    plot_scatter_histo(terminal_bool, list_evts_per_strip, raw_data_folder_name,
                       f"Charged particle events per strip - {round(sum(list_evts_per_strip[:NCC]), 0)} "
                       f"charged particles events recorded on collection strips",
                       "Events", "Strip", "#", 'blue', evt_counter)

    # h1d: measured charge per strip
    strip = 1
    for h1d_charge_per_strip, color in zip(h1d_charge_per_strip, colors):
        # if strips_overlapping_sources[0] + 1 - 3 < strip < strips_overlapping_sources[0] + 1 + 3:
        plot_charge_strip_histogram(terminal_bool, h1d_charge_per_strip, raw_data_folder_name,
                                    'Charge detected per strip',
                                    "Charge", "[ADC*µs]", "#", strip, color, 10, [0, 2000], evt_counter)
        strip += 1
