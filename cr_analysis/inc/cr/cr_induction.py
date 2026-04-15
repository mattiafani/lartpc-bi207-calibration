#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cr_induction.py — CRInductionAnalyzer class.

Responsibilities:
  - Find the bipolar signal on I2 strips (channels 88-127)
  - Locate the zero-crossing between positive and negative lobes
  - Validate each zero-crossing against the collection track time range
  - Compute Delta_T_I2 and Delta_I2 for the events CSV
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from scipy.signal import find_peaks as scipy_find_peaks

from inc.settings import NCC, NI1, NC, NTT, output_align


@dataclass
class I2StripInfo:
    """Zero-crossing result for a single I2 strip."""
    chn:              int     # 0-indexed channel number (88-127)
    strip:            int     # 1-indexed strip number (89-128)
    pos_peak_tick:    int     # tick of the positive lobe peak
    zero_cross_tick:  int     # tick of the zero-crossing
    neg_peak_tick:    int     # tick of the negative lobe peak
    pos_peak_adc:     float   # ADC value at positive peak
    neg_peak_adc:     float   # ADC value at negative peak (negative value)


@dataclass
class InductionResult:
    """I2 analysis result for a single event."""
    delta_t_i2:    int              # zero-crossing time difference between
    # first and last I2 strip hit (ticks)
    delta_i2:      int              # number of I2 strips with valid signal
    i2_strip_info: List[I2StripInfo] = field(default_factory=list)


# First I2 channel index
_I2_START = NCC + NI1   # = 88


class CRInductionAnalyzer:
    """
    Analyses the I2 induction plane of a CR muon event.

    The bipolar I2 signal has a positive lobe followed immediately by a
    negative lobe. The zero-crossing between them is the best timing
    estimator for the induced signal.

    Algorithm per strip:
      1. Find positive peak within the collection time window ± tolerance
      2. Scan forward from the positive peak until ADC crosses zero
      3. Confirm a negative peak exists shortly after the zero-crossing
      4. Accept the strip if all three conditions are met
    """

    def __init__(
        self,
        pos_peak_height:      int,
        pos_peak_width:       int,
        neg_peak_height:      int,
        time_tolerance_ticks: int,
    ):
        """
        Parameters
        ----------
        pos_peak_height : int
            Minimum height of the positive lobe in ADC counts.
        pos_peak_width : int
            Minimum width of the positive lobe in ticks.
        neg_peak_height : int
            Minimum height of the negative lobe (absolute value) in ADC counts.
        time_tolerance_ticks : int
            Extra ticks added on each side of the collection time range
            to account for the I2 plane being slightly closer to the
            anode (~1 cm, ~12-13 ticks at 0.5 µs/tick).
        """
        self.pos_peak_height = pos_peak_height
        self.pos_peak_width = pos_peak_width
        self.neg_peak_height = neg_peak_height
        self.time_tolerance_ticks = time_tolerance_ticks

    # ------------------------------------------------------------------ #
    #  Public interface                                                    #
    # ------------------------------------------------------------------ #

    def analyze(
        self,
        adc:   np.ndarray,
        t_min: int,
        t_max: int,
    ) -> InductionResult:
        """
        Analyse all I2 strips and return Delta_T_I2 and Delta_I2.

        Parameters
        ----------
        adc   : np.ndarray, shape (NTT, NC)
        t_min : int — minimum CR peak time from collection plane (ticks)
        t_max : int — maximum CR peak time from collection plane (ticks)

        Returns
        -------
        InductionResult
        """
        t_lo = max(0,       t_min - self.time_tolerance_ticks)
        t_hi = min(NTT - 1, t_max + self.time_tolerance_ticks)

        i2_hits: List[I2StripInfo] = []

        for chn in range(_I2_START, NC):
            result = self._analyze_strip(adc[:, chn], chn, t_lo, t_hi)
            if result is not None:
                i2_hits.append(result)

        if len(i2_hits) < 2:
            return InductionResult(
                delta_t_i2=0,
                delta_i2=len(i2_hits),
                i2_strip_info=i2_hits,
            )

        # Sort by channel order and compute Delta_T_I2
        i2_hits.sort(key=lambda h: h.chn)
        delta_t_i2 = i2_hits[-1].zero_cross_tick - i2_hits[0].zero_cross_tick

        return InductionResult(
            delta_t_i2=delta_t_i2,
            delta_i2=len(i2_hits),
            i2_strip_info=i2_hits,
        )

    # ------------------------------------------------------------------ #
    #  Private helpers                                                     #
    # ------------------------------------------------------------------ #

    def _analyze_strip(
        self,
        trace: np.ndarray,
        chn:   int,
        t_lo:  int,
        t_hi:  int,
    ) -> Optional[I2StripInfo]:
        """
        Find the zero-crossing on a single I2 strip.

        Returns I2StripInfo if a valid bipolar signal is found,
        None otherwise.
        """

        # ---- Step 1: find positive peak within time window --------------
        window = trace[t_lo:t_hi + 1]
        pos_peaks, _ = scipy_find_peaks(
            window,
            height=self.pos_peak_height,
            width=self.pos_peak_width,
        )

        if len(pos_peaks) == 0:
            return None

        # Use the tallest positive peak in the window
        best_pos = pos_peaks[np.argmax(window[pos_peaks])]
        pos_tick = t_lo + int(best_pos)
        pos_adc = float(trace[pos_tick])

        # ---- Step 2: scan forward for zero-crossing ---------------------
        zero_tick = self._find_zero_crossing(trace, pos_tick)
        if zero_tick is None:
            return None

        # ---- Step 3: confirm negative peak after zero-crossing ----------
        neg_tick, neg_adc = self._find_neg_peak(trace, zero_tick)
        if neg_tick is None:
            return None

        return I2StripInfo(
            chn=chn,
            strip=chn + 1,
            pos_peak_tick=pos_tick,
            zero_cross_tick=zero_tick,
            neg_peak_tick=neg_tick,
            pos_peak_adc=round(pos_adc, 2),
            neg_peak_adc=round(neg_adc, 2),
        )

    def _find_zero_crossing(
        self,
        trace:    np.ndarray,
        pos_tick: int,
    ) -> Optional[int]:
        """
        Scan forward from pos_tick until the signal crosses zero.
        Returns the first tick where ADC <= 0, or None if not found
        within a reasonable search window.
        """
        # Search up to 3× the typical peak width beyond the positive peak
        search_end = min(NTT - 1, pos_tick + 3 * 20)
        for t in range(pos_tick + 1, search_end + 1):
            if trace[t] <= 0:
                return t
        return None

    def _find_neg_peak(
        self,
        trace:     np.ndarray,
        zero_tick: int,
    ) -> Tuple[Optional[int], float]:
        """
        Find the negative peak in a short window after the zero-crossing.
        Returns (neg_tick, neg_adc) or (None, 0.0) if not found.
        """
        search_end = min(NTT - 1, zero_tick + 60)
        window = trace[zero_tick:search_end + 1]

        # find_peaks on inverted signal to detect negative peaks
        neg_peaks, _ = scipy_find_peaks(
            -window,
            height=self.neg_peak_height,
        )

        if len(neg_peaks) == 0:
            return None, 0.0

        best_neg = neg_peaks[np.argmin(window[neg_peaks])]
        neg_tick = zero_tick + int(best_neg)
        neg_adc = float(trace[neg_tick])

        return neg_tick, neg_adc
