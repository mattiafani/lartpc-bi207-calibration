#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cr_step2_analyze.py — Step 2: CR muon analysis.

Pure CSV-based analysis. Reads the two CSV files produced by Step 1
and produces output plots. No JSON files, no reprocessing.

Usage
-----
    python3 cr_step2_analyze.py

All parameters are controlled via config_cr.py.
"""

from pathlib import Path

from config_cr import CRConfig
from inc.cr.cr_config import CRConfigData
from inc.cr.cr_analyzer import CRAnalyzer
from inc.find_run_time import find_time_now
from inc.settings import output_align

_W = 60


def _sep(char='─'):
    return f"{output_align}{char * _W}"


def run_step2(cfg: CRConfigData) -> None:
    """Execute Step 2: CSV-based analysis and plot production."""

    print(f"\n [{find_time_now()}] > Step 2: CR muon analysis")
    print(_sep('═'))
    print(f"{output_align}  Dataset          : {cfg.raw_data_folder_name}")
    print(_sep())
    print(f"{output_align}  Input")
    print(f"{output_align}    Events  CSV    : {cfg.csv_path}")
    print(f"{output_align}    Charges CSV    : {cfg.csv_charges_path}")
    print(_sep())
    print(f"{output_align}  Output")
    print(f"{output_align}    Summary folder : {cfg.summary_dir}")
    print(f"{output_align}    Charge bin width: {
          cfg.norm_charge_bin_width} ADC·tt")
    print(_sep('═'))

    Path(cfg.summary_dir).mkdir(parents=True, exist_ok=True)

    analyzer = CRAnalyzer()
    analyzer.run_all(
        csv_path=cfg.csv_path,
        output_folder=cfg.summary_dir,
        delta_d_c=cfg.delta_d_c,
        dataset_name=cfg.raw_data_folder_name,
        norm_charge_bin_width=cfg.norm_charge_bin_width,
        delta_l_bin_width=cfg.delta_l_bin_width,
        track_pitch_bin_width=cfg.track_pitch_bin_width,
    )

    print(_sep('═'))
    print(f"\n [{find_time_now()}] > Step 2 complete.\n")


if __name__ == '__main__':
    cfg = CRConfigData.from_config(CRConfig)
    run_step2(cfg)
