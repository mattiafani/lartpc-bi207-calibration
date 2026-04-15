#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 18 11:48:20 2023

@author: Mattia Fanì (Los Alamos National Laboratory, USA) - mattia.fani@cern.ch

"""

import string

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from typing import Iterable

from point import Point
from wire_plane import WirePlane


class APAframe:

    def __init__(self,
                 width: float,
                 height: float,
                 dpi: int = 100):
        self.width = width
        self.height = height
        self.dpi = dpi
        self.fig = None
        self.ax = None
        self.wire_planes = []

    def generate_frame(self):

        self.fig = plt.figure(dpi=self.dpi)
        self.ax = plt.gca()
        rect = plt.Rectangle((0, 0), self.width, self.height, linewidth=1,
                             edgecolor='black', facecolor='none')
        self.ax.add_patch(rect)
        # set axis limits and labels
        self.ax.set_xlim([-.1 * self.width, 1.1 * self.width])
        self.ax.set_ylim([-.1 * self.height, 1.1 * self.height])
        self.ax.set_xlabel('x [mm]')
        self.ax.set_ylabel('y [mm]')
        # set aspect ratio and show plot
        plot_aspect = self.height / self.width
        self.ax.set_aspect(plot_aspect)
        plt.gca().set_aspect('equal')

    def add_wire_plane(self,
                       wire_plane: WirePlane):
        self.wire_planes.append(wire_plane)

    def add_wire_planes(self,
                        wire_planes: Iterable[WirePlane]):
        self.wire_planes += wire_planes

    def plot(self, near_wires_names=None, save_fig_path='', colors=None, title=None, distances=None):
        for wire_plane in self.wire_planes:
            wire_plane.plot()
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        if near_wires_names is not None:
            custom_lines = []
            if colors is None:
                colors = [c for _, c in near_wires_names]
            for color in colors:
                custom_lines.append(Line2D([0], [0], color=color, lw=4))
            if distances is None:
                wire_names = [wire_name for wire_name, _ in near_wires_names]
            else:
                wire_names = \
                    [f"{wire_name}, dist = {dist:.2f} mm" for (wire_name, _), dist in zip(near_wires_names, distances)]
            self.ax.legend(custom_lines, wire_names, bbox_to_anchor=(1.1, 1.0))
        plt.title(title)
        if save_fig_path != '':
            plt.savefig(save_fig_path, bbox_inches='tight')
        plt.show()
        plt.close(self.fig)

    def evaluate_point_distance(self,
                                point: Point,
                                linewidth: float = 2.0,
                                zorder: int = 10,
                                colors: string = None,
                                n_wires: int = 2):

        near_wires_names = []
        distances = []
        wires = []

        for i, wire_plane in enumerate(self.wire_planes):
            near_wires = wire_plane.evaluate_point_distance(point, n_wires)
            for wire, distance in near_wires:
                wire.set_linewidth(linewidth)
                wire.set_line_zorder(zorder)
                if colors is not None:
                    wire.set_color(colors[i])
                near_wires_names.append((str(wire), wire.color))
                distances.append(distance)
                wires.append(wire)

        return near_wires_names, distances, wires

    def __str__(self):
        str_to_return = ''
        for wire_plane in self.wire_planes:
            str_to_return += f'{wire_plane}'
        return str_to_return
