#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import math

PI = math.pi


def deg_to_rad(angle_deg):
    return PI / 180 * angle_deg


def get_m_from_deg(deg):
    return math.tan(deg_to_rad(deg))


def point_line_dist(a, b, c, x0, y0):
    return abs(a*x0 + b*y0 + c)/((a**2 + b**2)**(1/2))


def get_colors_legend_list(colors, n_wires):
    all_colors = []
    for c in colors:
        for i in range(n_wires):
            all_colors.append(c)
    return all_colors
