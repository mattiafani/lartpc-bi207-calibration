#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import numpy as np
import inc.settings
from pathlib import Path
from inc.bin_to_json import bin_to_json
from inc.simpleEventDisplay import displayEvents
from inc.basicFunctions import plot_histogram, plot_scatter_histo

DEFAULTS = {
    'input_conversion_bool': True,
    'input_evtdisplay_bool': True,
    'raw_data_folder_name': '20220505',
    'data_type': 'all',
}


def main(raw_data_folder_name, input_conversion_bool, input_evtdisplay_bool, isbatchbool):

    # LOADING TPC PARAMETERS
    inc.settings.settings()

    # SHOWING DATA TYPE MAP
    data_type_map = {
        0: 'background',
        1: 'source',
        2: 'cosmic',
        3: 'shower',
        4: 'all'
    }

    h1d_chn_w_peaks = []
    h1d_all_peaks_per_chn = np.zeros(inc.settings.N_CHANNELS+1)

    # data_type = data_type_map.get(input_data_type_int, DEFAULTS['data_type'])
    data_type = 'all'
    path_to_raw_data = f"../DATA/{raw_data_folder_name}/RAW/"
    path_to_folder_converted_files = f"../DATA/{raw_data_folder_name}/jsonData/"

    Path(path_to_folder_converted_files).mkdir(parents=True, exist_ok=True)

    # BIN TO JSON CONVERSION
    if input_conversion_bool:
        bin_to_json(path_to_raw_data, path_to_folder_converted_files,
                    raw_data_folder_name, h1d_chn_w_peaks,
                    h1d_all_peaks_per_chn)

        plot_histogram(h1d_chn_w_peaks, f"../DATA/{raw_data_folder_name}/{raw_data_folder_name}_h1d_chn_w_peaks.pdf",
                       f'{raw_data_folder_name} - 1 entry = the strip has at least one peak in the event', 'Strip', 'Entries [#]', 'blue', isbatchbool)

        plot_scatter_histo(h1d_all_peaks_per_chn, f"../DATA/{raw_data_folder_name}/{raw_data_folder_name}_h1d_all_peaks_per_chn.pdf",
                           f'{raw_data_folder_name} - All recorded peaks per strip', 'Strip', 'Entries [#]', 'darkblue', isbatchbool)

    # EVENT DISPLAY
    # if input_evtdisplay_bool and not input_conversion_bool:
    if input_evtdisplay_bool:
        path_to_folder_plots = f"../DATA/{raw_data_folder_name}/EventDisplay"

        # show_event(adc, runTime, evt_title, saveFileName, isbatchbool)

        displayEvents(path_to_folder_converted_files, raw_data_folder_name,
                      data_type, path_to_folder_plots, False, False, True, isbatchbool)


# ENABLING INPUT FROM TERMINAL
if __name__ == "__main__":
    inc.settings.settings()
    isbatchbool = True
    if len(sys.argv) == 4:
        print(f'\n{inc.settings.output_align}- Arguments OK. Running with INPUT parameters')
        raw_data_folder_name = sys.argv[1]
        input_conversion_bool = bool(int(sys.argv[2]))
        input_evtdisplay_bool = bool(int(sys.argv[3]))
        isbatchbool = True
    else:
        print(f'\n{inc.settings.output_align}! Arguments not found. Running with DEFAULT parameters')
        raw_data_folder_name = DEFAULTS['raw_data_folder_name']
        input_conversion_bool = DEFAULTS['input_conversion_bool']
        input_evtdisplay_bool = DEFAULTS['input_evtdisplay_bool']
        isbatchbool = False

    main(raw_data_folder_name, input_conversion_bool,
         input_evtdisplay_bool, isbatchbool)
