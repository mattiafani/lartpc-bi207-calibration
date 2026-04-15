#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
config_cr.py — User-facing configuration for the CR muon analysis.

All parameters that the user may want to tune are defined here.
'Private' detector parameters (NTT, NC, NCC, etc.) remain in inc/settings.py.

Output structure (all derived automatically from output_root and
raw_data_folder_name — the user only needs to set those two):

    {output_root}/
    └── {raw_data_folder_name}/
        ├── csv/
        │   ├── {raw_data_folder_name}-CR_events.csv
        │   └── {raw_data_folder_name}-CR_charges.csv
        └── plots/
            ├── event_displays/      ← 2D event displays (Step 1)
            ├── single_traces/       ← per-channel trace PDFs (Step 1)
            └── summary/             ← analysis histograms (Step 2)
"""


class CRConfig:

    # ------------------------------------------------------------------ #
    #  Data                                                                #
    # ------------------------------------------------------------------ #
    # raw_data_folder_name: str = '20220511'
    raw_data_folder_name: str = '20220511_dev01'

    # Root output directory — one subfolder per dataset is created here
    output_root: str = './output'

    # ------------------------------------------------------------------ #
    #  Step 1 — Selection: collection plane                                #
    # ------------------------------------------------------------------ #

    # Minimum number of collection strips (out of 48) required to have
    # exactly 1 peak for an event to be accepted as a CR candidate.
    # Set to 48 for the strict condition, or lower for tolerance of blips.
    min_strips_1peak: int = 44

    # Peak finding parameters for collection plane CR selection.
    # These override the values in settings.py for the CR analysis.
    peak_height: int = 18   # minimum peak height in ADC counts
    peak_width:  int = 5    # minimum peak width in ticks

    # ------------------------------------------------------------------ #
    #  Step 1 — Selection: induction 2 plane                              #
    # ------------------------------------------------------------------ #

    # Parameters for I2 bipolar signal detection.
    # Keep loose — the collection time window does the heavy filtering.
    i2_pos_peak_height:      int = 10   # min positive lobe height (ADC)
    i2_pos_peak_width:       int = 3    # min positive lobe width (ticks)
    i2_neg_peak_height:      int = 10   # min negative lobe height, abs (ADC)

    # Extra ticks added on each side of the collection time range to
    # account for the I2 plane being ~1 cm closer to the anode
    # (~12-13 ticks at 0.5 µs/tick — 15 ticks gives comfortable margin).
    i2_time_tolerance_ticks: int = 15

    # ------------------------------------------------------------------ #
    #  Physical constants for track length pitch calculation               #
    # ------------------------------------------------------------------ #
    delta_t_us:  float = 0.5    # µs per tick
    v_drift:     float = 1.57   # mm/µs — drift velocity
    delta_d_c:   float = 5.0    # mm — collection strip pitch
    delta_d_i:   float = 7.5    # mm — induction 2 strip pitch

    # ------------------------------------------------------------------ #
    #  Step 1 — Processing                                                 #
    # ------------------------------------------------------------------ #

    # Coherent noise removal plane flags: (collection, induction1, induction2)
    # coherent_noise_step1: tuple = (False, False, False)
    coherent_noise_step1: tuple = (False, False, True)
    # coherent_noise_step1: tuple = (True, True, True)

    # Print rejection reasons for every event (very verbose on large datasets)
    verbose: bool = False

    # Charge equalization — applies electronics gain correction factors
    # from settings.py (ch_eq_year). Designed for the radioactive source
    # analysis; keep False for CR studies until a dedicated CR calibration
    # is available.
    equalize_step1: bool = False

    # ------------------------------------------------------------------ #
    #  Step 1 — Display                                                    #
    # ------------------------------------------------------------------ #

    # 2-D event display (one PDF per selected event)
    # evtdisplay_step1: bool = False
    evtdisplay_step1: bool = True

    # Single-channel trace display.
    # List any combination of 'C', 'I1', 'I2', or [] to disable entirely.
    chndisplay_planes_step1: list = ['C', 'I1', 'I2']
    # chndisplay_planes_step1: list = []

    # ------------------------------------------------------------------ #
    #  Step 2 — Re-processing                                              #
    # ------------------------------------------------------------------ #

    # Coherent noise removal can be switched independently for Step 2
    # coherent_noise_step2: tuple = (False, False, False)
    coherent_noise_step2: tuple = (False, False, True)

    # See note on equalize_step1 above.
    equalize_step2: bool = False

    # ------------------------------------------------------------------ #
    #  Step 2 — Analysis                                                   #
    # ------------------------------------------------------------------ #

    # Bin widths for summary histograms
    delta_l_bin_width:     float = 5.0    # mm        — ΔL histograms
    track_pitch_bin_width: float = 0.02   # mm        — track pitch histograms
    norm_charge_bin_width: float = 1.0    # ADC·tt/mm — normalized charge per strip

    # ------------------------------------------------------------------ #
    #  Step 3 — Analysis                                                   #
    # ------------------------------------------------------------------ #

    # 2D histogram: equalized dQ/dx vs peak time tick
    dqdx_vs_time_x_bins:    int = 200    # peak time tick axis
    dqdx_vs_time_y_bins:    int = 200    # dQ/dx axis
    # fit range lower bound (ticks), 0 = data min
    dqdx_vs_time_fit_x_lo:  int = 0
    # fit range upper bound (ticks), 0 = data max
    dqdx_vs_time_fit_x_hi:  int = 0

    # Fit range scan: vary fit window symmetrically around the data center
    # and plot tau vs range width to assess systematic uncertainty
    dqdx_fit_range_scan:        bool = True  # enable/disable the scan
    dqdx_fit_scan_n_steps:      int = 20     # number of range widths to try
    dqdx_fit_scan_width_min:    int = 200    # minimum range width (ticks)
    dqdx_fit_scan_width_max:    int = 600    # maximum range width (ticks)
    # max relative error (delta_tau/tau) to be considered stable
    dqdx_fit_scan_stable_thr:   float = 5.0
    # drift-time slice width (ticks) for langaus MPV method
    dqdx_slice_bin_width:       int = 32
    # number of edge slices to exclude from exponential fit
    dqdx_slice_fit_exclude_edges: int = 1
