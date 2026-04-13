# /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 23 11:20:08 2023

@author: Mattia Fanì (Los Alamos National Laboratory, US) - mattia.fani@cern.ch

"""

import matplotlib.pyplot as plt
import numpy as np
from inc.find_run_time import find_time_now
from inc.store_info import hist_to_csv
from inc.settings import NC, NCC


def plot_histogram(terminal_bool, data, filename, title, xlabel, ylabel, color, bin_size, xmin, xmax, evt_nr):
    if len(data) == 0:
        print("Warning! inc.plot_histogram() Data input file is empty")

    else:
        bins = np.arange(0, xmax + bin_size, bin_size)
        plt.hist(data, bins=bins, color=color, alpha=0.7, rwidth=0.85)
        plt.grid(axis='y', alpha=0.5)
        plt.xlabel(xlabel, fontsize=16)
        plt.ylabel(ylabel, fontsize=16)
        plt.title(f"{title} - {evt_nr} evts, {len(data)} entries", fontsize=18)
        plt.xticks(range(0, xmax, int(xmax / 5)), fontsize=14)
        plt.yticks(fontsize=14)
        plt.savefig(filename, format='pdf')
        print(f' [{find_time_now()}] : {filename} file created')
        if terminal_bool is False:
            plt.show()

        plt.clf()
        plt.close()


def hist_basic(data, hist_range, bin_size, color, strip, xlabel, ylabel, raw_data_folder_name, evt_nr, title):
    fig, ax = plt.subplots(figsize=(32, 9))
    hist, bins, _ = ax.hist(data, bins=np.arange(hist_range[0], hist_range[1] + bin_size, bin_size),
                            color=color, alpha=0.7, rwidth=0.85,
                            label=f"Strip {strip}, {len(data)} charged particles detected")

    ax.grid(axis='y', alpha=0.5)
    ax.set_xlabel(xlabel, fontsize=16)
    ax.set_ylabel(ylabel, fontsize=16)
    ax.set_title(f"{raw_data_folder_name}, {evt_nr} triggered events - {title}", fontsize=18)
    ax.set_xticks(np.arange(hist_range[0], hist_range[1] + bin_size, 50))
    ax.set_yticks(ax.get_yticks())
    ax.tick_params(axis='both', labelsize=14)
    ax.legend()
    return hist, fig


def hist_basic_csv(data, hist_range, bin_size, color, strip, xlabel, ylabel, raw_data_folder_name, evt_nr, title):
    fig, ax = plt.subplots(figsize=(32, 9))
    hist, bins, _ = ax.hist(data, bins=np.arange(hist_range[0], hist_range[1] + bin_size, bin_size),
                            color=color, alpha=0.7, rwidth=0.85,
                            label=f"Strip {strip}, {len(data)} charged particles detected")

    ax.grid(axis='y', alpha=0.5)
    ax.set_xlabel(xlabel, fontsize=16)
    ax.set_ylabel(ylabel, fontsize=16)
    ax.set_title(f"{title}", fontsize=18)
    ax.set_xticks(np.arange(hist_range[0], hist_range[1] + bin_size, 50))
    ax.set_yticks(ax.get_yticks())
    ax.tick_params(axis='both', labelsize=14)
    ax.legend()
    return hist, fig


def plot_coincidence_histos(terminal_bool, data, raw_data_folder_name, title, name, data_type, xlabel, ylabel, strip, color,
                            bin_size, hist_range, evt_nr):

    hist, fig = hist_basic_csv(data, hist_range, bin_size, color, strip, xlabel,
                               ylabel, raw_data_folder_name, evt_nr, title)

    if not terminal_bool:
        plt.show()

    if int(strip) < 10:
        str_strip = '0' + str(strip)
    else:
        str_strip = str(strip)

    pl_name = f"./Plots/{raw_data_folder_name}/{raw_data_folder_name}_{data_type}_{name}_Strip{str_strip}"

    fig.savefig(f"{pl_name}.pdf",
                format='pdf', dpi=100)

    print(
        f' [{find_time_now()}] : {pl_name}.pdf file created')

    plt.clf()
    plt.close()


def plot_scatter_histo(terminal_bool, data, raw_data_folder_name, title, name, xlabel, ylabel, color, evt_nr):
    x = np.arange(1, len(data) + 1, 1)
    y = data

    plt.figure(figsize=(32, 9))

    plt.bar(x, y, edgecolor=color, color=color)
    plt.title(f"{raw_data_folder_name}, {evt_nr} triggered events - {title}", fontsize=18)
    plt.xlabel(xlabel, fontsize=16)
    plt.ylabel(ylabel, fontsize=16)
    plt.xticks(range(0, len(data) + 1, 5), fontsize=14)
    plt.yticks(fontsize=14)
    plt.grid(axis='y', alpha=0.5)
    plt.savefig(f"./Plots/{raw_data_folder_name}/{raw_data_folder_name}_{name}.pdf", format='pdf', dpi=100)

    if not terminal_bool:
        plt.show()

    print(f' [{find_time_now()}] : ./Plots/{raw_data_folder_name}/{raw_data_folder_name}_{name}.pdf file created')

    plt.clf()
    plt.close()


def plot_charge_strip_histogram(terminal_bool, data, raw_data_folder_name, title, name, xlabel, ylabel, strip, color,
                                bin_size, hist_range, evt_nr):

    hist, fig = hist_basic(data, hist_range, bin_size, color, strip, xlabel, ylabel, raw_data_folder_name, evt_nr,
                           title)

    if int(strip) < 10:
        str_strip = '0' + str(strip)
    else:
        str_strip = str(strip)

    fig.savefig(f"./Plots/{raw_data_folder_name}/{raw_data_folder_name}_{name}_Strip_{str_strip}.pdf",
                format='pdf', dpi=100)
    print(f' [{find_time_now()}] : ./Plots/{raw_data_folder_name}/'
          f'{raw_data_folder_name}_{name}_Strip_{str_strip}.pdf file created')

    if not terminal_bool:
        plt.show()

    plt.clf()
    plt.close()


def plot_scatter_histo_ci(terminal_bool, data, filename, title, xlabel, ylabel, color, evt_nr, strip):
    x = range(NCC + 1, NC + 1)
    y = data[NC:NCC + 1]  # this is okay

    plt.bar(x, y, edgecolor=color, color=color)
    plt.title(f"{title}: {evt_nr} total triggers - Collection strip: {strip + 1}", fontsize=18)
    plt.xlabel(xlabel, fontsize=16)
    plt.ylabel(ylabel, fontsize=16)
    plt.xticks(range(50, NC, 5), fontsize=14)
    plt.yticks(fontsize=14)
    plt.grid(axis='y', alpha=0.5)

    total_entries = round(sum(y), 0)
    legend_text = f"Collection strip: {strip + 1} - Total Entries: {total_entries}"
    plt.legend([legend_text], fontsize=12)

    plt.savefig(filename, format='pdf')
    print(f' [{find_time_now()}] : {filename} file created')
    if not terminal_bool:
        plt.show()

    plt.clf()
    plt.close()
