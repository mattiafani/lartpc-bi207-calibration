# /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 18:48:06 2023

@author: Mattia Fanì (Los Alamos National Laboratory, US) - mattia.fani@cern.ch

"""

import os
import json
import matplotlib.pyplot as plt
from pathlib import Path

from os import makedirs
from inc.remove_coherent_noise import remove_coherent_noise
from inc.find_run_time import find_time_now
from inc.prepare_data import prepare_data
from inc.analyze_single_strips import analyze_single_strips
from inc.show_event import show_event
from inc.settings import output_align, get_noisy_chns, IGNORED_FOLDER_PREFIX

plt.rcParams.update({'font.size': 20})


def polish_event_data(path_to_folder_plots, json_file, event, raw_data_folder_name, data, i, input_equalize_bool,
                      input_filter_bool, noisy_channels, terminal_bool):
    run_time, evt_title, save_file_name, event_id, binary_file_id, binary_event_id, converted_file_id, converted_event_id = \
        polish_event(path_to_folder_plots, json_file, event, raw_data_folder_name, data, i)

    # Prepare event for analysis: Baseline subtraction, check event dimension, check event type, equalization

    adc, is_event_ok = prepare_data(input_equalize_bool, input_filter_bool, noisy_channels,
                                    event, evt_title, save_file_name, run_time,
                                    terminal_bool, str(event['convertedFileID']),
                                    str(event['convertedEventID']))
    return run_time, evt_title, save_file_name, event_id, adc, is_event_ok, binary_file_id, binary_event_id, converted_file_id, converted_event_id


def polish_event(path_to_folder_plots, json_file, event, raw_data_folder_name, data, i):
    save_file_name = path_to_folder_plots + "/" + json_file[:-5] + "_" + str(
        event['convertedEventID']) + ".pdf"

    run_time = str(event['runTime'])
    event_id = str(event['eventId'])
    binary_file_id = str(event['binaryFileID'])
    binary_event_id = str(event['binaryEventID'])
    converted_file_id = str(event['convertedFileID'])
    converted_event_id = str(event['convertedEventID'])

    evt_title = (f"{raw_data_folder_name} - Evt ID: {event_id} ({binary_file_id}, "
                 f"{binary_event_id}) ({converted_file_id}, {converted_event_id})")

    # Remove coherent noise for calculations & event display - The bools correspond to strip planes: C, I1, I2
    data['all'][i] = remove_coherent_noise(False, False, False, event, evt_title, save_file_name)

    return run_time, evt_title, save_file_name, event_id, binary_file_id, binary_event_id, converted_file_id, converted_event_id


def open_files(terminal_bool, evt_counter, path_to_folder_converted_files, txt_filename, raw_data_folder_name, path_to_folder_plots,
               input_evtdisplay_bool, input_chndisplay_bool, input_equalize_bool, input_filter_bool,
               h1d_charge_per_strip, h1d_peaks, h1d_charge, list_evts_per_strip):

    noisy_channels = get_noisy_chns(raw_data_folder_name[:4])

    cnt = 0
    # check folder, open all json files
    for dirpath, dirnames, filenames in os.walk(path_to_folder_converted_files):
        dirnames.sort()
        filenames.sort()

        for json_file in filenames:
            if json_file[-5:] == ".json":

                print(f'{output_align}> Reading file {json_file}')

                # Excluding hidden files
                if json_file.startswith(IGNORED_FOLDER_PREFIX):
                    continue
                with open(path_to_folder_converted_files + json_file) as tf:
                    data = json.load(tf)

                    evt_counter += len(data['all'])

                    # loop over events = lines of the json file
                    for i, event in enumerate(data['all']):
                        cnt += 1

                        # !!! Entries start from 0. Comment this block before commit
                        if raw_data_folder_name[-4:] == '_dev':
                            if i != 8:
                                continue

                        run_time, evt_title, save_file_name, event_id, adc, is_event_ok, binary_file_id, binary_event_id, converted_file_id, converted_event_id =\
                            polish_event_data(path_to_folder_plots, json_file, event, raw_data_folder_name, data, i,
                                              input_equalize_bool, input_filter_bool, noisy_channels, terminal_bool)

                        if is_event_ok:
                            # Analyze strip by strip
                            r, s = analyze_single_strips(json_file[:4], cnt, terminal_bool, path_to_folder_plots,
                                                         txt_filename, raw_data_folder_name, run_time, evt_title,
                                                         save_file_name, event_id, adc, is_event_ok, binary_file_id,
                                                         binary_event_id, converted_file_id, converted_event_id,
                                                         input_chndisplay_bool, h1d_charge_per_strip, h1d_peaks,
                                                         h1d_charge, list_evts_per_strip)

                            # Event Display
                            if input_evtdisplay_bool:
                                show_event(adc, run_time, evt_title, save_file_name, terminal_bool)

                        else:
                            print(f"{output_align}! Event {evt_title} excluded from current analysis.")

                tf.close()

    return evt_counter


def read_data(terminal_bool, evt_counter, raw_data_folder_name, path_to_folder_plots, txt_filename,
              input_evtdisplay_bool, input_chndisplay_bool, input_equalize_bool, input_filter_bool,
              h1d_charge_per_strip, h1d_peaks, h1d_charge, list_evts_per_strip):

    path_to_folder_converted_files = f"../../DATA/{raw_data_folder_name}/jsonData/"
    Path(path_to_folder_converted_files).mkdir(parents=True, exist_ok=True)

    makedirs(path_to_folder_plots, exist_ok=True)
    print('\n [' + find_time_now() + ']' + ' > Read data starts')

    evt_counter = open_files(terminal_bool, evt_counter, path_to_folder_converted_files, txt_filename, raw_data_folder_name, path_to_folder_plots,
                             input_evtdisplay_bool, input_chndisplay_bool, input_equalize_bool, input_filter_bool,
                             h1d_charge_per_strip, h1d_peaks, h1d_charge, list_evts_per_strip)

    return evt_counter
