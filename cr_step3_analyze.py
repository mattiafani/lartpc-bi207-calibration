#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cr_step3_analyze.py — Step 3: CR muon equalized charge analysis.

Reads *-CR_charges_equalized.csv produced by Step 2 and produces
further analysis plots.

Usage
-----
    python3 cr_step3_analyze.py

All parameters are controlled via config_cr.py.
"""

from pathlib import Path

from config_cr import CRConfig
from inc.cr.cr_config import CRConfigData
from inc.cr.cr_step3_analyzer import CRStep3Analyzer
from inc.find_run_time import find_time_now
from inc.settings import output_align

_W = 60


def _sep(char='─'):
    return f"{output_align}{char * _W}"


def run_step3(cfg: CRConfigData) -> None:
    """Execute Step 3: equalized charge analysis."""

    # Derive equalized charges CSV path from charges path
    eq_charges_path = cfg.csv_charges_path.replace(
        '_charges', '_charges_equalized')

    print(f"\n [{find_time_now()}] > Step 3: CR muon equalized analysis")
    print(_sep('═'))
    print(f"{output_align}  Dataset          : {cfg.raw_data_folder_name}")
    print(_sep())
    print(f"{output_align}  Input")
    print(f"{output_align}    Equalized CSV  : {eq_charges_path}")
    print(_sep())
    print(f"{output_align}  Output")
    print(f"{output_align}    Step 3 folder  : {cfg.step3_dir}")
    print(_sep())
    print(f"{output_align}  Binning")
    print(f"{output_align}    dQ/dx vs time  : {
          cfg.dqdx_vs_time_x_bins} x {cfg.dqdx_vs_time_y_bins} bins")
    print(f"{output_align}    Fit range      : [{
          cfg.dqdx_vs_time_fit_x_lo or 'auto'}, {cfg.dqdx_vs_time_fit_x_hi or 'auto'}] tt")
    print(f"{output_align}    Range scan     : {'enabled (' + str(cfg.dqdx_fit_scan_n_steps) + ' steps, ' + str(cfg.dqdx_fit_scan_width_min) + '-' +
          str(cfg.dqdx_fit_scan_width_max) + ' tt, stable thr=' + str(cfg.dqdx_fit_scan_stable_thr) + ')' if cfg.dqdx_fit_range_scan else 'disabled'}")
    print(_sep('═'))

    Path(cfg.step3_dir).mkdir(parents=True, exist_ok=True)

    analyzer = CRStep3Analyzer()
    analyzer.run_all(
        equalized_charges_path=eq_charges_path,
        output_folder=cfg.step3_dir,
        dataset_name=cfg.raw_data_folder_name,
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

    print(_sep('═'))
    print(f"\n [{find_time_now()}] > Step 3 complete.\n")


if __name__ == '__main__':
    cfg = CRConfigData.from_config(CRConfig)
    run_step3(cfg)
