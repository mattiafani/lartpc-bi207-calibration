#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cr_writer.py — CRWriter class.

Two-table CSV persistence:

  *-CR_events.csv   — one row per selected event (metadata + summary)
  *-CR_charges.csv  — one row per collection strip per event (charge data)
                      linked to events table via event_id
"""

import csv
import os
from dataclasses import dataclass
from typing import List

# ------------------------------------------------------------------ #
#  Events table                                                        #
# ------------------------------------------------------------------ #

EVENTS_FIELDS = [
    'event_id',
    'binary_file_id',
    'binary_event_id',
    'converted_file_id',
    'converted_event_id',
    'json_file',
    'run_time',
    'n_strips_1peak',
    'n_peaks_total',
    'multi_hit_strips',
    't_peak_tick',
    'adc_peak',
    'delta_t_c',
    'delta_c',
    'delta_t_i2',
    'delta_i2',
    'delta_l_v1',
    'delta_l_v2',
    'track_pitch_length_v1',
    'track_pitch_length_v2',
]


@dataclass
class CREventCoords:
    """Coordinates, metadata and summary for a single selected CR event."""
    event_id:               str
    binary_file_id:         str
    binary_event_id:        str
    converted_file_id:      str
    converted_event_id:     str
    json_file:              str
    run_time:               str
    n_strips_1peak:         int
    n_peaks_total:          int
    multi_hit_strips:       str
    t_peak_tick:            int
    adc_peak:               float
    delta_t_c:              int
    delta_c:                int
    delta_t_i2:             int
    delta_i2:               int
    delta_l_v1:             float
    delta_l_v2:             float
    track_pitch_length_v1:  float
    track_pitch_length_v2:  float


# ------------------------------------------------------------------ #
#  Charges table                                                       #
# ------------------------------------------------------------------ #

CHARGES_FIELDS = [
    'event_id',
    'strip',
    'peak_time_tick',
    'peak_start_tick',
    'peak_end_tick',
    'peak_integral_adc_tt',
    't_peak_tick',
    'adc_peak',
    'normalized_charge_v1_adc_tt',
    'normalized_charge_v2_adc_tt',
]


@dataclass
class CRStripCharge:
    """Charge data for one collection strip in one selected CR event."""
    event_id:                    str
    strip:                       int
    peak_time_tick:              int
    peak_start_tick:             int
    peak_end_tick:               int
    peak_integral_adc_tt:        float
    t_peak_tick:                 int
    adc_peak:                    float
    normalized_charge_v1_adc_tt: float
    normalized_charge_v2_adc_tt: float


# ------------------------------------------------------------------ #
#  Writer / reader                                                     #
# ------------------------------------------------------------------ #

class CRWriter:
    """
    Handles two-table CSV persistence for selected CR events.

    Parameters
    ----------
    events_csv_path  : str — path to *-CR_events.csv
    charges_csv_path : str — path to *-CR_charges.csv (optional;
                             defaults to events path with _events→_charges)
    """

    def __init__(self, events_csv_path: str,
                 charges_csv_path: str = None):
        self.events_path = events_csv_path
        self.charges_path = charges_csv_path or \
            events_csv_path.replace('_events', '_charges')

    def initialize(self) -> None:
        """Create (or overwrite) both CSV files and write headers."""
        os.makedirs(os.path.dirname(self.events_path) or '.', exist_ok=True)
        for path, fields in [
            (self.events_path,  EVENTS_FIELDS),
            (self.charges_path, CHARGES_FIELDS),
        ]:
            with open(path, 'w', newline='') as f:
                csv.DictWriter(f, fieldnames=fields).writeheader()
        print(f"  [CRWriter] Events  CSV : {self.events_path}")
        print(f"  [CRWriter] Charges CSV : {self.charges_path}")

    def append_event(self, coords: CREventCoords) -> None:
        """Append one event row to the events CSV."""
        with open(self.events_path, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=EVENTS_FIELDS)
            writer.writerow({
                'event_id':           coords.event_id,
                'binary_file_id':     coords.binary_file_id,
                'binary_event_id':    coords.binary_event_id,
                'converted_file_id':  coords.converted_file_id,
                'converted_event_id': coords.converted_event_id,
                'json_file':          coords.json_file,
                'run_time':           coords.run_time,
                'n_strips_1peak':     coords.n_strips_1peak,
                'n_peaks_total':      coords.n_peaks_total,
                'multi_hit_strips':   coords.multi_hit_strips,
                't_peak_tick':        coords.t_peak_tick,
                'adc_peak':           coords.adc_peak,
                'delta_t_c':          coords.delta_t_c,
                'delta_c':            coords.delta_c,
                'delta_t_i2':         coords.delta_t_i2,
                'delta_i2':           coords.delta_i2,
                'delta_l_v1':             coords.delta_l_v1,
                'delta_l_v2':             coords.delta_l_v2,
                'track_pitch_length_v1':  coords.track_pitch_length_v1,
                'track_pitch_length_v2':  coords.track_pitch_length_v2,
            })

    def append_charges(self, charges: List[CRStripCharge]) -> None:
        """Append 48 strip-charge rows to the charges CSV."""
        with open(self.charges_path, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=CHARGES_FIELDS)
            for c in charges:
                writer.writerow({
                    'event_id':                    c.event_id,
                    'strip':                       c.strip,
                    'peak_time_tick':              c.peak_time_tick,
                    'peak_start_tick':             c.peak_start_tick,
                    'peak_end_tick':               c.peak_end_tick,
                    'peak_integral_adc_tt':        round(c.peak_integral_adc_tt, 2),
                    't_peak_tick':                 c.t_peak_tick,
                    'adc_peak':                    round(c.adc_peak, 2),
                    'normalized_charge_v1_adc_tt': round(c.normalized_charge_v1_adc_tt, 4),
                    'normalized_charge_v2_adc_tt': round(c.normalized_charge_v2_adc_tt, 4),
                })

    def read_events(self) -> List[CREventCoords]:
        """Load all event coordinates from the events CSV."""
        coords_list: List[CREventCoords] = []
        with open(self.events_path, 'r', newline='') as f:
            for row in csv.DictReader(f):
                coords_list.append(CREventCoords(
                    event_id=row['event_id'],
                    binary_file_id=row['binary_file_id'],
                    binary_event_id=row['binary_event_id'],
                    converted_file_id=row['converted_file_id'],
                    converted_event_id=row['converted_event_id'],
                    json_file=row['json_file'],
                    run_time=row['run_time'],
                    n_strips_1peak=int(row['n_strips_1peak']),
                    n_peaks_total=int(row['n_peaks_total']),
                    multi_hit_strips=row['multi_hit_strips'],
                    t_peak_tick=int(row['t_peak_tick']),
                    adc_peak=float(row['adc_peak']),
                    delta_t_c=int(row['delta_t_c']),
                    delta_c=int(row['delta_c']),
                    delta_t_i2=int(row['delta_t_i2']),
                    delta_i2=int(row['delta_i2']),
                    delta_l_v1=float(row['delta_l_v1']),
                    delta_l_v2=float(row['delta_l_v2']),
                    track_pitch_length_v1=float(row['track_pitch_length_v1']),
                    track_pitch_length_v2=float(row['track_pitch_length_v2']),
                ))
        return coords_list

    def read_charges(self) -> List[CRStripCharge]:
        """Load all strip charge data from the charges CSV."""
        charges_list: List[CRStripCharge] = []
        with open(self.charges_path, 'r', newline='') as f:
            for row in csv.DictReader(f):
                charges_list.append(CRStripCharge(
                    event_id=row['event_id'],
                    strip=int(row['strip']),
                    peak_time_tick=int(row['peak_time_tick']),
                    peak_start_tick=int(row['peak_start_tick']),
                    peak_end_tick=int(row['peak_end_tick']),
                    peak_integral_adc_tt=float(row['peak_integral_adc_tt']),
                    t_peak_tick=int(row['t_peak_tick']),
                    adc_peak=float(row['adc_peak']),
                    normalized_charge_v1_adc_tt=float(
                        row['normalized_charge_v1_adc_tt']),
                    normalized_charge_v2_adc_tt=float(
                        row['normalized_charge_v2_adc_tt']),
                ))
        return charges_list

    # ------------------------------------------------------------------ #
    #  Equalization factor CSV                                             #
    # ------------------------------------------------------------------ #

    @property
    def equalization_path(self) -> str:
        return self.events_path.replace('_events', '_equalization')

    @property
    def equalized_charges_path(self) -> str:
        return self.charges_path.replace('_charges', '_charges_equalized')

    def write_equalization(self, factors: list) -> None:
        """Write equalization factors to *-CR_equalization.csv."""
        fields = ['version', 'mean_lo', 'mean_lo_err',
                  'mean_hi', 'mean_hi_err', 'ratio']
        with open(self.equalization_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for row in factors:
                writer.writerow({k: round(v, 6) if isinstance(v, float)
                                 else v for k, v in row.items()})
        print(f"  [CRWriter] Equalization CSV      : {self.equalization_path}")

    def read_equalization(self) -> dict:
        """Read equalization factors. Returns dict keyed by version."""
        result = {}
        with open(self.equalization_path, 'r', newline='') as f:
            for row in csv.DictReader(f):
                result[row['version']] = {
                    'mean_lo':     float(row['mean_lo']),
                    'mean_lo_err': float(row['mean_lo_err']),
                    'mean_hi':     float(row['mean_hi']),
                    'mean_hi_err': float(row['mean_hi_err']),
                    'ratio':       float(row['ratio']),
                }
        return result

    def write_equalized_charges(
        self,
        charges: list,
        eq_v1:   float,
        eq_v2:   float,
    ) -> None:
        """
        Write *-CR_charges_equalized.csv with two extra columns.
        Strips 1-24: unchanged. Strips 25-48: scaled by eq_v1/eq_v2
        so their MPV aligns with strips 1-24.
        """
        eq_fields = CHARGES_FIELDS + [
            'normalized_charge_v1_eq_adc_tt',
            'normalized_charge_v2_eq_adc_tt',
        ]
        with open(self.equalized_charges_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=eq_fields)
            writer.writeheader()
            for c in charges:
                scale_v1 = eq_v1 if c.strip >= 25 else 1.0
                scale_v2 = eq_v2 if c.strip >= 25 else 1.0
                writer.writerow({
                    'event_id':                       c.event_id,
                    'strip':                          c.strip,
                    'peak_time_tick':                 c.peak_time_tick,
                    'peak_start_tick':                c.peak_start_tick,
                    'peak_end_tick':                  c.peak_end_tick,
                    'peak_integral_adc_tt':           round(c.peak_integral_adc_tt, 2),
                    't_peak_tick':                    c.t_peak_tick,
                    'adc_peak':                       round(c.adc_peak, 2),
                    'normalized_charge_v1_adc_tt':    round(c.normalized_charge_v1_adc_tt, 4),
                    'normalized_charge_v2_adc_tt':    round(c.normalized_charge_v2_adc_tt, 4),
                    'normalized_charge_v1_eq_adc_tt': round(
                        c.normalized_charge_v1_adc_tt * scale_v1, 4),
                    'normalized_charge_v2_eq_adc_tt': round(
                        c.normalized_charge_v2_adc_tt * scale_v2, 4),
                })
        print(f"  [CRWriter] Equalized charges CSV : {
              self.equalized_charges_path}")
