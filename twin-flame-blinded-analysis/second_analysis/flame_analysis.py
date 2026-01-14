#!/usr/bin/env python3
"""
Blinded Analysis of Twin Flame Luminosity Data
Author: Claude
Date: 2026-01-13
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from scipy import stats
from scipy.signal import correlate, correlation_lags
import warnings
warnings.filterwarnings('ignore')

# Set style for visualizations
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def load_timestamp_data(file_path):
    """Load and parse the timestamp/marker data from Excel file"""
    print(f"\n{'='*60}")
    print("Loading timestamp data...")
    print(f"{'='*60}")

    # Read the Excel file
    df = pd.read_excel(file_path, sheet_name=0)
    print(f"\nExcel file shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print("\nFirst few rows:")
    print(df.head(10))

    return df

def parse_timestamps(df):
    """Parse the timestamp data to extract markers for both runs"""
    print(f"\n{'='*60}")
    print("Parsing timestamp markers...")
    print(f"{'='*60}")

    # Let's look at the entire dataframe to understand structure
    print("\nFull dataframe:")
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 50)
    print(df)

    # Based on README, column 8 (Unnamed: 8) should have the timestamps for Run 2
    # And column near the middle should have timestamps for Run 1
    # Let's extract the two runs
    print("\n\nExtracting Run 1 data (columns 1-3):")
    run1_markers = df['Unnamed: 1'].dropna()
    run1_timestamps = df['Timestamp (note - rounds to nearest second)'].dropna()

    print("\nRun 1 Markers:")
    for i, marker in enumerate(run1_markers):
        print(f"{i}: {marker}")

    print("\n\nExtracting Run 2 data (columns 5-8):")
    run2_markers = df['Unnamed: 5'].dropna()
    run2_timestamps = df['Unnamed: 8'].dropna()

    print("\nRun 2 Markers:")
    for i, marker in enumerate(run2_markers):
        print(f"{i}: {marker}")

    return df

# Start the analysis
if __name__ == "__main__":
    # File paths
    timestamp_file = "COPY_timestamps_flame_play.xlsm"

    # Load timestamp data
    timestamp_df = load_timestamp_data(timestamp_file)

    # Parse timestamps
    parsed_timestamps = parse_timestamps(timestamp_df)