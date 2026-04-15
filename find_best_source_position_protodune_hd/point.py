#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import string
import matplotlib.pyplot as plt


class Point:

    def __init__(self,
                 x: float,
                 y: float,
                 color: string,
                 size: int = 5):
        self.x = x
        self.y = y
        self.color = color
        self.size = size

    def plot(self):
        plt.plot(self.x, self.y, 'o', color=self.color,
                 markersize=self.size, zorder=10)
