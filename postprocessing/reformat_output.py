# %% 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import os
import matplotlib.ticker as ticker 
from pathlib import Path
from matplotlib import cm

# %%
def extract_number(time_string):
    number_string = time_string.split()[-1]  # Get the last part of the string
    return float(number_string)  # Convert to float

# %%
# double check the zone id befor plotting

# Load the data
# Reads OUTPUT_ELEME.csv (TOUGH3) and OUTPUT_Flac.csv (written by flac_output_d.py) from one
# model's 3_coupling folder and writes TF_full.parquet (TOUGH + FLAC3D, TOUGH output times) and
# F_clean.parquet (FLAC3D only, all coupling steps), which the figure notebook reads.
#
# Two ways to run it (needs pandas + pyarrow, see requirements.txt):
#   - cell by cell (e.g. VS Code / Jupyter): set MODEL_RUN_DIR below and run the cells;
#   - from a terminal: python reformat_output.py <path/to/model>/3_coupling
import sys

MODEL_RUN_DIR = '../models_code/02_homogf/3_coupling'   # edit this when running cell by cell

if len(sys.argv) > 1 and Path(sys.argv[1]).is_dir():   # command-line argument takes priority
    MODEL_RUN_DIR = sys.argv[1]
base_path = Path(MODEL_RUN_DIR)
print(f"Reformatting output in: {base_path.resolve()}")

# File paths
eleme_file = base_path / 'OUTPUT_ELEME.csv'
flac_file = base_path / 'OUTPUT_Flac.csv'


try:
    df_T = pd.read_csv(eleme_file, low_memory=False)
    df_F = pd.read_csv(flac_file)
except FileNotFoundError as e:
    print(f"Error: {e}")
except pd.errors.EmptyDataError as e:
    print("One of the CSV files is empty.")
except pd.errors.ParserError as e:
    print("Error parsing one of the CSV files.")
else:
    print("CSV files loaded successfully.")

# %%
time_rows_F = df_F[df_F[df_F.columns[0]].str.contains("TIME", na=False)].index
temp = df_F.iloc[time_rows_F, 0]
a = temp.apply(extract_number)

time_rows_T = df_T[df_T[df_T.columns[0]].str.contains("TIME", na=False)].index
temp_T = df_T.iloc[time_rows_T[:-1], 0]
b = temp_T.apply(extract_number)

common_mask = a.isin(b)
common_ids4F = a.index[common_mask]
time_rows_T = temp_T.index
# num_cells = time_rows_T[1] - time_rows_T[0] - 1  # the total number of cells
num_cells = time_rows_F[1] - time_rows_F[0] - 1 # using FLAC3D so there's no added cells

# %% 
## combine the output from TOUGH and FLAC
all_combined = [] 

for i in range(len(time_rows_T)):
    # Get the time step line
    time_label = b.iloc[i] 

    T_start_idx = time_rows_T[i] + 1
    T_end_idx = T_start_idx + num_cells
    # Slice the data rows for the current time step
    temp_T = df_T.iloc[T_start_idx:T_end_idx].reset_index(drop=True)
    temp_T.drop(temp_T.index[-1], inplace=True) # drop the value for the injection cell

    F_start_idx = common_ids4F[i] + 1
    F_end_idx = F_start_idx + num_cells
    # Slice the data rows for the current time step
    temp_F = df_F.iloc[F_start_idx:F_end_idx].reset_index(drop=True)
    temp_F.drop(columns=['ELEM', 'X', 'Y', 'Z'], inplace=True)

    temp_T.columns = temp_T.columns.str.strip()
    temp_T['ELEM'] = temp_T['ELEM'].astype(str)
    temp_T['INDEX'] = temp_T['INDEX'].astype(int)
    cols_to_convert = temp_T.columns[2:]
    temp_T[cols_to_convert] = temp_T[cols_to_convert].apply(pd.to_numeric, errors='coerce')

    combined_data = pd.concat([temp_T, temp_F], axis=1)

    combined_data['Time'] = time_label

    # Append to list
    all_combined.append(combined_data)

full_combined_df = pd.concat(all_combined, ignore_index=True)


# output_file = base_path / "TF_full.csv"
# full_combined_df.to_csv(output_file, index=False)

output_file = base_path / "TF_full.parquet"
# cF_df.to_csv(output_file, index=False)
full_combined_df.to_parquet(output_file, engine='pyarrow', compression='snappy')

# %%
# get the FLAC output, which has more time entries => more suitable for plotting friction coefficient
clean_F = [] 

for i in range(len(a)):
    # Get the time step value
    time_label = a.iloc[i] 

    F_start_idx = time_rows_F[i] + 1
    F_end_idx = F_start_idx + num_cells
    # Slice the data rows for the current time step
    temp_F = df_F.iloc[F_start_idx:F_end_idx].reset_index(drop=True)

    temp_F['ELEM'] = temp_F['ELEM'].astype(str)
    cols_to_convert = temp_F.columns[1:]
    temp_F[cols_to_convert] = temp_F[cols_to_convert].apply(pd.to_numeric, errors='coerce')

    temp_F['Time'] = time_label
    temp_F['ROCK'] = temp_T['ROCK']

    # Append to list
    clean_F.append(temp_F)

cF_df = pd.concat(clean_F, ignore_index=True)

# output_file = base_path / "F_clean.csv"
# full_combined_df.to_csv(output_file, index=False)

output_file = base_path / "F_clean.parquet"
# cF_df.to_csv(output_file, index=False)
cF_df.to_parquet(output_file, engine='pyarrow', compression='snappy')
# %%
