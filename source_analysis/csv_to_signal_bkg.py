import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from inc.basic_functions import plot_coincidence_histos
from inc.settings import NCC

plot_dir = './Plots'
raw_data_folder_name = '20230722'
csv_file_name = '20230722_CR_5_18_20_BH_32_36_20'

colors = plt.cm.rainbow(np.linspace(0, 1, NCC))

n_entries = 0

result_file_title = f"{plot_dir}/{raw_data_folder_name}/{csv_file_name}.csv"

# Load the CSV data
df_r = pd.read_csv(result_file_title)

n_entries = df_r['evt_nr'].max()

# Initialize empty DataFrames
signal_df_Top = pd.DataFrame()
backgr_df_Top = pd.DataFrame()

signal_df_Bot = pd.DataFrame()
backgr_df_Bot = pd.DataFrame()

for c_strip_index, color in zip(range(NCC), colors):
    for source in 'Top', 'Bot':

        # Find coincidences csv file
        if c_strip_index < 10:
            filename_strip_index = '0' + str(c_strip_index)
        else:
            filename_strip_index = str(c_strip_index)

        file_title = f"{plot_dir}/{raw_data_folder_name}/{csv_file_name}_Coincidences_{source}_strip_{filename_strip_index}.csv"

        # Load the CSV data
        df = pd.read_csv(file_title)

        if c_strip_index == 16:
            # if c_strip_index == 15 or c_strip_index == 16:
            if source == 'Top':
                signal_df_Top = pd.concat([signal_df_Top, df['charge_C']], ignore_index=True)
            if source == 'Bot':
                signal_df_Bot = pd.concat([signal_df_Bot, df['charge_C']], ignore_index=True)
        elif 9 < c_strip_index < 22:
            if source == 'Top':
                backgr_df_Top = pd.concat([backgr_df_Top, df['charge_C']], ignore_index=True)
            if source == 'Bot':
                backgr_df_Bot = pd.concat([backgr_df_Bot, df['charge_C']], ignore_index=True)

# Define common plot parameters
bin_size = 20  # You can adjust the bin size as needed
x_range = (0, 1000)  # Set the common x-axis range

# Plot and save signal histogram for the "Top" source as PDF
plt.figure(dpi=100)
signal_counts_Top, signal_bins_Top, _ = plt.hist(signal_df_Top, bins=range(x_range[0], x_range[1] + bin_size, bin_size),
                                                 color='darkorange', alpha=0.7,
                                                 edgecolor='darkorange', linewidth=1.2, rwidth=0.85, density=False, label='Signal (Top)')
plt.xlim(x_range)
plt.xlabel('[ADC*µs]', fontsize=12)
plt.ylabel('[#]', fontsize=12)
plt.title(f'{csv_file_name} - Signal (Top)', fontsize=14)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.legend(fontsize=10)

# Reduce font size of axis tick labels
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)

plt.savefig(f"{plot_dir}/{raw_data_folder_name}/{csv_file_name}_SIGNAL_histogram_Top.pdf")

# Plot and save background histogram for the "Top" source as PDF
plt.figure(dpi=100)
background_counts_Top, background_bins_Top, _ = plt.hist(backgr_df_Top, bins=range(x_range[0], x_range[1] + bin_size, bin_size),
                                                         color='dodgerblue', alpha=0.7,
                                                         edgecolor='dodgerblue', linewidth=1.2, rwidth=0.85, density=False, label='Background (Top)')
plt.xlim(x_range)
plt.xlabel('[ADC*µs]', fontsize=12)
plt.ylabel('[#]', fontsize=12)
plt.title(f'{csv_file_name} - Background (Top)', fontsize=14)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.legend(fontsize=10)

# Reduce font size of axis tick labels
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)

plt.savefig(f"{plot_dir}/{raw_data_folder_name}/{csv_file_name}_BACKGROUND_histogram_Top.pdf")

# Plot and save signal histogram for the "Bottom" source as PDF
plt.figure(dpi=100)
signal_counts_Bot, signal_bins_Bot, _ = plt.hist(signal_df_Bot, bins=range(x_range[0], x_range[1] + bin_size, bin_size),
                                                 color='darkorange', alpha=0.7,
                                                 edgecolor='darkorange', linewidth=1.2, rwidth=0.85, density=False, label='Signal (Bot)')
plt.xlim(x_range)
plt.xlabel('[ADC*µs]', fontsize=12)
plt.ylabel('[#]', fontsize=12)
plt.title(f'{csv_file_name} - Signal (Bottom)', fontsize=14)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.legend(fontsize=10)

# Reduce font size of axis tick labels
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)

plt.savefig(f"{plot_dir}/{raw_data_folder_name}/{csv_file_name}_SIGNAL_histogram_Bot.pdf")

# Plot and save background histogram for the "Bottom" source as PDF
plt.figure(dpi=100)
background_counts_Bot, background_bins_Bot, _ = plt.hist(backgr_df_Bot, bins=range(x_range[0], x_range[1] + bin_size, bin_size),
                                                         color='dodgerblue', alpha=0.7,
                                                         edgecolor='dodgerblue', linewidth=1.2, rwidth=0.85, density=False, label='Background (Bot)')
plt.xlim(x_range)
plt.xlabel('[ADC*µs]', fontsize=12)
plt.ylabel('[#]', fontsize=12)
plt.title(f'{csv_file_name} - Background (Bottom)', fontsize=14)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.legend(fontsize=10)

# Reduce font size of axis tick labels
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)

plt.savefig(f"{plot_dir}/{raw_data_folder_name}/{csv_file_name}_BACKGROUND_histogram_Bot.pdf")

# Find peak bins
# signal_peak_bin = signal_bins[np.argmax(signal_counts)]
# background_peak_bin = background_bins[np.argmax(background_counts)]

print("signal_counts_Top = ", signal_counts_Top)
print("backgr counts_Top = ", background_counts_Top)
print("signal_counts_Bot = ", signal_counts_Bot)
print("backgr counts_Bot = ", background_counts_Bot)

SB_ratio_Top = np.divide(signal_counts_Top, background_counts_Top,
                         out=np.zeros_like(signal_counts_Top), where=background_counts_Top != 0)

SB_ratio_Bot = np.divide(signal_counts_Bot, background_counts_Bot,
                         out=np.zeros_like(signal_counts_Bot), where=background_counts_Bot != 0)

print("SB_ratio_Top = ", SB_ratio_Top)
print("SB_ratio_Bot = ", SB_ratio_Bot)

av_SB_ratio_Top = SB_ratio_Top[np.nonzero(SB_ratio_Top)].mean()
std_SB_ratio_Top = SB_ratio_Top[np.nonzero(SB_ratio_Top)].std()

av_SB_ratio_Bot = SB_ratio_Bot[np.nonzero(SB_ratio_Bot)].mean()
std_SB_ratio_Bot = SB_ratio_Bot[np.nonzero(SB_ratio_Bot)].std()

scaling_factor_Top = av_SB_ratio_Top
scaling_factor_Bot = av_SB_ratio_Bot

print("scaling_factor_Top = ", scaling_factor_Top)
print("scaling_factor_Bot = ", scaling_factor_Bot)

# Create and plot the scaled background histogram for the "Top" source
scaled_bkg_counts_Top = np.multiply(background_counts_Top, scaling_factor_Top)
print("scaled_bkg_counts_Top = ", scaled_bkg_counts_Top)

# Create and plot the scaled background histogram for the "Bottom" source
scaled_bkg_counts_Bot = np.multiply(background_counts_Bot, scaling_factor_Bot)
print("scaled_bkg_counts_Bot = ", scaled_bkg_counts_Bot)

# Calculate the SIGNAL_BKG_SUB histogram for the "Top" source
signal_bkg_sub_hist_Top = np.subtract(signal_counts_Top, background_counts_Top,
                                      out=np.zeros_like(signal_counts_Top), where=background_counts_Top != 0)
print("signal_bkg_sub_hist_Top = ", signal_bkg_sub_hist_Top)

# Calculate the SIGNAL_BKG_SUB histogram for the "Bottom" source
signal_bkg_sub_hist_Bot = np.subtract(signal_counts_Bot, background_counts_Bot,
                                      out=np.zeros_like(signal_counts_Bot), where=background_counts_Bot != 0)
print("signal_bkg_sub_hist_Bot = ", signal_bkg_sub_hist_Bot)

# Plot and save scaled background histogram for the "Top" source as PDF
plt.figure(dpi=100)
plt.bar(background_bins_Top[:-1], scaled_bkg_counts_Top, width=bin_size, color='navy', alpha=0.7,
        edgecolor='navy', linewidth=1.2, label='SCALED_BKG_Top')
plt.xlim(x_range)
plt.xlabel('[ADC*µs]', fontsize=12)
plt.ylabel('[#]', fontsize=12)
plt.title(f'{csv_file_name} - SCALED_BKG (Top)', fontsize=14)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.legend(fontsize=10)

# Plot and save scaled background histogram for the "Bottom" source as PDF
plt.figure(dpi=100)
plt.bar(background_bins_Bot[:-1], scaled_bkg_counts_Bot, width=bin_size, color='navy', alpha=0.7,
        edgecolor='navy', linewidth=1.2, label='SCALED_BKG (Bot)')
plt.xlim(x_range)
plt.xlabel('[ADC*µs]', fontsize=12)
plt.ylabel('[#]', fontsize=12)
plt.title(f'{csv_file_name} - SCALED_BKG (Bottom)', fontsize=14)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.legend(fontsize=10)

# Plot and save the SIGNAL_BKG_SUB histogram for the "Top" source as PDF
plt.figure(dpi=100)
plt.bar(signal_bins_Top[:-1], signal_bkg_sub_hist_Top, width=bin_size, color='limegreen', alpha=0.7,
        edgecolor='limegreen', linewidth=1.2, label='SIGNAL_BKG_SUB (Top)')
plt.xlim(x_range)
plt.xlabel('[ADC*µs]', fontsize=12)
plt.ylabel('[#]', fontsize=12)
plt.title(f'{csv_file_name} - SIGNAL_BKG_SUB (Top)', fontsize=14)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.legend(fontsize=10)

# Plot and save the SIGNAL_BKG_SUB histogram for the "Bottom" source as PDF
plt.figure(dpi=100)
plt.bar(signal_bins_Bot[:-1], signal_bkg_sub_hist_Bot, width=bin_size, color='forestgreen', alpha=0.7,
        edgecolor='forestgreen', linewidth=1.2, label='SIGNAL_BKG_SUB (Bot)')
plt.xlim(x_range)
plt.xlabel('[ADC*µs]', fontsize=12)
plt.ylabel('[#]', fontsize=12)
plt.title(f'{csv_file_name} - SIGNAL_BKG_SUB (Bottom)', fontsize=14)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.legend(fontsize=10)

# Create a histogram comparison plot with filled contours for the "Top" source
plt.figure(dpi=100)
plt.hist(signal_df_Top, bins=range(x_range[0], x_range[1] + bin_size, bin_size), color='darkorange', alpha=0.7,
         edgecolor='darkorange', linewidth=1.2, rwidth=0.85, density=False, label='Signal (Top)', histtype='step', fill=False)
plt.hist(backgr_df_Top, bins=range(x_range[0], x_range[1] + bin_size, bin_size), color='dodgerblue', alpha=0.7,
         edgecolor='dodgerblue', linewidth=1.2, rwidth=0.85, density=False, label='Background (Top)', histtype='step', fill=False)
plt.step(background_bins_Top[:-1], background_counts_Top,
         where='mid', color='navy', alpha=0.7, label='Scaled Background')
plt.legend(fontsize=10)

plt.xlim(x_range)
plt.xlabel('[ADC*µs]', fontsize=12)
plt.ylabel('[#]', fontsize=12)
plt.title(f'{csv_file_name} - Histogram Comparison - Top', fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.legend(fontsize=8)

# Reduce font size of axis tick labels
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)

plt.savefig(f"{plot_dir}/{raw_data_folder_name}/{csv_file_name}_HIST_COMPARISON_Top.pdf")

# Show plots (optional)
plt.show()

# Create a histogram comparison plot with filled contours for the "Bottom" source
plt.figure(dpi=100)
plt.hist(signal_df_Bot, bins=range(x_range[0], x_range[1] + bin_size, bin_size), color='darkorange', alpha=0.7,
         edgecolor='darkorange', linewidth=1.2, rwidth=0.85, density=False, label='Signal (Bottom)', histtype='step', fill=False)
plt.hist(backgr_df_Bot, bins=range(x_range[0], x_range[1] + bin_size, bin_size), color='darkblue', alpha=0.7,
         edgecolor='dodgerblue', linewidth=1.2, rwidth=0.85, density=False, label='Background (Bottom)', histtype='step', fill=False)
plt.step(background_bins_Bot[:-1], scaled_bkg_counts_Bot, where='mid',
         color='navy', alpha=0.7, label='Scaled Background')
plt.legend(fontsize=10)

plt.xlim(x_range)
plt.xlabel('[ADC*µs]', fontsize=12)
plt.ylabel('[#]', fontsize=12)
plt.title(f'{csv_file_name} - Histogram Comparison - Bottom', fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.legend(fontsize=8)

# Reduce font size of axis tick labels
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)

plt.savefig(f"{plot_dir}/{raw_data_folder_name}/{csv_file_name}_HIST_COMPARISON_Bot.pdf")

# Show plots (optional)
plt.show()
