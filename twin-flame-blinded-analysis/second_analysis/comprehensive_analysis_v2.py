#!/usr/bin/env python3
"""
Comprehensive Blinded Analysis of Twin Flame Luminosity Data - Version 2
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

def parse_timestamp_file_v2(file_path):
    """Parse the timestamp Excel file to extract experimental markers - improved version"""
    print(f"\n{'='*70}")
    print("PARSING TIMESTAMP DATA (V2)")
    print(f"{'='*70}")

    df = pd.read_excel(file_path, sheet_name=0)

    # The structure is:
    # Column 1 (Unnamed: 1): Markers
    # Column 3 (Timestamp...): Run 1 timestamps (column header says use column F which is Unnamed: 5)
    # Column 5 (Unnamed: 5): Run 1 validated timestamps (HH:MM:SS format)
    # Column 8 (Unnamed: 8): Run 2 validated timestamps (HH:MM:SS format)

    # Get markers from column 1
    all_markers = df['Unnamed: 1'].tolist()

    # Get Run 1 timestamps from column 5 (validated)
    run1_times_col = df['Unnamed: 5'].tolist()

    # Get Run 2 timestamps from column 8 (validated)
    run2_times_col = df['Unnamed: 8'].tolist()

    # Build Run 1 data
    run1_markers = []
    run1_timestamps = []
    for i, marker in enumerate(all_markers):
        if pd.notna(marker) and isinstance(marker, str):
            if any(x in marker for x in ['Vid Recording', 'Light', 'Control', 'Double']):
                if i < len(run1_times_col) and pd.notna(run1_times_col[i]):
                    time_val = run1_times_col[i]
                    if isinstance(time_val, str) and ':' in time_val and len(time_val) == 8:
                        run1_markers.append(marker)
                        run1_timestamps.append(time_val)

    # Build Run 2 data
    run2_markers = []
    run2_timestamps = []
    for i, marker in enumerate(all_markers):
        if pd.notna(marker) and isinstance(marker, str):
            if any(x in marker for x in ['Vid Recording', 'Light', 'Control', 'Double']):
                if i < len(run2_times_col) and pd.notna(run2_times_col[i]):
                    time_val = run2_times_col[i]
                    if isinstance(time_val, str) and ':' in time_val and len(time_val) == 8:
                        run2_markers.append(marker)
                        run2_timestamps.append(time_val)

    print("\nRun 1 Experimental Timeline (validated times):")
    for marker, time in zip(run1_markers, run1_timestamps):
        print(f"  {marker:30s} : {time}")

    print(f"\nRun 2 Experimental Timeline (validated times):")
    for marker, time in zip(run2_markers, run2_timestamps):
        print(f"  {marker:30s} : {time}")

    # Important notes from the data
    print("\n" + "="*70)
    print("IMPORTANT EXPERIMENTAL NOTES:")
    print("  Run 1: Condition A (1st Light) applied first, then Condition B (2nd Light)")
    print("  Run 2: Condition B (2nd Light) applied first (REVERSED from Run 1)")
    print("  Note: There are lag periods between conditions (for recording/switching)")
    print("="*70)

    return {
        'run1': {'markers': run1_markers, 'timestamps': run1_timestamps},
        'run2': {'markers': run2_markers, 'timestamps': run2_timestamps}
    }

def load_lightmeter_data(file_path):
    """Load and parse light meter CSV data"""
    df = pd.read_csv(file_path)
    print(f"\nLoaded {file_path}:")
    print(f"  Shape: {df.shape}")
    print(f"  Duration: {df['time'].max():.2f} seconds")
    print(f"  Sample rate: ~{len(df)/df['time'].max():.1f} Hz")
    print(f"  Lux range: {df['lux'].min():.2f} - {df['lux'].max():.2f}")
    return df

def synchronize_data_v2(lightmeter_df, filename, markers, timestamps):
    """Synchronize light meter data with experimental conditions - improved version"""
    # Extract end time from filename
    parts = filename.split('_')
    end_time_str = f"{parts[1]} {parts[2].replace('-', ':')}"
    end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")

    # Calculate start time
    duration = lightmeter_df['time'].max()
    start_time = end_time - timedelta(seconds=duration)

    print(f"\n  Synchronization info:")
    print(f"    Recording start: {start_time.strftime('%H:%M:%S')}")
    print(f"    Recording end: {end_time.strftime('%H:%M:%S')}")
    print(f"    Duration: {duration:.2f} seconds")

    # Rename columns for consistency
    lightmeter_df = lightmeter_df.rename(columns={'time': 'Time (s)', 'lux': 'Illuminance (lux)'})

    # Add absolute timestamps
    lightmeter_df['Timestamp'] = pd.to_datetime(start_time) + pd.to_timedelta(lightmeter_df['Time (s)'], unit='s')

    # Initialize all as 'Transition' (lag periods)
    lightmeter_df['Condition'] = 'Transition'

    # Parse timestamps and assign conditions
    for j in range(len(markers)):
        marker = markers[j]
        marker_time = datetime.strptime(f"2026-01-12 {timestamps[j]}", "%Y-%m-%d %H:%M:%S")

        # Control periods
        if 'Start Control' in marker:
            control_num = marker.split()[-1]
            for k in range(j+1, len(markers)):
                if f'End Control {control_num}' in markers[k]:
                    end_time_marker = datetime.strptime(f"2026-01-12 {timestamps[k]}", "%Y-%m-%d %H:%M:%S")
                    mask = (lightmeter_df['Timestamp'] >= marker_time) & (lightmeter_df['Timestamp'] <= end_time_marker)
                    lightmeter_df.loc[mask, 'Condition'] = f'Control_{control_num}'
                    break

        # Condition A (1st Light)
        elif 'Start 1st Light' in marker:
            for k in range(j+1, len(markers)):
                if 'End 1st Light' in markers[k]:
                    end_time_marker = datetime.strptime(f"2026-01-12 {timestamps[k]}", "%Y-%m-%d %H:%M:%S")
                    mask = (lightmeter_df['Timestamp'] >= marker_time) & (lightmeter_df['Timestamp'] <= end_time_marker)
                    lightmeter_df.loc[mask, 'Condition'] = 'Condition_A'
                    break

        # Condition B (2nd Light)
        elif 'Start 2nd Light' in marker:
            for k in range(j+1, len(markers)):
                if 'End 2nd Light' in markers[k]:
                    end_time_marker = datetime.strptime(f"2026-01-12 {timestamps[k]}", "%Y-%m-%d %H:%M:%S")
                    mask = (lightmeter_df['Timestamp'] >= marker_time) & (lightmeter_df['Timestamp'] <= end_time_marker)
                    lightmeter_df.loc[mask, 'Condition'] = 'Condition_B'
                    break

        # Condition AB (Both Lights)
        elif 'Start 1st + 2nd Lights' in marker:
            for k in range(j+1, len(markers)):
                if 'End Double Lights' in markers[k]:
                    end_time_marker = datetime.strptime(f"2026-01-12 {timestamps[k]}", "%Y-%m-%d %H:%M:%S")
                    mask = (lightmeter_df['Timestamp'] >= marker_time) & (lightmeter_df['Timestamp'] <= end_time_marker)
                    lightmeter_df.loc[mask, 'Condition'] = 'Condition_AB'
                    break

    # Print condition distribution
    condition_counts = lightmeter_df['Condition'].value_counts()
    print(f"\n  Condition distribution:")
    for cond in sorted(condition_counts.index):
        count = condition_counts[cond]
        print(f"    {cond:15s}: {count:5d} samples ({count/len(lightmeter_df)*100:.1f}%)")

    return lightmeter_df

def analyze_conditions(datasets):
    """Analyze luminosity changes under different conditions"""
    print(f"\n{'='*70}")
    print("CONDITION EFFECTS ANALYSIS")
    print(f"{'='*70}")

    results = {}

    for key, df in datasets.items():
        print(f"\n{key.upper()} Analysis:")
        print("-" * 50)

        # Get control baseline (combine all control periods)
        control_data = df[df['Condition'].str.contains('Control', na=False)]['Illuminance (lux)']
        if len(control_data) > 0:
            control_mean = control_data.mean()
            control_std = control_data.std()
            print(f"  Baseline (Control): {control_mean:.2f} ± {control_std:.2f} lux")

            # Analyze each condition
            for condition in ['Condition_A', 'Condition_B', 'Condition_AB']:
                cond_data = df[df['Condition'] == condition]['Illuminance (lux)']
                if len(cond_data) > 0:
                    cond_mean = cond_data.mean()
                    cond_std = cond_data.std()
                    change_pct = ((cond_mean - control_mean) / control_mean) * 100

                    # Statistical test
                    t_stat, p_value = ttest_ind(control_data, cond_data)

                    print(f"  {condition}: {cond_mean:.2f} ± {cond_std:.2f} lux")
                    print(f"    Change from baseline: {change_pct:+.1f}%")
                    print(f"    Statistical significance: p = {p_value:.4f} {'***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else 'ns'}")

            results[key] = {
                'control_mean': control_mean,
                'control_std': control_std
            }

    return results

def analyze_correlations(datasets):
    """Analyze correlations between Sensor A and B"""
    print(f"\n{'='*70}")
    print("SENSOR CORRELATION ANALYSIS")
    print(f"{'='*70}")

    # Analyze Run 1
    if 'run1_sensorA' in datasets and 'run1_sensorB' in datasets:
        print("\nRun 1 - Sensor A vs B Correlations:")
        print("-" * 50)

        dfA = datasets['run1_sensorA']
        dfB = datasets['run1_sensorB']

        # Merge on timestamp
        merged = pd.merge(dfA[['Timestamp', 'Illuminance (lux)', 'Condition']],
                         dfB[['Timestamp', 'Illuminance (lux)']],
                         on='Timestamp',
                         suffixes=('_A', '_B'),
                         how='inner')

        # Overall correlation
        if len(merged) > 0:
            corr_pearson, p_pearson = pearsonr(merged['Illuminance (lux)_A'], merged['Illuminance (lux)_B'])
            corr_spearman, p_spearman = spearmanr(merged['Illuminance (lux)_A'], merged['Illuminance (lux)_B'])

            print(f"  Overall Pearson correlation: r = {corr_pearson:.4f} (p = {p_pearson:.4f})")
            print(f"  Overall Spearman correlation: ρ = {corr_spearman:.4f} (p = {p_spearman:.4f})")

            # Correlation by condition
            print("\n  Correlation by condition:")
            for condition in merged['Condition'].unique():
                if 'Transition' not in condition:
                    cond_data = merged[merged['Condition'] == condition]
                    if len(cond_data) > 10:  # Need enough data points
                        corr, p = pearsonr(cond_data['Illuminance (lux)_A'], cond_data['Illuminance (lux)_B'])
                        print(f"    {condition}: r = {corr:.4f} (p = {p:.4f})")

    # Analyze Run 2
    if 'run2_sensorA' in datasets and 'run2_sensorB' in datasets:
        print("\nRun 2 - Sensor A vs B Correlations:")
        print("-" * 50)

        dfA = datasets['run2_sensorA']
        dfB = datasets['run2_sensorB']

        # Merge on timestamp
        merged = pd.merge(dfA[['Timestamp', 'Illuminance (lux)', 'Condition']],
                         dfB[['Timestamp', 'Illuminance (lux)']],
                         on='Timestamp',
                         suffixes=('_A', '_B'),
                         how='inner')

        # Overall correlation
        if len(merged) > 0:
            corr_pearson, p_pearson = pearsonr(merged['Illuminance (lux)_A'], merged['Illuminance (lux)_B'])
            corr_spearman, p_spearman = spearmanr(merged['Illuminance (lux)_A'], merged['Illuminance (lux)_B'])

            print(f"  Overall Pearson correlation: r = {corr_pearson:.4f} (p = {p_pearson:.4f})")
            print(f"  Overall Spearman correlation: ρ = {corr_spearman:.4f} (p = {p_spearman:.4f})")

            # Correlation by condition
            print("\n  Correlation by condition:")
            for condition in merged['Condition'].unique():
                if 'Transition' not in condition:
                    cond_data = merged[merged['Condition'] == condition]
                    if len(cond_data) > 10:
                        corr, p = pearsonr(cond_data['Illuminance (lux)_A'], cond_data['Illuminance (lux)_B'])
                        print(f"    {condition}: r = {corr:.4f} (p = {p:.4f})")

def main():
    """Main analysis pipeline"""
    print("\n" + "="*70)
    print("COMPREHENSIVE BLINDED FLAME LUMINOSITY ANALYSIS V2")
    print("="*70)

    # 1. Parse timestamps
    timestamp_data = parse_timestamp_file_v2('COPY_timestamps_flame_play.xlsm')

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
        df = synchronize_data_v2(df, file,
                                timestamp_data[run]['markers'],
                                timestamp_data[run]['timestamps'])

        # Store with a meaningful key
        if 'CandleA' in file:
            key = f"{run}_sensorA"
        else:
            key = f"{run}_sensorB"

        datasets[key] = df

    # 3. Analyze condition effects
    results = analyze_conditions(datasets)

    # 4. Analyze correlations
    analyze_correlations(datasets)

    # 5. Save processed data
    print(f"\n{'='*70}")
    print("SAVING PROCESSED DATA")
    print(f"{'='*70}")

    for key, df in datasets.items():
        output_file = f"processed_{key}.csv"
        df.to_csv(output_file, index=False)
        print(f"  Saved: {output_file}")

    return datasets, timestamp_data, results

if __name__ == "__main__":
    datasets, timestamp_data, results = main()