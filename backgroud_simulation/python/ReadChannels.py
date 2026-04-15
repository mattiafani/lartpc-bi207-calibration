#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 23:51:35 2023

@author: Mattia Fanì (LANL) - mattia.fani@cern.ch
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import sem


# Set the size of the figure
figsize = (8, 6)  

h1d_photons = {}
h1d_electrons = {}
h1d_fd = {}

nBins=200

for iChn in range(1, 9):
    
    df = pd.read_csv(f"Output/chn_r0{iChn}.csv")
    
    particle_string_list = ['Electrons', 'Photons', 'All']
    
    for particles in particle_string_list:

        fig, ax = plt.subplots(figsize=figsize)  
        
        if particles == 'Photons':
            data = df[df.iloc[:,0] == 0]
            hist_color = 'cornflowerblue'
            plot_title = f'h1d_EnergyPhotonsChn0{iChn}'
            values = data.iloc[:, 2]
            n_ph, bins_ph, patches_ph = ax.hist(list(values), bins=nBins, range=[0,2],\
                                       color=hist_color, label=particles)
            label_text = f"Channel 0{iChn}\nTotal Entries: {int(sum(n_ph))}"
            ylegend = 0.82
            
            # Store the histogram in the dictionary
            h1d_photons[f"chn{iChn}"] = {"bin_entries": n_ph, "bin_edge": bins_ph}
            
        elif particles == 'Electrons':
            data = df[df.iloc[:,0] == 1]
            hist_color = 'gold'
            plot_title = f'h1d_EnergyElectronsChn0{iChn}'
            values = data.iloc[:, 2]
            n_el, bins_el, patches_el = ax.hist(list(values), bins=nBins, range=[0,2],\
                                        color=hist_color, label=particles)
            label_text = f"Channel 0{iChn}\nTotal Entries: {int(sum(n_el))}"
            ylegend = 0.82
            
            # Store the histogram in the dictionary
            h1d_electrons[f"chn{iChn}"] = {"bin_entries": n_el, "bin_edge": bins_el}
                
        else:
            data0 = df[df.iloc[:,0] == 0]
            values0 = data0.iloc[:, 2]
            data1 = df[df.iloc[:,0] == 1]
            values1 = data1.iloc[:, 2]
            plot_title = f'h1d_EnergyAllChn0{iChn}'
            hist_color = ['cornflowerblue', 'gold']
            n_all, bins_all, patches_all = ax.hist([list(values0), list(values1)], bins=nBins, range=[0,2],\
                                        color=hist_color, label=['Photons', 'Electrons'],\
                                            stacked='True')
            label_text = f"Channel 0{iChn}\nTotal Entries: {int(sum(n_all[0])+sum(n_all[1]))}"
            ylegend = 0.76

        ax.set_xlabel('Deposited energy [MeV]', fontsize=14) 
        ax.set_ylabel('Entries [#]', fontsize=14)  
        
        ax.set_xticks([i/10 for i in range(0, 21, 2)])  
        
        ax.grid(axis='y')  
        
        bbox_props = dict(boxstyle='square', facecolor='white', alpha=0.5, \
                  edgecolor='black', linewidth=1)
        ax.text(0.98, ylegend, label_text, transform=ax.transAxes,\
                bbox=bbox_props,ha='right')
        
        # Add a legend to the plot
        ax.legend(fontsize=12)

        plt.savefig(f"Output/{plot_title}.pdf")
        plt.show()
        
        # Clear the plot
        plt.clf()
        plt.close()

###############################################################################
# Fake data
###############################################################################

hist_color = 'dimgray'

for iChn in range(1, 9):
    
    df = pd.read_csv(f"Output/chn_r0{iChn}.csv")
    values = df.iloc[:, 2]
    
    # Create figure
    fig_fd, ax_fd = plt.subplots(figsize=figsize)  
    
    plot_title = f'h1d_EnergyFakeDataChn0{iChn}'
    
    # Setting axis labels
    ax_fd.set_xlabel('Deposited energy [MeV]', fontsize=14) 
    ax_fd.set_ylabel('Entries [#]', fontsize=14)  
    
    n_fd, bins_fd, patches_fd = ax_fd.hist(values, bins=nBins, range=[0,2],\
                               color=hist_color, label='Fake data')  
        
    # Store the histogram in the dictionary
    h1d_fd[f"chn{iChn}"] = {"bin_entries": n_fd, "bin_edge": bins_fd}
    
    # Define tick number of x-axis
    ax_fd.set_xticks([i/10 for i in range(0, 21, 2)])  
    
    # Add a background grid to the plot
    ax_fd.grid(axis='y')  
    
    # Add label with the total number of entries for each plot
    label_text = f"Channel 0{iChn}\nTotal Entries: {int(sum(n_fd))}"
    bbox_props = dict(boxstyle='square', facecolor='white', alpha=0.5, \
              edgecolor='black', linewidth=1)
    ax_fd.text(0.98, 0.82, label_text, transform=ax_fd.transAxes,\
            bbox=bbox_props,ha='right')
    
    # Add a legend to the plot
    ax_fd.legend(fontsize=12)  
    
    plt.savefig(f"Output/{plot_title}.pdf")
    plt.show()
    
###############################################################################

h1d_photons_intChns = h1d_photons['chn4']['bin_entries'] +\
    h1d_photons['chn5']['bin_entries']
h1d_photons_outChns = h1d_photons['chn1']['bin_entries'] +\
    h1d_photons['chn2']['bin_entries']+\
    h1d_photons['chn3']['bin_entries']+\
    h1d_photons['chn6']['bin_entries']+\
    h1d_photons['chn7']['bin_entries']+\
    h1d_photons['chn8']['bin_entries']
    
h1d_ratioInnOut = np.divide(h1d_photons_intChns, h1d_photons_outChns,\
                  out=np.zeros_like(h1d_photons_intChns), where=h1d_photons_outChns!=0)
    
av_ratioInnOut = h1d_ratioInnOut[np.nonzero(h1d_ratioInnOut)].mean()
std_ratioInnOut = h1d_ratioInnOut[np.nonzero(h1d_ratioInnOut)].std()
sem_ratioInnOut = sem(h1d_ratioInnOut[np.nonzero(h1d_ratioInnOut)])
# scaling_factor = round(1./av_ratioInnOut,2)

h1d_scaled_photons_outChns = h1d_photons_outChns * av_ratioInnOut

h1d_true_intChns_electrons = h1d_electrons['chn4']['bin_entries']+h1d_electrons['chn5']['bin_entries']

###############################################################################

h1d_fd_intChns = h1d_fd['chn4']['bin_entries'] +\
    h1d_fd['chn5']['bin_entries']
h1d_fd_outChns = h1d_fd['chn1']['bin_entries'] +\
    h1d_fd['chn2']['bin_entries']+\
    h1d_fd['chn3']['bin_entries']+\
    h1d_fd['chn6']['bin_entries']+\
    h1d_fd['chn7']['bin_entries']+\
    h1d_fd['chn8']['bin_entries']
    
h1d_fd_intChns_electrons = h1d_fd_intChns - h1d_fd_outChns*av_ratioInnOut

###############################################################################

hist_color='silver'

fig, ax = plt.subplots(figsize=figsize)

ax.hist(h1d_photons['chn4']['bin_edge'][:-1],len(h1d_photons['chn4']['bin_edge'][:-1]),\
        weights=h1d_fd_outChns, color=hist_color, label='Fake data')

plot_title = 'h1d_FD_EnergyOuterChannels'

label_text = f"FD Outer channels\nTotal Entries: {int(np.sum(h1d_fd_outChns))}"
ylegend = 0.8

ax.set_xlabel('Deposited energy [MeV]', fontsize=14) 
ax.set_ylabel('[#]', fontsize=14)  

plt.title('FD Outer channels')

ax.set_xticks([i/10 for i in range(0, 21, 2)])  

ax.grid(axis='y')  

bbox_props = dict(boxstyle='square', facecolor='white', alpha=0.5, \
          edgecolor='black', linewidth=1)
ax.text(0.98, ylegend, label_text, transform=ax.transAxes,\
        bbox=bbox_props,ha='right')
    
# Add a legend to the plot
ax.legend(fontsize=12)

# Save the plot to a file and show it
plt.savefig(f"Output/{plot_title}.pdf")
plt.show()

###############################################################################

hist_color='grey'

fig, ax = plt.subplots(figsize=figsize)

ax.hist(h1d_photons['chn4']['bin_edge'][:-1],len(h1d_photons['chn4']['bin_edge'][:-1]),\
        weights=h1d_fd_intChns, color=hist_color, label='Fake data')

plot_title = 'h1d_FD_EnergyInnerChannels'

label_text = f"FD Inner channels\nTotal Entries: {int(np.sum(h1d_fd_intChns))}"
ylegend = 0.8

ax.set_xlabel('Deposited energy [MeV]', fontsize=14) 
ax.set_ylabel('[#]', fontsize=14)  

plt.title('FD Inner channels')

ax.set_xticks([i/10 for i in range(0, 21, 2)])  

ax.grid(axis='y')  

bbox_props = dict(boxstyle='square', facecolor='white', alpha=0.5, \
          edgecolor='black', linewidth=1)
ax.text(0.98, ylegend, label_text, transform=ax.transAxes,\
        bbox=bbox_props,ha='right')
    
# Add a legend to the plot
ax.legend(fontsize=12)

# Save the plot to a file and show it
plt.savefig(f"Output/{plot_title}.pdf")
plt.show()

###############################################################################

for iChn in {4,5}:
    
    hist_color = 'slateblue'
    if iChn == 5:
        hist_color = 'mediumpurple'
    
    for jChn in range(1, 9):
        
        dividend = h1d_photons[f'chn{iChn}']['bin_entries']
        divisor = h1d_photons[f'chn{jChn}']['bin_entries']
        
        ratio = np.divide(dividend, divisor, out=np.zeros_like(dividend), where=divisor!=0)
        
        fig, ax = plt.subplots(figsize=figsize)
        
        ax.hist(h1d_photons[f'chn{iChn}']['bin_edge'][:-1],len(h1d_photons[f'chn{iChn}']['bin_edge'][:-1]),\
                weights=ratio, color=hist_color, label='Photons')
            
        av_ratio = ratio[np.nonzero(ratio)].mean()
        std_ratio = ratio[np.nonzero(ratio)].std()
        sem_ratio = sem(ratio[np.nonzero(ratio)])        
    
        plot_title = f'h1d_EnergyRatioChn0{iChn}Chn0{jChn}'
    
        label_text = f"Channel 0{iChn}\nTotal Entries: {int(np.sum(dividend))}\nChannel 0{jChn}\nTotal Entries: {int(np.sum(divisor))}\nMean: {round(av_ratio,2)}, STD: {round(std_ratio,2)}"
        ylegend = 0.73
    
        ax.set_xlabel('Deposited energy [MeV]', fontsize=14) 
        ax.set_ylabel('[#]', fontsize=14)  
        
        # Add line
        plt.axhline(av_ratio, color='darkblue', linestyle='dashed', linewidth=.5)

        x = np.linspace(-0.075, 2, 11)
        ax.fill_between(x, av_ratio-std_ratio, av_ratio+std_ratio,\
                        color='lightskyblue', alpha=0.2)
        ax.fill_between(x, av_ratio-sem_ratio, av_ratio+sem_ratio,\
                        color='lightskyblue', alpha=0.4)
        
        plt.title(f'Ratio of Entries chn0{iChn}/chn0{jChn}')
        
        ax.set_xticks([i/10 for i in range(0, 21, 2)])  
        plt.ylim((0,1.2*max(ratio)))
        
        ax.grid(axis='y')  
        
        bbox_props = dict(boxstyle='square', facecolor='white', alpha=0.5, \
                  edgecolor='black', linewidth=1)
        ax.text(0.98, ylegend, label_text, transform=ax.transAxes,\
                bbox=bbox_props,ha='right')
            
        # Add a legend to the plot
        ax.legend(fontsize=12)
    
        # Save the plot to a file and show it
        plt.savefig(f"Output/{plot_title}.pdf")
        plt.show()
    
        # Clear the plot
        plt.clf()
        plt.close()
    
###############################################################################

hist_color='navy'

fig, ax = plt.subplots(figsize=figsize)

ax.hist(h1d_photons['chn4']['bin_edge'][:-1],len(h1d_photons['chn4']['bin_edge'][:-1]),\
        weights=h1d_photons_intChns, color=hist_color, label='Photons')

plot_title = 'h1d_EnergyInnerChannels'

label_text = f"Inner channels\nTotal Entries: {int(np.sum(h1d_photons_intChns))}"
ylegend = 0.8

ax.set_xlabel('Deposited energy [MeV]', fontsize=14) 
ax.set_ylabel('[#]', fontsize=14)  

plt.title('Inner channels')

ax.set_xticks([i/10 for i in range(0, 21, 2)])  

ax.grid(axis='y')  

bbox_props = dict(boxstyle='square', facecolor='white', alpha=0.5, \
          edgecolor='black', linewidth=1)
ax.text(0.98, ylegend, label_text, transform=ax.transAxes,\
        bbox=bbox_props,ha='right')
    
# Add a legend to the plot
ax.legend(fontsize=12)

# Save the plot to a file and show it
plt.savefig(f"Output/{plot_title}.pdf")
plt.show()

###############################################################################

hist_color='lightskyblue'

fig, ax = plt.subplots(figsize=figsize)

ax.hist(h1d_photons['chn4']['bin_edge'][:-1],len(h1d_photons['chn4']['bin_edge'][:-1]),\
        weights=h1d_photons_outChns, color=hist_color, label='Photons')

plot_title = 'h1d_EnergyOuterChannels'

label_text = f"Outer channels\nTotal Entries: {int(np.sum(h1d_photons_outChns))}"
ylegend = 0.8

ax.set_xlabel('Deposited energy [MeV]', fontsize=14) 
ax.set_ylabel('[#]', fontsize=14)  

plt.title('Outer channels')

ax.set_xticks([i/10 for i in range(0, 21, 2)])  

ax.grid(axis='y')  

bbox_props = dict(boxstyle='square', facecolor='white', alpha=0.5, \
          edgecolor='black', linewidth=1)
ax.text(0.98, ylegend, label_text, transform=ax.transAxes,\
        bbox=bbox_props,ha='right')
    
# Add a legend to the plot
ax.legend(fontsize=12)

# Save the plot to a file and show it
plt.savefig(f"Output/{plot_title}.pdf")
plt.show()

###############################################################################

hist_color='red'

fig, ax = plt.subplots(figsize=figsize)

ax.hist(h1d_photons['chn4']['bin_edge'][:-1],len(h1d_photons['chn4']['bin_edge'][:-1]),\
        weights=h1d_ratioInnOut, color=hist_color, label='Photons')

plot_title = 'h1d_EnergyRatioInnerOuter'

label_text = f"Ratio Inn/Out\nTotal Entries: {int(np.sum(h1d_ratioInnOut))}\nMean: {round(av_ratioInnOut,2)}, STD: {round(std_ratioInnOut,2)}"
ylegend = 0.78

ax.set_xlabel('Deposited energy [MeV]', fontsize=14) 
ax.set_ylabel('[#]', fontsize=14)  

plt.title('Ratio Inner/Outer channels')
plt.ylim((0,1.2*max(h1d_ratioInnOut)))
# plt.xlim((0,2.))

ax.set_xticks([i/10 for i in range(0, 21, 2)])  

ax.grid(axis='y')  

bbox_props = dict(boxstyle='square', facecolor='white', alpha=0.5, \
          edgecolor='black', linewidth=1)
ax.text(0.98, ylegend, label_text, transform=ax.transAxes,\
        bbox=bbox_props,ha='right')
    
# Add a legend to the plot
ax.legend(fontsize=12)

# Add line
plt.axhline(av_ratioInnOut, color='darkblue', linestyle='dashed', linewidth=.5)

x = np.linspace(-0.075, 2, 11)
ax.fill_between(x, av_ratioInnOut-std_ratioInnOut, av_ratioInnOut+std_ratioInnOut,\
                color='lightskyblue', alpha=0.2)
ax.fill_between(x, av_ratioInnOut-sem_ratioInnOut, av_ratioInnOut+sem_ratioInnOut,\
                color='lightskyblue', alpha=0.4)

# Save the plot to a file and show it
plt.savefig(f"Output/{plot_title}.pdf")
plt.show()

# Clear the plot
plt.clf()
plt.close()
    
###############################################################################

fig, ax = plt.subplots(figsize=figsize)

ax.hist([h1d_photons['chn4']['bin_edge'][:-1],h1d_photons['chn4']['bin_edge'][:-1]],\
        len(h1d_photons['chn4']['bin_edge'][:-1]),\
        weights=[h1d_photons_outChns,h1d_scaled_photons_outChns],\
        color=['lightskyblue','blue'], label=['Original','Scaled'])

plot_title = 'h1d_EnergyOuterChannels_scaled'

label_text = f"Outer channels\nTotal Entries: {int(np.sum(h1d_photons_outChns))}"
ylegend = 0.76

ax.set_xlabel('Deposited energy [MeV]', fontsize=14) 
ax.set_ylabel('[#]', fontsize=14)  

plt.title('Outer channels')

# ax.set_xticks([i/10 for i in range(0, 21, 2)])  

ax.grid(axis='y')  

bbox_props = dict(boxstyle='square', facecolor='white', alpha=0.5, \
          edgecolor='black', linewidth=1)
ax.text(0.98, ylegend, label_text, transform=ax.transAxes,\
        bbox=bbox_props,ha='right')
    
# Add a legend to the plot
ax.legend(fontsize=12)

# Save the plot to a file and show it
plt.savefig(f"Output/{plot_title}.pdf")
plt.show()

###############################################################################

fig, ax = plt.subplots(figsize=figsize)

ax.hist(h1d_photons['chn4']['bin_edge'][:-1],\
        len(h1d_photons['chn4']['bin_edge'][:-1]),\
        weights=h1d_fd_intChns_electrons,\
        color='green', label='Electrons (extrap.)')

plot_title = 'h1d_EnergySubtractedInnerChannels'
plt.ylim(0,1.2*max(h1d_fd_intChns_electrons))

label_text = f"Inner channels (subtr.)\nTotal Entries: {int(np.sum(h1d_fd_intChns_electrons))}"
ylegend = 0.82

ax.set_xlabel('Deposited energy [MeV]', fontsize=14) 
ax.set_ylabel('[#]', fontsize=14)  

ax.grid(axis='y')  

bbox_props = dict(boxstyle='square', facecolor='white', alpha=0.5, \
          edgecolor='black', linewidth=1)
ax.text(0.98, ylegend, label_text, transform=ax.transAxes,\
        bbox=bbox_props,ha='right')
    
# Add a legend to the plot
ax.legend(fontsize=12)

# Save the plot to a file and show it
plt.savefig(f"Output/{plot_title}.pdf")
plt.show()

###############################################################################

fig, ax = plt.subplots(figsize=figsize)

ax.hist(h1d_photons['chn4']['bin_edge'][:-1],\
        len(h1d_photons['chn4']['bin_edge'][:-1]),\
        weights=h1d_true_intChns_electrons,\
        color='lime', label='Electrons (from MC)')

plot_title = 'h1d_true_intChns_electrons'
plt.ylim(0,1.2*max(h1d_true_intChns_electrons))

label_text = f"Inner channels (MC)\nTotal Entries: {int(np.sum(h1d_true_intChns_electrons))}"
ylegend = 0.82

ax.set_xlabel('Deposited energy [MeV]', fontsize=14) 
ax.set_ylabel('[#]', fontsize=14)  

ax.grid(axis='y')  

bbox_props = dict(boxstyle='square', facecolor='white', alpha=0.5, \
          edgecolor='black', linewidth=1)
ax.text(0.98, ylegend, label_text, transform=ax.transAxes,\
        bbox=bbox_props,ha='right')
    
# Add a legend to the plot
ax.legend(fontsize=12)

# Save the plot to a file and show it
plt.savefig(f"Output/{plot_title}.pdf")
plt.show()

###############################################################################

fig, ax = plt.subplots(figsize=figsize)

h1d_Diff_ElMC_ElFD = (h1d_true_intChns_electrons - h1d_fd_intChns_electrons)

ax.hist(h1d_photons['chn4']['bin_edge'][:-1],\
        len(h1d_photons['chn4']['bin_edge'][:-1]),\
        weights=h1d_Diff_ElMC_ElFD,\
        color='violet', label='Electrons MC - FDextrap.')

plot_title = 'h1d_Diff_ElMC_ElFD'
plt.ylim(-400,500)

# label_text = f"Inner channels (MC)\nTotal Entries: {int(np.sum(h1d_true_intChns_electrons))}"
ylegend = 0.82

ax.set_xlabel('Deposited energy [MeV]', fontsize=14) 
ax.set_ylabel('[#]', fontsize=14)  

ax.grid(axis='y')  

# bbox_props = dict(boxstyle='square', facecolor='white', alpha=0.5, \
#           edgecolor='black', linewidth=1)
# ax.text(0.98, ylegend, label_text, transform=ax.transAxes,\
#         bbox=bbox_props,ha='right')
    
# Add a legend to the plot
ax.legend(fontsize=12)

# Save the plot to a file and show it
plt.savefig(f"Output/{plot_title}.pdf")
plt.show()

###############################################################################

fig, ax = plt.subplots(figsize=figsize)

h1d_Accuracy_ElMC_ElFD = np.divide(h1d_Diff_ElMC_ElFD, h1d_true_intChns_electrons,\
                  out=np.zeros_like(h1d_Diff_ElMC_ElFD), where=h1d_true_intChns_electrons!=0)

ax.hist(h1d_photons['chn4']['bin_edge'][:-1],\
        len(h1d_photons['chn4']['bin_edge'][:-1]),\
        weights=h1d_Accuracy_ElMC_ElFD,\
        color='fuchsia', label='Electrons (MC - FDextrap.)/MC')

plot_title = 'h1d_Accuracy_ElMC_ElFD'
plt.ylim(-50,50)

# label_text = f"Inner channels (MC)\nTotal Entries: {int(np.sum(h1d_true_intChns_electrons))}"
ylegend = 0.82

ax.set_xlabel('Deposited energy [MeV]', fontsize=14) 
ax.set_ylabel('[a.u.]', fontsize=14)  

ax.grid(axis='y')  

# bbox_props = dict(boxstyle='square', facecolor='white', alpha=0.5, \
#           edgecolor='black', linewidth=1)
# ax.text(0.98, ylegend, label_text, transform=ax.transAxes,\
#         bbox=bbox_props,ha='right')
    
# Add a legend to the plot
ax.legend(fontsize=12)

# Save the plot to a file and show it
plt.savefig(f"Output/{plot_title}.pdf")
plt.show()

