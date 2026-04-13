#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  4 01:36:43 2023

@author: Mattia Fanì (Los Alamos National Laboratory, US) - mattia.fani@cern.ch

"""


def find_charge_cluster(adc, chn_c, peak_charge, r, s, candidate_event_C):
    peak_charge_cluster = peak_charge
    flag = False

    # print(f"Event: {candidate_event_C}, strip: {chn_c}")

    # Check on clusters of blips #######################################################

    # 1. Add the contribution from the strip on the right
    # if the strip on the right has a larger integral than the current strip, we skip the current strip.
    # In that case, the next strip will have the current strip as the contribution to its left

    if chn_c != 47:
        c_strip_right = chn_c + 1
        charge_right = 0

        # if the next strip has a peak within the range of the current peak, we compare the two peaks

        for c_strip_right_event in range(len(s[c_strip_right])):
            if r[c_strip_right][0][1][c_strip_right_event] > r[chn_c][0][0][candidate_event_C] and \
                    r[c_strip_right][0][1][c_strip_right_event] < r[chn_c][0][2][candidate_event_C]:
                if r[c_strip_right][0][3][c_strip_right_event] > r[chn_c][0][3][candidate_event_C]:
                    flag = True
                    break

            else:
                for tick in range(r[chn_c][0][0][candidate_event_C], r[chn_c][0][2][candidate_event_C]):
                    # print(f" R | chn_c : {chn_c}, t={tick}, increment = {adc[tick, c_strip_right]}")
                    charge_right += adc[tick, c_strip_right]
                # print(f"charge_right = {charge_right}")
                if charge_right > 0:
                    charge_right = charge_right / 2  # ADC*µs
                    peak_charge_cluster += charge_right

        if flag:
            return 0

        else:

            # 2. Add the contribution from the strip on the left
            # This is safe, that strip will always be okay
            if chn_c != 0:
                c_strip_left = chn_c - 1
                charge_left = 0

                for tick in range(r[chn_c][0][0][candidate_event_C], r[chn_c][0][2][candidate_event_C]):
                    # print(f" L | chn_c : {chn_c}, t={tick}, increment = {adc[tick, c_strip_left]}")
                    charge_left += adc[tick, c_strip_left]
                # print(f"charge_left = {charge_left}")
                if charge_left > 0:
                    charge_left = charge_left / 2  # ADC*µs
                    peak_charge_cluster += charge_left

        return round(peak_charge_cluster, 1)
