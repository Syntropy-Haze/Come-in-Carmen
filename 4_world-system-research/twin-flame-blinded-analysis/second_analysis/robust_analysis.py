#!/usr/bin/env python3
"""
Robust Blinded Analysis with Manual Timestamp Entry
Author: Claude
Date: 2026-01-13
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from scipy import stats
from scipy.stats import ttest_ind, pearsonr, spearmanr, mannwhitneyu
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def get_timestamps_manual():
    """Manually enter the validated timestamps from the Excel file"""
    print(f"\n{'='*70}")
    print("EXPERIMENTAL TIMELINE (From Validated Timestamps)")
    print(f"{'='*70}")

    # Based on the Excel examination, here are the validated timestamps
    # Column F (Unnamed: 5) for Run 1, Column I (Unnamed: 8) for Run 2

    run1_data = [
        ('Vid Recording Started', '00:25:45'),
        ('1st Light in Place', '00:36:20'),
        ('2nd Light in Place', '00:36:39'),
        ('Start Control 1', '00:36:42'),
        ('End Control 1', '00:37:50'),
        ('Start 1st Light', '00:38:33'),  # This is Condition A in Run 1
        ('End 1st Light', '00:40:10'),
        ('Start Control 2', '00:40:53'),
        ('End Control 2', '00:42:00'),
        ('Start 2nd Light', '00:42:11'),  # This is Condition B in Run 1
        ('End 2nd Light', '00:43:11'),
        ('Start Control 3', '00:43:36'),
        ('End Control 3', '00:44:39'),
        ('Start 1st + 2nd Lights', '00:45:02'),  # Condition AB
        ('End Double Lights', '00:46:03'),
        ('Start Control 4', '00:46:17'),
        ('End Control 4', '00:47:20'),
        ('Lights Out', '00:47:36')
    ]

    run2_data = [
        ('Vid Recording Started', '01:55:27'),
        ('1st Light in Place', '02:02:21'),
        ('2nd Light in Place', '02:02:36'),
        ('Start Control 1', '02:02:44'),
        ('End Control 1', '02:03:48'),
        ('Start 1st Light', '02:03:54'),  # This is Condition B in Run 2 (reversed!)
        ('End 1st Light', '02:04:54'),
        ('Start Control 2', '02:05:02'),
        ('End Control 2', '02:06:06'),
        ('Start 2nd Light', '02:06:14'),  # This is Condition A in Run 2 (reversed!)
        ('End 2nd Light', '02:07:13'),
        ('Start Control 3', '02:07:26'),
        ('End Control 3', '02:08:28'),
        ('Start 1st + 2nd Lights', '02:08:43'),  # Condition AB
        ('End Double Lights', '02:09:54'),
        ('Start Control 4', '02:10:03'),
        ('End Control 4', '02:11:01'),
        ('Lights Out', '02:11:37'),
        ('Vid Recording Ended', '02:13:04')
    ]

    print("\nRun 1 Timeline (A applied first, B second):")
    for marker, time in run1_data:
        print(f"  {marker:30s} : {time}")

    print("\nRun 2 Timeline (B applied first, A second - REVERSED):")
    for marker, time in run2_data:
        print(f"  {marker:30s} : {time}")

    return {'run1': run1_data, 'run2': run2_data}

def load_and_sync_robust(file_path, run_data, run_type):
    """Load and synchronize data with robust condition assignment"""
    df = pd.read_csv(file_path)

    # Extract timing info from filename
    parts = file_path.split('_')
    end_time_str = f"{parts[1]} {parts[2].replace('-', ':')}"
    end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")

    duration = df['time'].max()
    start_time = end_time - timedelta(seconds=duration)

    print(f"\n{file_path}:")
    print(f"  Recording: {start_time.strftime('%H:%M:%S')} to {end_time.strftime('%H:%M:%S')} ({duration:.1f}s)")

    # Rename columns
    df = df.rename(columns={'time': 'Time (s)', 'lux': 'Illuminance (lux)'})

    # Add timestamps
    df['Timestamp'] = pd.to_datetime(start_time) + pd.to_timedelta(df['Time (s)'], unit='s')

    # Initialize all as transition
    df['Condition'] = 'Transition'

    # Parse condition periods
    for i, (marker, time_str) in enumerate(run_data):
        if any(x in marker for x in ['Start', 'End']):
            marker_time = datetime.strptime(f"2026-01-12 {time_str}", "%Y-%m-%d %H:%M:%S")

            # Control periods
            if 'Start Control' in marker:
                control_num = marker.split()[-1]
                for j, (end_marker, end_time_str) in enumerate(run_data[i+1:], i+1):
                    if f'End Control {control_num}' in end_marker:
                        end_time = datetime.strptime(f"2026-01-12 {end_time_str}", "%Y-%m-%d %H:%M:%S")
                        mask = (df['Timestamp'] >= marker_time) & (df['Timestamp'] <= end_time)
                        df.loc[mask, 'Condition'] = f'Control_{control_num}'
                        break

            # Experimental conditions - account for reversal between runs
            elif 'Start 1st Light' in marker:
                for j, (end_marker, end_time_str) in enumerate(run_data[i+1:], i+1):
                    if 'End 1st Light' in end_marker:
                        end_time = datetime.strptime(f"2026-01-12 {end_time_str}", "%Y-%m-%d %H:%M:%S")
                        mask = (df['Timestamp'] >= marker_time) & (df['Timestamp'] <= end_time)
                        # Run 1: 1st Light = Condition A
                        # Run 2: 1st Light = Condition B (reversed)
                        if run_type == 'run1':
                            df.loc[mask, 'Condition'] = 'Condition_A'
                        else:  # run2
                            df.loc[mask, 'Condition'] = 'Condition_B'
                        break

            elif 'Start 2nd Light' in marker:
                for j, (end_marker, end_time_str) in enumerate(run_data[i+1:], i+1):
                    if 'End 2nd Light' in end_marker:
                        end_time = datetime.strptime(f"2026-01-12 {end_time_str}", "%Y-%m-%d %H:%M:%S")
                        mask = (df['Timestamp'] >= marker_time) & (df['Timestamp'] <= end_time)
                        # Run 1: 2nd Light = Condition B
                        # Run 2: 2nd Light = Condition A (reversed)
                        if run_type == 'run1':
                            df.loc[mask, 'Condition'] = 'Condition_B'
                        else:  # run2
                            df.loc[mask, 'Condition'] = 'Condition_A'
                        break

            elif 'Start 1st + 2nd Lights' in marker:
                for j, (end_marker, end_time_str) in enumerate(run_data[i+1:], i+1):
                    if 'End Double Lights' in end_marker:
                        end_time = datetime.strptime(f"2026-01-12 {end_time_str}", "%Y-%m-%d %H:%M:%S")
                        mask = (df['Timestamp'] >= marker_time) & (df['Timestamp'] <= end_time)
                        df.loc[mask, 'Condition'] = 'Condition_AB'
                        break

    # Report condition distribution
    condition_counts = df['Condition'].value_counts().sort_index()
    print(f"  Condition distribution:")
    for cond, count in condition_counts.items():
        print(f"    {cond:15s}: {count:5d} samples ({count/len(df)*100:.1f}%)")

    return df

def analyze_effects(df, name):
    """Analyze condition effects with statistical tests"""
    print(f"\n{name}:")
    print("-" * 50)

    results = {}

    # Get baseline from all control periods
    control_data = df[df['Condition'].str.contains('Control', na=False)]['Illuminance (lux)']

    if len(control_data) > 0:
        baseline_mean = control_data.mean()
        baseline_std = control_data.std()
        baseline_median = control_data.median()

        print(f"  Baseline (all controls):")
        print(f"    Mean: {baseline_mean:.2f} ± {baseline_std:.2f} lux")
        print(f"    Median: {baseline_median:.2f} lux")
        print(f"    n = {len(control_data)}")

        results['baseline'] = {
            'mean': baseline_mean,
            'std': baseline_std,
            'median': baseline_median,
            'n': len(control_data)
        }

        # Analyze each condition
        for condition in ['Condition_A', 'Condition_B', 'Condition_AB']:
            cond_data = df[df['Condition'] == condition]['Illuminance (lux)']

            if len(cond_data) > 0:
                cond_mean = cond_data.mean()
                cond_std = cond_data.std()
                cond_median = cond_data.median()

                # Calculate changes
                change_pct = ((cond_mean - baseline_mean) / baseline_mean) * 100
                median_change_pct = ((cond_median - baseline_median) / baseline_median) * 100

                # Statistical tests
                t_stat, p_ttest = ttest_ind(control_data, cond_data, equal_var=False)
                u_stat, p_mann = mannwhitneyu(control_data, cond_data, alternative='two-sided')

                # Effect size
                pooled_std = np.sqrt((control_data.var() + cond_data.var()) / 2)
                cohens_d = (cond_mean - baseline_mean) / pooled_std if pooled_std > 0 else 0

                print(f"\n  {condition}:")
                print(f"    Mean: {cond_mean:.2f} ± {cond_std:.2f} lux")
                print(f"    Change from baseline: {change_pct:+.1f}%")
                print(f"    Median: {cond_median:.2f} lux (change: {median_change_pct:+.1f}%)")
                print(f"    n = {len(cond_data)}")
                print(f"    t-test: p = {p_ttest:.4f} {'***' if p_ttest < 0.001 else '**' if p_ttest < 0.01 else '*' if p_ttest < 0.05 else 'ns'}")
                print(f"    Mann-Whitney: p = {p_mann:.4f}")
                print(f"    Cohen's d: {cohens_d:.3f}")

                results[condition] = {
                    'mean': cond_mean,
                    'std': cond_std,
                    'median': cond_median,
                    'change_pct': change_pct,
                    'p_ttest': p_ttest,
                    'cohens_d': cohens_d,
                    'n': len(cond_data)
                }

    return results

def main():
    """Main analysis pipeline"""
    print("\n" + "="*70)
    print("ROBUST BLINDED TWIN FLAME LUMINOSITY ANALYSIS")
    print("="*70)

    # Get timestamps
    timestamp_data = get_timestamps_manual()

    # Load and process all files
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
    for file_path, run_type, key in files:
        df = load_and_sync_robust(file_path, timestamp_data[run_type], run_type)
        datasets[key] = df

    # Analyze effects
    print(f"\n{'='*70}")
    print("CONDITION EFFECTS ANALYSIS")
    print(f"{'='*70}")

    all_results = {}
    for key, df in datasets.items():
        results = analyze_effects(df, key.upper())
        all_results[key] = results

    # Analyze correlations between sensors
    print(f"\n{'='*70}")
    print("SENSOR CORRELATION ANALYSIS")
    print(f"{'='*70}")

    for run in ['run1', 'run2']:
        sensorA_key = f'{run}_sensorA'
        sensorB_key = f'{run}_sensorB'

        if sensorA_key in datasets and sensorB_key in datasets:
            print(f"\n{run.upper()} - Sensor Correlations:")
            print("-" * 40)

            dfA = datasets[sensorA_key]
            dfB = datasets[sensorB_key]

            # Merge on nearest timestamp
            merged = pd.merge_asof(
                dfA[['Timestamp', 'Illuminance (lux)', 'Condition']].sort_values('Timestamp'),
                dfB[['Timestamp', 'Illuminance (lux)']].sort_values('Timestamp'),
                on='Timestamp',
                direction='nearest',
                tolerance=pd.Timedelta('0.1s'),
                suffixes=('_A', '_B')
            ).dropna()

            if len(merged) > 0:
                # Overall correlation
                r_pearson, p_pearson = pearsonr(merged['Illuminance (lux)_A'], merged['Illuminance (lux)_B'])
                r_spearman, p_spearman = spearmanr(merged['Illuminance (lux)_A'], merged['Illuminance (lux)_B'])

                print(f"  Overall (n={len(merged)}):")
                print(f"    Pearson r = {r_pearson:.4f} (p = {p_pearson:.4e})")
                print(f"    Spearman ρ = {r_spearman:.4f} (p = {p_spearman:.4e})")

                # By condition
                print(f"\n  By condition:")
                for condition in sorted(merged['Condition'].unique()):
                    if 'Transition' not in condition:
                        cond_data = merged[merged['Condition'] == condition]
                        if len(cond_data) > 30:
                            r, p = pearsonr(cond_data['Illuminance (lux)_A'], cond_data['Illuminance (lux)_B'])
                            print(f"    {condition:15s}: r = {r:.4f} (n = {len(cond_data):4d})")

    # Save processed data
    print(f"\n{'='*70}")
    print("SAVING RESULTS")
    print(f"{'='*70}")

    for key, df in datasets.items():
        output_file = f"robust_{key}.csv"
        df.to_csv(output_file, index=False)
        print(f"  Saved: {output_file}")

    # Create summary visualization
    create_summary_plot(datasets, all_results)

    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)

def create_summary_plot(datasets, results):
    """Create a comprehensive summary plot"""
    fig, axes = plt.subplots(4, 2, figsize=(16, 20))

    # Time series plots
    for idx, (run, row) in enumerate([('run1', 0), ('run2', 2)]):
        for sensor_idx, sensor in enumerate(['A', 'B']):
            ax = axes[row, sensor_idx]
            key = f'{run}_sensor{sensor}'

            if key in datasets:
                df = datasets[key]

                # Plot by condition
                colors = {
                    'Control_1': 'gray', 'Control_2': 'gray', 'Control_3': 'gray', 'Control_4': 'gray',
                    'Condition_A': 'red', 'Condition_B': 'blue', 'Condition_AB': 'purple',
                    'Transition': 'lightgray'
                }

                for condition in df['Condition'].unique():
                    mask = df['Condition'] == condition
                    ax.scatter(df[mask]['Time (s)'], df[mask]['Illuminance (lux)'],
                             c=colors.get(condition, 'black'), alpha=0.4, s=0.5, label=condition)

                ax.set_title(f'{run.upper()} - Sensor {sensor}', fontweight='bold')
                ax.set_xlabel('Time (s)')
                ax.set_ylabel('Illuminance (lux)')
                ax.legend(loc='upper right', fontsize=8, markerscale=5)
                ax.grid(True, alpha=0.3)

    # Box plots
    for idx, (run, row) in enumerate([('run1', 1), ('run2', 3)]):
        for sensor_idx, sensor in enumerate(['A', 'B']):
            ax = axes[row, sensor_idx]
            key = f'{run}_sensor{sensor}'

            if key in datasets:
                df = datasets[key]

                # Order conditions properly for each run
                if run == 'run1':
                    condition_order = ['Control_1', 'Condition_A', 'Control_2', 'Condition_B',
                                     'Control_3', 'Condition_AB', 'Control_4']
                else:  # run2 - reversed order
                    condition_order = ['Control_1', 'Condition_B', 'Control_2', 'Condition_A',
                                     'Control_3', 'Condition_AB', 'Control_4']

                data_to_plot = []
                labels = []
                for cond in condition_order:
                    cond_data = df[df['Condition'] == cond]['Illuminance (lux)']
                    if len(cond_data) > 0:
                        data_to_plot.append(cond_data.values)
                        labels.append(cond.replace('_', '\n'))

                if data_to_plot:
                    bp = ax.boxplot(data_to_plot, labels=labels, patch_artist=True)

                    # Color the boxes
                    for i, box in enumerate(bp['boxes']):
                        if 'Control' in labels[i]:
                            box.set_facecolor('lightgray')
                        elif 'A' in labels[i] and 'B' not in labels[i]:
                            box.set_facecolor('lightcoral')
                        elif 'B' in labels[i] and 'A' not in labels[i]:
                            box.set_facecolor('lightblue')
                        elif 'AB' in labels[i]:
                            box.set_facecolor('plum')

                ax.set_title(f'{run.upper()} - Sensor {sensor} by Condition', fontweight='bold')
                ax.set_ylabel('Illuminance (lux)')
                ax.tick_params(axis='x', rotation=0)
                ax.grid(True, alpha=0.3, axis='y')

                # Add significance markers
                if key in results and 'baseline' in results[key]:
                    baseline_mean = results[key]['baseline']['mean']
                    y_max = ax.get_ylim()[1]

                    for i, cond_label in enumerate(labels):
                        cond_key = cond_label.replace('\n', '_')
                        if cond_key in results[key]:
                            p_val = results[key][cond_key]['p_ttest']
                            if p_val < 0.001:
                                ax.text(i+1, y_max*0.95, '***', ha='center', fontweight='bold')
                            elif p_val < 0.01:
                                ax.text(i+1, y_max*0.95, '**', ha='center', fontweight='bold')
                            elif p_val < 0.05:
                                ax.text(i+1, y_max*0.95, '*', ha='center', fontweight='bold')

    plt.suptitle('Robust Twin Flame Luminosity Analysis\n' +
                '(Run 1: A→B, Run 2: B→A)', fontsize=16, fontweight='bold')
    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    plt.savefig('robust_analysis_summary.png', dpi=150, bbox_inches='tight')
    print("  Saved: robust_analysis_summary.png")
    plt.close()  # Close instead of show to avoid hanging

if __name__ == "__main__":
    main()