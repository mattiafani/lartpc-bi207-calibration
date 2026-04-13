#!/bin/bash
# setup.sh — Environment setup for CR muon analysis on lxplus
# Usage: source setup.sh

# LCG environment (Python 3.12+, numpy, scipy, matplotlib)
source /cvmfs/sft.cern.ch/lcg/views/LCG_109/x86_64-el9-gcc13-opt/setup.sh

# Force matplotlib non-interactive backend (no display on lxplus)
export MPLBACKEND=Agg

# Set working directory to the Analysis folder
export ANALYSIS_DIR=/eos/project/f/flic-bi207/bi207/Analysis
cd $ANALYSIS_DIR

# Confirm setup
echo ""
echo "  Python version     : $(python3 --version)"
echo "  Working dir        : $(pwd)"
echo "  Matplotlib backend : $MPLBACKEND"
python3 -c "import numpy, scipy, matplotlib; print('  Packages           : OK')"
echo ""
