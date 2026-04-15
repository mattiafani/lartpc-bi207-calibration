#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 11 15:34:22 2023

@author: Mattia Fanì (Los Alamos National Laboratory, US) - mattia.fani@cern.ch

"""

import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 20})


def remove_coherent_noise(b0, b1, b2, data):

    common_baseline_C = np.zeros(645)
    common_baseline_i1 = np.zeros(645)
    common_baseline_i2 = np.zeros(645)

    # determining the common baseline
    for t in range(645):
        ichn_count_C = -1
        ichn_count_i1 = -1
        ichn_count_i2 = -1
        for ichn in range(128):
            if ichn < 48 and b0:
                if len(data) == 645:
                    common_baseline_C[t] += data[t][ichn]
                    ichn_count_C += 1
            elif ichn >= 48 and ichn < 88 and b1:
                if len(data) == 645:
                    common_baseline_i1[t] += data[t][ichn]
                    ichn_count_i1 += 1
            elif ichn >= 88 and b2:
                if len(data) == 645:
                    common_baseline_i2[t] += data[t][ichn]
                    ichn_count_i2 += 1

        if b0:
            common_baseline_C[t] = common_baseline_C[t]/ichn_count_C
        if b1:
            common_baseline_i1[t] = common_baseline_i1[t]/ichn_count_i1
        if b2:
            common_baseline_i2[t] = common_baseline_i2[t]/ichn_count_i2

    # subtracting the common baseline
    for ichn in range(128):
        for t in range(645):
            if ichn < 48 and b0:
                data[t][ichn] = data[t][ichn]-common_baseline_C[t]

            elif ichn >= 48 and ichn < 88 and b1:
                data[t][ichn] = data[t][ichn]-common_baseline_i1[t]

            elif ichn >= 88 and b2:
                # print(f"{ichn}, {t}, {data[t][ichn]}")
                data[t][ichn] = data[t][ichn]-common_baseline_i2[t]

    return data
