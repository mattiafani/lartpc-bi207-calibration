#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import math
import time

from tqdm import tqdm
from pathlib import Path
from numpy import pi, sin, cos, arange

from utils import get_colors_legend_list
from apa_frame import APAframe
from point import Point
from wire_plane import WirePlane

# Dimensions - see table 1.2 page 14 here: https://dune.bnl.gov/docs/technical-proposal/far-detector-single-phase-chapter-fdsp-apa.pdf

APA_WIDTH = 2300  # mm # Active width
APA_HEIGHT = 5984  # mm # Active length
ANGLE_DEG = 90-35.7  # deg
WIRE_SIZE = 0.150  # mm
WIRE_OFFSET = WIRE_SIZE/2  # mm

XG_PITCH = 4.790  # mm # wire spacing, wire thickness considered zero
# mm # wire spacing perpendicular to wire
UV_PITCH = 4.669/sin(pi/180*(ANGLE_DEG))

STEP_Y = 4.669/cos(pi/180*(35.7))
# STEP_Y    = 100

DPI = 1000  # image resolution
DEFAULT_COLORS = ['palegreen', 'thistle', 'powderblue']


def main():
    n_wires = 2  # number of wires per plane to consider for overlapping
    n_best_points = 50  # first n candidate positions to plot and save pdf

    step_size = XG_PITCH  # mm # scan step size
    # step_size = 100

    plot_dir = f"./Plots_{time.strftime('%Y%m%d-%H%M%S')}/"
    Path(plot_dir).mkdir(parents=True, exist_ok=True)

    apa_frame = APAframe(width=APA_WIDTH, height=APA_HEIGHT, dpi=DPI)
    wire_planes = {
        'limegreen': WirePlane(apa_frame=apa_frame, start_x=XG_PITCH/2, end_x=apa_frame.width,
                               start_y=apa_frame.height, deg=180-ANGLE_DEG, pitch=UV_PITCH,
                               color=DEFAULT_COLORS[0], name='U', wires_per_femb=40,
                               assign_femb_number=True, offset_femb=48),
        'magenta': WirePlane(apa_frame=apa_frame, start_x=XG_PITCH/2, end_x=apa_frame.width,
                             start_y=apa_frame.height, deg=ANGLE_DEG, pitch=UV_PITCH,
                             color=DEFAULT_COLORS[1], name='V', wires_per_femb=40,
                             assign_femb_number=True, offset_femb=88),
        'blue': WirePlane(apa_frame=apa_frame, start_x=XG_PITCH/2, end_x=apa_frame.width,
                          start_y=apa_frame.height, deg=90, pitch=XG_PITCH,
                          color=DEFAULT_COLORS[2], name='X', wires_per_femb=48,
                          assign_femb_number=True, offset_femb=0),
    }
    apa_frame.add_wire_planes(wire_planes.values())

    point_distances = []
    print(f"\nEvaluating {(int(apa_frame.width / step_size + 1) * int(apa_frame.height / step_size + 1))} "
          f"points with a step_size of {step_size} mm...")
    # for x0 in tqdm(arange(XG_PITCH/2, apa_frame.width, step_size)):
    for x0 in tqdm(arange(0, apa_frame.width, 1)):
        # for y0 in arange(apa_frame.height, 0, -1*STEP_Y):
        for y0 in arange(apa_frame.height, apa_frame.height-100, -1):
            # for y0 in arange(800*STEP_Y, 400*STEP_Y, -1*STEP_Y):
            test_point = Point(x=x0, y=y0, color='orange', size=5)
            near_wires_names, distances, _ = \
                apa_frame.evaluate_point_distance(
                    test_point, linewidth=0.1, zorder=1, n_wires=1)
            femb_number = near_wires_names[0][0].split('_')[1][4:]
            if not all(wire_name.split('_')[1][4:] == femb_number for wire_name, _ in near_wires_names[1:]):
                continue
            point_distances.append((test_point, distances))
    point_distances = sorted(
        point_distances, key=lambda i: sum(i[1]) / len(i[1]))
    best_points = [p for p, d in point_distances[:n_best_points]]
    print("Done.\n")

    print("Displaying and saving plots...")
    for n, point in enumerate(best_points):
        print(f"Generating plot {n + 1}/{len(best_points)}...")
        near_wires_names, distances, wires = \
            apa_frame.evaluate_point_distance(point, linewidth=1, zorder=5,
                                              colors=list(wire_planes.keys()), n_wires=n_wires)
        apa_frame.generate_frame()
        point.plot()
        apa_frame.plot(near_wires_names,
                       save_fig_path=f'{plot_dir}Position_{
                           str(n + 1).zfill(int(math.log10(n_best_points)) + 1)}_x'
                       f'{round(point_distances[n][0].x, 1)}_y{
                           round(point_distances[n][0].y, 1)}.pdf',
                       colors=get_colors_legend_list(
                           wire_planes.keys(), n_wires),
                       title=f"Position {
                           n+1}: ({point.x:.1f}, {point.y:.1f}) - "
                       f"Average distance = {
                           round(sum(distances) / len(distances), 2)} mm",
                       distances=distances
                       )
        for j, wire in enumerate(wires):

            wire.reset_aspect(color=DEFAULT_COLORS[int(j / n_wires)])

    print("Done.")

    # for wire_plane in wire_planes.values():
    #     print(wire_plane)


if __name__ == '__main__':
    main()
