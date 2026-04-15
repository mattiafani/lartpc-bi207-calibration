# /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 09 18:48:06 2023

@author: Mattia Fanì (Los Alamos National Laboratory, US) - mattia.fani@cern.ch

"""

from scipy.signal import find_peaks
from inc.settings import NTT


def find_peak_range(data, chn, pe):
    # we need this function because find_peak's properties['left_bases'] and properties['right_bases']
    # don't return peak start and end points but some different points, earlier and later than we expected

    peak_start = []
    peak_top = []
    peak_end = []
    peak_integral = []
    integral = 0
    start = 0
    end = 0

    for peak in pe:
        integral = 0

        # We go backwards first
        i = peak  # peak tick number
        while data[i] > 0 and i > 0:
            start = i

            # if chn < NCC:
            #     print(f"chn={chn}, i={i}, data[i]={data[i]}")

            integral += data[i]
            i = i - 1

        # peak buffer zone - !!! Leave it here for now
        # k=i
        # while(k > i-6 and k>0 and k<inc.settings.N_TIME_TICKS-1):
        #     start = k
        #     integral += data[k]
        #     k=k-1

        # We restart from peak + 1 and go forward
        i = peak + 1
        while data[i] >= 0 and i < NTT - 1:
            end = i

            # if chn < NCC:
            #     print(f"chn={chn}, i={i}, data[i]={data[i]}")

            integral += data[i]
            i = i + 1
            # Looking at events on 20230629, I have the impression that
            # post-increment makes us safer from noise

        # peak buffer zone - !!! Leave it here for now
        # k=i
        # while(k < i+6 and k>0 and k<inc.settings.N_TIME_TICKS-1):
        #     end = k
        #     integral += data[k]
        #     k=k+1

        peak_start.append(start)
        peak_top.append(peak)
        peak_end.append(end)
        peak_integral.append(round(integral / 2, 1))  # ADC*µs

        # print(f"chn={chn}, peak={peak}, pe={pe}, integral={integral}")
    # print(f"peak_start={peak_start}, peak_top={peak_top}, peak_end={peak_end}, peak_integral={peak_integral}")

    return peak_start, peak_top, peak_end, peak_integral


def find_peaks_50l(data, chn, peak_height, peak_width):
    pe, prop = find_peaks(data, height=peak_height, width=peak_width)
    peak_start, peak_top, peak_end, integral = [], [], [], []
    if pe.size > 0:
        for _ in pe:
            peak_start, peak_top, peak_end, integral = find_peak_range(data, chn, pe)
    return pe, prop, (peak_start, peak_top, peak_end, integral)


def find_blips_50l(data, chn, height, width, distance):

    be, prop = find_peaks(data, height=height, width=width, distance=distance)

    peak_ranges = []
    if be.size > 0:
        peak_start, peak_top, peak_end, integral = find_peak_range(data, chn, be)
        peak_ranges.append((peak_start, peak_top, peak_end, integral))
        # print(f"Return: peak_ranges={peak_ranges}")

    return be, peak_ranges
