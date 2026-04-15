#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 20 16:01:46 2023

@author: Mattia Fanì (Los Alamos National Laboratory, US) - mattia.fani@cern.ch

"""

import matplotlib.pyplot as plt
from inc.settings import NCC, NTT
import numpy as np


def singleEvtDisplay(chn, y, peaks, isbatchbool):
    plt.plot(y, label='Chn_' + str(chn))
    plt.plot(peaks, y[peaks], "x")
    plt.ylabel('ADC (baseline subtracted)')
    plt.xlabel('time ticks')
    plt.legend()
    plt.grid()
    if not isbatchbool:
        plt.show()


def nicer_single_evt_display(chn, y, peaks, save_file_name, evt_title, yrange, peak_ranges, charge, isbatchbool):
    fig, ax = plt.subplots(figsize=(32, 9))

    str_chn = str(chn).zfill(3)

    # Plot label

    label = 'Chn_' + str_chn
    if chn < NCC:
        ps = [p * .5 for p in peaks]
        p_list = [y[p] for p in peaks]
        label += f";\nPeaks: {ps} µs, {p_list} ADC\nCharge: {charge} ADC*µs"

    else:
        ps = [p * .5 for p in peaks]
        label += f";\nCharged particle(s) detected at: {ps} µs"

    lr = []
    rr = []
    if int(len(peaks)) > 0:
        lr = peak_ranges[0][0]
        rr = peak_ranges[0][2]

    label += f"\nRanges: {lr}, {rr} ticks"

    ax.plot(y, label=label)
    zeros = y[peaks]
    if chn > NCC - 1 and len(peaks) > 0:
        zeros = np.zeros(len(peaks))
    ax.plot(peaks, zeros, "x")

    # Color area under recognized peaks
    if len(peak_ranges) > 0:
        for peak_start, peak_end in zip(peak_ranges[0][0], peak_ranges[0][2]):
            peak_region_x = np.arange(peak_start, peak_end)
            peak_region_y = y[peak_region_x]
            if chn < NCC:
                ax.fill_between(peak_region_x, 0, peak_region_y, color='gold', alpha=0.5)

    ax.set_ylabel('ADC (baseline subtracted)', labelpad=10, fontsize=24)
    ax.set_xlabel('time ticks [0.5 µs/tick]', fontsize=24)
    ax.legend(fontsize=24)

    # Primary grid on both x and y axes
    ax.grid(True, which='major', axis='both', linewidth=1, color='gray')

    # Secondary grid on x-axis
    ax.grid(True, which='minor', axis='x', linewidth=0.5, linestyle='dashed', color='gray')

    # Set x-axis ticks and minor ticks
    ax.set_xticks(np.arange(0, NTT + 1, 50))
    ax.set_xticks(np.arange(0, NTT + 1, 10), minor=True)

    # Set y-axis range and position
    if yrange:
        if chn < NCC:
            ax.set_ylim(-20, 300)
        else:
            ax.set_ylim(-250, 250)

    ax.set_xlim(0, len(y))
    ax.yaxis.set_label_coords(-.04, 0.5)
    ax.spines['right'].set_visible(False)

    plt.title(f"{evt_title} - Strip {chn + 1}", fontsize=30)

    plt.subplots_adjust(left=0.06, right=0.94, top=0.96, bottom=0.08)
    plt.tight_layout()

    str_strip = str(chn + 1).zfill(3)

    plt.savefig(f"{save_file_name}_Strip{str_strip}" + '.pdf', dpi=100)

    if not isbatchbool:
        plt.show()

    plt.clf()
    plt.close()
