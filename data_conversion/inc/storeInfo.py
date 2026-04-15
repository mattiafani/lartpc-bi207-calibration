# /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 18:48:06 2023

@author: Mattia Fanì (Los Alamos National Laboratory, US) - mattia.fani@cern.ch

"""

import os

def storeInfo(raw_data_folder_name,i_event, i_raw_file_name, i_raw_file_counter, i_binary_event, i_converted_file_counter, i_converted_event):

    print(f"\nSelected Event: {i_event}, {i_raw_file_name}, ({i_raw_file_counter},{i_binary_event}) ({i_converted_file_counter},{i_converted_event})\n")

    filename = f"../DATA/{raw_data_folder_name}/{raw_data_folder_name}_selectedEvents.txt"

    # Check if the file exists or not
    if not os.path.exists(filename):
        # Define the header string with column names
        header = "i_event,i_raw_file_name,i_raw_file_counter,i_binary_event,i_converted_file_counter,i_converted_event\n"
        # Create the file and write the header
        with open(filename, "a") as f:
            f.write(header)

    # Append data to the file
    with open(filename, "a") as f:
        # Write the data to the file
        f.write(f"{i_event},{i_raw_file_name},{i_raw_file_counter},{i_binary_event},{i_converted_file_counter},{i_converted_event}\n")
    
    # Close the file
    f.close()



