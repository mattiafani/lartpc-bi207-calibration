# /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 18:48:06 2023
@author: Mattia Fanì (Los Alamos National Laboratory, US) - mattia.fani@cern.ch

"""

from os import makedirs
from inc.find_run_time import find_time_now
from inc.conditions_to_event_display import conditions_to_event_display
from inc.remove_coherent_noise import remove_coherent_noise
import inc.settings
import json
import os
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 20})


def most_frequent(List):
    return max(set(List), key=List.count)


def displayEvents(pathToJsonFolder, fileName, dataType, plotDir, b0, b1, b2, isbatchbool):

    inc.settings.settings()

    print('\n ['+find_time_now()+']'+' > Event display starts')

    # check folder, open all json files

    for (dirpath, dirnames, filenames) in os.walk(pathToJsonFolder):

        dirnames.sort()
        filenames.sort()

        for jsonFile in filenames:

            if jsonFile[-5:] == ".json":

                print(f'{inc.settings.output_align}> Reading file {jsonFile}')

                # Excluding hidden files
                if jsonFile.startswith(inc.settings.IGNORED_FOLDER_PREFIX):
                    continue

                with open(pathToJsonFolder+jsonFile) as f:
                    data = json.load(f)

                if len(data[dataType]) == 0:
                    continue
                    # print(f"{inc.settings.output_align}! ERROR: Input list is empty")

                else:

                    evt_nr_mismatch = False

                    for i in range(0, len(data[dataType])):

                        # Defining empty evt display. Skipped channels will be zero
                        adc = np.empty((inc.settings.N_TIME_TICKS, inc.settings.N_CHANNELS))

                        for x in range(0, 128):
                            channel = 'chn'+str(x)
                            mostFreqADC = most_frequent(data[dataType][i][channel])

                            if len(np.array(data[dataType][i][channel])) != 645:
                                print(f'{inc.settings.output_align}! len(data[{dataType}][{i}][{channel}]) = '
                                      f'{len(np.array(data[dataType][i][channel]))} instead of '
                                      f'{inc.settings.N_TIME_TICKS}. Channel skipped')
                                evt_nr_mismatch == True
                                continue
                            else:
                                adc[:, x] = np.array(data[dataType][i][channel])-mostFreqADC

                        if conditions_to_event_display(adc):

                            adc = remove_coherent_noise(b0, b1, b2, adc)

                            # Setting image quality
                            # Disegard IDEs' unused local variable warning
                            fig = plt.figure(figsize=(16, 8), dpi=100)
                            plt.pcolor(adc, vmin=-100, vmax=100, cmap='YlGnBu_r')
                            plt.colorbar()
                            plt.xlabel('Strips'), plt.ylabel('Time ticks [0.5 µs/tick]')
                            plt.title(data[dataType][i]['runTime'] +
                                      ' - ID: ' + str(data[dataType][i]['eventId']) +
                                      ' ('+str(data[dataType][i]['binaryFileID']) +
                                      ', '+str(data[dataType][i]['binaryEventID']) +
                                      ') ('+str(data[dataType][i]['convertedFileID']) +
                                      ', '+str(data[dataType][i]['convertedEventID']) +
                                      ')')
                            plt.xticks(np.arange(0, 129, 10))
                            makedirs(plotDir, exist_ok=True)

                            saveFileName = plotDir+"/"+jsonFile[:-5]+"_" + \
                                str(data[dataType][i]['convertedEventID'])+".pdf"

                            plt.savefig(saveFileName)
                            if not isbatchbool:
                                plt.show()

                            print(f' [{find_time_now()}] : {saveFileName} file created')

                            plt.clf()
                            plt.close()

    print(' ['+find_time_now()+']'+" > Event display completed")
