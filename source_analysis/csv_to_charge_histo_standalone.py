#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import matplotlib.pyplot as plt
import matplotlib.cm as cm  # rainbow histos
import numpy as np
import pandas as pd

from inc.basic_functions import plot_coincidence_histos
from inc.settings import NCC

plot_dir = './Plots'
raw_data_folder_name = '20230723'
csv_file_name = '20230723_CR_5_18_20_BH_32_36_20'

colors = plt.cm.rainbow(np.linspace(0, 1, NCC))

n_entries = 0

result_file_title = f"{plot_dir}/{raw_data_folder_name}/{csv_file_name}.csv"

# Load the CSV data
df_r = pd.read_csv(result_file_title)

n_entries = df_r['evt_nr'].max()

signal_df = pd.DataFrame()
backgr_df = pd.DataFrame()

for c_strip_index, color in zip(range(NCC), colors):
    for source in 'Top', 'Bot':

        # Find coincidences csv file
        if c_strip_index < 10:
            filename_strip_index = '0'+str(c_strip_index)
        else:
            filename_strip_index = str(c_strip_index)

        # coincidences_file_name = f"{plot_dir}/{raw_data_folder_name}/{csv_file_name}.csv"
        file_title = f"{plot_dir}/{raw_data_folder_name}/{
            csv_file_name}_Coincidences_{source}_strip_{filename_strip_index}.csv"
        plot_title_coincidence = f"{
            csv_file_name} - {source} source, Coincidences - {n_entries} events"
        plot_title_coincidence_cluster = f"{
            csv_file_name} - {source} source, Coincidences Cluster - {n_entries} events"

        # Load the CSV data
        df = pd.read_csv(file_title)

        plot_coincidence_histos(True, df['charge_C'], raw_data_folder_name, plot_title_coincidence,
                                source, 'Coincidence', "[ADC*µs]", "#", c_strip_index+1,
                                color, 10, [0, 2000], n_entries)

        plot_coincidence_histos(True, df['charge_cluster'], raw_data_folder_name, plot_title_coincidence_cluster,
                                source, 'Coincidence_Cluster', "[ADC*µs]", "#", c_strip_index+1,
                                color, 10, [0, 2000], n_entries)
