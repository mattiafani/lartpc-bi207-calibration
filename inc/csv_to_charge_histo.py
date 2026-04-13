#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  9 00:30:41 2023

@author: Mattia Fanì (Los Alamos National Laboratory, US) - mattia.fani@cern.ch

"""

import matplotlib.pyplot as plt
import matplotlib.cm as cm  # rainbow histos
import numpy as np
import pandas as pd

from inc.basic_functions import plot_coincidence_histos
from inc.settings import NCC


def csv_to_charge_histo(plot_dir, raw_data_folder_name, csv_file_name):

    colors = plt.cm.rainbow(np.linspace(0, 1, NCC))

    n_entries = 0

    result_file_title = f"{plot_dir}/{raw_data_folder_name}/{csv_file_name}.csv"

    # Load the CSV data
    df_r = pd.read_csv(result_file_title)

    n_entries = df_r['evt_nr'].max()

    for c_strip_index, color in zip(range(NCC), colors):
        for source in 'Top', 'Bot':

            # Find coincidences csv file
            if c_strip_index < 10:
                filename_strip_index = '0'+str(c_strip_index)
            else:
                filename_strip_index = str(c_strip_index)

            # coincidences_file_name = f"{plot_dir}/{raw_data_folder_name}/{csv_file_name}.csv"
            file_title = f"{plot_dir}/{raw_data_folder_name}/{csv_file_name}_Coincidences_{source}_strip_{filename_strip_index}.csv"
            plot_title_coincidence = f"{csv_file_name} - {source} source, Coincidences - {n_entries} events"
            plot_title_coincidence_cluster = f"{csv_file_name} - {source} source, Coincidences Cluster- {n_entries} events"

            # Load the CSV data
            df = pd.read_csv(file_title)
            # Specify the column name you want to plot

            plot_coincidence_histos(False, df['charge_C'], raw_data_folder_name, plot_title_coincidence,
                                    source, "[ADC*µs]", "#", c_strip_index+1,
                                    color, 10, [0, 2000], n_entries)

            plot_coincidence_histos(False, df['cluster_charge_C'], raw_data_folder_name, plot_title_coincidence_cluster,
                                    source, "[ADC*µs]", "#", c_strip_index+1,
                                    color, 10, [0, 2000], n_entries)
