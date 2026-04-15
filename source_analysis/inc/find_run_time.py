#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import time
import datetime


def find_run_time(i_raw_file_name):
    file = i_raw_file_name.replace('.bin', '')
    fileSplit = file.split('_', 10)
    unixdate = fileSplit[-1]
    rundate = datetime.datetime.strptime(time.ctime(
        int(unixdate) / 100), "%a %b %d %H:%M:%S %Y").date()

    return rundate, unixdate


def find_time_now():
    time_now = time.strftime("%Y%m%d-%H%M%S")

    return time_now
