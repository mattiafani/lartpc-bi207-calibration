#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cr_display.py — CRDisplay class.

Responsibilities:
  - 2-D event display for all 128 channels
  - Single-channel trace display per plane
    * Collection : peak marker at ADC value, gold shading, charge in legend
    * I1 / I2    : zero-crossing marker at ADC=0, crossover time in legend
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Optional

from inc.settings import NC, NCC, NI1, NTT, output_align
from inc.find_run_time import find_time_now
from inc.find_peaks_50l import find_peaks_50l
from inc.cr.cr_induction import InductionResult, I2StripInfo

plt.rcParams.update({'font.size': 20})

_PLANE_BOUNDARIES = [NCC, NCC + NI1]
_PLANE_LABELS = [
    (NCC / 2,           'Collection (C)'),
    (NCC + NI1 / 2,     'Induction 1 (I1)'),
    (NCC + NI1 + NI1/2, 'Induction 2 (I2)'),
]


class CRDisplay:
    """Handles all visualisation for the CR muon analysis."""

    def __init__(self, output_folder: str, terminal_bool: bool):
        self.output_folder = output_folder
        self.batch = terminal_bool
        Path(output_folder).mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ #
    #  2-D event display                                                   #
    # ------------------------------------------------------------------ #

    def show_event_2d(self, adc: np.ndarray, run_time: str,
                      evt_title: str, save_file_name: str) -> None:
        fig, ax = plt.subplots(figsize=(16, 8), dpi=100)
        mesh = ax.pcolor(adc, vmin=-100, vmax=100, cmap='YlGnBu_r')
        fig.colorbar(mesh, ax=ax)

        for x in _PLANE_BOUNDARIES:
            ax.axvline(x=x, color='white', linewidth=1.2,
                       linestyle='--', alpha=0.7)

        y_label = adc.shape[0] * 0.97
        for x_pos, label in _PLANE_LABELS:
            ax.text(x_pos, y_label, label, color='white', fontsize=13,
                    ha='center', va='top',
                    bbox=dict(boxstyle='round,pad=0.2', fc='black', alpha=0.4))

        ax.set_xlabel('Strips')
        ax.set_ylabel('Time ticks [0.5 µs/tick]')
        ax.set_xticks(np.arange(0, NC + 1, 10))
        ax.set_title(f"{run_time} - {evt_title}")

        fig.savefig(save_file_name)
        if not self.batch:
            plt.show()

        print(f' [{find_time_now()}] : {save_file_name} saved')
        plt.clf()
        plt.close()

    # ------------------------------------------------------------------ #
    #  Single-channel trace display                                        #
    # ------------------------------------------------------------------ #

    def show_channel_traces(
        self,
        adc:              np.ndarray,
        planes:           List[str],
        save_file_name:   str,
        evt_title:        str,
        year:             str,
        peak_height:      int,
        peak_width:       int,
        induction_result: Optional[InductionResult] = None,
    ) -> None:
        """
        Produce one PDF per channel for the requested planes.

        Parameters
        ----------
        adc              : np.ndarray, shape (NTT, NC)
        planes           : list of str — any subset of ['C', 'I1', 'I2']
        peak_height      : int — collection plane peak height threshold
        peak_width       : int — collection plane peak width threshold
        induction_result : InductionResult from CRInductionAnalyzer,
                           used to mark zero-crossings on I2 traces
        """
        Path(save_file_name).parent.mkdir(parents=True, exist_ok=True)

        # Build a lookup: chn -> I2StripInfo for fast access
        i2_lookup = {}
        if induction_result is not None:
            for info in induction_result.i2_strip_info:
                i2_lookup[info.chn] = info

        plane_channel_indices = self._plane_ranges(planes)

        for chn in plane_channel_indices:
            if chn < NCC:
                # Collection — use peak finder with CR parameters
                peaks, _, peak_ranges = find_peaks_50l(
                    adc[:, chn], chn, peak_height, peak_width
                )
                charge = 0.0
                if len(peak_ranges) == 4 and len(peak_ranges[3]) > 0:
                    charge = sum(peak_ranges[3])
                self._trace_collection(
                    chn=chn,
                    y=adc[:, chn],
                    peaks=peaks,
                    peak_ranges=[peak_ranges] if len(peaks) > 0 else [],
                    charge=charge,
                    save_file_name=save_file_name,
                    evt_title=evt_title,
                )
            else:
                # Induction — use I2StripInfo if available
                i2_info = i2_lookup.get(chn, None)
                self._trace_induction(
                    chn=chn,
                    y=adc[:, chn],
                    i2_info=i2_info,
                    save_file_name=save_file_name,
                    evt_title=evt_title,
                )

    # ------------------------------------------------------------------ #
    #  Private: collection trace                                           #
    # ------------------------------------------------------------------ #

    def _trace_collection(self, chn: int, y: np.ndarray, peaks,
                          peak_ranges: list, charge: float,
                          save_file_name: str, evt_title: str) -> None:
        fig, ax = plt.subplots(figsize=(32, 9))

        ps = [round(float(p) * 0.5, 1) for p in peaks]
        p_list = [round(float(y[p]), 1) for p in peaks]
        label = (f'Chn_{str(chn).zfill(3)};'
                 f'\nPeaks: {ps} µs, {p_list} ADC'
                 f'\nCharge: {round(float(charge), 1)} ADC*tt')

        lr, rr = [], []
        if len(peak_ranges) > 0:
            lr = [int(v) for v in peak_ranges[0][0]]
            rr = [int(v) for v in peak_ranges[0][2]]
        label += f"\nRanges: {lr}, {rr} ticks"

        ax.plot(y, label=label)

        if len(peaks) > 0:
            ax.plot(peaks, y[peaks], 'x')

        # Gold shading under peaks
        if len(peak_ranges) > 0:
            for p_start, p_end in zip(peak_ranges[0][0], peak_ranges[0][2]):
                rx = np.arange(p_start, p_end)
                ax.fill_between(rx, 0, y[rx], color='gold', alpha=0.5)

        self._format_axes(ax, chn, y, evt_title)
        self._save_and_close(fig, save_file_name, chn)

    # ------------------------------------------------------------------ #
    #  Private: induction trace                                            #
    # ------------------------------------------------------------------ #

    def _trace_induction(self, chn: int, y: np.ndarray,
                         i2_info: Optional[I2StripInfo],
                         save_file_name: str, evt_title: str) -> None:
        fig, ax = plt.subplots(figsize=(32, 9))

        label = f'Chn_{str(chn).zfill(3)}'

        if i2_info is not None:
            zc_us = round(i2_info.zero_cross_tick * 0.5, 1)
            label += (f';\nCrossover at: {zc_us} µs'
                      f' (tick {i2_info.zero_cross_tick})'
                      f'\nPos peak: {i2_info.pos_peak_adc} ADC'
                      f' @ tick {i2_info.pos_peak_tick}'
                      f'\nNeg peak: {i2_info.neg_peak_adc} ADC'
                      f' @ tick {i2_info.neg_peak_tick}')
            # Mark the zero-crossing with an 'x' at ADC=0
            ax.plot(i2_info.zero_cross_tick, 0, 'x',
                    color='orange', markersize=12, markeredgewidth=2)
        else:
            label += ';\nNo crossover detected'

        ax.plot(y, label=label)
        self._format_axes(ax, chn, y, evt_title)
        self._save_and_close(fig, save_file_name, chn)

    # ------------------------------------------------------------------ #
    #  Private: shared formatting                                          #
    # ------------------------------------------------------------------ #

    def _format_axes(self, ax, chn: int, y: np.ndarray,
                     evt_title: str) -> None:
        ax.set_ylabel('ADC (baseline subtracted)', labelpad=10, fontsize=24)
        ax.set_xlabel('time ticks [0.5 µs/tick]', fontsize=24)
        ax.legend(fontsize=24)
        ax.grid(True, which='major', axis='both', linewidth=1, color='gray')
        ax.grid(True, which='minor', axis='x', linewidth=0.5,
                linestyle='dashed', color='gray')
        ax.set_xticks(np.arange(0, NTT + 1, 50))
        ax.set_xticks(np.arange(0, NTT + 1, 10), minor=True)
        ax.set_ylim(-20, 300) if chn < NCC else ax.set_ylim(-250, 250)
        ax.set_xlim(0, len(y))
        ax.yaxis.set_label_coords(-0.04, 0.5)
        ax.spines['right'].set_visible(False)
        plt.title(f"{evt_title} - Strip {chn + 1}", fontsize=30)
        plt.subplots_adjust(left=0.06, right=0.94, top=0.96, bottom=0.08)
        plt.tight_layout()

    def _save_and_close(self, fig, save_file_name: str, chn: int) -> None:
        str_strip = str(chn + 1).zfill(3)
        out_path = f"{save_file_name}_Strip{str_strip}.pdf"
        plt.savefig(out_path, dpi=100)
        if not self.batch:
            plt.show()
        plt.clf()
        plt.close()

    # ------------------------------------------------------------------ #
    #  Private: plane range helper                                         #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _plane_ranges(planes: List[str]) -> List[int]:
        indices = []
        if 'C' in planes:
            indices += list(range(0,         NCC))
        if 'I1' in planes:
            indices += list(range(NCC,       NCC + NI1))
        if 'I2' in planes:
            indices += list(range(NCC + NI1, NC))
        return sorted(indices)
