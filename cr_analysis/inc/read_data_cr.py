# read_data_cr.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import matplotlib.pyplot as plt
from pathlib import Path
from os import makedirs

from inc.remove_coherent_noise import remove_coherent_noise
from inc.find_run_time import find_time_now
from inc.prepare_data_cr import prepare_data_cr
from inc.show_event import show_event
from inc.settings import output_align, get_noisy_chns, IGNORED_FOLDER_PREFIX

plt.rcParams.update({'font.size': 20})


def polish_event_cr(path_to_folder_plots, json_file, event,
                    raw_data_folder_name, data, i):

    save_file_name = (path_to_folder_plots + "/" + json_file[:-5]
                      + "_" + str(event['convertedEventID']) + ".pdf")

    run_time = str(event['runTime'])
    event_id = str(event['eventId'])
    binary_file_id = str(event['binaryFileID'])
    binary_event_id = str(event['binaryEventID'])
    converted_file_id = str(event['convertedFileID'])
    converted_event_id = str(event['convertedEventID'])

    evt_title = (f"{raw_data_folder_name} - Evt ID: {event_id} "
                 f"({binary_file_id}, {binary_event_id}) "
                 f"({converted_file_id}, {converted_event_id})")

    # Remove coherent noise — collection plane only (b0=True, b1=False, b2=False)
    data['all'][i] = remove_coherent_noise(
        True, False, False, event, evt_title, save_file_name)

    return (run_time, evt_title, save_file_name, event_id,
            binary_file_id, binary_event_id, converted_file_id, converted_event_id)


def open_files_cr(terminal_bool, evt_counter, path_to_folder_converted_files,
                  raw_data_folder_name, path_to_folder_plots,
                  input_evtdisplay_bool, input_chndisplay_bool,
                  input_equalize_bool, input_filter_bool,
                  h1d_peaks, h1d_charge):

    noisy_channels = get_noisy_chns(raw_data_folder_name[:4])
    cnt = 0

    for dirpath, dirnames, filenames in os.walk(path_to_folder_converted_files):
        dirnames.sort()
        filenames.sort()

        for json_file in filenames:
            if json_file[-5:] != ".json":
                continue
            if json_file.startswith(IGNORED_FOLDER_PREFIX):
                continue

            print(f'{output_align}> Reading file {json_file}')

            with open(path_to_folder_converted_files + json_file) as tf:
                data = json.load(tf)
                evt_counter += len(data['all'])

                for i, event in enumerate(data['all']):
                    cnt += 1

                    (run_time, evt_title, save_file_name, event_id,
                     binary_file_id, binary_event_id,
                     converted_file_id, converted_event_id) = \
                        polish_event_cr(path_to_folder_plots, json_file,
                                        event, raw_data_folder_name, data, i)

                    adc, is_event_ok = prepare_data_cr(
                        input_equalize_bool, noisy_channels, event,
                        evt_title, save_file_name, run_time, terminal_bool,
                        str(event['convertedFileID']),
                        str(event['convertedEventID']))

                    if is_event_ok:
                        if input_evtdisplay_bool:
                            show_event(adc, run_time, evt_title,
                                       save_file_name, terminal_bool)
                    else:
                        print(f"{output_align}! Event {evt_title} "
                              f"not selected as CR candidate.")

            tf.close()

    return evt_counter


def read_data_cr(terminal_bool, evt_counter, raw_data_folder_name,
                 path_to_folder_plots, input_evtdisplay_bool,
                 input_chndisplay_bool, input_equalize_bool,
                 input_filter_bool, h1d_peaks, h1d_charge):

    path_to_folder_converted_files = (
        f"../DATA/{raw_data_folder_name}/jsonData/")
    Path(path_to_folder_converted_files).mkdir(parents=True, exist_ok=True)
    makedirs(path_to_folder_plots, exist_ok=True)

    print('\n [' + find_time_now() + ']' + ' > CR read data starts')

    evt_counter = open_files_cr(
        terminal_bool, evt_counter, path_to_folder_converted_files,
        raw_data_folder_name, path_to_folder_plots, input_evtdisplay_bool,
        input_chndisplay_bool, input_equalize_bool, input_filter_bool,
        h1d_peaks, h1d_charge)

    return evt_counter
