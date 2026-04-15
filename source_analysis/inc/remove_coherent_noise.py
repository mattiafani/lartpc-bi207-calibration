#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 11 15:34:22 2023

@author: Mattia Fanì (Los Alamos National Laboratory, US) - mattia.fani@cern.ch

"""

import numpy as np
import matplotlib.pyplot as plt

from inc.settings import NTT, NC, NCC, NI1

plt.rcParams.update({'font.size': 20})


def remove_coherent_noise(b0, b1, b2, data, evt_title, saveFileName):
    common_baseline_C = np.zeros(NTT)
    common_baseline_i1 = np.zeros(NTT)
    common_baseline_i2 = np.zeros(NTT)

    # determining the common baseline
    for t in range(NTT):
        ichn_count_C = 0
        ichn_count_i1 = 0
        ichn_count_i2 = 0
        for ichn in range(NC):
            channel = 'chn' + str(ichn)
            if ichn < NCC and b0:
                if len(np.array(data[channel])) == NTT:
                    common_baseline_C[t] += data[channel][t]
                    ichn_count_C += 1
            elif NCC <= ichn < NCC + NI1 and b1:
                if len(np.array(data[channel])) == NTT:
                    common_baseline_i1[t] += data[channel][t]
                    ichn_count_i1 += 1
            elif ichn >= NCC + NI1 and b2:
                if len(np.array(data[channel])) == NTT:
                    common_baseline_i2[t] += data[channel][t]
                    ichn_count_i2 += 1

        if b0:
            common_baseline_C[t] = common_baseline_C[t] / ichn_count_C
        if b1:
            common_baseline_i1[t] = common_baseline_i1[t] / ichn_count_i1
        if b2:
            common_baseline_i2[t] = common_baseline_i2[t] / ichn_count_i2

    # subtracting the common baseline
    for ichn in range(NC):
        channel = 'chn' + str(ichn)
        for t in range(NTT):
            if ichn < NCC and b0:
                data[channel][t] = data[channel][t] - common_baseline_C[t]

            elif NCC <= ichn < NCC + NI1 and b1:
                data[channel][t] = data[channel][t] - common_baseline_i1[t]

            elif ichn >= NCC + NI1 and b2:
                data[channel][t] = data[channel][t] - common_baseline_i2[t]

    return data
