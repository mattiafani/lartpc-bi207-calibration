#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from inc.find_run_time import find_time_now
plt.rcParams.update({'font.size': 20})


def show_event(adc, runTime, evt_title, saveFileName, isbatchbool):

    # Setting image quality
    fig = plt.figure(figsize=(16, 8), dpi=100)  # This line has to stay
    plt.pcolor(adc, vmin=-100, vmax=100, cmap='YlGnBu_r')
    plt.colorbar()
    plt.xlabel('Strips'), plt.ylabel('Time ticks [0.5 µs/tick]')
    plt.title(f"{runTime} - {evt_title}")
    plt.xticks(np.arange(0, 129, 10))

    plt.savefig(saveFileName)
    if not isbatchbool:
        plt.show()

    print(f' [{find_time_now()}] : {saveFileName} file created')

    plt.clf()
    plt.close()
