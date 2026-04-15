#/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

def globalVariables():
    
    global EleEne
    global GamInt
    global GamEne
    global GamFrq
    global EleFrq
    global prb
    
    global pitch
    global edge
    global height
    global source_radius
    
    global photonRes
    
    # dimensions are expressed in mm
    pitch=0.577
    edge=13.164
    height=520. # drift length
    source_radius=5.
    
    photonRes=0.07 # From 2022 data?
    
    # Gamma interaction lengths in mm, from NIST
    GamInt=[0,120.,80.,160.] 
    
    # Gamma energy at the generation, MeV
    GamEne=[0,1.064,0.57,1.77]
    
    # Gamma generation probability 
    GamFrq=[0,0.75,0.98,0.069]
    
    # Electron energy at cgeneration, MeV
    EleEne=[0,0.976,1.049,1.060,0.482,0.556,0.566]
    
    # Electron generation probability 
    EleFrq=[0,0.0703,0.0184,0.0054,0.0152,0.0044,0.0015]
    
    # Summing up all the probabilities. 
    # Probabilities will then be normalized to prb9
    # Particles are generated as independent events to each other 
    # We only care about geometry
    
    prb = np.zeros(10)
    prb[1]=GamFrq[1]
    prb[2]=prb[1]+GamFrq[2]
    prb[3]=prb[2]+GamFrq[3]
    prb[4]=prb[3]+EleFrq[1]
    prb[5]=prb[4]+EleFrq[2]
    prb[6]=prb[5]+EleFrq[3]
    prb[7]=prb[6]+EleFrq[4]
    prb[8]=prb[7]+EleFrq[5]
    prb[9]=prb[8]+EleFrq[6] 
    # WARNING: prb9 = 1.91419995 (Fortran), 1.9142000000000001 (Python)
    

