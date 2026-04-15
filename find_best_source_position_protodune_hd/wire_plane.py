#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 18 11:48:20 2023

@author: Mattia Fanì (Los Alamos National Laboratory, USA) - mattia.fani@cern.ch

"""

import string

from point import Point
from wire import Wire


class WirePlane:

    def __init__(self,
                 apa_frame,
                 start_x: float,
                 end_x: float,
                 start_y: float,
                 deg: float,
                 pitch: float,
                 color: string,
                 name: string,
                 wires_per_femb: int,
                 assign_femb_number: bool = False,
                 offset_femb: int = 0.
                 ):

        self.apa_frame = apa_frame
        self.start_x, self.end_x, self.start_y = start_x, end_x, start_y
        self.deg = deg
        self.color = color
        self.pitch = pitch
        self.name = name
        self.wires_per_femb = wires_per_femb
        self.offset_femb = offset_femb
        self.wires = []
        
        if self.start_x == 0: self.start_x = 0.0001 # you know...

        assert 0 <= start_x <= self.apa_frame.width
        assert 0 <= end_x <= self.apa_frame.width
        
        self.__generate_plane(assign_femb_number=assign_femb_number)
        self.__communicate_num_wires()

    def __generate_wire(self,
                        x: float,
                        i: int,
                        assign_femb_number: bool = False):
        wire = Wire(self.apa_frame, x, self.start_y, self.deg, self.color, self.name, i)
        if assign_femb_number:
            wire.set_femb_number((i // self.wires_per_femb) if i % self.wires_per_femb == 0
                                 else (i // self.wires_per_femb) + 1)
            wire.set_wires_per_femb(self.wires_per_femb)
            wire.set_offset_femb(self.offset_femb)
        self.wires.append(wire)

    def __generate_plane(self,
                         assign_femb_number: bool = False):
        x = self.start_x
        i = 1
        
        if self.end_x > self.start_x:
            while x <= self.end_x:
                # print(f"1 - {x}, {i}")
                self.__generate_wire(x, i, assign_femb_number=assign_femb_number)
                i += 1
                x += self.pitch
                
        else:
            while x >= self.end_x:
                # print(f"2 - {x}, {i}")
                self.__generate_wire(x, i, assign_femb_number=assign_femb_number)
                i += 1
                x -= self.pitch

    def __communicate_num_wires(self):
        for wire in self.wires:
            wire.set_num_femb_wires(len(self.wires))

    def plot(self):
        for wire in self.wires:
            wire.plot()

    def evaluate_point_distance(self,
                                point: Point,
                                n_wires: int = 2):
        distances = []
        for wire in self.wires:
            distances.append((wire, wire.evaluate_point_distance(point)))
        distances = sorted(distances, key=lambda i: i[1])
        return distances[:n_wires]

    def __str__(self):
        name = '['
        for wire in self.wires:
            name += f'\n\t{str(wire)}'
        name += '\n]'
        return name
