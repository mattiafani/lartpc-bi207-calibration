import pandas as pd
from tqdm import tqdm
from inc.settings import NCC, NI1, NI2
from inc.csv_to_charge_histo import csv_to_charge_histo


def find_non_adjacent_most_frequent(df, category):
    # Find the two non-adjacent most frequent strips in Induction planes
    most_frequent = df[df['Strip plane'] == category]['strip_nr'].value_counts().nlargest(2).index.tolist()
    if abs(most_frequent[0] - most_frequent[1]) < 3:
        most_frequent = df[df['Strip plane'] == category]['strip_nr'].value_counts().nlargest(3).index.tolist()
        most_frequent = [x for i, x in enumerate(most_frequent) if i != 1]
        if abs(most_frequent[0] - most_frequent[1]) < 3:
            most_frequent = df[df['Strip plane'] ==
                               category]['strip_nr'].value_counts().nlargest(3).index.tolist()
            most_frequent = [x for i, x in enumerate(most_frequent) if i != 1]
    return sorted(most_frequent)


###############################################################################
# Find position of top and bottom source
###############################################################################

# Load the CSV file into a DataFrame
# df = pd.read_csv('./Plots/20230722/20230722_CR_5_18_20_BH_32_36_20_dev.csv')

plot_dir = './Plots'
raw_data_folder_name = '20230723'
csv_file_name = '20230723_CR_5_18_20_BH_32_36_20'

df = pd.read_csv(f"{plot_dir}/{raw_data_folder_name}/{csv_file_name}.csv")

# Define the strip planes
plane_labels = ['Collection ', 'Induction 1 ', 'Induction 2 ']
planes = [0, NCC, NCC+NI1, NCC+NI1+NI2]

# Create a new column to account for the strip plane classification of each row
df['Strip plane'] = pd.cut(df['strip_nr'], bins=planes, labels=plane_labels)

# Find the most frequent strip in Collection plane
most_frequent_C = df[df['Strip plane'] == 'Collection ']['strip_nr'].mode().values[0]

# Find the two non-adjacent most frequent strips in I1, I2
most_frequent_I1 = find_non_adjacent_most_frequent(df, 'Induction 1 ')
most_frequent_I2 = find_non_adjacent_most_frequent(df, 'Induction 2 ')

# Define the strips overlapping the top and bottom source (to be reviewed at each data taking campaign)
C_strip = most_frequent_C
I1_strip_Top, I1_strip_Bot = most_frequent_I1
I2_strip_Top, I2_strip_Bot = most_frequent_I2
print("C_strip:", C_strip)
print("I1_strip_Top:", I1_strip_Top)
print("I1_strip_Bot:", I1_strip_Bot)
print("I2_strip_Top:", I2_strip_Top)
print("I2_strip_Bot:", I2_strip_Bot)

###############################################################################
# Find coincidences
###############################################################################

# Set a time difference threshold for coincidences
time_diff_threshold = 30

# for c_strip_index in range(C_strip-4, C_strip+4):
for c_strip_index in range(NCC):

    top_coincidences = []
    bottom_coincidences = []

    # Iterate through each unique event number
    for evt_nr in tqdm(df['evt_nr'].unique(), desc=f"Searching for coincidences on strip {c_strip_index}..."):
        # Extract rows for the current event number
        event_rows = df[df['evt_nr'] == evt_nr]

        # Filter rows based on strip_nr
        c_rows = event_rows[event_rows['strip_nr'] == c_strip_index]
        i1_top_rows = event_rows[event_rows['strip_nr'] == I1_strip_Top]
        i2_top_rows = event_rows[event_rows['strip_nr'] == I2_strip_Top]
        i1_bot_rows = event_rows[event_rows['strip_nr'] == I1_strip_Bot]
        i2_bot_rows = event_rows[event_rows['strip_nr'] == I2_strip_Bot]

        for c_row in c_rows.iterrows():
            for i1_top_row in i1_top_rows.iterrows():
                for i2_top_row in i2_top_rows.iterrows():
                    # Calculate differences for Top source coincidences
                    diff_i1_top_c = (c_row[1]['evt_pk_t'] - i1_top_row[1]['evt_en_t'])
                    diff_i2_top_c = (c_row[1]['evt_pk_t'] - i2_top_row[1]['evt_en_t'])

                    if 0 < diff_i1_top_c < time_diff_threshold and 0 < diff_i2_top_c < time_diff_threshold:
                        top_coincidences.append([evt_nr, c_strip_index, I1_strip_Top, I2_strip_Top,
                                                 c_row[1]['evt_pk_t'], c_row[1]['evt_en_t'], i1_top_row[1]['evt_en_t'], i2_top_row[1]['evt_en_t'],
                                                 c_row[1]['charge'], c_row[1]['charge_cluster']])

        for c_row in c_rows.iterrows():
            for i1_bot_row in i1_bot_rows.iterrows():
                for i2_bot_row in i2_bot_rows.iterrows():
                    # Calculate differences for Bottom source coincidences
                    diff_i1_bot_c = (c_row[1]['evt_pk_t'] - i1_bot_row[1]['evt_en_t'])
                    diff_i2_bot_c = (c_row[1]['evt_pk_t'] - i2_bot_row[1]['evt_en_t'])

                    if 0 < diff_i1_bot_c < time_diff_threshold and 0 < diff_i2_bot_c < time_diff_threshold:
                        bottom_coincidences.append([evt_nr, c_strip_index, I1_strip_Bot, I2_strip_Bot,
                                                    c_row[1]['evt_pk_t'], c_row[1]['evt_en_t'], i1_bot_row[1]['evt_en_t'], i2_bot_row[1]['evt_en_t'],
                                                    c_row[1]['charge'], c_row[1]['charge_cluster']])

    # Create DataFrames for top and bottom coincidences
    top_coincidence_df = pd.DataFrame(top_coincidences, columns=['evt_nr', 'c_strip_index', 'I1_strip', 'I2_strip',
                                                                 'evt_pk_t_C', 'evt_en_t_C', 'evt_en_t_I1', 'evt_en_t_I2', 'charge_C', 'charge_cluster'])
    bottom_coincidence_df = pd.DataFrame(bottom_coincidences, columns=['evt_nr', 'c_strip_index', 'I1_strip', 'I2_strip',
                                                                       'evt_pk_t_C', 'evt_en_t_C', 'evt_en_t_I1', 'evt_en_t_I2', 'charge_C', 'charge_cluster'])

    # Save DataFrames as CSV files
    if c_strip_index < 10:
        filename_strip_index = '0'+str(c_strip_index)
    else:
        filename_strip_index = str(c_strip_index)

    top_coincidence_df.to_csv(
        f'{plot_dir}/{raw_data_folder_name}/{csv_file_name}_Coincidences_Top_strip_{filename_strip_index}.csv', index=False)

    bottom_coincidence_df.to_csv(
        f'{plot_dir}/{raw_data_folder_name}/{csv_file_name}_Coincidences_Bot_strip_{filename_strip_index}.csv', index=False)


###############################################################################
# Draw plots
###############################################################################

# csv_to_charge_histo(plot_dir, raw_data_folder_name, csv_file_name)
