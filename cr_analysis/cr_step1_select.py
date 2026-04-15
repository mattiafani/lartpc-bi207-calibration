#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cr_step1_select.py — Step 1: CR muon event selection.

Walks all JSON files in the data folder, applies the CR selection
criteria, and writes two CSV files:
  - *-CR_events.csv  : one row per selected event (metadata + summary)
  - *-CR_charges.csv : one row per collection strip per event (charge data)

Processing is split into two stages for performance:
  Stage 1 (every event)    : baseline subtraction only — cheap
  Stage 2 (selected only)  : coherent noise removal   — expensive

Usage
-----
    python3 cr_step1_select.py

All parameters are controlled via config_cr.py.
"""

import os
from pathlib import Path
from inc.remove_coherent_noise import remove_coherent_noise

from config_cr import CRConfig
from inc.cr.cr_config import CRConfigData
from inc.cr.cr_reader import CRReader
from inc.cr.cr_processor import CRProcessor
from inc.cr.cr_selector import CRSelector
from inc.cr.cr_induction import CRInductionAnalyzer
from inc.cr.cr_writer import CRWriter, CREventCoords, CRStripCharge
from inc.cr.cr_display import CRDisplay
from inc.find_run_time import find_time_now
from inc.settings import get_noisy_chns, output_align

_W = 60   # separator width


def _sep(char='─'):
    return f"{output_align}{char * _W}"


def run_step1(cfg: CRConfigData) -> int:
    """
    Execute Step 1: selection + CSV output.

    Returns
    -------
    n_selected : int
        Number of CR candidate events written to CSV.
    """

    print(f"\n [{find_time_now()}] > Step 1: CR muon selection")
    print(_sep('═'))
    print(f"{output_align}  Dataset          : {cfg.raw_data_folder_name}")
    print(f"{output_align}  Output root      : {cfg.output_root}")
    print(_sep())
    print(f"{output_align}  Selection")
    print(f"{output_align}    Min strips (1 peak) : {
          cfg.min_strips_1peak} / 48")
    print(f"{output_align}    Peak height / width : {cfg.peak_height} ADC / {cfg.peak_width} ticks")
    print(f"{output_align}    I2 pos/neg height   : {
          cfg.i2_pos_peak_height} / {cfg.i2_neg_peak_height} ADC")
    print(f"{output_align}    I2 time tolerance   : {
          cfg.i2_time_tolerance_ticks} ticks")
    print(_sep())
    print(f"{output_align}  Processing")
    print(f"{output_align}    Coherent noise      : {
          cfg.coherent_noise_step1}")
    print(f"{output_align}    Equalization        : {cfg.equalize_step1}")
    print(f"{output_align}    Verbose rejections  : {cfg.verbose}")
    print(_sep())
    print(f"{output_align}  Display")
    print(f"{output_align}    2D event display    : {cfg.evtdisplay_step1}")
    print(f"{output_align}    Single traces       : {
          cfg.chndisplay_planes_step1 or 'disabled'}")
    print(_sep('═'))

    # Create output directories
    for d in (cfg.csv_dir, cfg.event_display_dir, cfg.single_traces_dir):
        Path(d).mkdir(parents=True, exist_ok=True)

    # Pre-scan to know total files and events
    print(f"\n [{find_time_now()}] > Scanning data folder...")
    reader = CRReader(cfg.raw_data_folder_name)
    n_files, n_events = reader.scan()
    print(f"{output_align}  Found {
          n_files} JSON files, {n_events} total events.")
    print(_sep())

    noisy_channels = get_noisy_chns(cfg.year)
    processor = CRProcessor(
        coherent_noise_flags=cfg.coherent_noise_step1,
        equalize=cfg.equalize_step1,
        year=cfg.year,
        noisy_channels=noisy_channels,
    )
    induction_analyzer = CRInductionAnalyzer(
        pos_peak_height=cfg.i2_pos_peak_height,
        pos_peak_width=cfg.i2_pos_peak_width,
        neg_peak_height=cfg.i2_neg_peak_height,
        time_tolerance_ticks=cfg.i2_time_tolerance_ticks,
    )
    selector = CRSelector(
        cfg.min_strips_1peak,
        cfg.peak_height,
        cfg.peak_width,
        induction_analyzer,
        cfg.delta_t_us,
        cfg.v_drift,
        cfg.delta_d_c,
        cfg.delta_d_i,
        verbose=cfg.verbose,
    )
    writer = CRWriter(cfg.csv_path, cfg.csv_charges_path)
    display = CRDisplay(cfg.event_display_dir, terminal_bool=True)

    writer.initialize()

    n_total = 0
    n_selected = 0
    b0, b1, b2 = cfg.coherent_noise_step1

    print(f"\n [{find_time_now()}] > Processing events...\n")

    for json_file, event, data, i, f_cnt, e_cnt in \
            reader.iter_events(n_files, n_events):

        n_total += 1

        meta = CRReader.event_metadata(
            event=event,
            raw_data_folder_name=cfg.raw_data_folder_name,
            path_to_folder_plots=cfg.event_display_dir,
            json_file=json_file,
        )

        # ----------------------------------------------------------------
        # Stage 1 — cheap, runs on every event.
        # ----------------------------------------------------------------
        adc, dim_ok = processor.build_adc(
            event=event,
            j_evt_nr=meta['converted_event_id'],
        )
        if not dim_ok:
            continue

        selection = selector.select(
            adc=adc,
            j_file_nr=meta['converted_file_id'],
            j_evt_nr=meta['converted_event_id'],
        )

        if not selection.is_cr_candidate:
            continue

        # ----------------------------------------------------------------
        # Stage 2 — expensive, runs only for selected events.
        # ----------------------------------------------------------------
        data['all'][i] = remove_coherent_noise(
            b0, b1, b2, event, meta['evt_title'], meta['save_file_name']
        )
        adc, dim_ok = processor.build_adc(
            event=data['all'][i],
            j_evt_nr=meta['converted_event_id'],
        )
        if not dim_ok:
            continue

        selection = selector.select(
            adc=adc,
            j_file_nr=meta['converted_file_id'],
            j_evt_nr=meta['converted_event_id'],
            first_time=False,
        )

        if not selection.is_cr_candidate:
            print(
                f"{output_align}  [evt {e_cnt:>5}/{n_events}]"
                f"  Rejected after noise removal: "
                f"{selection.rejection_reason}."
            )
            continue

        n_selected += 1
        pct = 100.0 * e_cnt / n_events if n_events > 0 else 0.0
        print(
            f"{output_align}  [evt {e_cnt:>5}/{n_events} | {pct:5.1f}%]"
            f"  ✓ CR candidate #{n_selected}"
            f"  Evt {meta['event_id']}"
            f"  ΔL_v1={selection.delta_l_v1:.1f} mm"
            f"  I2={selection.delta_i2} strips"
        )

        # ----------------------------------------------------------------
        # Write events table row
        # ----------------------------------------------------------------
        writer.append_event(CREventCoords(
            event_id=meta['event_id'],
            binary_file_id=meta['binary_file_id'],
            binary_event_id=meta['binary_event_id'],
            converted_file_id=meta['converted_file_id'],
            converted_event_id=meta['converted_event_id'],
            json_file=json_file,
            run_time=meta['run_time'],
            n_strips_1peak=selection.n_strips_with_1peak,
            n_peaks_total=selection.n_peaks_total,
            multi_hit_strips=selection.multi_hit_strips,
            t_peak_tick=selection.t_peak_tick,
            adc_peak=selection.adc_peak,
            delta_t_c=selection.delta_t_c,
            delta_c=selection.delta_c,
            delta_t_i2=selection.delta_t_i2,
            delta_i2=selection.delta_i2,
            delta_l_v1=selection.delta_l_v1,
            delta_l_v2=selection.delta_l_v2,
            track_pitch_length_v1=selection.track_pitch_length_v1,
            track_pitch_length_v2=selection.track_pitch_length_v2,
        ))

        # ----------------------------------------------------------------
        # Write charges table rows (one per collection strip)
        # ----------------------------------------------------------------
        delta_l_v1 = selection.delta_l_v1
        delta_l_v2 = selection.delta_l_v2
        charges = [
            CRStripCharge(
                event_id=meta['event_id'],
                strip=ch.chn + 1,
                peak_time_tick=ch.peak_time,
                peak_start_tick=ch.peak_start,
                peak_end_tick=ch.peak_end,
                # ADC·tt (from find_peak_range)
                peak_integral_adc_tt=ch.peak_integral,
                t_peak_tick=ch.peak_top,
                adc_peak=ch.adc_peak,
                normalized_charge_v1_adc_tt=round(
                    ch.peak_integral / selection.track_pitch_length_v1, 4
                ) if selection.track_pitch_length_v1 > 0 else 0.0,
                normalized_charge_v2_adc_tt=round(
                    ch.peak_integral / selection.track_pitch_length_v2, 4
                ) if selection.track_pitch_length_v2 > 0 else 0.0,
            )
            for ch in selection.channel_peak_info
        ]
        writer.append_charges(charges)

        # ----------------------------------------------------------------
        # 2-D event display
        # ----------------------------------------------------------------
        if cfg.evtdisplay_step1:
            display.show_event_2d(
                adc=adc,
                run_time=meta['run_time'],
                evt_title=meta['evt_title'],
                save_file_name=meta['save_file_name'] + '.pdf',
            )

        # ----------------------------------------------------------------
        # Single-channel traces
        # ----------------------------------------------------------------
        if cfg.chndisplay_planes_step1:
            evt_subdir = CRReader.event_subdir(
                cfg.single_traces_dir,
                meta['event_id'],
                meta['converted_file_id'],
                meta['converted_event_id'],
            )
            evt_prefix = f"Event_{meta['event_id']}_{
                meta['converted_event_id']}"
            display.show_channel_traces(
                adc=adc,
                planes=cfg.chndisplay_planes_step1,
                save_file_name=os.path.join(evt_subdir, evt_prefix),
                evt_title=meta['evt_title'],
                year=cfg.year,
                peak_height=cfg.peak_height,
                peak_width=cfg.peak_width,
                induction_result=selection.induction_result,
            )

    sel_pct = 100.0 * n_selected / n_total if n_total > 0 else 0.0
    print(f"\n{_sep('═')}")
    print(f"\n [{find_time_now()}] > Step 1 complete")
    print(_sep())
    print(f"{output_align}  Events processed : {n_total}")
    print(f"{output_align}  CR candidates    : {n_selected} ({sel_pct:.1f}%)")
    print(f"{output_align}  Events  CSV      : {cfg.csv_path}")
    print(f"{output_align}  Charges CSV      : {cfg.csv_charges_path}")
    print(_sep('═'))

    return n_selected


if __name__ == '__main__':
    cfg = CRConfigData.from_config(CRConfig)
    run_step1(cfg)
