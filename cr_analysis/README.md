# CR Muon Analysis — `cr_analysis/`

This directory contains the cosmic ray (CR) muon analysis pipeline for the
50-liter LArTPC prototype operated at CERN's Building 182.
CR muons crossing the detector are used to study detector response,
perform charge equalization across collection strips, and measure the
electron lifetime in liquid argon.

---

## Physics Overview

Cosmic ray muons are assumed at MIP (minimum-ionising particles). They traverse the
full active volume, crossing all 48 collection strips by detector construction & trigger definition. The charge deposited
per unit track length follows a convolved Landau-Gaussian distribution, whose most probable
value (MPV) provides a stable reference for:

- **Charge equalization** — correcting for gain non-uniformity between the
  two halves of the collection plane (strips 1–24 vs 25–48)
- **Electron lifetime measurement** — the exponential attenuation of charge
  as a function of drift time reveals the LAr purity

---

## Detector Parameters

| Parameter | Value |
|-----------|-------|
| Active volume | ~50 litres |
| Collection strips | 48 × 5 mm pitch |
| Induction 1 strips | 40 × 7.5 mm pitch |
| Induction 2 strips | 40 × 7.5 mm pitch |
| Time ticks | 645 × 0.5 µs/tick |
| Drift velocity | 1.57 mm/µs |
| Max drift distance | ~52 cm |

---

## Pipeline

```
Step 1  →  cr_step1_select.py
Step 2  →  cr_step2_analyze.py
Step 3  →  cr_step3_analyze.py
Extra   →  cr_superposition.py
```

### Step 1 — Event selection (`cr_step1_select.py`)

Walks all JSON files in the data folder and selects CR muon candidates.

**Selection criteria:**
- At least 44/48 collection strips have exactly one peak above threshold
- Multi-peak strips are resolved using the track time window
- Induction 2 plane shows a bipolar signal within ±15 ticks of the
  collection time window

**Processing:**
- Stage 1 (every event): baseline subtraction using the most-frequent-value
  method (robust to CR signal contamination)
- Stage 2 (selected events only): coherent noise removal using a symmetric
  trimmed mean

**Outputs:**
```
output/{dataset}/csv/{dataset}-CR_events.csv     # one row per event
output/{dataset}/csv/{dataset}-CR_charges.csv    # one row per strip per event
output/{dataset}/plots/event_displays/           # optional 2D event displays
output/{dataset}/plots/single_traces/            # optional per-channel traces
```

**Track length formulas:**

Two versions of the 3D track length ΔL are computed:

- **v1** (ICARUS, Navas-Concha et al. 2002, assuming equal pitch):

$$\Delta L_{v1} = \delta d_c \sqrt{\left(\frac{\Delta T \cdot \delta t \cdot v_d}{\delta d_c}\right)^2 + \frac{4}{3}\left(\Delta C^2 + \Delta I^2 - \Delta C \cdot \Delta I\right)}$$

- **v2** (precise, $\delta d_c \neq \delta d_i$):

$$\Delta L_{v2} = \sqrt{\left(\Delta T \cdot \delta t \cdot v_d\right)^2 + \frac{4}{3}\left(\Delta C^2 \cdot \delta d_c^2 + \Delta I^2 \cdot \delta d_i^2 + \Delta C \cdot \Delta I \cdot \delta d_c \cdot \delta d_i\right)}$$

The track pitch length is $\Delta z = \Delta L / \Delta C$ [mm].
The normalized charge is $\mathrm{d}Q/\mathrm{d}x = Q_\mathrm{peak} / \Delta z$ [ADC·tt·mm⁻¹].

---

### Step 2 — Analysis and equalization (`cr_step2_analyze.py`)

Pure CSV-based analysis using PyROOT. No JSON files are read.

**Produces:**
- ΔL and track pitch length histograms (v1 and v2)
- 48 × 2 dQ/dx histograms with Landau⊗Gaussian fits
- MPV scatter plots (strip number vs MPV) with weighted mean lines
- Equalized dQ/dx histograms and MPV scatter plots
- `{dataset}-CR_equalization.csv` — equalization factors per version
- `{dataset}-CR_charges_equalized.csv` — charges with equalized columns

**Equalization:**
Strips 25–48 are scaled by `mean_lo / mean_hi` (ratio of weighted mean MPV
of strips 1–24 to strips 25–48) to correct for the observed ~2× gain
difference between the two halves of the collection plane.

**Requires:** ROOT (run on lxplus with `source setup_lxplus.sh`)

```
output/{dataset}/plots/summary/
```

---

### Step 3 — Electron lifetime (`cr_step3_analyze.py`)

Reads `*-CR_charges_equalized.csv` and measures the electron lifetime.

**Methods:**
1. **2D histogram** — equalized dQ/dx vs peak time with black MPV overlay
   points and pol1 fit line
2. **Langaus slice method** — divides the drift axis into slices of
   `dqdx_slice_bin_width` ticks, fits each slice with a Landau⊗Gaussian,
   extracts the MPV, then fits `Q_0 \cdot \exp(-t/\tau_e) + C` (C fixed to
   minimum MPV) to the MPV vs drift time scatter
3. **Fit range scan** — varies the fit window symmetrically around tick 322
   to assess the systematic uncertainty on τ

**Electron lifetime result:**
From the exponential fit to the Langaus MPV vs drift time:
$Q(t) = Q_0 \cdot e^{-t/\tau_e} + C$, with τ_e extracted directly.

```
output/{dataset}/plots/step3/
output/{dataset}/plots/step3/langaus_slices/
output/{dataset}/plots/step3/fit_range_scan/
```

---

### Superposition display (`cr_superposition.py`)

Overlays all selected CR events into a single 2D ADC display (no averaging)
using PyROOT. Produces one plot per detector view (full, collection,
induction 1, induction 2), in both raw and equalized versions.

```
output/{dataset}/plots/{dataset}_CR_superposition_{view}.pdf
output/{dataset}/plots/{dataset}_CR_superposition_{view}_eq_{v1|v2}.pdf
```

---

## Configuration

All user-facing parameters are in `config_cr.py`. Key parameters:

```python
raw_data_folder_name = '20220511'   # dataset to analyse
output_root          = './output'

# Step 1 — Selection
min_strips_1peak = 44       # minimum strips with exactly 1 peak
peak_height      = 18       # ADC
peak_width       = 5        # ticks
evtdisplay_step1 = False    # disable for large runs
chndisplay_planes_step1 = []

# Step 2 — Analysis (PyROOT)
norm_charge_bin_width  = 1.0   # ADC·tt·mm⁻¹
delta_l_bin_width      = 5.0   # mm
track_pitch_bin_width  = 0.02  # mm

# Step 3 — Electron lifetime
dqdx_slice_bin_width         = 32   # ticks per drift slice
dqdx_slice_fit_exclude_edges = 1    # edge slices excluded from expo fit
dqdx_fit_range_scan          = True # enable systematic scan
```

---

## Data

Raw data is expected at `../DATA/{dataset}/jsonData/` relative to the
`cr_analysis/` working directory.
JSON files are produced by the `data_conversion/` pipeline.

---

## Dependencies

| Package | Used in |
|---------|---------|
| Python ≥ 3.10 | all steps |
| NumPy, SciPy | Step 1 |
| Matplotlib | Step 1 displays |
| ROOT / PyROOT | Steps 2, 3, superposition |

ROOT must be sourced via `setup_lxplus.sh` on lxplus (LCG_109) for Step 2
and beyond. Step 1 runs locally on macOS with a standard Python venv.

---

## Running

```bash
cd cr_analysis

# Step 1 — select CR events (run locally or on lxplus)
python3 cr_step1_select.py

# Step 2 — analysis + equalization (requires ROOT, run on lxplus)
source ../setup_lxplus.sh
python3 cr_step2_analyze.py

# Step 3 — electron lifetime (requires ROOT)
python3 cr_step3_analyze.py

# Superposition display (requires ROOT)
python3 cr_superposition.py
```

For large datasets, run Step 1 in a screen session:

```bash
screen -S cr_step1
python3 cr_step1_select.py
# Ctrl+A D to detach
```

---

## Output Structure

```
output/{dataset}/
├── csv/
│   ├── {dataset}-CR_events.csv
│   ├── {dataset}-CR_charges.csv
│   ├── {dataset}-CR_equalization.csv       (Step 2)
│   └── {dataset}-CR_charges_equalized.csv  (Step 2)
└── plots/
    ├── event_displays/   (Step 1, optional)
    ├── single_traces/    (Step 1, optional)
    ├── summary/          (Step 2)
    └── step3/            (Step 3)
```

---

## References

- S. Navas-Concha et al., *NIM A* **486** (2002) 462–474 — track length formula (v1)
- ICARUS Collaboration, *NIM A* **527** (2004) 329–410 — dQ/dx methodology
