#!/usr/bin/env python3
"""
Comprehensive Blinded Analysis of Twin Flame Luminosity Data
Author: Claude
Date: 2026-01-13
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from scipy import stats
from scipy.signal import correlate, correlation_lags, find_peaks
from scipy.stats import ttest_ind, pearsonr, spearmanr
import warnings
warnings.filterwarnings('ignore')

# Set style for visualizations
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def parse_timestamp_file(file_path):
    """Parse the timestamp Excel file to extract experimental markers"""
    print(f"\n{'='*70}")
    print("PARSING TIMESTAMP DATA")
    print(f"{'='*70}")

    df = pd.read_excel(file_path, sheet_name=0)

    # Extract Run 1 data
    run1_data = []
    markers = df['Unnamed: 1'].dropna().tolist()
    timestamps = df['Timestamp (note - rounds to nearest second)'].dropna().tolist()

    # Skip headers and notes
    valid_indices = []
    for i, marker in enumerate(markers):
        if isinstance(marker, str) and ('Start' in marker or 'End' in marker or 'Recording' in marker or 'Light' in marker):
            valid_indices.append(i)

    # Extract Run 1 timestamps (using column 3)
    run1_markers = []
    run1_times = []
    for i in valid_indices:
        if i < len(markers) and i < len(timestamps):
            marker = markers[i]
            ts = timestamps[i]
            if pd.notna(ts) and ts != 'Check file':
                run1_markers.append(marker)
                run1_times.append(ts)

    # Extract Run 2 timestamps (using column 8)
    run2_times = df['Unnamed: 8'].dropna().tolist()
    # Filter out headers
    run2_times = [t for t in run2_times if isinstance(t, str) and ':' in t and len(t) == 8]

    # Pair Run 2 times with the same markers (they should follow same sequence)
    run2_markers = []
    run2_timestamps = []
    marker_idx = 0
    for i, marker in enumerate(markers):
        if isinstance(marker, str) and ('Start' in marker or 'End' in marker or 'Recording' in marker or 'Light' in marker):
            if marker_idx < len(run2_times):
                run2_markers.append(marker)
                run2_timestamps.append(run2_times[marker_idx])
                marker_idx += 1

    print("\nRun 1 Experimental Timeline:")
    for marker, time in zip(run1_markers, run1_times):
        print(f"  {marker:30s} : {time}")

    print(f"\nRun 2 Experimental Timeline:")
    for marker, time in zip(run2_markers, run2_timestamps):
        print(f"  {marker:30s} : {time}")

    # Note from data:
    print("\n" + "="*70)
    print("IMPORTANT NOTES FROM DATA:")
    print("  Run 1: Condition A (1st Light) applied first, then Condition B (2nd Light)")
    print("  Run 2: Condition B (2nd Light) applied first (REVERSED from Run 1)")
    print("="*70)

    return {
        'run1': {'markers': run1_markers, 'timestamps': run1_times},
        'run2': {'markers': run2_markers, 'timestamps': run2_timestamps}
    }

def load_lightmeter_data(file_path):
    """Load and parse light meter CSV data"""
    df = pd.read_csv(file_path)
    print(f"\nLoaded {file_path}:")
    print(f"  Shape: {df.shape}")
    print(f"  Columns: {list(df.columns)}")
    print(f"  First few rows:")
    print(df.head())
    return df

def parse_time_string(time_str):
    """Convert time string (HH:MM:SS) to datetime object"""
    if isinstance(time_str, str) and ':' in time_str:
        # Handle both HH:MM:SS and full datetime formats
        if len(time_str) == 8:  # HH:MM:SS format
            return datetime.strptime(f"2026-01-12 {time_str}", "%Y-%m-%d %H:%M:%S")
        else:  # Full datetime format
            return pd.to_datetime(time_str)
    return pd.to_datetime(time_str)

def synchronize_data(lightmeter_df, filename, markers, timestamps):
    """Synchronize light meter data with experimental conditions"""
    # Extract end time from filename
    # Format: lightmeter_2026-01-12_HH-MM-SS_...
    parts = filename.split('_')
    end_time_str = f"{parts[1]} {parts[2].replace('-', ':')}"
    end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")

    # Calculate start time (using 'time' column from the CSV)
    duration = lightmeter_df['time'].max()
    start_time = end_time - timedelta(seconds=duration)

    print(f"\n  Light meter recording:")
    print(f"    Start: {start_time}")
    print(f"    End: {end_time}")
    print(f"    Duration: {duration:.2f} seconds")

    # Rename columns for consistency
    lightmeter_df.rename(columns={'time': 'Time (s)', 'lux': 'Illuminance (lux)'}, inplace=True)

    # Add absolute timestamps to lightmeter data
    lightmeter_df['Timestamp'] = pd.to_datetime(start_time) + pd.to_timedelta(lightmeter_df['Time (s)'], unit='s')

    # Parse marker timestamps and add condition labels
    conditions = []
    for i, row_time in enumerate(lightmeter_df['Timestamp']):
        condition = 'Unknown'

        # Check which condition period this timestamp falls into
        for j in range(len(markers)):
            marker = markers[j]
            marker_time = parse_time_string(timestamps[j])

            if 'Start Control' in marker:
                # Find corresponding end
                control_num = marker.split()[-1]
                for k in range(j+1, len(markers)):
                    if f'End Control {control_num}' in markers[k]:
                        end_time = parse_time_string(timestamps[k])
                        if marker_time <= row_time <= end_time:
                            condition = f'Control_{control_num}'
                        break

            elif 'Start 1st Light' in marker:
                for k in range(j+1, len(markers)):
                    if 'End 1st Light' in markers[k]:
                        end_time = parse_time_string(timestamps[k])
                        if marker_time <= row_time <= end_time:
                            condition = 'Condition_A'  # 1st Light = A
                        break

            elif 'Start 2nd Light' in marker:
                for k in range(j+1, len(markers)):
                    if 'End 2nd Light' in markers[k]:
                        end_time = parse_time_string(timestamps[k])
                        if marker_time <= row_time <= end_time:
                            condition = 'Condition_B'  # 2nd Light = B
                        break

            elif 'Start 1st + 2nd Lights' in marker:
                for k in range(j+1, len(markers)):
                    if 'End Double Lights' in markers[k]:
                        end_time = parse_time_string(timestamps[k])
                        if marker_time <= row_time <= end_time:
                            condition = 'Condition_AB'
                        break

        conditions.append(condition)

    lightmeter_df['Condition'] = conditions

    # Count conditions
    condition_counts = lightmeter_df['Condition'].value_counts()
    print(f"\n  Condition distribution:")
    for cond, count in condition_counts.items():
        print(f"    {cond:15s}: {count:5d} samples ({count/len(lightmeter_df)*100:.1f}%)")

    return lightmeter_df

def main():
    """Main analysis pipeline"""
    print("\n" + "="*70)
    print("COMPREHENSIVE BLINDED FLAME LUMINOSITY ANALYSIS")
    print("="*70)

    # 1. Parse timestamps
    timestamp_data = parse_timestamp_file('COPY_timestamps_flame_play.xlsm')

    # 2. Load all light meter files
    print(f"\n{'='*70}")
    print("LOADING LIGHT METER DATA")
    print(f"{'='*70}")

    files = [
        'lightmeter_2026-01-12_00-47-53_TwinFlame1_CandleA.csv',
        'lightmeter_2026-01-12_00-48-13_TwinFlame1_CandleB.csv',
        'lightmeter_2026-01-12_02-11-46_TwinFlame2_CandleA.csv',
        'lightmeter_2026-01-12_02-12-00_TwinFlame2_CandleB.csv'
    ]

    datasets = {}
    for file in files:
        df = load_lightmeter_data(file)
        # Determine which run this belongs to
        if 'TwinFlame1' in file:
            run = 'run1'
        else:
            run = 'run2'

        # Synchronize with timestamps
        print(f"\nSynchronizing {file}...")
        df = synchronize_data(df, file,
                             timestamp_data[run]['markers'],
                             timestamp_data[run]['timestamps'])

        # Store with a meaningful key
        if 'CandleA' in file:
            key = f"{run}_sensorA"
        else:
            key = f"{run}_sensorB"

        datasets[key] = df

    # 3. Analyze baseline statistics
    print(f"\n{'='*70}")
    print("BASELINE STATISTICS (Control Periods)")
    print(f"{'='*70}")

    for key, df in datasets.items():
        control_data = df[df['Condition'].str.contains('Control', na=False)]['Illuminance (lux)']
        if len(control_data) > 0:
            print(f"\n{key}:")
            print(f"  Mean: {control_data.mean():.2f} lux")
            print(f"  Std Dev: {control_data.std():.2f} lux")
            print(f"  Min: {control_data.min():.2f} lux")
            print(f"  Max: {control_data.max():.2f} lux")

    # 4. Analyze condition effects
    print(f"\n{'='*70}")
    print("CONDITION EFFECTS ANALYSIS")
    print(f"{'='*70}")

    for key, df in datasets.items():
        print(f"\n{key} - Mean luminosity by condition:")
        condition_means = df.groupby('Condition')['Illuminance (lux)'].agg(['mean', 'std', 'count'])
        print(condition_means)

    # Save processed data for further analysis
    print(f"\n{'='*70}")
    print("SAVING PROCESSED DATA")
    print(f"{'='*70}")

    for key, df in datasets.items():
        output_file = f"processed_{key}.csv"
        df.to_csv(output_file, index=False)
        print(f"  Saved: {output_file}")

    return datasets, timestamp_data

if __name__ == "__main__":
    datasets, timestamp_data = main()