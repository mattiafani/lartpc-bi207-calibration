#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cr_step3_analyzer.py — CRStep3Analyzer class (PyROOT implementation).

Reads *-CR_charges_equalized.csv and produces Step 3 analysis plots.

ROOT is imported lazily — run on lxplus for guaranteed compatibility.
"""

import os
import csv
import numpy as np
from pathlib import Path
from typing import List, Tuple

from inc.settings import NCC, output_align
from inc.find_run_time import find_time_now
from inc.cr.langaus import declare_langaus as _declare_langaus


# ------------------------------------------------------------------ #
#  Lazy ROOT loader                                                    #
# ------------------------------------------------------------------ #

def _get_root():
    try:
        import ROOT
        ROOT.gROOT.SetBatch(True)
        ROOT.gErrorIgnoreLevel = ROOT.kWarning
        return ROOT
    except Exception as e:
        raise RuntimeError(
            f"ROOT is not available or failed to load:\n  {e}\n"
            f"Please run Step 3 on lxplus (source setup.sh)."
        )


# ------------------------------------------------------------------ #
#  CRStep3Analyzer                                                     #
# ------------------------------------------------------------------ #

class CRStep3Analyzer:
    """
    Reads *-CR_charges_equalized.csv and produces Step 3 analysis plots.
    """

    def run_all(
        self,
        equalized_charges_path:  str,
        output_folder:           str,
        dataset_name:            str,
        dqdx_vs_time_x_bins:     int = 200,
        dqdx_vs_time_y_bins:     int = 200,
        dqdx_vs_time_fit_x_lo:   int = 0,
        dqdx_vs_time_fit_x_hi:   int = 0,
        dqdx_fit_range_scan:     bool = False,
        dqdx_fit_scan_n_steps:   int = 20,
        dqdx_fit_scan_width_min: int = 200,
        dqdx_fit_scan_width_max: int = 600,
        dqdx_fit_scan_stable_thr: float = 5.0,
        dqdx_slice_bin_width:    int = 32,
        dqdx_slice_fit_exclude_edges: int = 1,
    ) -> None:
        """
        Run the full Step 3 analysis pipeline.

        Parameters
        ----------
        equalized_charges_path : path to *-CR_charges_equalized.csv
        output_folder          : Step 3 output directory
        dataset_name           : used in titles and filenames
        dqdx_vs_time_x_bins    : bins on peak time tick axis
        dqdx_vs_time_y_bins    : bins on dQ/dx axis
        """
        ROOT = _get_root()
        _declare_langaus(ROOT)
        Path(output_folder).mkdir(parents=True, exist_ok=True)

        rows = self._read_equalized_charges(equalized_charges_path)
        if not rows:
            print(f"{output_align}!! No data in {equalized_charges_path}")
            return

        print(f"{output_align}  Loaded {len(rows)} equalized charge rows.")

        root_path = os.path.join(
            output_folder, f"{dataset_name}-CR_e_lifetime.root")
        root_file = ROOT.TFile(root_path, "RECREATE")

        mpv_slice_pts = self._plot_dqdx_langaus_slices(
            ROOT, rows, root_file, output_folder, dataset_name,
            dqdx_slice_bin_width, dqdx_slice_fit_exclude_edges)

        self._plot_dqdx_vs_time(
            ROOT, rows, root_file, output_folder, dataset_name,
            dqdx_vs_time_x_bins, dqdx_vs_time_y_bins,
            dqdx_vs_time_fit_x_lo, dqdx_vs_time_fit_x_hi,
            mpv_slice_pts, dqdx_slice_bin_width)

        if dqdx_fit_range_scan:
            self._scan_fit_ranges(
                ROOT, rows, root_file, output_folder, dataset_name,
                dqdx_vs_time_x_bins, dqdx_vs_time_y_bins,
                dqdx_fit_scan_n_steps,
                dqdx_fit_scan_width_min,
                dqdx_fit_scan_width_max,
                dqdx_fit_scan_stable_thr)

        root_file.Close()
        print(f" [{find_time_now()}] : {root_path} saved")

    # ------------------------------------------------------------------ #
    #  CSV reader                                                          #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _read_equalized_charges(path: str) -> List[dict]:
        rows = []
        with open(path, 'r', newline='') as f:
            for row in csv.DictReader(f):
                rows.append({
                    'strip':                          int(row['strip']),
                    'peak_time_tick':                 int(row['peak_time_tick']),
                    'normalized_charge_v1_eq_adc_tt': float(row['normalized_charge_v1_eq_adc_tt']),
                    'normalized_charge_v2_eq_adc_tt': float(row['normalized_charge_v2_eq_adc_tt']),
                })
        return rows

    # ------------------------------------------------------------------ #
    #  2D histogram: equalized dQ/dx vs peak time tick                    #
    # ------------------------------------------------------------------ #

    def _plot_dqdx_vs_time(
        self,
        ROOT,
        rows:          List[dict],
        root_file,
        output_folder: str,
        dataset_name:  str,
        x_bins:        int,
        y_bins:        int,
        fit_x_lo:      int = 0,
        fit_x_hi:      int = 0,
        mpv_slice_pts: dict = None,
        slice_width:   int = 64,
    ) -> None:

        times = np.array([r['peak_time_tick'] for r in rows], dtype=float)
        dqdx_v1 = np.array([r['normalized_charge_v1_eq_adc_tt']
                           for r in rows], dtype=float)
        dqdx_v2 = np.array([r['normalized_charge_v2_eq_adc_tt']
                           for r in rows], dtype=float)

        x_lo = float(np.floor(times.min() * 0.95))
        x_hi = float(np.ceil(times.max() * 1.05))

        # Common y range across both versions for direct comparability
        y_lo = float(min(dqdx_v1.min(), dqdx_v2.min()) * 0.9)
        y_hi = float(max(dqdx_v1.max(), dqdx_v2.max()) * 1.1)

        # Fit range: use config values if set, otherwise fall back to data range
        flo = float(fit_x_lo) if fit_x_lo > 0 else x_lo
        fhi = float(fit_x_hi) if fit_x_hi > 0 else x_hi

        for version, dqdx in (('v1', dqdx_v1), ('v2', dqdx_v2)):
            hname = f"h2_dqdx_eq_vs_time_{version}"
            title = (f"{dataset_name} - Equalized dQ/dx vs Peak Time ({version})"
                     ";Peak time [tt]"
                     ";dQ/dx [ADC #scale[0.6]{#bullet} tt"
                     " #scale[0.6]{#bullet} mm^{-1 }]")

            h = ROOT.TH2F(hname, title,
                          x_bins, x_lo, x_hi,
                          y_bins, y_lo, y_hi)
            h.SetStats(0)
            h.GetZaxis().SetTitle("Entries")

            for t, q in zip(times, dqdx):
                h.Fill(t, q)

            root_file.cd()
            h.Write()

            # Build TGraphErrors from langaus MPV slice points
            g_mpv_overlay = None
            if mpv_slice_pts and version in mpv_slice_pts:
                pts = mpv_slice_pts[version]
                n_p = len(pts)
                if n_p > 0:
                    half_w = slice_width / 2.0
                    g_mpv_overlay = ROOT.TGraphErrors(n_p)
                    g_mpv_overlay.SetName(f"g_mpv_overlay_{version}")
                    for i, (tc, mpv, mpv_err) in enumerate(pts):
                        g_mpv_overlay.SetPoint(i, float(tc), float(mpv))
                        g_mpv_overlay.SetPointError(i, half_w, float(mpv_err))
                    g_mpv_overlay.SetMarkerStyle(20)
                    g_mpv_overlay.SetMarkerSize(0.8)
                    g_mpv_overlay.SetMarkerColor(ROOT.kBlack)
                    g_mpv_overlay.SetLineColor(ROOT.kBlack)

            self._save_canvas_2d(
                ROOT, h, g_mpv_overlay,
                output_folder,
                f"{dataset_name}_dqdx_eq_vs_time_{version}")

            # Direct pol1 fit over full range
            fit_direct = ROOT.TF1(f"pol1_direct_{version}", "pol1", x_lo, x_hi)
            fit_direct.SetParameter(0, float(np.mean(dqdx)))
            fit_direct.SetParameter(1, 0.0)
            fit_direct.SetLineColor(ROOT.kRed + 1)
            fit_direct.SetLineWidth(2)
            h.Fit(fit_direct, "R")

            slope_d = fit_direct.GetParameter(1)
            slope_d_err = fit_direct.GetParError(1)
            intercept_d = fit_direct.GetParameter(0)
            intercept_d_err = fit_direct.GetParError(0)
            if abs(slope_d) > 0:
                tau_tt_d = abs(intercept_d / slope_d)
                tau_ms_d = tau_tt_d * 0.5 / 1000.0
                rel_err_d = ((intercept_d_err / abs(intercept_d))**2 +
                             (slope_d_err / abs(slope_d))**2) ** 0.5
                tau_ms_d_err = tau_ms_d * rel_err_d
            else:
                tau_ms_d = tau_ms_d_err = 0.0

            root_file.cd()
            fit_direct.Write(f"fit_direct_{version}")

            self._save_canvas_2d(
                ROOT, h, None,
                output_folder,
                f"{dataset_name}_dqdx_eq_vs_time_{version}_direct",
                fit_params={
                    'slope':         slope_d,
                    'slope_err':     slope_d_err,
                    'intercept':     intercept_d,
                    'intercept_err': intercept_d_err,
                    'tau_ms':        tau_ms_d,
                    'tau_ms_err':    tau_ms_d_err,
                    'chi2':          fit_direct.GetChisquare(),
                    'ndf':           fit_direct.GetNDF(),
                })

    # ------------------------------------------------------------------ #
    #  Langaus slices: MPV per drift-time bin -> pol1 fit -> tau          #
    # ------------------------------------------------------------------ #

    def _plot_dqdx_langaus_slices(
        self,
        ROOT,
        rows:          List[dict],
        root_file,
        output_folder: str,
        dataset_name:  str,
        slice_width:   int = 32,
        exclude_edges: int = 1,
    ) -> None:
        """
        Divide the drift axis into slices of `slice_width` ticks.
        For each slice, fit the dQ/dx distribution with langaus and
        extract the MPV via GetMaximumX(). Then fit MPV vs slice center
        with pol1 to extract the electron lifetime.

        Saves:
          - one PDF per slice per version (langaus fit)
          - one scatter + pol1 PDF per version (MPV vs time)
        """
        from inc.settings import NTT

        slices_dir = os.path.join(output_folder, 'langaus_slices')
        Path(slices_dir).mkdir(parents=True, exist_ok=True)

        times = np.array([r['peak_time_tick'] for r in rows], dtype=float)
        dqdx_v1 = np.array([r['normalized_charge_v1_eq_adc_tt']
                           for r in rows], dtype=float)
        dqdx_v2 = np.array([r['normalized_charge_v2_eq_adc_tt']
                           for r in rows], dtype=float)

        # Slice boundaries
        t_min = 0
        t_max = NTT
        edges = list(range(t_min, t_max, slice_width))
        if edges[-1] < t_max:
            edges.append(t_max)
        n_slices = len(edges) - 1

        # Common dQ/dx range for 1D histograms
        dqdx_all = np.concatenate([dqdx_v1, dqdx_v2])
        q_lo = float(np.percentile(dqdx_all, 1) * 0.9)
        q_hi = float(np.percentile(dqdx_all, 99) * 1.1)
        n_bins_q = 100

        mpv_results = {}  # {version: [(t_ctr, mpv, mpv_err), ...]}

        for version, dqdx in (('v1', dqdx_v1), ('v2', dqdx_v2)):
            mpv_pts = []  # list of (t_center, mpv, mpv_err)

            for si in range(n_slices):
                t_lo_s = edges[si]
                t_hi_s = edges[si + 1]
                t_ctr = (t_lo_s + t_hi_s) / 2.0
                mask = (times >= t_lo_s) & (times < t_hi_s)
                vals = dqdx[mask]

                if len(vals) < 20:
                    continue

                str_s = f"{t_lo_s:03d}_{t_hi_s:03d}"
                hname = f"h_slice_{version}_{str_s}"
                title = (f"{dataset_name} - dQ/dx ({version})"
                         f" t=[{t_lo_s},{t_hi_s}) tt"
                         f";dQ/dx [ADC #scale[0.6]{{#bullet}}"
                         f" tt #scale[0.6]{{#bullet}} mm^{{-1 }}];Entries")

                h = ROOT.TH1F(hname, title, n_bins_q, q_lo, q_hi)
                h.SetLineColor(ROOT.kBlue + 1)
                h.SetLineWidth(1)
                for v in vals:
                    h.Fill(v)

                # Langaus fit
                peak_bin = h.GetMaximumBin()
                peak_val = h.GetMaximum()
                threshold = 0.05 * peak_val
                x_lo_f = h.GetXaxis().GetBinLowEdge(1)
                x_hi_f = h.GetXaxis().GetBinUpEdge(h.GetNbinsX())
                for b in range(peak_bin, 0, -1):
                    if h.GetBinContent(b) < threshold:
                        x_lo_f = h.GetXaxis().GetBinLowEdge(b + 1)
                        break
                for b in range(peak_bin, h.GetNbinsX() + 1):
                    if h.GetBinContent(b) < threshold:
                        x_hi_f = h.GetXaxis().GetBinUpEdge(b - 1)
                        break

                fname_f = f"langaus_slice_{version}_{str_s}"
                fit_func = ROOT.TF1(fname_f, ROOT.langaufun, x_lo_f, x_hi_f, 4)
                fit_func.SetParNames("Width", "MP", "Area", "GSigma")
                mp_est = h.GetXaxis().GetBinCenter(peak_bin)
                fit_func.SetParameters(
                    max(1.0, h.GetRMS() * 0.2),
                    mp_est,
                    h.GetEntries() * h.GetBinWidth(1),
                    max(1.0, h.GetRMS() * 0.1))
                fit_func.SetLineColor(ROOT.kRed + 1)
                fit_func.SetLineWidth(2)

                result = h.Fit(fname_f, "RQSN")
                if result and result.IsValid():
                    h.GetListOfFunctions().Add(fit_func)
                    mpv = fit_func.GetMaximumX()
                    mpv_err = fit_func.GetParError(1)
                    mpv_pts.append((t_ctr, mpv, mpv_err))
                else:
                    print(f"{output_align}  Slice fit failed: {
                          version} t=[{t_lo_s},{t_hi_s})")

                # Save slice canvas
                ROOT.gStyle.SetOptStat("nemr")
                ROOT.gStyle.SetOptFit(111)
                ROOT.gStyle.SetTitleFont(42, "XYZ")
                ROOT.gStyle.SetLabelFont(42, "XYZ")
                ROOT.gStyle.SetTitleFont(42, "t")
                ROOT.gStyle.SetStatFont(42)

                cs = ROOT.TCanvas(f"c_{hname}", hname, 1200, 700)
                cs.SetLeftMargin(0.12)
                cs.SetBottomMargin(0.12)
                cs.SetTopMargin(0.10)
                cs.SetRightMargin(0.05)
                h.SetStats(1)
                h.GetXaxis().SetTitleSize(0.05)
                h.GetYaxis().SetTitleSize(0.05)
                h.GetXaxis().SetLabelSize(0.04)
                h.GetYaxis().SetLabelSize(0.04)
                h.Draw("HIST")
                if result and result.IsValid():
                    fit_func.Draw("SAME")
                    cs.Update()
                    st = h.FindObject("stats")
                    if st:
                        st.SetX1NDC(0.60)
                        st.SetX2NDC(0.94)
                        st.SetY1NDC(0.45)
                        st.SetY2NDC(0.92)
                        st.SetTextFont(42)
                        st.SetTextSize(0.030)
                        st.Draw()
                    # MPV box
                    mpv_box = ROOT.TPaveText(0.6, 0.4, 0.94, 0.3, "NDC")
                    mpv_box.SetFillColor(0)
                    mpv_box.SetFillStyle(1001)
                    mpv_box.SetBorderSize(1)
                    mpv_box.SetTextFont(42)
                    mpv_box.SetTextSize(0.038)
                    mpv_box.AddText(f"MPV = {
                                    mpv:.1f} [ADC #scale[0.6]{{#bullet}} tt #scale[0.6]{{#bullet}} mm^{{ -1 }}]")
                    mpv_box.Draw()
                cs.Update()
                out_s = os.path.join(slices_dir,
                                     f"{dataset_name}_slice_{version}_{str_s}.pdf")
                cs.SaveAs(out_s)
                print(f" [{find_time_now()}] : {out_s} saved")
                cs.Close()

                root_file.cd()
                h.Write()
                if result and result.IsValid():
                    fit_func.Write()

            # MPV scatter + pol1 fit
            if len(mpv_pts) < 2:
                print(f"{output_align}  Not enough slices for expo fit ({version})")
                continue

            # Exclude edge slices from the fit (but keep them in the plot)
            fit_pts = mpv_pts[exclude_edges: len(mpv_pts) - exclude_edges] \
                if exclude_edges > 0 and len(mpv_pts) > 2 * exclude_edges \
                else mpv_pts
            if len(fit_pts) < 2:
                print(
                    f"{output_align}  Not enough slices after edge exclusion ({version})")
                fit_pts = mpv_pts

            n_pts = len(mpv_pts)       # all points for graph
            n_fit = len(fit_pts)       # subset for fit
            t_arr = np.array([p[0] for p in mpv_pts], dtype=float)
            mpv_arr = np.array([p[1] for p in mpv_pts], dtype=float)
            err_arr = np.array([p[2] for p in mpv_pts], dtype=float)
            t_fit = np.array([p[0] for p in fit_pts], dtype=float)
            mpv_fit = np.array([p[1] for p in fit_pts], dtype=float)

            gname = f"g_mpv_slices_{version}"
            g_mpv = ROOT.TGraphErrors(n_pts)
            g_mpv.SetName(gname)
            g_mpv.SetTitle(
                f"{dataset_name} - Langaus MPV vs Drift Time ({version})"
                ";Peak time [tt]"
                ";MPV [ADC #scale[0.6]{#bullet} tt #scale[0.6]{#bullet} mm^{-1 }]")
            half_w_s = float(slice_width) / 2.0
            for i, (t, m, e) in enumerate(zip(t_arr, mpv_arr, err_arr)):
                g_mpv.SetPoint(i, float(t), float(m))
                g_mpv.SetPointError(i, half_w_s, float(e))
            g_mpv.SetMarkerStyle(20)
            g_mpv.SetMarkerSize(0.9)
            g_mpv.SetMarkerColor(ROOT.kBlue + 1)
            g_mpv.SetLineColor(ROOT.kBlue + 1)

            # Exponential fit: Q0 * exp(-t/tau)
            # Fix C to min MPV to stabilize the 2-param exponential fit
            c_fixed = float(np.min(mpv_fit))
            q0_est = float(np.max(mpv_fit)) - c_fixed
            expo_fit = ROOT.TF1(f"expo_slices_{version}",
                                f"[0]*exp(-x/[1])+{c_fixed:.6f}",
                                float(t_fit.min()), float(t_fit.max()))
            expo_fit.SetParNames("Q0", "tau")
            expo_fit.SetParameters(q0_est, 500.0)
            expo_fit.SetParLimits(0, q0_est * 0.01, q0_est * 100)
            expo_fit.SetParLimits(1, 10, 1e8)
            expo_fit.SetLineColor(ROOT.kRed + 1)
            expo_fit.SetLineWidth(2)
            g_mpv.Fit(expo_fit, "R")

            q0 = expo_fit.GetParameter(0)
            q0_err = expo_fit.GetParError(0)
            tau_tt = expo_fit.GetParameter(1)
            tau_tt_err = expo_fit.GetParError(1)
            tau_ms = tau_tt * 0.5 / 1000.0
            tau_ms_err = tau_tt_err * 0.5 / 1000.0
            chi2_fit = expo_fit.GetChisquare()
            ndf_fit = expo_fit.GetNDF()

            # Canvas

            charge_unit = "ADC #scale[0.6]{#bullet} tt #scale[0.6]{#bullet} mm^{ -1 }"

            ROOT.gStyle.SetOptStat(0)
            ROOT.gStyle.SetOptFit(0)
            ROOT.gStyle.SetTitleFont(42, "XYZ")
            ROOT.gStyle.SetLabelFont(42, "XYZ")
            ROOT.gStyle.SetTitleFont(42, "t")

            cg = ROOT.TCanvas(f"c_{gname}", gname, 1200, 700)
            cg.SetLeftMargin(0.12)
            cg.SetBottomMargin(0.12)
            cg.SetTopMargin(0.10)
            cg.SetRightMargin(0.05)

            g_mpv.GetXaxis().SetTitleSize(0.05)
            g_mpv.GetYaxis().SetTitleSize(0.05)
            g_mpv.GetXaxis().SetLabelSize(0.04)
            g_mpv.GetYaxis().SetLabelSize(0.04)
            g_mpv.GetXaxis().SetTitleOffset(1.0)
            g_mpv.GetYaxis().SetTitleOffset(1.1)
            g_mpv.Draw("AP")
            # g_mpv.GetYaxis().SetRangeUser(85, 100)
            expo_fit.Draw("SAME")

            box = ROOT.TPaveText(0.66, 0.52, 0.94, 0.88, "NDC")
            box.SetFillColor(0)
            box.SetFillStyle(1001)
            box.SetBorderSize(1)
            box.SetTextFont(42)
            box.SetTextSize(0.028)
            box.SetTextAlign(12)
            box.AddText(
                "Fit: Q_{0} #upoint exp(#font[122]{-}t / #tau_{e}) + C  (C fixed)")
            box.AddText(f"Q_{{0}} = {q0:.2f} #pm {
                        q0_err:.2f} [ADC #scale[0.6]{{#bullet}} tt #scale[0.6]{{#bullet}} mm^{{ -1 }}]")

            box.AddText(f"#tau_{{e}} [tt] = {tau_tt:.1f} #pm {tau_tt_err:.1f}")
            box.AddText(f"#tau_{{e}} [ms] = {tau_ms:.3f} #pm {tau_ms_err:.3f}")
            box.AddText(f"C (fixed) = {c_fixed:.2f} [{charge_unit}]")
            box.AddText(f"#chi^{{2}} / ndf = {chi2_fit:.2f} / {ndf_fit}")
            box.Draw()

            cg.Update()
            out_g = os.path.join(output_folder,
                                 f"{dataset_name}_mpv_slices_{version}.pdf")
            cg.SaveAs(out_g)
            print(f" [{find_time_now()}] : {out_g} saved")

            root_file.cd()
            g_mpv.Write()
            expo_fit.Write()
            cg.Close()

            mpv_results[version] = mpv_pts

        return mpv_results  # {version: [(t_ctr, mpv, mpv_err), ...]}

    # ------------------------------------------------------------------ #
    #  Fit range scan: tau vs range width                                  #
    # ------------------------------------------------------------------ #

    def _scan_fit_ranges(
        self,
        ROOT,
        rows:          List[dict],
        root_file,
        output_folder: str,
        dataset_name:  str,
        x_bins:        int,
        y_bins:        int,
        n_steps:       int,
        width_min:     int,
        width_max:     int,
        stable_thr:    float = 5.0,
    ) -> None:
        """
        Vary fit window symmetrically around the data center.
        For each width, perform the direct 2D pol1 fit and record tau.
        Saves one PDF per fit (2*n_steps total) plus a tau-vs-width
        summary plot for each version (2 PDFs).
        """
        scan_dir = os.path.join(output_folder, 'fit_range_scan')
        Path(scan_dir).mkdir(parents=True, exist_ok=True)

        times = np.array([r['peak_time_tick'] for r in rows], dtype=float)
        dqdx_v1 = np.array([r['normalized_charge_v1_eq_adc_tt']
                           for r in rows], dtype=float)
        dqdx_v2 = np.array([r['normalized_charge_v2_eq_adc_tt']
                           for r in rows], dtype=float)

        x_lo = float(np.floor(times.min() * 0.95))
        x_hi = float(np.ceil(times.max() * 1.05))
        y_lo = float(min(dqdx_v1.min(), dqdx_v2.min()) * 0.9)
        y_hi = float(max(dqdx_v1.max(), dqdx_v2.max()) * 1.1)

        # Center fixed at physical mid-drift (NTT/2 = 645/2 = 322 ticks)
        x_ctr = 322.0

        # Reversed log spacing: dense near maximum width, sparse near minimum
        widths = width_max - np.logspace(
            np.log10(1), np.log10(width_max - width_min + 1), n_steps)[::-1] + 1

        # results[version] = list of (width, tau, tau_err)
        results = {'v1': [], 'v2': []}

        for step_idx, width in enumerate(widths):
            flo = max(x_lo, x_ctr - width / 2.0)
            fhi = min(x_hi, x_ctr + width / 2.0)
            str_w = f"{int(width):04d}"

            for version, dqdx in (('v1', dqdx_v1), ('v2', dqdx_v2)):
                hname = f"h2_scan_{version}_w{str_w}"
                title = (f"{dataset_name} - Equalized dQ/dx vs Peak Time ({version})"
                         f" - fit width {int(width)} tt"
                         ";Peak time [tt]"
                         ";dQ/dx [ADC #scale[0.6]{#bullet}"
                         " tt #scale[0.6]{#bullet} mm^{-1 }]")

                h = ROOT.TH2F(hname, title, x_bins, x_lo, x_hi,
                              y_bins, y_lo, y_hi)
                h.SetStats(0)
                for t, q in zip(times, dqdx):
                    h.Fill(t, q)

                fit = ROOT.TF1(f"pol1_scan_{version}_w{str_w}",
                               "pol1", flo, fhi)
                fit.SetParameter(0, float(np.mean(dqdx)))
                fit.SetParameter(1, 0.0)
                fit.SetLineColor(ROOT.kRed + 1)
                fit.SetLineWidth(2)
                h.Fit(fit, "R")

                slope = fit.GetParameter(1)
                slope_err = fit.GetParError(1)
                intercept = fit.GetParameter(0)
                intercept_err = fit.GetParError(0)

                if abs(slope) > 0:
                    tau_tt = abs(intercept / slope)
                    tau_ms = tau_tt * 0.5 / 1000.0
                    rel_err = ((intercept_err / abs(intercept))**2 +
                               (slope_err / abs(slope))**2) ** 0.5
                    tau_ms_err = tau_ms * rel_err
                else:
                    tau_ms = tau_ms_err = 0.0

                results[version].append((float(width), tau_ms, tau_ms_err))

                root_file.cd()
                h.Write()

                self._save_canvas_2d(
                    ROOT, h, None,
                    scan_dir,
                    f"{dataset_name}_scan_{version}_w{str_w}",
                    fit_params={
                        'slope':         slope,
                        'slope_err':     slope_err,
                        'intercept':     intercept,
                        'intercept_err': intercept_err,
                        'tau_ms':        tau_ms,
                        'tau_ms_err':    tau_ms_err,
                        'chi2':          fit.GetChisquare(),
                        'ndf':           fit.GetNDF(),
                    })

        # Summary: tau vs range width
        for version in ('v1', 'v2'):
            pts = results[version]
            n = len(pts)
            widths_a = np.array([p[0] for p in pts], dtype=float)
            taus_a = np.array([p[1] for p in pts], dtype=float)
            errs_a = np.array([p[2] for p in pts], dtype=float)

            # Split into stable (rel. error < 200%) and unstable points
            # Note: direct 2D fit errors can be large; 200% is a loose threshold
            mask = np.array([e / t < stable_thr if t > 0 else False
                             for t, e in zip(taus_a, errs_a)])
            if not mask.any():
                print(f"{output_align}  [{version}] WARNING: all points unstable. "
                      f"tau range: {taus_a.min():.3f}-{taus_a.max():.3f} ms, "
                      f"err range: {errs_a.min():.3f}-{errs_a.max():.3f} ms")
            widths_s = widths_a[mask]
            taus_s = taus_a[mask]
            errs_s = errs_a[mask]
            widths_u = widths_a[~mask]
            taus_u = taus_a[~mask]
            errs_u = errs_a[~mask]
            ns = int(mask.sum())
            nu = n - ns

            print(f"{output_align}  [{version}] scan: {
                  ns} stable, {nu} unstable points")

            gtitle = (f"{dataset_name} - #tau_{{e}} vs Fit Range Width ({version})"
                      ";Fit range width [tt];Electron lifetime [ms]")

            def _make_tge(name, title, ws, ts, es, color, style):
                """Build TGraphErrors from numpy arrays, filling point by point."""
                g = ROOT.TGraphErrors(len(ws))
                g.SetName(name)
                g.SetTitle(title)
                for i, (w, t, e) in enumerate(zip(ws, ts, es)):
                    g.SetPoint(i, float(w), float(t))
                    g.SetPointError(i, 0.0, float(e))
                g.SetMarkerStyle(style)
                g.SetMarkerSize(0.9)
                g.SetMarkerColor(color)
                g.SetLineColor(color)
                return g

            # Stable points — blue filled circles
            gname = f"g_tau_vs_width_{version}"
            g = _make_tge(gname, gtitle, widths_s, taus_s, errs_s,
                          ROOT.kBlue + 1, 20) if ns > 0 else None

            # Unstable points — gray open circles
            gname_u = f"g_tau_vs_width_{version}_unstable"
            g_u = _make_tge(gname_u, gtitle, widths_u, taus_u, errs_u,
                            ROOT.kGray + 1, 24) if nu > 0 else None

            ROOT.gStyle.SetOptStat(0)
            ROOT.gStyle.SetOptFit(0)
            ROOT.gStyle.SetTitleFont(42, "XYZ")
            ROOT.gStyle.SetLabelFont(42, "XYZ")
            ROOT.gStyle.SetTitleFont(42, "t")

            cname = f"c_tau_vs_width_{version}"
            c = ROOT.TCanvas(cname, cname, 1200, 700)
            c.SetLeftMargin(0.12)
            c.SetBottomMargin(0.12)
            c.SetTopMargin(0.10)
            c.SetRightMargin(0.05)

            if g is None and g_u is None:
                print(
                    f"{output_align}  [{version}] no points to plot, skipping summary")
                c.Close()
                continue

            # Draw all points in a single TGraphErrors — stable blue, unstable gray
            # achieved by drawing stable first with AP, then unstable with P SAME
            g_draw = g if g is not None else g_u
            g_draw.SetTitle(
                f"{dataset_name} - #tau_{{e}} vs Fit Range Width ({version})"
                ";Fit range width [tt];Electron lifetime [ms]")
            g_draw.GetXaxis().SetTitleSize(0.05)
            g_draw.GetYaxis().SetTitleSize(0.05)
            g_draw.GetXaxis().SetLabelSize(0.04)
            g_draw.GetYaxis().SetLabelSize(0.04)
            g_draw.GetXaxis().SetTitleOffset(1.0)
            g_draw.GetYaxis().SetTitleOffset(1.1)
            g_draw.Draw("AP")

            if g is not None and g_u is not None:
                g_u.Draw("P SAME")

            c.Update()

            # Legend
            leg = ROOT.TLegend(0.13, 0.75, 0.50, 0.88)
            leg.SetTextFont(42)
            leg.SetTextSize(0.033)
            leg.SetBorderSize(1)
            leg.SetFillColor(0)
            if g is not None:
                leg.AddEntry(g,   "Stable (#delta#tau / #tau < 50%)", "P")
            if g_u is not None:
                leg.AddEntry(g_u, "Unstable (#delta#tau / #tau #geq 50%)", "P")
            leg.Draw()

            # Mean and RMS of tau values (stable only) as a summary box
            tau_mean = float(np.mean(taus_s)) if ns > 0 else 0.0
            tau_rms = float(np.std(taus_s, ddof=1)) if ns > 1 else 0.0
            box = ROOT.TPaveText(0.55, 0.75, 0.94, 0.88, "NDC")
            box.SetFillColor(0)
            box.SetFillStyle(1001)
            box.SetBorderSize(1)
            box.SetTextFont(42)
            box.SetTextSize(0.033)
            box.SetTextAlign(12)
            box.AddText(f"Mean #tau_{{e}} = {tau_mean:.3f} ms  (stable only)")
            box.AddText(f"RMS = {tau_rms:.3f} ms  (systematic)")
            box.Draw()

            c.Update()
            out = os.path.join(output_folder,
                               f"{dataset_name}_tau_vs_width_{version}.pdf")
            c.SaveAs(out)
            print(f" [{find_time_now()}] : {out} saved")

            root_file.cd()
            if g is not None:
                g.Write()
            if g_u is not None:
                g_u.Write()
            c.Close()

    # ------------------------------------------------------------------ #
    #  Canvas: 2D histogram with profile and pol1 fit                      #
    # ------------------------------------------------------------------ #

    def _save_canvas_2d(
        self,
        ROOT,
        h,
        profile,
        output_folder: str,
        fname:         str,
        fit_params:    dict = None,
    ) -> None:
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetOptFit(0)
        ROOT.gStyle.SetTitleFont(42, "XYZ")
        ROOT.gStyle.SetLabelFont(42, "XYZ")
        ROOT.gStyle.SetTitleFont(42, "t")
        ROOT.gStyle.SetPalette(ROOT.kBird)

        c = ROOT.TCanvas(f"c_{fname}", fname, 1200, 900)
        c.SetLeftMargin(0.12)
        c.SetBottomMargin(0.12)
        c.SetTopMargin(0.10)
        c.SetRightMargin(0.14)   # extra room for colour axis

        h.GetXaxis().SetTitleSize(0.05)
        h.GetYaxis().SetTitleSize(0.05)
        h.GetZaxis().SetTitleSize(0.05)
        h.GetXaxis().SetLabelSize(0.04)
        h.GetYaxis().SetLabelSize(0.04)
        h.GetZaxis().SetLabelSize(0.04)
        h.GetXaxis().SetTitleOffset(1.0)
        h.GetYaxis().SetTitleOffset(1.1)
        h.GetZaxis().SetTitleOffset(1.4)
        h.Draw("COLZ")

        if profile is not None:
            profile.Draw("P SAME")

        # Draw fit line if fit params provided (function attached to histogram)
        if fit_params:
            funcs = h.GetListOfFunctions()
            if funcs and funcs.GetSize() > 0:
                funcs.Last().Draw("SAME")

        # Entries box (always) — expand if fit params provided
        if fit_params:
            box = ROOT.TPaveText(0.50, 0.60, 0.86, 0.88, "NDC")
        else:
            box = ROOT.TPaveText(0.50, 0.82, 0.86, 0.90, "NDC")
        box.SetFillColor(0)
        box.SetFillStyle(1001)
        box.SetBorderSize(1)
        box.SetTextFont(42)
        box.SetTextSize(0.028)
        box.SetTextAlign(12)
        box.SetMargin(0.05)
        box.AddText(f"Entries = {int(h.GetEntries())}")
        if fit_params:
            chi2 = fit_params.get('chi2', 0.0)
            ndf = fit_params.get('ndf',  1)
            box.AddText(f"#chi^{{2}} / ndf = {chi2:.2f} / {ndf}")
            box.AddText(f"Slope     = {fit_params['slope']:.4f} #pm {
                        fit_params['slope_err']:.4f}")
            box.AddText(f"Intercept = {fit_params['intercept']:.2f} #pm {
                        fit_params['intercept_err']:.2f}")
            box.AddText(f"#tau_{{e}} = {fit_params['tau_ms']:.3f} #pm {
                        fit_params['tau_ms_err']:.3f} ms")
        box.Draw()

        c.Update()
        out = os.path.join(output_folder, f"{fname}.pdf")
        c.SaveAs(out)
        print(f" [{find_time_now()}] : {out} saved")
        c.Close()

    # ------------------------------------------------------------------ #
    #  Utilities                                                           #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _auto_range(
        data:   np.ndarray,
        margin: float = 0.1,
    ) -> Tuple[float, float]:
        """Return (min*(1-margin), max*(1+margin))."""
        return float(data.min() * (1 - margin)), float(data.max() * (1 + margin))
