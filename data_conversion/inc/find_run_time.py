#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 14:49:45 2023

@author: Mattia Fanì (Los Alamos National Laboratory, US) - mattia.fani@cern.ch
Based on work of: 
    Francesco Pietropaolo (CERN)
    Serhan Tufanli (CERN)
    Chris Macias (University of Iowa, US)
    Furkan Dolek (Cukurova University, TR, and CERN)
"""

import time
import datetime

def find_run_time(i_raw_file_name):

    file = i_raw_file_name.replace('.bin','')
    fileSplit = file.split('_',10)
    unixdate = fileSplit[-1]
    rundate = datetime.datetime.strptime(time.ctime(int(unixdate)/100), "%a %b %d %H:%M:%S %Y").date()
    
    return rundate, unixdate

def find_time_now():
    time_now=time.strftime("%Y%m%d-%H%M%S")
    
    return time_now

