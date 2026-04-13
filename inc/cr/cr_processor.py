#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cr_processor.py — CRProcessor class.

Responsibilities:
  - Coherent noise removal (trimmed mean, top & bottom)
  - Per-channel baseline subtraction (most_frequent)
  - Optional charge equalization
  - Returns a full 128-channel adc array (NTT x NC)
"""

import numpy as np
from scipy import stats
from typing import Tuple

from inc.settings import NC, NCC, NI1, NTT, output_align, ch_eq_year
from inc.utils.utils import most_frequent


class CRProcessor:
    """
    Processes a single raw event dict into a baseline-subtracted,
    noise-cleaned adc array of shape (NTT, NC).
    """

    # Fraction to trim from both ends of the channel distribution
    # when estimating the coherent baseline.
    TRIM_FRACTION: float = 0.1

    def __init__(
        self,
        coherent_noise_flags: Tuple[bool, bool, bool],
        equalize: bool,
        year: str,
        noisy_channels: list,
    ):
        """
        Parameters
        ----------
        coherent_noise_flags : (b0, b1, b2)
            Enable coherent noise removal per plane
            (collection, induction1, induction2).
        equalize : bool
            Apply charge equalization.
        year : str
            Four-digit year string, e.g. '2022'.
        noisy_channels : list
            Zero-indexed list of channels to zero out when equalizing.
        """
        self.b0, self.b1, self.b2 = coherent_noise_flags
        self.equalize = equalize
        self.year = year
        self.noisy_channels = noisy_channels

    # ------------------------------------------------------------------ #
    #  Public interface                                                    #
    # ------------------------------------------------------------------ #

    def build_adc(self, event: dict, j_evt_nr: str,
                  first_time: bool = True) -> Tuple[np.ndarray, bool]:
        """
        Stage 1 — cheap, runs on every event.
        Baseline subtraction and optional equalization only.
        No coherent noise removal.

        Returns
        -------
        adc : np.ndarray, shape (NTT, NC)
        is_dimension_ok : bool
        """
        return self._build_adc(event, j_evt_nr, first_time)

    def apply_coherent_noise_removal(self, adc: np.ndarray) -> np.ndarray:
        """
        Stage 2 — expensive, should only run on selected events.
        Subtracts the per-tick trimmed-mean baseline from each enabled plane.

        Returns
        -------
        adc : np.ndarray, shape (NTT, NC), modified in place and returned.
        """
        if any((self.b0, self.b1, self.b2)):
            adc = self._remove_coherent_noise(adc)
        return adc

    def process(self, event: dict, j_evt_nr: str,
                first_time: bool = True) -> Tuple[np.ndarray, bool]:
        """
        Convenience method for Step 2: runs both stages in one call
        since all events loaded in Step 2 are already selected.

        Returns
        -------
        adc : np.ndarray, shape (NTT, NC)
        is_dimension_ok : bool
        """
        adc, ok = self.build_adc(event, j_evt_nr, first_time)
        if not ok:
            return adc, False
        adc = self.apply_coherent_noise_removal(adc)
        return adc, True

    # ------------------------------------------------------------------ #
    #  Private helpers                                                     #
    # ------------------------------------------------------------------ #

    def _build_adc(self, event: dict, j_evt_nr: str,
                   first_time: bool) -> Tuple[np.ndarray, bool]:
        """Baseline-subtract all channels and optionally equalize."""
        adc = np.zeros((NTT, NC))

        ch_eq = ch_eq_year(self.year) if self.equalize else None

        for chn in range(NC):
            channel = f'chn{chn}'
            raw = event.get(channel, [])

            if len(raw) != NTT:
                if first_time:
                    print(
                        f'{output_align}!! Event {j_evt_nr}: strip {chn + 1} '
                        f'has dimension {len(raw)} instead of {NTT}.'
                    )
                return adc, False

            baseline = most_frequent(raw)
            adc[:, chn] = np.array(raw, dtype=float) - baseline

            if self.equalize and ch_eq is not None:
                adc[:, chn] = np.round(adc[:, chn] * ch_eq[chn], decimals=1)
                if chn in self.noisy_channels:
                    adc[:, chn] = 0.0

        return adc, True

    def _remove_coherent_noise(self, adc: np.ndarray) -> np.ndarray:
        """
        Subtract the per-tick trimmed-mean baseline from each plane.
        Uses a symmetric trim (top & bottom TRIM_FRACTION) so that
        events without signal are unaffected.
        """
        plane_slices = {
            'C':  (self.b0, slice(0,        NCC)),
            'I1': (self.b1, slice(NCC,       NCC + NI1)),
            'I2': (self.b2, slice(NCC + NI1, NC)),
        }

        for _, (enabled, sl) in plane_slices.items():
            if not enabled:
                continue
            plane_adc = adc[:, sl]          # shape (NTT, n_chns_in_plane)
            baseline = self._trimmed_mean_per_tick(plane_adc)
            adc[:, sl] = plane_adc - baseline[:, np.newaxis]

        return adc

    def _trimmed_mean_per_tick(self, plane: np.ndarray) -> np.ndarray:
        """
        Compute the trimmed mean across channels for each time tick.

        Parameters
        ----------
        plane : np.ndarray, shape (NTT, n_chns)

        Returns
        -------
        baseline : np.ndarray, shape (NTT,)
        """
        return np.array([
            stats.trim_mean(plane[t, :], self.TRIM_FRACTION)
            for t in range(NTT)
        ])
