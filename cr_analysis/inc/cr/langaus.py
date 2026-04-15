#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
langaus.py — Landau⊗Gaussian convolution for PyROOT.

Call declare_langaus(ROOT) once per session before using langaufun in TF1.
The #ifndef guard makes repeated calls safe (e.g. Spyder re-runs).
"""

LANGAUS_SOURCE = """
#ifndef LANGAUFUN_DEFINED
#define LANGAUFUN_DEFINED
Double_t langaufun(Double_t *x, Double_t *par) {
    // Numeric convolution of Landau and Gaussian.
    // par[0] = Width  -- Landau width (xi)
    // par[1] = MP     -- Landau most probable (before convolution)
    // par[2] = Area   -- normalization
    // par[3] = GSigma -- Gaussian sigma (electronics + diffusion)
    Double_t invsq2pi = 0.3989422804014;
    Double_t mpshift  = -0.22278298;
    Double_t mpc  = par[1] - mpshift * par[0];
    Double_t fwhm = 2.355 * par[3];
    Int_t    np   = 100;
    Double_t step = (fwhm > 0) ? 5.0 * par[3] / np : 1.0;
    Double_t sum  = 0.0, xx, fland;
    for (Int_t i = 1; i <= np/2; i++) {
        xx    = x[0] + (i - 0.5) * step;
        fland = TMath::Landau(xx, mpc, par[0]) / par[0];
        sum  += fland * TMath::Gaus(x[0], xx, par[3]);
        xx    = x[0] - (i - 0.5) * step;
        fland = TMath::Landau(xx, mpc, par[0]) / par[0];
        sum  += fland * TMath::Gaus(x[0], xx, par[3]);
    }
    return par[2] * step * sum * invsq2pi / par[3];
}
#endif
"""


def declare_langaus(ROOT) -> None:
    """Declare langaufun in the ROOT interpreter (safe to call multiple times)."""
    ROOT.gInterpreter.Declare(LANGAUS_SOURCE)
