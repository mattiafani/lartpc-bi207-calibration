# /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 18:48:06 2023

@author: Mattia Fanì (Los Alamos National Laboratory, US) - mattia.fani@cern.ch
Based on work of: 
    Francesco Pietropaolo (CERN)
    Serhan Tufanli (CERN)
    Chris Macias (University of Iowa, US)
    Furkan Dolek (Cukurova University, TR, and CERN)

"""

import numpy as np
import os
import os.path
import time
import json

import inc.settings
from inc.find_run_time import find_run_time
from inc.find_run_time import find_time_now
from inc.singleEvtDisplay import singleEvtDisplay
from inc.raw_conv import raw_convertor_conv
from inc.findPeaks import findPeaks, findBlips
from inc.findPeaksCount import findPeaksCount
# from inc.storeInfo import storeInfo

def save_file(n_expected_files, dataOutputFile, totalList, i_converted_file_counter,
              path_to_converted_files, raw_data_folder_name):
    
    j = n_expected_files
    nDigits = 1
    while j > 10:
        j = int(j/10)
        nDigits = nDigits + 1
    
    prefix = str(i_converted_file_counter).zfill(nDigits)

    file_name = str(raw_data_folder_name) + \
                '_' + prefix + '.json'

    dataOutputFile = str(path_to_converted_files) + file_name
    
    with open(dataOutputFile, 'w') as fout:
        json.dump(totalList, fout)

    print(' [' + find_time_now() + ']' + ' > File ' + file_name + ' saved')
    
    i_converted_file_counter += 1

    return i_converted_file_counter, dataOutputFile


def init_total_list():
    return {'background': [], 'source': [], 'cosmic': [], 'shower': [], 'all': []}


def saveBinToJSON(path_to_raw_data, path_to_converted_files, raw_data_folder_name,\
                  ifSingleEvtDisplay, sourcePosFinder, sourcePosFinderAll):
    inc.settings.settings()
    
    peak_height = 18
    peak_width = 5
    blip_height = 35
    blip_distance = 10
    
    source_strip_c = 34

    print('\n [' + find_time_now() + ']' + ' > RAW files conversion starts')

    i_raw_file_counter = 0
    i_converted_file_counter = 1
    n_converted_events = 0
    i_event = 0
    i_converted_event = 0
    totalList = init_total_list()

    dataOutputFile = str(path_to_converted_files) + str(raw_data_folder_name) + \
                     '_' + str(i_converted_file_counter) + '.json'
    
    nFiles = 0
    for (dirpath, dirnames, filenames) in os.walk(path_to_raw_data):
        for i_raw_file_name in filenames:
            nFiles = nFiles+1
            
    n_expected_entries = inc.settings.N_EXPECTED_EVTS_PER_RAW_FILE*nFiles
    n_expected_files = int(n_expected_entries / 10)

    for (dirpath, dirnames, filenames) in os.walk(path_to_raw_data):
    
        dirnames.sort()
        filenames.sort()

        i_binary_event = 0

        # Scanning all files in the directory
        for i_raw_file_name in filenames:

            # Excluding hidden files
            if raw_data_folder_name.startswith(inc.settings.IGNORED_FOLDER_PREFIX):
                continue
            
            else:
                            
                # Reset the event counter for each new raw file
                n_converted_events = 0

                # Opening file
                if i_raw_file_name.endswith(".bin") and "ADC_OFT" not in i_raw_file_name:
                    i_raw_file_counter += 1

                    raw_file = os.path.join(dirpath, i_raw_file_name)  # file opened in memory
                    print('\n [' + find_time_now() + '] : ' + str(i_raw_file_counter) + ',', i_raw_file_name)
                    rundate, unixdate = find_run_time(i_raw_file_name)
                    flag_eof = False

                    while n_converted_events < inc.settings.N_EXPECTED_EVTS_PER_RAW_FILE and not flag_eof:
                        # for i_converted_file_counter in np.arange(1,inc.settings.N_EXPECTED_EVTS_PER_RAW_FILE,1):   
                        
                        for k in range(inc.settings.N_EVTS_PER_CONV_FILE):  # number of event per file

                            i_event += 1  # from 1 to n_events
                            i_binary_event += 1  # from 1 to end_of_file (25)
                            i_converted_event += 1  # from 1 to inc.settings.N_EVTS_PER_CONV_FILE (10)

                            try:
                                n_converted_events += 1

                                print(
                                    f'{inc.settings.output_align}: i_event={i_event}, i_binary_event={i_binary_event}, '
                                    f'i_converted_event={i_converted_event}')
                                fembdata = raw_convertor_conv(raw_file, trigno=i_binary_event)

                                data = {'runUnixTime': unixdate,
                                        'runTime': time.ctime(int(unixdate) / 100),
                                        'runDate': str(rundate),
                                        'eventTime': int(unixdate) - (25 - i_converted_event) * 3,
                                        'COLLECTION_BIAS_VOLTAGE': inc.settings.COLLECTION_BIAS_VOLTAGE,
                                        'CATHODE_HV': inc.settings.CATHODE_HV,
                                        'binaryFileID': i_raw_file_counter,
                                        'convertedFileID': i_converted_file_counter,
                                        'eventId': i_event,
                                        'binaryEventID': i_binary_event,
                                        'convertedEventID': i_converted_event
                                        }

                                y_std = np.empty(inc.settings.N_CHANNELS)
                                peak_count = 0
                                source_blip_count = 0
                                count_single_peak_chns = 0

                                # Now reading the 128 channels
                                for j in range(8):
                                    for l in range(16):
                                        chn = 16 * j + l
                                        
                                        source_blips = []
                                        blips = []
                                        peaks = []
                                        properties = []
                                        
                                        y = np.array(fembdata[chn]) % 0x10000  # single channel trace
                                        y_std[inc.settings.chanPhy[chn] - 1] = np.std(y)
                                        data['chn' + str(inc.settings.chanPhy[chn] - 1)] = y.tolist()

                                        myArray = np.array(y.tolist())
                                        findPeaksCount(myArray, chn, peak_height, peak_width, sourcePosFinder, sourcePosFinderAll)
                                        
                                        if inc.settings.chanPhy[chn] <= 48:
                                            baselineValues = myArray.mean()
                                            withOutBaseline = myArray - baselineValues
                                        
                                        if inc.settings.chanPhy[chn] > source_strip_c - 2 and inc.settings.chanPhy[chn] < source_strip_c + 2:
                                            source_blips, properties = findBlips(myArray, chn, blip_height, peak_width, distance=blip_distance)
                                        elif inc.settings.chanPhy[chn] < 48:
                                            blips, properties = findBlips(myArray, chn, peak_height, peak_width, distance=blip_distance)
                                            
                                        if inc.settings.chanPhy[chn] < 48:
                                        
                                            # Counters for event tagging
                                            
                                            peaks, properties = findPeaks(myArray, chn, peak_height, peak_width) 
                                            
                                            if len(peaks) > 0:
                                                peak_count += 1

                                            # Cosmic
                                            if len(peaks) > 0 and len(peaks) < 3:
                                                count_single_peak_chns += 1
                                                
                                            # Source
                                            if len(source_blips) > 0:
                                                source_blip_count += 1
                                                
                                            # print (f"Strip {inc.settings.chanPhy[chn]}: peaks= {peaks}, source_blips= {source_blips}, blips={blips}")
                                                
                                        # Display wire by wire        
                                        if ifSingleEvtDisplay:
                                            singleEvtDisplay(chn, withOutBaseline, peaks, source_blips, blips)
                                                
                                        y = 0
                                        del y
                                y_std = y_std.tolist()
                                
                                totalList['all'].append(data)
                                
                                if peak_count > 35 and count_single_peak_chns < 10:
                                    totalList['shower'].append(data)
                                    
                                if count_single_peak_chns > 45:
                                    totalList['cosmic'].append(data)
                                    
                                if source_blip_count > 0:
                                    totalList['source'].append(data)
                                
                                if peak_count < 2:  
                                    totalList['background'].append(data)  
                            
                            except TypeError:
                                print(
                                    f"{inc.settings.output_align}- EOF : i_event={i_event}, i_binary_event={i_binary_event}, "
                                    f"i_converted_event={i_converted_event}")
                                
                                i_event -= 1
                                i_converted_event -= 1
                                i_binary_event = 0
                                flag_eof = True
                                break

                            if i_converted_event == inc.settings.N_EVTS_PER_CONV_FILE:
                                i_converted_file_counter, dataOutputFile = \
                                    save_file(n_expected_files, dataOutputFile, totalList, i_converted_file_counter,
                                              path_to_converted_files, raw_data_folder_name)
                                totalList = init_total_list()
                                i_converted_event = 0

            if i_converted_event == inc.settings.N_EVTS_PER_CONV_FILE:
                i_converted_file_counter, dataOutputFile = \
                    save_file(n_expected_files, dataOutputFile, totalList, i_converted_file_counter,
                              path_to_converted_files, raw_data_folder_name)
                totalList = init_total_list()
                i_converted_event = 0

        if dirpath.split('/')[-1].startswith('run'):
            i_converted_file_counter, dataOutputFile = \
                save_file(n_expected_files, dataOutputFile, totalList, i_converted_file_counter,
                          path_to_converted_files, raw_data_folder_name)
            totalList = init_total_list()
            i_converted_event = 0

    # save_file(n_expected_files, dataOutputFile, totalList, i_converted_file_counter, path_to_converted_files, raw_data_folder_name)
    print(' [' + find_time_now() + ']' + ' > Conversion completed')
