#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cr_analyzer.py — CRAnalyzer class (PyROOT implementation).

Pure CSV-based analysis for Step 2. No JSON files, no reprocessing.
Reads *-CR_events.csv and *-CR_charges.csv and produces:
  - One .root file with all histograms and fits
  - Individual PDF canvases per histogram

ROOT is imported lazily inside run_all() so that importing this module
does not fail on systems where ROOT is not installed or has a version
incompatibility (e.g. macOS ROOT 6.36.x with Python 3.12).
Run Step 2 on lxplus (source setup.sh) for guaranteed ROOT compatibility.
"""

from inc.cr.langaus import declare_langaus as _declare_langaus
import os
import numpy as np
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from inc.settings import NCC, output_align
from inc.find_run_time import find_time_now
from inc.cr.cr_writer import CRWriter, CREventCoords, CRStripCharge


# ------------------------------------------------------------------ #
#  Lazy ROOT loader                                                    #
# ------------------------------------------------------------------ #

def _get_root():
    """
    Import ROOT lazily. Raises a clear RuntimeError if unavailable.
    """
    try:
        import ROOT
        ROOT.gROOT.SetBatch(True)
        ROOT.gErrorIgnoreLevel = ROOT.kWarning
        return ROOT
    except Exception as e:
        raise RuntimeError(
            f"ROOT is not available or failed to load:\n  {e}\n"
            f"Please run Step 2 on lxplus (source setup.sh) where "
            f"ROOT from LCG_109 is known to work."
        )


# ------------------------------------------------------------------ #
#  Landau⊗Gaussian convolution (classic langaus)                      #
# ------------------------------------------------------------------ #


# ------------------------------------------------------------------ #
#  CRAnalyzer                                                          #
# ------------------------------------------------------------------ #

class CRAnalyzer:
    """
    Reads the two CR CSV files and produces ROOT histograms,
    Landau⊗Gaussian fits, and PDF canvases.
    """

    def run_all(
        self,
        csv_path:              str,
        output_folder:         str,
        delta_d_c:             float,
        dataset_name:          str,
        norm_charge_bin_width: float = 1.0,
        delta_l_bin_width:     float = 5.0,
        track_pitch_bin_width: float = 0.02,
    ) -> None:
        """
        Run the full Step 2 analysis pipeline.

        Parameters
        ----------
        csv_path              : path to *-CR_events.csv
        output_folder         : summary output directory
        delta_d_c             : collection strip pitch in mm
        dataset_name          : used in titles and filenames
        norm_charge_bin_width : bin width for dQ/dx histograms (ADC·tt·mm⁻¹)
        delta_l_bin_width     : bin width for ΔL histograms (mm)
        track_pitch_bin_width : bin width for pitch histograms (mm)
        """
        ROOT = _get_root()
        _declare_langaus(ROOT)

        Path(output_folder).mkdir(parents=True, exist_ok=True)

        writer = CRWriter(csv_path)
        events = writer.read_events()
        charges = writer.read_charges()

        n_evts = len(events)
        if n_evts == 0:
            print(f"{output_align}!! No events found in {csv_path}")
            return

        print(f"{output_align}  Loaded {n_evts} events and "
              f"{len(charges)} strip-charge rows.")

        root_path = os.path.join(
            output_folder, f"{dataset_name}-CR_analysis.root")
        root_file = ROOT.TFile(root_path, "RECREATE")

        self._fill_delta_l(
            ROOT, events, root_file, output_folder, dataset_name,
            delta_l_bin_width, track_pitch_bin_width)

        self._fill_norm_charges(
            ROOT, writer, charges, root_file, output_folder, dataset_name,
            norm_charge_bin_width)

        root_file.Close()
        print(f" [{find_time_now()}] : {root_path} saved")

    # ------------------------------------------------------------------ #
    #  ΔL and track pitch histograms                                       #
    # ------------------------------------------------------------------ #

    def _fill_delta_l(
        self,
        ROOT,
        events:                List[CREventCoords],
        root_file,
        output_folder:         str,
        dataset_name:          str,
        delta_l_bin_width:     float,
        track_pitch_bin_width: float,
    ) -> None:

        n_evts = len(events)

        for version in ('v1', 'v2'):
            delta_l = [getattr(e, f'delta_l_{version}') for e in events]
            pitch = [getattr(e, f'track_pitch_length_{version}')
                     for e in events]

            for data, bw, xtitle, fname in (
                (delta_l, delta_l_bin_width,
                 '#DeltaL [mm]',
                 f'delta_l_{version}'),
                (pitch, track_pitch_bin_width,
                 '#Deltaz [mm]',
                 f'track_pitch_{version}'),
            ):
                lo, hi = self._auto_range(data, bw)
                n_bins = max(1, int(round((hi - lo) / bw)))
                title = (
                    f"{dataset_name} - {'Track length' if 'delta_l' in fname else 'Track pitch length'} ({version});{xtitle};Events")

                h = ROOT.TH1F(f"h_{fname}", title, n_bins, lo, hi)
                h.SetLineColor(ROOT.kBlue + 1)
                h.SetLineWidth(1)
                for v in data:
                    h.Fill(v)

                ROOT.gStyle.SetOptStat("nemr")
                root_file.cd()
                h.Write()
                self._save_canvas(ROOT, h, output_folder,
                                  f"{dataset_name}_{fname}")

    # ------------------------------------------------------------------ #
    #  dQ/dx histograms + Landau⊗Gaussian fits                            #
    # ------------------------------------------------------------------ #

    def _fill_norm_charges(
        self,
        ROOT,
        writer,
        charges:       List[CRStripCharge],
        root_file,
        output_folder: str,
        dataset_name:  str,
        bin_width:     float,
    ) -> None:

        by_strip_v1: Dict[int, List[float]] = defaultdict(list)
        by_strip_v2: Dict[int, List[float]] = defaultdict(list)

        for c in charges:
            if 1 <= c.strip <= NCC:
                by_strip_v1[c.strip].append(c.normalized_charge_v1_adc_tt)
                by_strip_v2[c.strip].append(c.normalized_charge_v2_adc_tt)

        if not by_strip_v1:
            print(f"{output_align}!! No charge data for collection strips.")
            return

        all_vals = [v for d in (by_strip_v1, by_strip_v2)
                    for vals in d.values() for v in vals]
        x_lo, x_hi = self._auto_range(all_vals, bin_width)
        n_bins = max(1, int(round((x_hi - x_lo) / bin_width)))

        eq_factors = []  # equalization factors per version
        eq_map = {}  # version -> eq dict

        for version, by_strip in (('v1', by_strip_v1), ('v2', by_strip_v2)):
            mpv_data = []  # list of (strip, mpv, mpv_err)

            for strip in range(1, NCC + 1):
                data = by_strip.get(strip, [])
                str_s = str(strip).zfill(2)
                hname = f"h_norm_charge_{version}_strip{str_s}"
                title = (f"{dataset_name} - Strip {strip} - dQ/dx ({version})"
                         ";dQ/dx [ADC #scale[0.6]{#bullet} tt #scale[0.6]{#bullet} mm^{-1 }];Entries")

                h = ROOT.TH1F(hname, title, n_bins, x_lo, x_hi)
                h.SetLineColor(ROOT.kBlue + 1)
                h.SetLineWidth(1)
                for v in data:
                    h.Fill(v)

                fit_func = self._fit_langaus(ROOT, h, strip, version)

                # Collect MPV and its uncertainty (MP parameter error as proxy)
                if fit_func:
                    mpv = fit_func.GetMaximumX()
                    mpv_err = fit_func.GetParError(1)  # MP parameter error
                    mpv_data.append((strip, mpv, mpv_err))

                root_file.cd()
                h.Write()
                if fit_func:
                    fit_func.Write(
                        f"fit_norm_charge_{version}_strip{str_s}")

                self._save_canvas_with_fit(
                    ROOT, h, fit_func, output_folder,
                    f"{dataset_name}_norm_charge_{version}_Strip{str_s}",
                    strip, version)

            # Scatter plot of MPV vs strip number; returns eq factors
            if mpv_data:
                eq = self._make_mpv_scatter(
                    ROOT, mpv_data, root_file, output_folder,
                    dataset_name, version, suffix='')
                eq_factors.append({
                    'version':     version,
                    'mean_lo':     eq['mean_lo'],
                    'mean_lo_err': eq['mean_lo_err'],
                    'mean_hi':     eq['mean_hi'],
                    'mean_hi_err': eq['mean_hi_err'],
                    'ratio':       eq['ratio'],
                })
                eq_map[version] = eq

        # Write equalization CSV
        if eq_factors:
            writer.write_equalization(eq_factors)

        # Write equalized charges CSV and produce equalized plots
        if eq_map and charges:
            # eq factor = mean_lo / mean_hi  (scale strips 25-48 UP)
            scale_v1 = (eq_map['v1']['mean_lo'] / eq_map['v1']['mean_hi']
                        if eq_map.get('v1', {}).get('mean_hi', 0) != 0 else 1.0)
            scale_v2 = (eq_map['v2']['mean_lo'] / eq_map['v2']['mean_hi']
                        if eq_map.get('v2', {}).get('mean_hi', 0) != 0 else 1.0)
            writer.write_equalized_charges(charges, scale_v1, scale_v2)

            # Build equalized charge lists for plotting
            by_strip_v1_eq = defaultdict(list)
            by_strip_v2_eq = defaultdict(list)
            for c in charges:
                s = c.strip
                fv1 = scale_v1 if s >= 25 else 1.0
                fv2 = scale_v2 if s >= 25 else 1.0
                by_strip_v1_eq[s].append(c.normalized_charge_v1_adc_tt * fv1)
                by_strip_v2_eq[s].append(c.normalized_charge_v2_adc_tt * fv2)

            # Equalized charge plots + MPV scatter
            all_eq = [v for d in (by_strip_v1_eq, by_strip_v2_eq)
                      for vals in d.values() for v in vals]
            xlo_eq, xhi_eq = self._auto_range(all_eq, bin_width)
            nb_eq = max(1, int(round((xhi_eq - xlo_eq) / bin_width)))

            for version, by_strip_eq in (('v1', by_strip_v1_eq),
                                         ('v2', by_strip_v2_eq)):
                mpv_data_eq = []
                for strip in range(1, NCC + 1):
                    data = by_strip_eq.get(strip, [])
                    str_s = str(strip).zfill(2)
                    hname = f"h_norm_charge_{version}_eq_strip{str_s}"
                    title = (f"{dataset_name} - Strip {strip}"
                             f" - dQ/dx equalized ({version})"
                             ";dQ/dx [ADC #scale[0.6]{#bullet}"
                             " tt #scale[0.6]{#bullet} mm^{-1 }];Entries")
                    h = ROOT.TH1F(hname, title, nb_eq, xlo_eq, xhi_eq)
                    h.SetLineColor(ROOT.kBlue + 1)
                    h.SetLineWidth(1)
                    for v in data:
                        h.Fill(v)
                    fit_func = self._fit_langaus(ROOT, h, strip, version)
                    if fit_func:
                        mpv = fit_func.GetMaximumX()
                        mpv_err = fit_func.GetParError(1)
                        mpv_data_eq.append((strip, mpv, mpv_err))
                    root_file.cd()
                    h.Write()
                    if fit_func:
                        fit_func.Write(
                            f"fit_norm_charge_{version}_eq_strip{str_s}")
                    self._save_canvas_with_fit(
                        ROOT, h, fit_func, output_folder,
                        f"{dataset_name}_norm_charge_{
                            version}_eq_Strip{str_s}",
                        strip, version)
                if mpv_data_eq:
                    self._make_mpv_scatter(
                        ROOT, mpv_data_eq, root_file, output_folder,
                        dataset_name, version, suffix='_eq')

    # ------------------------------------------------------------------ #
    #  Landau⊗Gaussian fit                                                 #
    # ------------------------------------------------------------------ #

    def _fit_langaus(
        self,
        ROOT,
        h:       object,
        strip:   int,
        version: str,
    ) -> Optional[object]:
        """
        Fit histogram with Landau⊗Gaussian convolution.
        Fit range: contiguous region above 5% of peak height.
        Returns TF1 or None if fit fails / too few entries.
        """
        if h.GetEntries() < 10:
            return None

        peak_bin = h.GetMaximumBin()
        peak_val = h.GetMaximum()
        threshold = 0.05 * peak_val

        x_lo = h.GetXaxis().GetBinLowEdge(1)
        x_hi = h.GetXaxis().GetBinUpEdge(h.GetNbinsX())

        for b in range(peak_bin, 0, -1):
            if h.GetBinContent(b) < threshold:
                x_lo = h.GetXaxis().GetBinLowEdge(b + 1)
                break
        for b in range(peak_bin, h.GetNbinsX() + 1):
            if h.GetBinContent(b) < threshold:
                x_hi = h.GetXaxis().GetBinUpEdge(b - 1)
                break

        fname = f"langaus_{version}_s{strip}"
        f = ROOT.TF1(fname, ROOT.langaufun, x_lo, x_hi, 4)
        f.SetParNames("Width", "MP", "Area", "GSigma")

        mp_est = h.GetXaxis().GetBinCenter(peak_bin)
        width_est = max(1.0, h.GetRMS() * 0.2)
        sigma_est = max(1.0, h.GetRMS() * 0.1)
        area_est = h.GetEntries() * h.GetBinWidth(1)

        f.SetParameters(width_est, mp_est, area_est, sigma_est)
        f.SetParLimits(0, 0.01, h.GetRMS())
        f.SetParLimits(1, x_lo, x_hi)
        f.SetParLimits(2, 0, area_est * 10)
        f.SetParLimits(3, 0.01, h.GetRMS())
        f.SetLineColor(ROOT.kRed + 1)
        f.SetLineWidth(2)

        result = h.Fit(fname, "RQSN")
        if result and result.IsValid():
            h.GetListOfFunctions().Add(f)
            return f

        print(f"{output_align}  Fit failed: {version} strip {strip}")
        return None

    # ------------------------------------------------------------------ #
    #  Canvas: ΔL and pitch                                                #
    # ------------------------------------------------------------------ #

    def _save_canvas(
        self,
        ROOT,
        h,
        output_folder: str,
        fname:         str,
    ) -> None:
        ROOT.gStyle.SetOptStat("nemr")
        ROOT.gStyle.SetTitleFont(42, "XYZ")
        ROOT.gStyle.SetLabelFont(42, "XYZ")
        ROOT.gStyle.SetTitleFont(42, "t")

        c = ROOT.TCanvas(f"c_{fname}", fname, 1200, 700)
        c.SetLeftMargin(0.12)
        c.SetBottomMargin(0.12)
        c.SetTopMargin(0.10)
        c.SetRightMargin(0.05)

        h.SetStats(1)
        h.GetXaxis().SetTitleSize(0.05)
        h.GetYaxis().SetTitleSize(0.05)
        h.GetXaxis().SetLabelSize(0.04)
        h.GetYaxis().SetLabelSize(0.04)
        h.GetXaxis().SetTitleOffset(1.0)
        h.GetYaxis().SetTitleOffset(1.1)
        h.Draw("HIST")
        c.Update()

        # Move stat box to top right, no overlap
        st = h.FindObject("stats")
        if st:
            st.SetX1NDC(0.72)
            st.SetX2NDC(0.94)
            st.SetY1NDC(0.72)
            st.SetY2NDC(0.92)
            st.Draw()

        c.Update()
        out = os.path.join(output_folder, f"{fname}.pdf")
        c.SaveAs(out)
        print(f" [{find_time_now()}] : {out} saved")
        c.Close()

    # ------------------------------------------------------------------ #
    #  Canvas: dQ/dx with Landau⊗Gaussian fit                             #
    # ------------------------------------------------------------------ #

    def _save_canvas_with_fit(
        self,
        ROOT,
        h,
        fit_func,
        output_folder: str,
        fname:         str,
        strip:         int,
        version:       str,
    ) -> None:
        ROOT.gStyle.SetOptStat("nemr")
        ROOT.gStyle.SetOptFit(111)    # chi2/ndf, params (no prob)
        ROOT.gStyle.SetTitleFont(42, "XYZ")
        ROOT.gStyle.SetLabelFont(42, "XYZ")
        ROOT.gStyle.SetTitleFont(42, "t")
        ROOT.gStyle.SetStatFont(42)
        ROOT.gStyle.SetFitFormat("6.3g")
        ROOT.gStyle.SetStatFormat("6.4g")

        c = ROOT.TCanvas(f"c_{fname}", fname, 1200, 700)
        c.SetLeftMargin(0.12)
        c.SetBottomMargin(0.12)
        c.SetTopMargin(0.10)
        c.SetRightMargin(0.05)

        h.SetStats(1)
        h.GetXaxis().SetTitleSize(0.05)
        h.GetYaxis().SetTitleSize(0.05)
        h.GetXaxis().SetLabelSize(0.04)
        h.GetYaxis().SetLabelSize(0.04)
        h.GetXaxis().SetTitleOffset(1.0)
        h.GetYaxis().SetTitleOffset(1.1)
        h.Draw("HIST")

        primitives = []  # keep references alive

        if fit_func:
            fit_func.Draw("SAME")

            mpv = fit_func.GetMaximumX()
            fit_x_lo = fit_func.GetXmin()
            fit_x_hi = fit_func.GetXmax()
            y_max = h.GetMaximum()
            x_axis_lo = h.GetXaxis().GetXmin()
            x_axis_hi = h.GetXaxis().GetXmax()

            c.Update()

            # Stat+fit box: top right, tall enough for all entries
            st = h.FindObject("stats")
            if st:
                st.SetX1NDC(0.60)
                st.SetX2NDC(0.94)
                st.SetY1NDC(0.45)
                st.SetY2NDC(0.92)
                st.SetTextFont(42)
                st.SetTextSize(0.036)
                st.Draw()
                primitives.append(st)

            # MPV in separate TPaveText, top left
            mpv_box = ROOT.TPaveText(0.94, 0.32, 0.6, 0.42, "NDC")
            mpv_box.SetFillColor(0)
            mpv_box.SetFillStyle(1001)
            mpv_box.SetBorderSize(1)
            mpv_box.SetTextFont(42)
            mpv_box.SetTextSize(0.038)
            # mpv_box.AddText(f"MPV = {mpv:.1f} ADC tt mm^{{-1}}")
            mpv_box.AddText(
                f"MPV = {mpv:.1f} [ADC #scale[0.6]{{#bullet}} tt #scale[0.6]{{#bullet}} mm^{{ -1 }}]")

            mpv_box.Draw()
            primitives.append(mpv_box)

        c.Update()
        out = os.path.join(output_folder, f"{fname}.pdf")
        c.SaveAs(out)
        print(f" [{find_time_now()}] : {out} saved")
        c.Close()

    # ------------------------------------------------------------------ #
    #  MPV scatter plot vs strip number                                    #
    # ------------------------------------------------------------------ #

    def _make_mpv_scatter(
        self,
        ROOT,
        mpv_data:      list,
        root_file,
        output_folder: str,
        dataset_name:  str,
        version:       str,
        suffix:        str = '',
    ) -> dict:
        """
        Scatter plot of langaus MPV vs strip number (1-48).
        Unweighted means and SEM computed for strips 1-24 and 25-48.
        Returns dict with mean_lo, mean_lo_err, mean_hi, mean_hi_err, ratio.
        suffix: '' for raw, '_eq' for equalized.
        """
        n = len(mpv_data)
        strips = np.array([d[0] for d in mpv_data], dtype=float)
        mpvs = np.array([d[1] for d in mpv_data], dtype=float)
        errs = np.array([d[2] for d in mpv_data], dtype=float)

        gname = f"g_mpv_{version}{suffix}"
        g = ROOT.TGraphErrors(n,
                              strips, mpvs,
                              np.zeros(n, dtype=float), errs)
        g.SetName(gname)
        g.SetTitle(
            f"{dataset_name} - {"Equalized" if suffix else "Raw"} dQ/dx MPV vs Strip ({
                version})"
            ";Strip number;MPV [ADC #scale[0.6]{#bullet} tt #scale[0.6]{#bullet} mm^{-1 }]")
        g.SetMarkerStyle(20)
        g.SetMarkerSize(0.9)
        g.SetMarkerColor(ROOT.kBlue + 1)
        g.SetLineColor(ROOT.kBlue + 1)

        # Unweighted mean and standard error of the mean for each half
        def unweighted_mean(points):
            vals = np.array([d[1] for d in points])
            mean = float(np.mean(vals))
            err = float(np.std(vals, ddof=1) / np.sqrt(len(vals)))
            return mean, err

        pts_lo = [d for d in mpv_data if 1 <= d[0] <= 24]
        pts_hi = [d for d in mpv_data if 25 <= d[0] <= 48]

        c0_lo, c0_lo_err = unweighted_mean(pts_lo) if pts_lo else (0.0, 0.0)
        c0_hi, c0_hi_err = unweighted_mean(pts_hi) if pts_hi else (0.0, 0.0)
        ratio = c0_hi / c0_lo if c0_lo != 0 else 0.0

        # Horizontal lines at weighted means
        f_lo = ROOT.TLine(1,  c0_lo, 24, c0_lo)
        f_lo.SetLineColor(ROOT.kRed + 1)
        f_lo.SetLineWidth(2)

        f_hi = ROOT.TLine(25, c0_hi, 48, c0_hi)
        f_hi.SetLineColor(ROOT.kGreen + 2)
        f_hi.SetLineWidth(2)

        # ---- canvas ----
        cname = f"c_mpv_{version}{suffix}"
        c = ROOT.TCanvas(cname, cname, 1200, 700)
        c.SetLeftMargin(0.12)
        c.SetBottomMargin(0.12)
        c.SetTopMargin(0.10)
        c.SetRightMargin(0.05)

        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetOptFit(0)
        ROOT.gStyle.SetTitleFont(42, "XYZ")
        ROOT.gStyle.SetLabelFont(42, "XYZ")
        ROOT.gStyle.SetTitleFont(42, "t")

        g.GetXaxis().SetRangeUser(0, 49)
        g.GetXaxis().SetTitleSize(0.05)
        g.GetYaxis().SetTitleSize(0.05)
        g.GetXaxis().SetLabelSize(0.04)
        g.GetYaxis().SetLabelSize(0.04)
        g.GetXaxis().SetTitleOffset(1.0)
        g.GetYaxis().SetTitleOffset(1.1)
        g.Draw("AP")

        f_lo.Draw("SAME")
        f_hi.Draw("SAME")

        # Vertical separator at strip 24.5
        y_lo = g.GetYaxis().GetXmin() if hasattr(
            g.GetYaxis(), 'GetXmin') else mpvs.min() * 0.9
        y_hi = mpvs.max() * 1.05
        sep = ROOT.TLine(24.5, y_lo, 24.5, y_hi)
        sep.SetLineColor(ROOT.kGray + 1)
        sep.SetLineStyle(2)
        sep.SetLineWidth(1)
        sep.Draw()

        # Results box — bottom right for equalized, top right for raw
        if suffix == '_eq':
            box = ROOT.TPaveText(0.4, 0.2, 0.7, 0.3, "NDC")
        else:
            box = ROOT.TPaveText(0.55, 0.68, 0.94, 0.88, "NDC")
        box.SetFillColor(0)
        box.SetFillStyle(1001)
        box.SetBorderSize(1)
        box.SetTextFont(42)
        box.SetTextSize(0.033)
        box.SetTextAlign(12)
        box.AddText(f"Strips  1-24: <MPV> = {c0_lo:.1f} #pm {c0_lo_err:.1f}")
        box.AddText(f"Strips 25-48: <MPV> = {c0_hi:.1f} #pm {c0_hi_err:.1f}")
        if suffix != '_eq':
            box.AddText(f"Ratio (25-48)/(1-24) = {ratio:.3f}")
        box.Draw()

        c.Update()
        out = os.path.join(output_folder,
                           f"{dataset_name}_MPV_scatter_{version}{suffix}.pdf")
        c.SaveAs(out)
        print(f" [{find_time_now()}] : {out} saved")

        root_file.cd()
        g.Write()
        # Note: TLines are not persistable in ROOT files
        c.Close()

        return {
            'mean_lo':     c0_lo,
            'mean_lo_err': c0_lo_err,
            'mean_hi':     c0_hi,
            'mean_hi_err': c0_hi_err,
            'ratio':       ratio,
        }

    # ------------------------------------------------------------------ #
    #  Utilities                                                           #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _auto_range(
        data:      list,
        bin_width: float = None,
    ) -> Tuple[float, float]:
        """Return (0.9·min, 1.1·max), snapped to bin edges if bin_width given."""
        lo = 0.9 * min(data)
        hi = 1.1 * max(data)
        if bin_width is not None:
            lo = np.floor(lo / bin_width) * bin_width
            hi = np.ceil(hi / bin_width) * bin_width
        return float(lo), float(hi)
