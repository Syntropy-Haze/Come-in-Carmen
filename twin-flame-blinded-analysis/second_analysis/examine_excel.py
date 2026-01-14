#!/usr/bin/env python3
"""
Examine Excel file structure to properly extract timestamps
"""

import pandas as pd
import numpy as np

# Read the Excel file
df = pd.read_excel('COPY_timestamps_flame_play.xlsm', sheet_name=0)

print("="*80)
print("EXCEL FILE STRUCTURE EXAMINATION")
print("="*80)

print(f"\nShape: {df.shape}")
print(f"\nColumns: {list(df.columns)}")

# Show all data with better formatting
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', 30)
pd.set_option('display.max_rows', None)

print("\n" + "="*80)
print("FULL DATAFRAME:")
print("="*80)
print(df)

# Let's examine each column more carefully
print("\n" + "="*80)
print("COLUMN BY COLUMN ANALYSIS:")
print("="*80)

for col in df.columns:
    print(f"\n{col}:")
    print("-" * 40)
    non_null = df[col].dropna()
    if len(non_null) > 0:
        for i, val in enumerate(non_null):
            print(f"  Row {df[df[col] == val].index[0]}: {val}")
    else:
        print("  [All null]")

# Let's look for the validated timestamp columns specifically
print("\n" + "="*80)
print("LOOKING FOR VALIDATED TIMESTAMPS:")
print("="*80)

# Column F (index 5) should be Run 1 validated timestamps
print("\nColumn F (Unnamed: 5) - Run 1:")
col5_data = df.iloc[:, 5].dropna()
for idx, val in col5_data.items():
    if pd.notna(val):
        print(f"  Row {idx}: {val}")

# Column I (index 8) should be Run 2 validated timestamps
print("\nColumn I (Unnamed: 8) - Run 2:")
col8_data = df.iloc[:, 8].dropna()
for idx, val in col8_data.items():
    if pd.notna(val):
        print(f"  Row {idx}: {val}")

# Let's pair markers with timestamps
print("\n" + "="*80)
print("PAIRING MARKERS WITH TIMESTAMPS:")
print("="*80)

markers_col = df.iloc[:, 1]  # Column B - markers
run1_times = df.iloc[:, 5]  # Column F - Run 1 validated times
run2_times = df.iloc[:, 8]  # Column I - Run 2 validated times

print("\nRun 1 Marker-Timestamp Pairs:")
for i in range(len(df)):
    if pd.notna(markers_col[i]) and pd.notna(run1_times[i]):
        marker = markers_col[i]
        time = run1_times[i]
        # Check if it's a valid timestamp (HH:MM:SS format)
        if isinstance(time, str) and ':' in str(time) and len(str(time)) == 8:
            print(f"  {marker:30s} -> {time}")

print("\nRun 2 Marker-Timestamp Pairs:")
for i in range(len(df)):
    if pd.notna(markers_col[i]) and pd.notna(run2_times[i]):
        marker = markers_col[i]
        time = run2_times[i]
        # Check if it's a valid timestamp (HH:MM:SS format)
        if isinstance(time, str) and ':' in str(time) and len(str(time)) == 8:
            print(f"  {marker:30s} -> {time}")