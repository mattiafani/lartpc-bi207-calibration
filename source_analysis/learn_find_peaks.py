#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 29 14:51:53 2023

@author: matt
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.datasets import electrocardiogram
from scipy.signal import find_peaks
x = electrocardiogram()[2000:4000]
peaks, properties = find_peaks(x, height=0, width=5, distance=150)

print(peaks)
print(properties)

print(" ")
print(properties['left_bases'])
print(properties['right_bases'])

diff = [properties['right_bases'][i]-properties['left_bases'][i] for i in range(len(properties['left_bases']))]
print(diff)

plt.plot(x)
plt.plot(peaks, x[peaks], "x")
plt.plot(np.zeros_like(x), "--", color="gray")
plt.show()
