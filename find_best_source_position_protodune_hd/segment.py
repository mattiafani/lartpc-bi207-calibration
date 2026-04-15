#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 18 11:48:20 2023

@author: Mattia Fanì (Los Alamos National Laboratory, USA) - mattia.fani@cern.ch

"""

import string
import matplotlib
import matplotlib.pyplot as plt


class Segment:

    def __init__(self,
                 start: tuple[float, float],
                 end: tuple[float, float],
                 color: string,
                 linewidth: float = 0.1,
                 zorder: int = 1):
        
        self.start = start
        self.end = end
        self.color = color
        self.linewidth = linewidth
        self.zorder = zorder
        
        self.m = self.__get_m()
        self.q = self.__get_q()
        self.a = self.__get_a()
        self.b = self.__get_b()
        self.c = self.__get_c()

    def __get_m(self):
        return (self.end[1]-self.start[1])/(self.end[0]-self.start[0])

    def __get_q(self):
        return self.start[1] - self.start[0]*(self.end[1]-self.start[1])/(self.end[0]-self.start[0])

    def __get_a(self):
        return self.m

    @staticmethod
    def __get_b():
        return -1

    def __get_c(self):
        return self.q

    def get_y(self,
              x: float,
              strict: bool = True):
        if (strict and min(self.start[0], self.end[0]) <= x <= max(self.start[0], self.end[0])) or not strict:
            return self.m * x + self.q
        if x < min(self.start[0], self.end[0]):
            print("ERROR: required x less than min of x coordinates of the segment")
            return -1
        print("ERROR: required x greater than min of x coordinates of the segment")
        return -1

    def set_linewidth(self, linewidth):
        self.linewidth = linewidth
        
    def set_line_zorder(self, zorder):
        self.zorder = zorder

    def set_color(self, color):
        self.color = color

    def plot(self,
             ax: matplotlib.axes):
        ax.add_line(plt.Line2D((self.start[0], self.end[0]),
                               (self.start[1], self.end[1]),
                               linewidth=self.linewidth,
                               color=self.color,
                               zorder=self.zorder))
