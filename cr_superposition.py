#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cr_superposition.py — Superposition event display of all selected CR events.

Reads *-CR_events.csv, reloads each raw ADC from JSON files, applies
baseline subtraction and coherent noise removal, then overlays all events
into TH2F histograms (no averaging) rendered with PyROOT.

For each view (full 3-view, collection, induction1, induction2) two PDFs
are produced: one with linear z scale and one with log z scale.

Usage
-----
    python3 cr_superposition.py

Output (in output/{dataset}/plots/)
------
    {dataset}_CR_superposition_{view}.pdf
    {dataset}_CR_superposition_{view}_log.pdf
"""

import os
import csv
import json
import numpy as np
from pathlib import Path
from collections import defaultdict

from config_cr import CRConfig
from inc.cr.cr_config import CRConfigData
from inc.cr.cr_processor import CRProcessor
from inc.find_run_time import find_time_now
from inc.settings import (NTT, NC, NCC, NI1, NI2,
                          get_noisy_chns, output_align)
from inc.remove_coherent_noise import remove_coherent_noise

_W = 60


def _sep(char='─'):
    return f"{output_align}{char * _W}"


def _get_root():
    try:
        import ROOT
        ROOT.gROOT.SetBatch(True)
        ROOT.gErrorIgnoreLevel = ROOT.kWarning
        return ROOT
    except Exception as e:
        raise RuntimeError(
            f"ROOT unavailable: {e}\nRun on lxplus or install ROOT.")


def run_superposition(cfg: CRConfigData) -> None:

    ROOT = _get_root()

    events_csv = cfg.csv_path
    data_path = Path(f"../DATA/{cfg.raw_data_folder_name}/jsonData/")
    out_dir = cfg.plot_dir
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    print(f"\n [{find_time_now()}] > CR superposition display")
    print(_sep('='))
    print(f"{output_align}  Dataset   : {cfg.raw_data_folder_name}")
    print(f"{output_align}  Events CSV: {events_csv}")
    print(f"{output_align}  Output    : {out_dir}")
    print(_sep('='))

    # Read selected events
    selected = []
    with open(events_csv, 'r', newline='') as f:
        for row in csv.DictReader(f):
            selected.append({
                'json_file':          row['json_file'],
                'converted_event_id': int(row['converted_event_id']),
            })

    n_sel = len(selected)
    if n_sel == 0:
        print(f"{output_align}!! No events in {events_csv}")
        return
    print(f"{output_align}  Found {n_sel} selected events.")

    # Accumulator
    adc_sum = np.zeros((NTT, NC), dtype=float)
    n_loaded = 0

    noisy_channels = get_noisy_chns(cfg.year)
    processor = CRProcessor(
        coherent_noise_flags=cfg.coherent_noise_step1,
        equalize=cfg.equalize_step1,
        year=cfg.year,
        noisy_channels=noisy_channels,
    )
    b0, b1, b2 = cfg.coherent_noise_step1

    # Group by json_file to minimise file opens
    by_file = defaultdict(list)
    for ev in selected:
        by_file[ev['json_file']].append(ev['converted_event_id'])

    for json_file, event_ids in sorted(by_file.items()):
        full_path = data_path / json_file
        if not full_path.exists():
            print(f"{output_align}  !! Not found: {full_path}")
            continue
        with open(full_path) as tf:
            data = json.load(tf)
        for i, event in enumerate(data['all']):
            if int(event['convertedEventID']) not in event_ids:
                continue
            adc, ok = processor.build_adc(
                event=event, j_evt_nr=str(event['convertedEventID']))
            if not ok:
                continue
            data['all'][i] = remove_coherent_noise(
                b0, b1, b2, event,
                f"{cfg.raw_data_folder_name}_evt{event['convertedEventID']}", "")
            adc, ok = processor.build_adc(
                event=data['all'][i], j_evt_nr=str(event['convertedEventID']))
            if not ok:
                continue
            adc_sum += adc
            n_loaded += 1
            print(f"{output_align}  [{n_loaded:>4}/{n_sel}]  {json_file}"
                  f"  evt {event['convertedEventID']}")

    if n_loaded == 0:
        print(f"{output_align}!! No events loaded.")
        return

    print(f"\n{output_align}  Loaded {n_loaded}/{n_sel}. Producing plots...")

    # ------------------------------------------------------------------ #
    #  Define views: (name, ch_start, ch_end, label)                      #
    # ------------------------------------------------------------------ #
    views = [
        ('full',        0,           NC,          'All planes'),
        ('collection',  0,           NCC,         'Collection'),
        ('induction1',  NCC,         NCC + NI1,   'Induction 1'),
        ('induction2',  NCC + NI1,   NC,          'Induction 2'),
    ]

    dn = cfg.raw_data_folder_name

    for view_name, ch_lo, ch_hi, view_label in views:
        n_ch = ch_hi - ch_lo
        adc_sub = adc_sum[:, ch_lo:ch_hi]

        hname = f"h_{view_name}"
        title = (f"{dn} - CR muon superposition ({n_loaded} events)"
                 f" - {view_label}"
                 f";Channel;Time tick")

        h = ROOT.TH2F(hname, title,
                      n_ch,  ch_lo - 0.5, ch_hi - 0.5,
                      NTT,   -0.5,         NTT - 0.5)
        h.SetStats(0)

        for t in range(NTT):
            for ch in range(n_ch):
                val = float(adc_sub[t, ch])
                if val != 0:
                    h.SetBinContent(ch + 1, t + 1, val)

        _save_superposition_canvas(
            ROOT, h, out_dir,
            f"{dn}_CR_superposition_{view_name}")

    # ------------------------------------------------------------------ #
    #  Equalized superposition (v1 and v2)                                #
    # ------------------------------------------------------------------ #
    eq_csv = cfg.csv_path.replace('_events', '_equalization')
    if not Path(eq_csv).exists():
        print(f"{output_align}  !! Equalization CSV not found: {eq_csv}")
        print(f"{output_align}     Run Step 2 first to generate it.")
    else:
        eq_factors = {}
        with open(eq_csv, 'r', newline='') as f:
            for row in csv.DictReader(f):
                eq_factors[row['version']] = {
                    'mean_lo': float(row['mean_lo']),
                    'mean_hi': float(row['mean_hi']),
                }

        for version in ('v1', 'v2'):
            if version not in eq_factors:
                print(f"{output_align}  !! No equalization factors for {version}")
                continue

            mean_lo = eq_factors[version]['mean_lo']
            mean_hi = eq_factors[version]['mean_hi']
            scale = mean_lo / mean_hi if mean_hi > 0 else 1.0

            print(f"{output_align}  Equalization {version}: "
                  f"mean_lo={mean_lo:.2f}, mean_hi={mean_hi:.2f}, "
                  f"scale={scale:.4f}")

            # Scale strips 25-48 (channels 24-47) up to match strips 1-24
            adc_eq = adc_sum.copy()
            adc_eq[:, 24:NCC] *= scale

            for view_name, ch_lo, ch_hi, view_label in views:
                n_ch = ch_hi - ch_lo
                adc_sub = adc_eq[:, ch_lo:ch_hi]

                hname = f"h_{view_name}_eq_{version}"
                title = (f"{dn} - CR muon superposition ({n_loaded} events)"
                         f" - {view_label} - equalized ({version})"
                         f";Channel;Time tick")

                h = ROOT.TH2F(hname, title,
                              n_ch,  ch_lo - 0.5, ch_hi - 0.5,
                              NTT,   -0.5,         NTT - 0.5)
                h.SetStats(0)

                for t in range(NTT):
                    for ch in range(n_ch):
                        val = float(adc_sub[t, ch])
                        if val != 0:
                            h.SetBinContent(ch + 1, t + 1, val)

                _save_superposition_canvas(
                    ROOT, h, out_dir,
                    f"{dn}_CR_superposition_{view_name}_eq_{version}")

    print(f"\n [{find_time_now()}] > Superposition complete.\n")


def _save_superposition_canvas(
    ROOT,
    h,
    out_dir: str,
    fname:   str,
) -> None:

    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetTitleFont(42, "XYZ")
    ROOT.gStyle.SetLabelFont(42, "XYZ")
    ROOT.gStyle.SetTitleFont(42, "t")
    ROOT.gStyle.SetPalette(ROOT.kBird)

    c = ROOT.TCanvas(f"c_{fname}", fname, 3200, 1400)
    c.SetLeftMargin(0.08)
    c.SetBottomMargin(0.12)
    c.SetTopMargin(0.10)
    c.SetRightMargin(0.12)

    h.GetXaxis().SetTitleSize(0.04)
    h.GetYaxis().SetTitleSize(0.04)
    h.GetXaxis().SetLabelSize(0.03)
    h.GetYaxis().SetLabelSize(0.03)
    h.GetXaxis().SetTitleOffset(1.0)
    h.GetYaxis().SetTitleOffset(0.8)
    h.GetZaxis().SetTitle("ADC (summed)")
    h.GetZaxis().SetTitleSize(0.03)
    h.GetZaxis().SetTitleOffset(1.2)

    h.Draw("COLZ")

    c.Update()
    out = os.path.join(out_dir, f"{fname}.pdf")
    c.SaveAs(out)
    print(f" [{find_time_now()}] : {out} saved")
    c.Close()


if __name__ == '__main__':
    cfg = CRConfigData.from_config(CRConfig)
    run_superposition(cfg)
