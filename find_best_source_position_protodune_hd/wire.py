#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 18 11:48:20 2023

@author: Mattia Fanì (Los Alamos National Laboratory, USA) - mattia.fani@cern.ch

"""

import math
import string

from point import Point
from utils import get_m_from_deg, point_line_dist
from segment import Segment


class Wire:

    def __init__(self,
                 apa_frame,
                 start_x: float,
                 start_y: float,
                 deg: float,
                 color: string,
                 wire_plane_name: string,
                 idx: int):

        self.apa_frame = apa_frame
        self.original_start_x, self.original_start_y = start_x, start_y
        self.start_x, self.start_y = start_x, start_y
        self.end_x, self.end_y = None, None
        self.deg = deg
        self.m = get_m_from_deg(deg)
        self.color = color
        self.wire_plane_name = wire_plane_name
        self.idx = idx
        self.num_femb_wires = None
        self.segments = []
        self.femb_number = ''
        self.wires_per_femb = -1
        self.offset_femb = 0

        assert 0 <= self.start_x <= apa_frame.width
        assert self.start_y == 0 or self.start_y == apa_frame.height
        assert 0 < self.deg < 180

        self.__generate_stream()

    def __generate_stream(self):
        if self.start_y == 0:
            while self.start_y != self.apa_frame.height:
                self.__add_new_segment(self.start_x, self.start_y, from_top=False)
            self.end_x, self.end_y = self.start_x, self.start_y
        else:
            while self.start_y != 0:
                self.__add_new_segment(self.start_x, self.start_y, from_top=True)
            self.end_x, self.end_y = self.start_x, self.start_y

    def __add_new_segment(self,
                          start_x: float,
                          start_y: float,
                          from_top: bool = False):

        if (self.m > 0 and not from_top) or (self.m <= 0 and from_top):
            end_x = self.apa_frame.width
            end_y = self.m * (self.apa_frame.width - start_x) + start_y
        else:
            end_x = 0
            end_y = -self.m * start_x + start_y

        if end_y > self.apa_frame.height and not from_top:
            end_y = self.apa_frame.height
            end_x = 1/self.m * (end_y - start_y) + start_x
        elif end_y < 0 and from_top:
            end_y = 0
            end_x = 1/self.m * (end_y - start_y) + start_x

        end_x = min(self.apa_frame.width, max(0, end_x))

        if (start_x != end_x and start_y != end_y) or self.deg == 90:
            self.segments.append(Segment((start_x, start_y), (end_x, end_y), color=self.color))
        self.start_x = end_x
        self.start_y = end_y
        self.deg = 180 - self.deg
        self.m = get_m_from_deg(self.deg)

    def set_num_femb_wires(self, num_femb_wires):
        self.num_femb_wires = num_femb_wires

    def plot(self):
        for segment in self.segments:
            segment.plot(self.apa_frame.ax)

    def evaluate_point_distance(self, point: Point):
        dist = math.inf
        for segment in self.segments:
            dist = min(dist, point_line_dist(segment.a, segment.b, segment.c, point.x, point.y))
        return dist

    def set_femb_number(self, femb_number):
        self.femb_number = femb_number

    def set_wires_per_femb(self, wires_per_femb):
        self.wires_per_femb = wires_per_femb

    def set_offset_femb(self, offset_femb):
        self.offset_femb = offset_femb

    def reset_aspect(self, color):
        self.set_linewidth(0.1)
        self.set_line_zorder(1)
        self.set_color(color=color)

    def set_linewidth(self, linewidth):
        for segment in self.segments:
            segment.set_linewidth(linewidth)
            
    def set_line_zorder(self, zorder):
        for segment in self.segments:
            segment.set_line_zorder(zorder)

    def set_color(self, color):
        for segment in self.segments:
            segment.set_color(color)

    def get_wire_plane_name(self):
        return self.wire_plane_name

    def get_wire_number(self):
        return self.idx

    def get_femb_number(self):
        return self.femb_number

    def get_wire_femb_number(self):
        return (self.idx - 1) % self.wires_per_femb + self.offset_femb + 1

    def __str__(self):
        wire_name = f"{self.get_wire_plane_name()}_" \
                    f"{str(self.get_wire_number()).zfill(int(math.log10(self.num_femb_wires)) + 1)}"
        if self.get_femb_number() != '':
            wire_name += f" FEMB{str(self.get_femb_number()).zfill(2)}_{str(self.get_wire_femb_number()).zfill(3)}"
        return wire_name
