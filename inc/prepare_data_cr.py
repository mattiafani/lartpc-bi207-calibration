# prepare_data_cr.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from inc.settings import NCC, NTT, output_align, ch_eq_year, get_cosmic_rejection_parameters
from inc.find_peaks_50l import find_peaks_50l
from inc.utils.utils import most_frequent


def prepare_data_cr(equalize_bool, noisy_channels, data, evt_title,
                    save_file_name, run_time, isbatchbool,
                    j_file_nr, j_evt_nr, first_time=True):

    is_event_ok = False
    is_data_dimension_incorrect = False
    is_cr_candidate = False

    adc = np.empty((NTT, NCC))  # collection plane only

    # Baseline subtraction for collection channels only
    for chn in range(NCC):
        channel = f'chn{chn}'

        if len(data[channel]) != NTT:
            if first_time:
                print(f'{output_align}!! Event {j_evt_nr}: strip {chn+1} '
                      f'has dimension {len(data[channel])} instead of {NTT}.')
            is_data_dimension_incorrect = True
            break

        most_freq_adc = most_frequent(data[channel])
        adc[:, chn] = np.array(data[channel]) - most_freq_adc

        if equalize_bool:
            ch_eq = ch_eq_year(evt_title[:4])
            adc[:, chn] = np.round(adc[:, chn] * ch_eq[chn], decimals=1)
            if len(noisy_channels) > 0:
                for noisy_channel in noisy_channels:
                    if chn == noisy_channel:
                        adc[:, chn] = 0

    # CR selection: require exactly 1 peak on every collection strip
    if not is_data_dimension_incorrect:

        peak_width, peak_height, _ = get_cosmic_rejection_parameters(
            evt_title[:4])
        n_strips_with_one_peak = 0

        for chn in range(NCC):
            peaks, prop, peak_ranges = find_peaks_50l(
                adc[:, chn], chn, peak_height, peak_width)

            if len(peaks) == 1:
                n_strips_with_one_peak += 1

        if n_strips_with_one_peak == NCC:
            is_cr_candidate = True
            if first_time:
                print(f"{output_align}> CR candidate: Event ({j_file_nr}, {j_evt_nr}) "
                      f"— all {NCC} collection strips (1-{NCC}) have exactly 1 peak.")
        else:
            if first_time:
                print(f"{output_align}  Event ({j_file_nr}, {j_evt_nr}): "
                      f"{n_strips_with_one_peak}/{NCC} strips with exactly 1 peak — rejected.")

    if is_cr_candidate and not is_data_dimension_incorrect:
        is_event_ok = True

    return adc, is_event_ok
