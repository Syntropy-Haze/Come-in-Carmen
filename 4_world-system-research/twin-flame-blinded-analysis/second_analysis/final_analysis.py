#!/usr/bin/env python3
"""
Final Comprehensive Blinded Analysis of Twin Flame Luminosity Data
Author: Claude
Date: 2026-01-13
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from scipy import stats
from scipy.signal import find_peaks, correlate
from scipy.stats import ttest_ind, pearsonr, spearmanr, mannwhitneyu
import warnings
warnings.filterwarnings('ignore')

# Set style for visualizations
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def parse_timestamps_correctly():
    """Parse the timestamp Excel file with correct structure"""
    print(f"\n{'='*70}")
    print("PARSING EXPERIMENTAL TIMESTAMPS")
    print(f"{'='*70}")

    df = pd.read_excel('COPY_timestamps_flame_play.xlsm', sheet_name=0)

    # Extract markers (column B, starting from row 5)
    markers = df.iloc[5:23, 1].tolist()  # Rows 5-22 contain the actual markers

    # Extract Run 1 timestamps (column F, starting from row 5)
    run1_times = df.iloc[5:23, 5].tolist()

    # Extract Run 2 timestamps (column I, starting from row 5)
    run2_times = df.iloc[5:23, 8].tolist()

    # Build clean lists
    run1_data = []
    run2_data = []

    for i, marker in enumerate(markers):
        if pd.notna(marker) and isinstance(marker, str):
            # Run 1
            if i < len(run1_times) and pd.notna(run1_times[i]):
                time1 = run1_times[i]
                if isinstance(time1, str) and ':' in time1 and len(time1) == 8:
                    run1_data.append((marker, time1))

            # Run 2
            if i < len(run2_times) and pd.notna(run2_times[i]):
                time2 = run2_times[i]
                if isinstance(time2, str) and ':' in time2 and len(time2) == 8:
                    run2_data.append((marker, time2))

    print("\nRun 1 Timeline:")
    for marker, time in run1_data:
        print(f"  {marker:30s} : {time}")

    print("\nRun 2 Timeline:")
    for marker, time in run2_data:
        print(f"  {marker:30s} : {time}")

    print("\n" + "="*70)
    print("EXPERIMENTAL DESIGN NOTES:")
    print("  Run 1: Condition A (1st Light) → Condition B (2nd Light) → AB")
    print("  Run 2: Condition B (2nd Light) → Condition A (1st Light) → AB (REVERSED)")
    print("  Control periods between each condition")
    print("  Transition/lag periods between conditions (for switching)")
    print("="*70)

    return {
        'run1': run1_data,
        'run2': run2_data
    }

def load_and_synchronize(file_path, run_data):
    """Load light meter data and synchronize with experimental conditions"""
    # Load data
    df = pd.read_csv(file_path)

    # Extract end time from filename
    parts = file_path.split('_')
    end_time_str = f"{parts[1]} {parts[2].replace('-', ':')}"
    end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")

    # Calculate start time
    duration = df['time'].max()
    start_time = end_time - timedelta(seconds=duration)

    print(f"\n{file_path}:")
    print(f"  Start: {start_time.strftime('%H:%M:%S')}, End: {end_time.strftime('%H:%M:%S')}")
    print(f"  Duration: {duration:.1f}s, Samples: {len(df)}, Rate: {len(df)/duration:.1f} Hz")

    # Rename columns
    df = df.rename(columns={'time': 'Time (s)', 'lux': 'Illuminance (lux)'})

    # Add absolute timestamps
    df['Timestamp'] = pd.to_datetime(start_time) + pd.to_timedelta(df['Time (s)'], unit='s')

    # Initialize conditions
    df['Condition'] = 'Transition'

    # Assign conditions based on markers
    for i, (marker, time_str) in enumerate(run_data):
        marker_time = datetime.strptime(f"2026-01-12 {time_str}", "%Y-%m-%d %H:%M:%S")

        # Find end marker
        if 'Start Control' in marker:
            control_num = marker.split()[-1]
            for j, (end_marker, end_time_str) in enumerate(run_data[i+1:], i+1):
                if f'End Control {control_num}' in end_marker:
                    end_time = datetime.strptime(f"2026-01-12 {end_time_str}", "%Y-%m-%d %H:%M:%S")
                    mask = (df['Timestamp'] >= marker_time) & (df['Timestamp'] <= end_time)
                    df.loc[mask, 'Condition'] = f'Control_{control_num}'
                    break

        elif 'Start 1st Light' in marker:
            for j, (end_marker, end_time_str) in enumerate(run_data[i+1:], i+1):
                if 'End 1st Light' in end_marker:
                    end_time = datetime.strptime(f"2026-01-12 {end_time_str}", "%Y-%m-%d %H:%M:%S")
                    mask = (df['Timestamp'] >= marker_time) & (df['Timestamp'] <= end_time)

                    # Check which run to determine if this is Condition A or B
                    if 'TwinFlame1' in file_path:  # Run 1: 1st Light = A
                        df.loc[mask, 'Condition'] = 'Condition_A'
                    else:  # Run 2: 1st Light = B (reversed)
                        df.loc[mask, 'Condition'] = 'Condition_B'
                    break

        elif 'Start 2nd Light' in marker:
            for j, (end_marker, end_time_str) in enumerate(run_data[i+1:], i+1):
                if 'End 2nd Light' in end_marker:
                    end_time = datetime.strptime(f"2026-01-12 {end_time_str}", "%Y-%m-%d %H:%M:%S")
                    mask = (df['Timestamp'] >= marker_time) & (df['Timestamp'] <= end_time)

                    # Check which run to determine if this is Condition A or B
                    if 'TwinFlame1' in file_path:  # Run 1: 2nd Light = B
                        df.loc[mask, 'Condition'] = 'Condition_B'
                    else:  # Run 2: 2nd Light = A (reversed)
                        df.loc[mask, 'Condition'] = 'Condition_A'
                    break

        elif 'Start 1st + 2nd Lights' in marker:
            for j, (end_marker, end_time_str) in enumerate(run_data[i+1:], i+1):
                if 'End Double Lights' in end_marker:
                    end_time = datetime.strptime(f"2026-01-12 {end_time_str}", "%Y-%m-%d %H:%M:%S")
                    mask = (df['Timestamp'] >= marker_time) & (df['Timestamp'] <= end_time)
                    df.loc[mask, 'Condition'] = 'Condition_AB'
                    break

    # Show condition distribution
    print(f"  Conditions: {dict(df['Condition'].value_counts().sort_index())}")

    return df

def analyze_baseline_and_conditions(df, name):
    """Analyze baseline statistics and condition effects"""
    print(f"\n{name}:")
    print("-" * 40)

    results = {}

    # Combine all control periods for baseline
    control_mask = df['Condition'].str.contains('Control', na=False)
    if control_mask.sum() > 0:
        control_data = df[control_mask]['Illuminance (lux)']
        baseline_mean = control_data.mean()
        baseline_std = control_data.std()
        baseline_median = control_data.median()

        print(f"  Baseline (all controls combined):")
        print(f"    Mean: {baseline_mean:.2f} lux")
        print(f"    Median: {baseline_median:.2f} lux")
        print(f"    Std Dev: {baseline_std:.2f} lux")
        print(f"    n = {len(control_data)} samples")

        results['baseline'] = {
            'mean': baseline_mean,
            'std': baseline_std,
            'median': baseline_median,
            'n': len(control_data)
        }

        # Analyze each experimental condition
        for condition in ['Condition_A', 'Condition_B', 'Condition_AB']:
            cond_data = df[df['Condition'] == condition]['Illuminance (lux)']
            if len(cond_data) > 0:
                cond_mean = cond_data.mean()
                cond_std = cond_data.std()
                cond_median = cond_data.median()

                # Calculate change from baseline
                change_pct = ((cond_mean - baseline_mean) / baseline_mean) * 100

                # Statistical tests
                t_stat, p_ttest = ttest_ind(control_data, cond_data)
                u_stat, p_mann = mannwhitneyu(control_data, cond_data)

                # Effect size (Cohen's d)
                pooled_std = np.sqrt((control_data.std()**2 + cond_data.std()**2) / 2)
                cohens_d = (cond_mean - baseline_mean) / pooled_std

                print(f"\n  {condition}:")
                print(f"    Mean: {cond_mean:.2f} lux (Change: {change_pct:+.1f}%)")
                print(f"    Median: {cond_median:.2f} lux")
                print(f"    Std Dev: {cond_std:.2f} lux")
                print(f"    n = {len(cond_data)} samples")
                print(f"    t-test p-value: {p_ttest:.4f} {'***' if p_ttest < 0.001 else '**' if p_ttest < 0.01 else '*' if p_ttest < 0.05 else 'ns'}")
                print(f"    Mann-Whitney p-value: {p_mann:.4f}")
                print(f"    Effect size (Cohen's d): {cohens_d:.3f}")

                results[condition] = {
                    'mean': cond_mean,
                    'std': cond_std,
                    'median': cond_median,
                    'n': len(cond_data),
                    'change_pct': change_pct,
                    'p_ttest': p_ttest,
                    'p_mann': p_mann,
                    'cohens_d': cohens_d
                }

    return results

def analyze_sensor_correlations(datasets):
    """Analyze correlations between Sensor A and B"""
    print(f"\n{'='*70}")
    print("SENSOR CORRELATION ANALYSIS")
    print(f"{'='*70}")

    results = {}

    for run in ['run1', 'run2']:
        sensorA_key = f'{run}_sensorA'
        sensorB_key = f'{run}_sensorB'

        if sensorA_key in datasets and sensorB_key in datasets:
            print(f"\n{run.upper()} - Sensor A vs B:")
            print("-" * 40)

            dfA = datasets[sensorA_key]
            dfB = datasets[sensorB_key]

            # Merge on timestamp (nearest match within 0.1 seconds)
            merged = pd.merge_asof(
                dfA[['Timestamp', 'Illuminance (lux)', 'Condition']].sort_values('Timestamp'),
                dfB[['Timestamp', 'Illuminance (lux)']].sort_values('Timestamp'),
                on='Timestamp',
                direction='nearest',
                tolerance=pd.Timedelta('0.1s'),
                suffixes=('_A', '_B')
            )

            # Remove rows where merge failed
            merged = merged.dropna()

            if len(merged) > 0:
                # Overall correlation
                corr_pearson, p_pearson = pearsonr(merged['Illuminance (lux)_A'], merged['Illuminance (lux)_B'])
                corr_spearman, p_spearman = spearmanr(merged['Illuminance (lux)_A'], merged['Illuminance (lux)_B'])

                print(f"  Overall correlations (n={len(merged)}):")
                print(f"    Pearson r: {corr_pearson:.4f} (p={p_pearson:.4e})")
                print(f"    Spearman ρ: {corr_spearman:.4f} (p={p_spearman:.4e})")

                # Correlation by condition
                print(f"\n  Correlations by condition:")
                condition_corrs = {}
                for condition in ['Control_1', 'Control_2', 'Control_3', 'Control_4',
                                'Condition_A', 'Condition_B', 'Condition_AB']:
                    cond_data = merged[merged['Condition'] == condition]
                    if len(cond_data) > 30:  # Need enough data
                        corr, p = pearsonr(cond_data['Illuminance (lux)_A'], cond_data['Illuminance (lux)_B'])
                        print(f"    {condition:15s}: r={corr:.4f} (n={len(cond_data):4d}, p={p:.4e})")
                        condition_corrs[condition] = corr

                # Cross-correlation to detect time lags
                if len(merged) > 100:
                    # Normalize signals
                    sig_a = (merged['Illuminance (lux)_A'] - merged['Illuminance (lux)_A'].mean()) / merged['Illuminance (lux)_A'].std()
                    sig_b = (merged['Illuminance (lux)_B'] - merged['Illuminance (lux)_B'].mean()) / merged['Illuminance (lux)_B'].std()

                    # Calculate cross-correlation
                    correlation = np.correlate(sig_a, sig_b, mode='same')
                    lags = np.arange(-len(correlation)//2, len(correlation)//2) * 0.1  # Convert to seconds

                    # Find peak correlation
                    peak_idx = np.argmax(np.abs(correlation))
                    peak_lag = lags[peak_idx] if peak_idx < len(lags) else 0

                    print(f"\n  Cross-correlation analysis:")
                    print(f"    Peak correlation lag: {peak_lag:.2f} seconds")
                    if abs(peak_lag) > 0.1:
                        if peak_lag > 0:
                            print(f"    (Sensor B leads Sensor A by {abs(peak_lag):.2f}s)")
                        else:
                            print(f"    (Sensor A leads Sensor B by {abs(peak_lag):.2f}s)")

                results[run] = {
                    'overall_pearson': corr_pearson,
                    'overall_spearman': corr_spearman,
                    'condition_correlations': condition_corrs,
                    'peak_lag': peak_lag if len(merged) > 100 else None
                }

    return results

def create_visualizations(datasets, timestamp_data):
    """Create comprehensive visualizations"""
    print(f"\n{'='*70}")
    print("CREATING VISUALIZATIONS")
    print(f"{'='*70}")

    # Create figure with subplots
    fig = plt.figure(figsize=(20, 24))

    # Run 1 - Time series with conditions
    ax1 = plt.subplot(6, 2, 1)
    if 'run1_sensorA' in datasets:
        df = datasets['run1_sensorA']
        colors = {'Control_1': 'gray', 'Control_2': 'gray', 'Control_3': 'gray', 'Control_4': 'gray',
                 'Condition_A': 'red', 'Condition_B': 'blue', 'Condition_AB': 'purple', 'Transition': 'lightgray'}

        for condition in df['Condition'].unique():
            mask = df['Condition'] == condition
            ax1.scatter(df[mask]['Time (s)'], df[mask]['Illuminance (lux)'],
                       c=colors.get(condition, 'black'), alpha=0.3, s=1, label=condition)

        ax1.set_title('Run 1 - Sensor A Time Series', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Illuminance (lux)')
        ax1.legend(loc='upper right', fontsize=8)
        ax1.grid(True, alpha=0.3)

    ax2 = plt.subplot(6, 2, 2)
    if 'run1_sensorB' in datasets:
        df = datasets['run1_sensorB']
        for condition in df['Condition'].unique():
            mask = df['Condition'] == condition
            ax2.scatter(df[mask]['Time (s)'], df[mask]['Illuminance (lux)'],
                       c=colors.get(condition, 'black'), alpha=0.3, s=1, label=condition)

        ax2.set_title('Run 1 - Sensor B Time Series', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Illuminance (lux)')
        ax2.legend(loc='upper right', fontsize=8)
        ax2.grid(True, alpha=0.3)

    # Run 2 - Time series with conditions
    ax3 = plt.subplot(6, 2, 3)
    if 'run2_sensorA' in datasets:
        df = datasets['run2_sensorA']
        for condition in df['Condition'].unique():
            mask = df['Condition'] == condition
            ax3.scatter(df[mask]['Time (s)'], df[mask]['Illuminance (lux)'],
                       c=colors.get(condition, 'black'), alpha=0.3, s=1, label=condition)

        ax3.set_title('Run 2 - Sensor A Time Series', fontsize=12, fontweight='bold')
        ax3.set_xlabel('Time (s)')
        ax3.set_ylabel('Illuminance (lux)')
        ax3.legend(loc='upper right', fontsize=8)
        ax3.grid(True, alpha=0.3)

    ax4 = plt.subplot(6, 2, 4)
    if 'run2_sensorB' in datasets:
        df = datasets['run2_sensorB']
        for condition in df['Condition'].unique():
            mask = df['Condition'] == condition
            ax4.scatter(df[mask]['Time (s)'], df[mask]['Illuminance (lux)'],
                       c=colors.get(condition, 'black'), alpha=0.3, s=1, label=condition)

        ax4.set_title('Run 2 - Sensor B Time Series', fontsize=12, fontweight='bold')
        ax4.set_xlabel('Time (s)')
        ax4.set_ylabel('Illuminance (lux)')
        ax4.legend(loc='upper right', fontsize=8)
        ax4.grid(True, alpha=0.3)

    # Box plots for conditions - Run 1
    ax5 = plt.subplot(6, 2, 5)
    if 'run1_sensorA' in datasets:
        df = datasets['run1_sensorA']
        conditions = ['Control_1', 'Condition_A', 'Control_2', 'Condition_B', 'Control_3', 'Condition_AB', 'Control_4']
        data_to_plot = []
        labels = []
        for cond in conditions:
            cond_data = df[df['Condition'] == cond]['Illuminance (lux)']
            if len(cond_data) > 0:
                data_to_plot.append(cond_data)
                labels.append(cond.replace('_', ' '))

        if data_to_plot:
            ax5.boxplot(data_to_plot, labels=labels)
            ax5.set_title('Run 1 - Sensor A by Condition', fontsize=12, fontweight='bold')
            ax5.set_ylabel('Illuminance (lux)')
            ax5.tick_params(axis='x', rotation=45)

    ax6 = plt.subplot(6, 2, 6)
    if 'run1_sensorB' in datasets:
        df = datasets['run1_sensorB']
        data_to_plot = []
        labels = []
        for cond in conditions:
            cond_data = df[df['Condition'] == cond]['Illuminance (lux)']
            if len(cond_data) > 0:
                data_to_plot.append(cond_data)
                labels.append(cond.replace('_', ' '))

        if data_to_plot:
            ax6.boxplot(data_to_plot, labels=labels)
            ax6.set_title('Run 1 - Sensor B by Condition', fontsize=12, fontweight='bold')
            ax6.set_ylabel('Illuminance (lux)')
            ax6.tick_params(axis='x', rotation=45)

    # Box plots for conditions - Run 2
    ax7 = plt.subplot(6, 2, 7)
    if 'run2_sensorA' in datasets:
        df = datasets['run2_sensorA']
        # Note: Run 2 has reversed order (B first, then A)
        conditions = ['Control_1', 'Condition_B', 'Control_2', 'Condition_A', 'Control_3', 'Condition_AB', 'Control_4']
        data_to_plot = []
        labels = []
        for cond in conditions:
            cond_data = df[df['Condition'] == cond]['Illuminance (lux)']
            if len(cond_data) > 0:
                data_to_plot.append(cond_data)
                labels.append(cond.replace('_', ' '))

        if data_to_plot:
            ax7.boxplot(data_to_plot, labels=labels)
            ax7.set_title('Run 2 - Sensor A by Condition', fontsize=12, fontweight='bold')
            ax7.set_ylabel('Illuminance (lux)')
            ax7.tick_params(axis='x', rotation=45)

    ax8 = plt.subplot(6, 2, 8)
    if 'run2_sensorB' in datasets:
        df = datasets['run2_sensorB']
        data_to_plot = []
        labels = []
        for cond in conditions:
            cond_data = df[df['Condition'] == cond]['Illuminance (lux)']
            if len(cond_data) > 0:
                data_to_plot.append(cond_data)
                labels.append(cond.replace('_', ' '))

        if data_to_plot:
            ax8.boxplot(data_to_plot, labels=labels)
            ax8.set_title('Run 2 - Sensor B by Condition', fontsize=12, fontweight='bold')
            ax8.set_ylabel('Illuminance (lux)')
            ax8.tick_params(axis='x', rotation=45)

    # Sensor A vs B scatter plots
    ax9 = plt.subplot(6, 2, 9)
    if 'run1_sensorA' in datasets and 'run1_sensorB' in datasets:
        dfA = datasets['run1_sensorA']
        dfB = datasets['run1_sensorB']

        # Merge data
        merged = pd.merge_asof(
            dfA[['Timestamp', 'Illuminance (lux)', 'Condition']].sort_values('Timestamp'),
            dfB[['Timestamp', 'Illuminance (lux)']].sort_values('Timestamp'),
            on='Timestamp',
            direction='nearest',
            tolerance=pd.Timedelta('0.1s'),
            suffixes=('_A', '_B')
        ).dropna()

        if len(merged) > 0:
            # Color by condition
            for condition in merged['Condition'].unique():
                if 'Transition' not in condition:
                    mask = merged['Condition'] == condition
                    ax9.scatter(merged[mask]['Illuminance (lux)_A'], merged[mask]['Illuminance (lux)_B'],
                              alpha=0.3, s=1, label=condition)

            ax9.set_title('Run 1 - Sensor Correlation', fontsize=12, fontweight='bold')
            ax9.set_xlabel('Sensor A (lux)')
            ax9.set_ylabel('Sensor B (lux)')
            ax9.legend(fontsize=8)
            ax9.grid(True, alpha=0.3)

    ax10 = plt.subplot(6, 2, 10)
    if 'run2_sensorA' in datasets and 'run2_sensorB' in datasets:
        dfA = datasets['run2_sensorA']
        dfB = datasets['run2_sensorB']

        # Merge data
        merged = pd.merge_asof(
            dfA[['Timestamp', 'Illuminance (lux)', 'Condition']].sort_values('Timestamp'),
            dfB[['Timestamp', 'Illuminance (lux)']].sort_values('Timestamp'),
            on='Timestamp',
            direction='nearest',
            tolerance=pd.Timedelta('0.1s'),
            suffixes=('_A', '_B')
        ).dropna()

        if len(merged) > 0:
            for condition in merged['Condition'].unique():
                if 'Transition' not in condition:
                    mask = merged['Condition'] == condition
                    ax10.scatter(merged[mask]['Illuminance (lux)_A'], merged[mask]['Illuminance (lux)_B'],
                               alpha=0.3, s=1, label=condition)

            ax10.set_title('Run 2 - Sensor Correlation', fontsize=12, fontweight='bold')
            ax10.set_xlabel('Sensor A (lux)')
            ax10.set_ylabel('Sensor B (lux)')
            ax10.legend(fontsize=8)
            ax10.grid(True, alpha=0.3)

    # Mean comparison bar plots
    ax11 = plt.subplot(6, 2, 11)
    run1_means = []
    run2_means = []
    conditions_list = ['Baseline', 'Cond_A', 'Cond_B', 'Cond_AB']

    # Collect means for both runs
    for run, means_list in [('run1', run1_means), ('run2', run2_means)]:
        for sensor in ['A', 'B']:
            key = f'{run}_sensor{sensor}'
            if key in datasets:
                df = datasets[key]

                # Baseline (all controls)
                control_mean = df[df['Condition'].str.contains('Control', na=False)]['Illuminance (lux)'].mean()
                means_list.append(control_mean)

                # Conditions
                for cond in ['Condition_A', 'Condition_B', 'Condition_AB']:
                    cond_mean = df[df['Condition'] == cond]['Illuminance (lux)'].mean()
                    means_list.append(cond_mean if not np.isnan(cond_mean) else 0)

    if run1_means:
        x = np.arange(len(conditions_list))
        width = 0.35

        ax11.bar(x - width/2, run1_means[:4], width, label='Sensor A', alpha=0.8)
        ax11.bar(x + width/2, run1_means[4:8] if len(run1_means) >= 8 else [0]*4, width, label='Sensor B', alpha=0.8)

        ax11.set_title('Run 1 - Mean Luminosity Comparison', fontsize=12, fontweight='bold')
        ax11.set_ylabel('Mean Illuminance (lux)')
        ax11.set_xticks(x)
        ax11.set_xticklabels(conditions_list)
        ax11.legend()
        ax11.grid(True, alpha=0.3)

    ax12 = plt.subplot(6, 2, 12)
    if run2_means:
        x = np.arange(len(conditions_list))
        width = 0.35

        ax12.bar(x - width/2, run2_means[:4], width, label='Sensor A', alpha=0.8)
        ax12.bar(x + width/2, run2_means[4:8] if len(run2_means) >= 8 else [0]*4, width, label='Sensor B', alpha=0.8)

        ax12.set_title('Run 2 - Mean Luminosity Comparison', fontsize=12, fontweight='bold')
        ax12.set_ylabel('Mean Illuminance (lux)')
        ax12.set_xticks(x)
        ax12.set_xticklabels(conditions_list)
        ax12.legend()
        ax12.grid(True, alpha=0.3)

    plt.suptitle('Comprehensive Twin Flame Luminosity Analysis', fontsize=16, fontweight='bold')
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])

    # Save figure
    plt.savefig('flame_analysis_comprehensive.png', dpi=150, bbox_inches='tight')
    print("  Saved: flame_analysis_comprehensive.png")

    plt.show()

def main():
    """Main analysis pipeline"""
    print("\n" + "="*70)
    print("FINAL COMPREHENSIVE TWIN FLAME LUMINOSITY ANALYSIS")
    print("="*70)

    # Parse timestamps
    timestamp_data = parse_timestamps_correctly()

    # Load and synchronize all data files
    print(f"\n{'='*70}")
    print("LOADING AND SYNCHRONIZING DATA")
    print(f"{'='*70}")

    files = [
        ('lightmeter_2026-01-12_00-47-53_TwinFlame1_CandleA.csv', 'run1', 'run1_sensorA'),
        ('lightmeter_2026-01-12_00-48-13_TwinFlame1_CandleB.csv', 'run1', 'run1_sensorB'),
        ('lightmeter_2026-01-12_02-11-46_TwinFlame2_CandleA.csv', 'run2', 'run2_sensorA'),
        ('lightmeter_2026-01-12_02-12-00_TwinFlame2_CandleB.csv', 'run2', 'run2_sensorB')
    ]

    datasets = {}
    for file_path, run, key in files:
        df = load_and_synchronize(file_path, timestamp_data[run])
        datasets[key] = df

    # Analyze conditions
    print(f"\n{'='*70}")
    print("CONDITION EFFECTS ANALYSIS")
    print(f"{'='*70}")

    all_results = {}
    for key, df in datasets.items():
        results = analyze_baseline_and_conditions(df, key.upper())
        all_results[key] = results

    # Analyze correlations
    correlation_results = analyze_sensor_correlations(datasets)

    # Create visualizations
    create_visualizations(datasets, timestamp_data)

    # Save processed data
    print(f"\n{'='*70}")
    print("SAVING PROCESSED DATA")
    print(f"{'='*70}")

    for key, df in datasets.items():
        output_file = f"final_{key}.csv"
        df.to_csv(output_file, index=False)
        print(f"  Saved: {output_file}")

    # Generate summary report
    generate_summary_report(all_results, correlation_results)

    return datasets, all_results, correlation_results

def generate_summary_report(all_results, correlation_results):
    """Generate a summary report of key findings"""
    print(f"\n{'='*70}")
    print("SUMMARY OF KEY FINDINGS")
    print(f"{'='*70}")

    # Condition effects summary
    print("\n1. CONDITION EFFECTS ON LUMINOSITY:")
    print("-" * 40)

    for run in ['run1', 'run2']:
        print(f"\n{run.upper()}:")
        for sensor in ['A', 'B']:
            key = f'{run}_sensor{sensor}'
            if key in all_results and 'baseline' in all_results[key]:
                results = all_results[key]
                baseline = results['baseline']['mean']

                print(f"  Sensor {sensor}:")
                for cond in ['Condition_A', 'Condition_B', 'Condition_AB']:
                    if cond in results:
                        change = results[cond]['change_pct']
                        p_val = results[cond]['p_ttest']
                        effect = results[cond]['cohens_d']
                        sig = '***' if p_val < 0.001 else '**' if p_val < 0.01 else '*' if p_val < 0.05 else 'ns'
                        print(f"    {cond}: {change:+.1f}% change (p={p_val:.4f} {sig}, d={effect:.2f})")

    # Correlation summary
    print("\n2. SENSOR CORRELATIONS:")
    print("-" * 40)

    for run in ['run1', 'run2']:
        if run in correlation_results:
            corr = correlation_results[run]
            print(f"\n{run.upper()}:")
            print(f"  Overall Pearson r: {corr['overall_pearson']:.4f}")
            print(f"  Overall Spearman ρ: {corr['overall_spearman']:.4f}")

            if 'condition_correlations' in corr:
                print(f"  Condition-specific correlations:")
                for cond, r in corr['condition_correlations'].items():
                    print(f"    {cond}: r={r:.4f}")

    # Key observations
    print("\n3. KEY OBSERVATIONS:")
    print("-" * 40)

    observations = []

    # Check for consistent effects across runs
    a_effects_run1 = []
    a_effects_run2 = []
    b_effects_run1 = []
    b_effects_run2 = []

    for sensor in ['A', 'B']:
        if f'run1_sensor{sensor}' in all_results:
            if 'Condition_A' in all_results[f'run1_sensor{sensor}']:
                a_effects_run1.append(all_results[f'run1_sensor{sensor}']['Condition_A']['change_pct'])
            if 'Condition_B' in all_results[f'run1_sensor{sensor}']:
                b_effects_run1.append(all_results[f'run1_sensor{sensor}']['Condition_B']['change_pct'])

        if f'run2_sensor{sensor}' in all_results:
            if 'Condition_A' in all_results[f'run2_sensor{sensor}']:
                a_effects_run2.append(all_results[f'run2_sensor{sensor}']['Condition_A']['change_pct'])
            if 'Condition_B' in all_results[f'run2_sensor{sensor}']:
                b_effects_run2.append(all_results[f'run2_sensor{sensor}']['Condition_B']['change_pct'])

    if a_effects_run1 and a_effects_run2:
        avg_a_run1 = np.mean(a_effects_run1)
        avg_a_run2 = np.mean(a_effects_run2)
        observations.append(f"• Condition A average effect: Run1={avg_a_run1:+.1f}%, Run2={avg_a_run2:+.1f}%")

    if b_effects_run1 and b_effects_run2:
        avg_b_run1 = np.mean(b_effects_run1)
        avg_b_run2 = np.mean(b_effects_run2)
        observations.append(f"• Condition B average effect: Run1={avg_b_run1:+.1f}%, Run2={avg_b_run2:+.1f}%")

    # Check for order effects
    observations.append("• Order of conditions was reversed between runs (A→B in Run1, B→A in Run2)")

    # Check correlation patterns
    if 'run1' in correlation_results and 'run2' in correlation_results:
        r1 = correlation_results['run1']['overall_pearson']
        r2 = correlation_results['run2']['overall_pearson']
        observations.append(f"• Strong positive correlation between sensors in both runs (r={r1:.3f}, {r2:.3f})")

    for obs in observations:
        print(obs)

    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)

if __name__ == "__main__":
    datasets, results, correlations = main()