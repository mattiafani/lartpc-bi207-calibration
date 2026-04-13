#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cr_config.py — Internal dataclass representation of CRConfig.

Loads and validates the user-facing config_cr.CRConfig, derives all
output paths from output_root and raw_data_folder_name, and exposes
typed attributes for use throughout the CR analysis classes.
"""

import os
from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class CRConfigData:
    """
    Validated, typed mirror of the user-facing CRConfig class.
    Instantiate via CRConfigData.from_config(CRConfig).
    """

    # Data
    raw_data_folder_name: str
    output_root:          str

    # Step 1 — Selection: collection plane
    min_strips_1peak:        int
    peak_height:             int
    peak_width:              int

    # Step 1 — Selection: induction 2 plane
    i2_pos_peak_height:      int
    i2_pos_peak_width:       int
    i2_neg_peak_height:      int
    i2_time_tolerance_ticks: int

    # Physical constants
    delta_t_us:  float
    v_drift:     float
    delta_d_c:   float
    delta_d_i:   float

    # Step 1 — Processing
    coherent_noise_step1:    Tuple[bool, bool, bool]
    equalize_step1:          bool
    verbose:                 bool

    # Step 1 — Display
    evtdisplay_step1:        bool
    chndisplay_planes_step1: List[str]

    # Step 2 — Re-processing
    coherent_noise_step2:    Tuple[bool, bool, bool]
    equalize_step2:          bool

    # Step 2 — Analysis
    delta_l_bin_width:     float
    track_pitch_bin_width: float
    norm_charge_bin_width: float

    # Step 3 — Analysis
    dqdx_vs_time_x_bins:        int
    dqdx_vs_time_y_bins:        int
    dqdx_vs_time_fit_x_lo:      int
    dqdx_vs_time_fit_x_hi:      int
    dqdx_fit_range_scan:        bool
    dqdx_fit_scan_n_steps:      int
    dqdx_fit_scan_width_min:    int
    dqdx_fit_scan_width_max:    int
    dqdx_fit_scan_stable_thr:   float
    dqdx_slice_bin_width:         int
    dqdx_slice_fit_exclude_edges: int

    # ------------------------------------------------------------------ #
    #  Derived fields (computed in __post_init__)                          #
    # ------------------------------------------------------------------ #
    year:                str = field(init=False)

    # CSV paths
    csv_dir:             str = field(init=False)
    csv_path:            str = field(init=False)   # events CSV
    csv_charges_path:    str = field(init=False)   # charges CSV

    # Plot folders
    plot_dir:            str = field(init=False)   # dataset plot root
    event_display_dir:   str = field(init=False)   # 2D event displays
    single_traces_dir:   str = field(init=False)   # single-channel traces
    summary_dir:         str = field(init=False)   # Step 2 histograms
    step3_dir:           str = field(init=False)   # Step 3 plots

    def __post_init__(self):
        self.year = self.raw_data_folder_name[:4]

        dataset_root = os.path.join(
            self.output_root, self.raw_data_folder_name)

        # CSV
        self.csv_dir = os.path.join(dataset_root, 'csv')
        self.csv_path = os.path.join(
            self.csv_dir, f"{self.raw_data_folder_name}-CR_events.csv")
        self.csv_charges_path = os.path.join(
            self.csv_dir, f"{self.raw_data_folder_name}-CR_charges.csv")

        # Plots
        self.plot_dir = os.path.join(dataset_root, 'plots')
        self.event_display_dir = os.path.join(self.plot_dir, 'event_displays')
        self.single_traces_dir = os.path.join(self.plot_dir, 'single_traces')
        self.summary_dir = os.path.join(self.plot_dir, 'summary')
        self.step3_dir = os.path.join(self.plot_dir, 'electron_lifetime')

        self._validate()

    def _validate(self):
        valid_planes = {'C', 'I1', 'I2'}
        for plane in self.chndisplay_planes_step1:
            if plane not in valid_planes:
                raise ValueError(
                    f"Invalid plane '{plane}' in chndisplay_planes_step1. "
                    f"Must be one of {valid_planes}."
                )
        if not 0 <= self.min_strips_1peak <= 48:
            raise ValueError(
                f"min_strips_1peak must be between 0 and 48, "
                f"got {self.min_strips_1peak}."
            )

    @classmethod
    def from_config(cls, cfg) -> 'CRConfigData':
        """Instantiate from a user-facing CRConfig class."""
        return cls(
            raw_data_folder_name=cfg.raw_data_folder_name,
            output_root=cfg.output_root,
            min_strips_1peak=cfg.min_strips_1peak,
            peak_height=cfg.peak_height,
            peak_width=cfg.peak_width,
            i2_pos_peak_height=cfg.i2_pos_peak_height,
            i2_pos_peak_width=cfg.i2_pos_peak_width,
            i2_neg_peak_height=cfg.i2_neg_peak_height,
            i2_time_tolerance_ticks=cfg.i2_time_tolerance_ticks,
            delta_t_us=cfg.delta_t_us,
            v_drift=cfg.v_drift,
            delta_d_c=cfg.delta_d_c,
            delta_d_i=cfg.delta_d_i,
            coherent_noise_step1=tuple(cfg.coherent_noise_step1),
            equalize_step1=cfg.equalize_step1,
            verbose=cfg.verbose,
            evtdisplay_step1=cfg.evtdisplay_step1,
            chndisplay_planes_step1=list(cfg.chndisplay_planes_step1),
            coherent_noise_step2=tuple(cfg.coherent_noise_step2),
            equalize_step2=cfg.equalize_step2,
            norm_charge_bin_width=cfg.norm_charge_bin_width,
            delta_l_bin_width=cfg.delta_l_bin_width,
            track_pitch_bin_width=cfg.track_pitch_bin_width,
            dqdx_vs_time_x_bins=cfg.dqdx_vs_time_x_bins,
            dqdx_vs_time_y_bins=cfg.dqdx_vs_time_y_bins,
            dqdx_vs_time_fit_x_lo=cfg.dqdx_vs_time_fit_x_lo,
            dqdx_vs_time_fit_x_hi=cfg.dqdx_vs_time_fit_x_hi,
            dqdx_fit_range_scan=cfg.dqdx_fit_range_scan,
            dqdx_fit_scan_n_steps=cfg.dqdx_fit_scan_n_steps,
            dqdx_fit_scan_width_min=cfg.dqdx_fit_scan_width_min,
            dqdx_fit_scan_width_max=cfg.dqdx_fit_scan_width_max,
            dqdx_fit_scan_stable_thr=cfg.dqdx_fit_scan_stable_thr,
            dqdx_slice_bin_width=cfg.dqdx_slice_bin_width,
            dqdx_slice_fit_exclude_edges=cfg.dqdx_slice_fit_exclude_edges,
        )
