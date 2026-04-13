#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cr_selector.py — CRSelector class.

Responsibilities:
  - Run find_peaks_50l on collection channels 0-47 only
  - Apply the CR selection criterion:
      >= min_strips_1peak out of NCC strips have exactly 1 peak
  - For strips with 2+ peaks, use the track time range (open interval
    defined by the single-peak strips) to identify the CR hit:
      * exactly 1 peak inside the range  -> keep it
      * 0 or 2+ peaks inside the range   -> reject the event
  - Store one unambiguous CR peak per strip in SelectionResult
  - Compute event-level summary fields for the events CSV
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional

from inc.settings import NCC, output_align
from inc.find_peaks_50l import find_peaks_50l
from inc.cr.cr_induction import CRInductionAnalyzer, InductionResult


@dataclass
class ChannelPeakInfo:
    """
    Peak information for a single collection channel.
    After track-range disambiguation, exactly one CR peak is stored.
    """
    chn:           int
    n_peaks_raw:   int      # total peaks found before disambiguation
    peak_time:     int      # tick of the selected CR peak
    peak_start:    int      # start tick of the selected CR peak
    peak_top:      int      # top tick of the selected CR peak
    peak_end:      int      # end tick of the selected CR peak
    peak_integral: float    # ADC*tt of the selected CR peak
    adc_peak:      float    # max ADC value within the selected peak


@dataclass
class SelectionResult:
    """Result of the CR selection for a single event."""
    is_cr_candidate:     bool
    n_strips_with_1peak: int
    channel_peak_info:   List[ChannelPeakInfo] = field(default_factory=list)
    rejection_reason:    Optional[str] = None
    # Event-level collection summary (populated only when is_cr_candidate=True)
    n_peaks_total:       int = 0
    multi_hit_strips:    str = ''
    t_peak_tick:         int = 0
    adc_peak:            float = 0.0
    # Collection geometry
    delta_t_c:           int = 0    # peak_time(strip_48) - peak_time(strip_1)
    delta_c:             int = 48   # always 48 for now
    # I2 induction plane
    delta_t_i2:          int = 0
    delta_i2:            int = 0
    induction_result:    Optional[InductionResult] = None
    # Track length pitch
    delta_l_v1:            float = 0.0
    delta_l_v2:            float = 0.0
    track_pitch_length_v1: float = 0.0   # delta_l_v1 / delta_c  (mm)
    track_pitch_length_v2: float = 0.0   # delta_l_v2 / delta_c  (mm)


class CRSelector:
    """
    Applies the CR muon selection to the collection plane of a
    processed adc array.
    """

    def __init__(
        self,
        min_strips_1peak:        int,
        peak_height:             int,
        peak_width:              int,
        induction_analyzer:      CRInductionAnalyzer,
        delta_t_us:              float,
        v_drift:                 float,
        delta_d_c:               float,
        delta_d_i:               float,
        verbose:                 bool = False,
    ):
        self.min_strips_1peak = min_strips_1peak
        self.peak_height = peak_height
        self.peak_width = peak_width
        self.induction_analyzer = induction_analyzer
        self.delta_t_us = delta_t_us
        self.v_drift = v_drift
        self.delta_d_c = delta_d_c
        self.delta_d_i = delta_d_i
        self.verbose = verbose

    # ------------------------------------------------------------------ #
    #  Public interface                                                    #
    # ------------------------------------------------------------------ #

    def select(self, adc: np.ndarray, j_file_nr: str, j_evt_nr: str,
               first_time: bool = True) -> SelectionResult:
        """
        Run the selection on the collection plane of adc.

        Parameters
        ----------
        adc        : np.ndarray, shape (NTT, NC)
        j_file_nr  : str
        j_evt_nr   : str
        first_time : bool — controls terminal output

        Returns
        -------
        SelectionResult
        """

        # ---- Step 1: run peak finding on all collection strips ----------
        raw_peaks = {}
        n_strips_with_1peak = 0

        for chn in range(NCC):
            peaks, _, peak_ranges = find_peaks_50l(
                adc[:, chn], chn, self.peak_height, self.peak_width
            )
            raw_peaks[chn] = (peaks, peak_ranges)
            if len(peaks) == 1:
                n_strips_with_1peak += 1

        # ---- Step 2: check minimum single-peak strip count --------------
        if n_strips_with_1peak < self.min_strips_1peak:
            reason = (
                f"Only {n_strips_with_1peak}/{NCC} collection strips "
                f"have exactly 1 peak (need >= {self.min_strips_1peak})"
            )
            if first_time and self.verbose:
                print(f"{output_align}  Event ({j_file_nr}, {j_evt_nr}): "
                      f"rejected — {reason}.")
            return SelectionResult(
                is_cr_candidate=False,
                n_strips_with_1peak=n_strips_with_1peak,
                rejection_reason=reason,
            )

        # ---- Step 3: build track time range from single-peak strips -----
        single_peak_times = [
            int(raw_peaks[chn][0][0])
            for chn in range(NCC)
            if len(raw_peaks[chn][0]) == 1
        ]
        t_min = min(single_peak_times)
        t_max = max(single_peak_times)

        # ---- Step 4: disambiguate multi-peak strips ---------------------
        channel_peak_info: List[ChannelPeakInfo] = []

        for chn in range(NCC):
            peaks, peak_ranges = raw_peaks[chn]
            n_peaks = len(peaks)

            if n_peaks == 1:
                cr_idx = 0
            else:
                inside = [
                    idx for idx, t in enumerate(peaks)
                    if t_min < int(t) < t_max
                ]
                if len(inside) != 1:
                    reason = (
                        f"Strip {chn + 1} has {n_peaks} peaks and "
                        f"{len(inside)} fall inside track range "
                        f"({t_min}, {t_max}) ticks"
                    )
                    if first_time and self.verbose:
                        print(
                            f"{output_align}  Event ({j_file_nr}, {
                                j_evt_nr}): "
                            f"rejected — {reason}."
                        )
                    return SelectionResult(
                        is_cr_candidate=False,
                        n_strips_with_1peak=n_strips_with_1peak,
                        rejection_reason=reason,
                    )
                cr_idx = inside[0]

            # Extract selected peak's properties
            p_start, p_top, p_end, p_integral = [], [], [], []
            if n_peaks > 0 and len(peak_ranges) == 4:
                p_start, p_top, p_end, p_integral = peak_ranges

            # Max ADC within the peak range
            start = int(p_start[cr_idx]) if p_start else 0
            end = int(p_end[cr_idx]) if p_end else 0
            adc_peak_val = float(np.max(adc[start:end + 1, chn])) \
                if end > start else float(adc[int(peaks[cr_idx]), chn])

            channel_peak_info.append(ChannelPeakInfo(
                chn=chn,
                n_peaks_raw=n_peaks,
                peak_time=int(peaks[cr_idx]),
                peak_start=start,
                peak_top=int(p_top[cr_idx]) if p_top else 0,
                peak_end=end,
                peak_integral=float(p_integral[cr_idx]) if p_integral else 0.0,
                adc_peak=round(adc_peak_val, 2),
            ))

        # ---- Step 5: compute event-level summary fields -----------------
        n_peaks_total = sum(ch.n_peaks_raw for ch in channel_peak_info)
        multi_hit_strips = ','.join(
            str(ch.chn + 1)
            for ch in channel_peak_info
            if ch.n_peaks_raw > 1
        )

        # Strip with the highest ADC value across the track
        best_ch = max(channel_peak_info, key=lambda ch: ch.adc_peak)
        t_peak_tick = best_ch.peak_top
        adc_peak = best_ch.adc_peak

        # Collection geometry
        delta_t_c = channel_peak_info[47].peak_time - \
            channel_peak_info[0].peak_time
        delta_c = 48

        # ---- Step 6: I2 induction plane analysis ------------------------
        ind_result = self.induction_analyzer.analyze(adc, t_min, t_max)

        if first_time:
            print(
                f"{output_align}> CR candidate: Event "
                f"({j_file_nr}, {j_evt_nr}) — "
                f"{n_strips_with_1peak}/{NCC} strips with 1 peak, "
                f"track range ({t_min}, {t_max}) ticks, "
                f"peak ADC {adc_peak} @ tick {t_peak_tick}, "
                f"I2 strips: {ind_result.delta_i2}."
            )

        # ---- Step 7: track length pitch ---------------------------------
        delta_l_v1, delta_l_v2 = self._compute_delta_l(
            delta_t_c=delta_t_c,
            delta_c=delta_c,
            delta_i=ind_result.delta_i2,
        )
        track_pitch_length_v1 = round(
            delta_l_v1 / delta_c, 3) if delta_c > 0 else 0.0
        track_pitch_length_v2 = round(
            delta_l_v2 / delta_c, 3) if delta_c > 0 else 0.0

        return SelectionResult(
            is_cr_candidate=True,
            n_strips_with_1peak=n_strips_with_1peak,
            channel_peak_info=channel_peak_info,
            n_peaks_total=n_peaks_total,
            multi_hit_strips=multi_hit_strips,
            t_peak_tick=t_peak_tick,
            adc_peak=adc_peak,
            delta_t_c=delta_t_c,
            delta_c=delta_c,
            delta_t_i2=ind_result.delta_t_i2,
            delta_i2=ind_result.delta_i2,
            induction_result=ind_result,
            delta_l_v1=delta_l_v1,
            delta_l_v2=delta_l_v2,
            track_pitch_length_v1=track_pitch_length_v1,
            track_pitch_length_v2=track_pitch_length_v2,
        )

    # ------------------------------------------------------------------ #
    #  Private helpers                                                     #
    # ------------------------------------------------------------------ #

    def _compute_delta_l(
        self,
        delta_t_c: int,
        delta_c:   int,
        delta_i:   int,
    ) -> tuple:
        """
        Compute the track length pitch using two formulas.

        Parameters
        ----------
        delta_t_c : int   — peak time difference strip_48 - strip_1 (ticks)
        delta_c   : int   — number of collection strips crossed (48)
        delta_i   : int   — number of I2 strips crossed

        Returns
        -------
        (delta_l_v1, delta_l_v2) : (float, float) in mm
        """
        dt = self.delta_t_us   # µs/tick
        vd = self.v_drift      # mm/µs
        ddc = self.delta_d_c    # mm
        ddi = self.delta_d_i    # mm

        # --- Formula 1 (ICARUS, Navas-Concha et al. 2002, eq. 11) ---
        # ΔL is dimensionless (in units of wire pitches), multiply by δd to get mm.
        # Drift term: (ΔT · δt · v_d / δd)²  — dimensionless
        # Spatial term: 4/3 · (ΔC² + ΔI² - ΔC·ΔI)  — dimensionless (same pitch assumed)
        drift_term_v1 = (delta_t_c * dt * vd / ddc) ** 2
        spatial_v1 = (4.0 / 3.0) * (
            delta_c ** 2 + delta_i ** 2 - delta_c * delta_i
        )
        delta_l_v1 = round(float(ddc * np.sqrt(drift_term_v1 + spatial_v1)), 3)

        # --- Formula 2 (precise, δd_c ≠ δd_i, Case II) ---
        # All terms already in mm²: result is directly in mm.
        # Drift term: (v_d · ΔT · δt)²  — mm²
        # Spatial term: 4/3 · (ΔC²·δd_c² + ΔI²·δd_i² + ΔC·ΔI·δd_c·δd_i)  — mm²
        drift_term_v2 = (delta_t_c * dt * vd) ** 2
        spatial_v2 = (4.0 / 3.0) * (
            delta_c ** 2 * ddc ** 2
            + delta_i ** 2 * ddi ** 2
            + delta_c * delta_i * ddc * ddi
        )
        delta_l_v2 = round(float(np.sqrt(drift_term_v2 + spatial_v2)), 3)

        return delta_l_v1, delta_l_v2
