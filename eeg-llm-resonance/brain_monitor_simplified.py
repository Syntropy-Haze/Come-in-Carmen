#!/usr/bin/env python3
"""
Live Brain Monitor - "Betweenness" Edition (Simplified)

Real-time EEG monitoring that tracks coherence patterns and "betweenness" -
the coherence that exists in the whole but not necessarily in the parts.

This is a simplified version demonstrating key concepts. Full implementation
requires EEG hardware and LSL (Lab Streaming Layer) setup.

Key metrics:
- Broadband coherence across channels
- Weighted Phase Lag Index (WPLI) - robust to volume conduction
- "Betweenness" - emergent whole-system coherence
- Band-specific coherence (theta, alpha, beta)
"""

import numpy as np
from scipy import signal
from scipy.signal import hilbert, butter, filtfilt
from collections import deque
import time


class BrainMonitor:
    """
    Simplified brain monitor for tracking coherence patterns.

    Tracks "betweenness" - coherence in the whole but not the parts.
    """

    def __init__(self, sampling_rate=256, channels=4):
        self.sampling_rate = sampling_rate
        self.channels = channels
        self.buffer_size = sampling_rate * 3  # 3-second buffer

        # Initialize buffers for each channel
        self.buffers = {
            f'ch_{i}': deque(maxlen=self.buffer_size)
            for i in range(channels)
        }

        # Define frequency bands
        self.bands = {
            'theta': (4, 8),
            'alpha': (8, 13),
            'beta': (13, 30),
            'gamma': (30, 50)
        }

        # Metrics history
        self.history = {
            'broadband_coherence': [],
            'wpli': [],
            'betweenness': [],
            'band_power': {band: [] for band in self.bands}
        }

    def bandpass_filter(self, data, low, high, order=4):
        """Apply Butterworth bandpass filter"""
        nyquist = self.sampling_rate / 2
        low_norm = low / nyquist
        high_norm = high / nyquist

        # Ensure valid frequency range
        if low_norm >= 1 or high_norm >= 1:
            return data

        b, a = butter(order, [low_norm, high_norm], btype='band')
        return filtfilt(b, a, data, axis=-1)

    def compute_wpli(self, phase_data):
        """
        Weighted Phase Lag Index - measure of phase synchronization
        robust to volume conduction effects.

        WPLI = |E[|Im(S)|]| / E[|Im(S)|]
        where S is the cross-spectrum between signals
        """
        n_channels = phase_data.shape[0]
        wpli_pairs = []

        for i in range(n_channels):
            for j in range(i+1, n_channels):
                # Phase difference
                phase_diff = phase_data[i] - phase_data[j]

                # Imaginary part of phase difference
                imag_part = np.sin(phase_diff)

                # WPLI computation
                wpli = np.abs(np.mean(imag_part)) / (np.mean(np.abs(imag_part)) + 1e-10)
                wpli_pairs.append(wpli)

        return np.mean(wpli_pairs) if wpli_pairs else 0

    def compute_imaginary_coherence(self, phase_data):
        """
        Imaginary coherence - only captures non-zero lag coupling,
        removing zero-lag artifacts from volume conduction.
        """
        n_channels = phase_data.shape[0]
        imcoh_pairs = []

        for i in range(n_channels):
            for j in range(i+1, n_channels):
                # Complex representation
                z_i = np.exp(1j * phase_data[i])
                z_j = np.exp(1j * phase_data[j])

                # Cross-spectrum
                cross_spec = z_i * np.conj(z_j)

                # Imaginary coherence
                imcoh = np.abs(np.mean(np.imag(cross_spec)))
                imcoh_pairs.append(imcoh)

        return np.mean(imcoh_pairs) if imcoh_pairs else 0

    def compute_betweenness(self, data):
        """
        Compute "betweenness" - coherence that emerges in the whole
        but not necessarily in individual channel pairs.

        This captures emergent properties of the full system.
        """
        if len(data.shape) == 1:
            data = data.reshape(1, -1)

        # Global coherence (all channels together)
        analytic = hilbert(data, axis=1)
        phases = np.angle(analytic)

        # Global phase coherence
        global_coherence = np.abs(np.mean(np.exp(1j * phases)))

        # Average pairwise coherence
        pairwise_coherences = []
        n_channels = data.shape[0]

        for i in range(n_channels):
            for j in range(i+1, n_channels):
                pair_phases = phases[[i, j], :]
                pair_coherence = np.abs(np.mean(np.exp(1j * pair_phases)))
                pairwise_coherences.append(pair_coherence)

        avg_pairwise = np.mean(pairwise_coherences) if pairwise_coherences else 0

        # Betweenness = global coherence - average pairwise coherence
        # Positive values indicate emergent whole-system coherence
        betweenness = global_coherence - avg_pairwise

        return betweenness

    def compute_band_power(self, data):
        """Compute power in each frequency band"""
        band_powers = {}

        for band_name, (low, high) in self.bands.items():
            # Filter to band
            filtered = self.bandpass_filter(data, low, high)

            # Compute power (variance of filtered signal)
            power = np.var(filtered)
            band_powers[band_name] = power

        # Normalize to percentages
        total_power = sum(band_powers.values())
        if total_power > 0:
            band_powers = {k: v/total_power for k, v in band_powers.items()}

        return band_powers

    def process_chunk(self, data_chunk):
        """
        Process a chunk of EEG data and compute metrics.

        Args:
            data_chunk: array of shape [channels, samples]

        Returns:
            dict of computed metrics
        """
        # Ensure proper shape
        if len(data_chunk.shape) == 1:
            data_chunk = data_chunk.reshape(1, -1)

        # Get phases for coherence metrics
        analytic = hilbert(data_chunk, axis=1)
        phases = np.angle(analytic)

        # Compute metrics
        metrics = {
            'wpli': self.compute_wpli(phases),
            'imaginary_coherence': self.compute_imaginary_coherence(phases),
            'betweenness': self.compute_betweenness(data_chunk),
            'band_power': self.compute_band_power(data_chunk.flatten()),
        }

        # Broadband coherence
        metrics['broadband_coherence'] = np.abs(np.mean(np.exp(1j * phases)))

        # Update history
        self.history['broadband_coherence'].append(metrics['broadband_coherence'])
        self.history['wpli'].append(metrics['wpli'])
        self.history['betweenness'].append(metrics['betweenness'])

        for band in self.bands:
            self.history['band_power'][band].append(metrics['band_power'][band])

        return metrics

    def get_summary_stats(self):
        """Get summary statistics from recent history"""
        if len(self.history['broadband_coherence']) == 0:
            return None

        stats = {
            'mean_coherence': np.mean(self.history['broadband_coherence'][-100:]),
            'std_coherence': np.std(self.history['broadband_coherence'][-100:]),
            'mean_wpli': np.mean(self.history['wpli'][-100:]),
            'mean_betweenness': np.mean(self.history['betweenness'][-100:]),
        }

        # Band power averages
        for band in self.bands:
            if self.history['band_power'][band]:
                stats[f'{band}_power'] = np.mean(self.history['band_power'][band][-100:])

        return stats

    def display_metrics(self, metrics):
        """Display metrics in readable format"""
        print("\n" + "="*50)
        print("BRAIN STATE METRICS")
        print("="*50)

        print(f"\nCoherence Metrics:")
        print(f"  Broadband Coherence: {metrics['broadband_coherence']:.3f}")
        print(f"  WPLI (phase sync):   {metrics['wpli']:.3f}")
        print(f"  Betweenness:         {metrics['betweenness']:+.3f}")

        print(f"\nBand Power Distribution:")
        for band, power in metrics['band_power'].items():
            bar = '█' * int(power * 20)
            print(f"  {band:6s}: {bar:20s} {power:.1%}")

        # Show emergence indicator
        if metrics['betweenness'] > 0.1:
            print("\n⚡ HIGH BETWEENNESS - Emergent whole-system coherence detected!")
        elif metrics['betweenness'] > 0.05:
            print("\n✨ Moderate betweenness - System integration emerging")


def demo_brain_monitor():
    """Demonstrate brain monitor with simulated data"""
    print("BRAIN MONITOR DEMONSTRATION")
    print("-" * 50)
    print("Simulating EEG data and computing coherence metrics...")

    monitor = BrainMonitor(sampling_rate=256, channels=4)

    # Simulate different brain states
    states = [
        ("Baseline", 0.3),
        ("Focused Attention", 0.7),
        ("Meditation", 0.9),
        ("Creative Flow", 0.6),
    ]

    for state_name, coherence_level in states:
        print(f"\n\nSimulating: {state_name}")
        print("-" * 30)

        # Generate data with specified coherence level
        t = np.linspace(0, 1, 256)
        base_signal = np.sin(2 * np.pi * 10 * t)  # 10 Hz base

        # Create channels with varying phase offsets (lower offset = higher coherence)
        data = []
        for i in range(4):
            phase_offset = (1 - coherence_level) * np.random.randn() * np.pi
            noise = (1 - coherence_level) * np.random.randn(256) * 0.5
            channel = np.sin(2 * np.pi * 10 * t + phase_offset) + noise
            data.append(channel)

        data = np.array(data)

        # Process and display
        metrics = monitor.process_chunk(data)
        monitor.display_metrics(metrics)

        time.sleep(1)  # Pause for readability

    # Show summary
    print("\n\n" + "="*50)
    print("SESSION SUMMARY")
    print("="*50)

    summary = monitor.get_summary_stats()
    if summary:
        print(f"\nAverage Metrics Across Session:")
        print(f"  Mean Coherence:   {summary['mean_coherence']:.3f} ± {summary['std_coherence']:.3f}")
        print(f"  Mean WPLI:        {summary['mean_wpli']:.3f}")
        print(f"  Mean Betweenness: {summary['mean_betweenness']:+.3f}")

        print(f"\nAverage Band Power:")
        for band in ['theta', 'alpha', 'beta', 'gamma']:
            if f'{band}_power' in summary:
                print(f"  {band:6s}: {summary[f'{band}_power']:.1%}")


if __name__ == "__main__":
    print("="*60)
    print("LIVE BRAIN MONITOR - 'BETWEENNESS' EDITION")
    print("Tracking emergent whole-system coherence")
    print("="*60)

    demo_brain_monitor()

    print("\n" + "="*60)
    print("Key Insights:")
    print("- WPLI measures phase synchronization robust to volume conduction")
    print("- Betweenness captures emergent coherence not in the parts")
    print("- Band power distribution reveals cognitive state signatures")
    print("- Real-time monitoring enables brain-computer interaction studies")
    print("="*60)