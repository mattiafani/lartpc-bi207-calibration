#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

from inc.settings import NTT, NC, NCC, NI1

plt.rcParams.update({'font.size': 20})


def remove_coherent_noise(b0, b1, b2, data, evt_title, saveFileName):
    common_baseline_C = np.zeros(NTT)
    common_baseline_i1 = np.zeros(NTT)
    common_baseline_i2 = np.zeros(NTT)

    for t in range(NTT):
        values_C = []
        values_i1 = []
        values_i2 = []

        for ichn in range(NC):
            channel = 'chn' + str(ichn)
            if ichn < NCC and b0:
                if len(np.array(data[channel])) == NTT:
                    values_C.append(data[channel][t])
            elif NCC <= ichn < NCC + NI1 and b1:
                if len(np.array(data[channel])) == NTT:
                    values_i1.append(data[channel][t])
            elif ichn >= NCC + NI1 and b2:
                if len(np.array(data[channel])) == NTT:
                    values_i2.append(data[channel][t])

        trim = 0.1  # exclude the top and bottom 10% from the mean
        if b0 and values_C:
            common_baseline_C[t] = stats.trim_mean(values_C, trim)
        if b1 and values_i1:
            common_baseline_i1[t] = stats.trim_mean(values_i1, trim)
        if b2 and values_i2:
            common_baseline_i2[t] = stats.trim_mean(values_i2, trim)

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
