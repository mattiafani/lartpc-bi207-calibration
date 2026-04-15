#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 23 15:06:12 2023

@author: Mattia Fanì (Los Alamos National Laboratory, US) - mattia.fani@cern.ch

"""

ch = [25, 26, 89, 27, 28, 90, 29, 30, 31, 32,
      91, 33, 34, 92, 35, 36, 37, 38, 93, 39,
      40, 94, 41, 42, 43, 44, 95, 45, 46, 96,
      47, 48, 113, 114, 115, 116, 117, 118, 119, 120,
      121, 122, 123, 124, 125, 126, 127, 128, 97, 98,
      99, 100, 101, 102, 103, 104, 105, 106, 107,
      108, 109, 110, 111, 112, 13, 14, 85, 15, 16,
      86, 17, 18, 19, 20, 87, 21, 22, 88, 23,
      24, 1, 2, 81, 3, 4, 82, 5, 6, 7,
      8, 83, 9, 10, 84, 11, 12, 49, 50, 51,
      52, 53, 54, 55, 56, 57, 58, 59, 60, 61,
      62, 63, 64, 65, 66, 67, 68, 69, 70, 71,
      72, 73, 74, 75, 76, 77, 78, 79, 80]

ch_sorted = list(ch)

for i in range(len(ch)):

    # Invert orientation Collection Plane
    if ch[i] < 25:
        for j in range(len(ch)):
            if ch[j] + ch[i] == 49:
                print(f"i = {i}, ch[i] = {ch[i]} | j = {j}, ch[{j}] = {ch[j]}")
                k = ch_sorted[i]
                ch_sorted[i] = ch_sorted[j]
                ch_sorted[j] = k
                print(f"-> ch_sorted[i] = {ch_sorted[i]} | ch_sorted[j] = {ch_sorted[j]}")

    # Invert orientation Induction 1 plane
    if 48 < ch[i] < 69:
        for j in range(len(ch)):
            if ch[j]-48 + ch[i]-48 == 40:
                print(f"i = {i}, ch[i] = {ch[i]} | j = {j}, ch[{j}] = {ch[j]}")
                k = ch_sorted[i]
                ch_sorted[i] = ch_sorted[j]
                ch_sorted[j] = k
                print(f"-> ch_sorted[i] = {ch_sorted[i]} | ch_sorted[j] = {ch_sorted[j]}")

    # Invert orientation Induction 2 plane
    if 88 < ch[i] < 109:
        for j in range(len(ch)):
            if ch[j]-88 + ch[i]-88 == 40:
                print(f"i = {i}, ch[i] = {ch[i]} | j = {j}, ch[{j}] = {ch[j]}")
                k = ch_sorted[i]
                ch_sorted[i] = ch_sorted[j]
                ch_sorted[j] = k
                print(f"-> ch_sorted[i] = {ch_sorted[i]} | ch_sorted[j] = {ch_sorted[j]}")

print(ch_sorted)
