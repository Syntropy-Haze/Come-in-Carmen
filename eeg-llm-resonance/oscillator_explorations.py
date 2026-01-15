#!/usr/bin/env python3
"""
Oscillator Framework: From Kuramoto Models to GPT-2 Coherence

This demonstrates the progression from toy oscillator models to analyzing
AI systems as collections of coupled oscillators.

Part 1: Kuramoto oscillators showing phase transitions
Part 2: GPT-2 hidden states analyzed as oscillators
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import hilbert

# ============================================================================
# PART 1: KURAMOTO OSCILLATORS - TOY MODEL OF SYNCHRONIZATION
# ============================================================================

def kuramoto_simulation(N=50, T=2000, dt=0.01, K_vals=None):
    """
    Simulate Kuramoto oscillators to show phase transition in synchrony.

    The Kuramoto model describes N oscillators with phases θᵢ evolving as:
    dθᵢ/dt = ωᵢ + (K/N) Σⱼ sin(θⱼ - θᵢ)

    Where:
    - ωᵢ is the natural frequency of oscillator i
    - K is the coupling strength
    - The sum couples each oscillator to all others

    Returns: coupling values and mean coherence for each
    """
    if K_vals is None:
        K_vals = np.linspace(0, 5, 50)

    # Natural frequencies from normal distribution
    omegas = np.random.normal(loc=1.0, scale=0.1, size=N)

    def compute_R(theta):
        """Order parameter R measures synchronization (0=random, 1=synchronized)"""
        return abs(np.sum(np.exp(1j * theta)) / N)

    R_means = []

    for K in K_vals:
        theta = np.random.uniform(0, 2*np.pi, N)  # Random initial phases
        R_t = []

        for t in range(T):
            # Kuramoto dynamics
            dtheta = omegas + (K/N) * np.sum(np.sin(theta[:, None] - theta[None, :]), axis=1)
            theta += dt * dtheta

            if t % 10 == 0:  # Sample every 10 steps
                R_t.append(compute_R(theta))

        R_means.append(np.mean(R_t))

    return K_vals, R_means


# ============================================================================
# PART 2: GPT-2 AS OSCILLATOR SYSTEM
# ============================================================================

def get_gpt2_hidden_states(prompt, layer_idx=-2):
    """
    Extract hidden states from GPT-2 for a given prompt.

    Note: This is a simplified version. Full implementation requires:
    - transformers library
    - GPT2Model and GPT2Tokenizer

    Returns: array of shape [seq_len, hidden_dim]
    """
    try:
        from transformers import GPT2Tokenizer, GPT2Model
        import torch

        tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        model = GPT2Model.from_pretrained("gpt2", output_hidden_states=True)
        model.eval()

        inputs = tokenizer(prompt, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)

        # Get specified layer (default: penultimate)
        hidden_states = outputs.hidden_states[layer_idx]
        return hidden_states[0].cpu().numpy()  # [seq_len, hidden_dim]

    except ImportError:
        print("Note: transformers library not installed. Returning mock data.")
        # Return mock data for demonstration
        seq_len = len(prompt.split())
        return np.random.randn(max(seq_len, 5), 768)


def compute_llm_coherence(hidden_states):
    """
    Compute coherence of LLM hidden states using phase analysis.

    Process:
    1. Treat each hidden dimension as an oscillator
    2. Extract phase via Hilbert transform
    3. Compute coherence (order parameter R) across dimensions

    Returns: coherence value for each token position
    """
    # Transpose so each row is one "neuron" across token positions
    H_transposed = hidden_states.T  # [hidden_dim, seq_len]

    # Get phases via Hilbert transform
    analytic_signal = hilbert(H_transposed, axis=1)
    phases = np.angle(analytic_signal)  # [hidden_dim, seq_len]

    # Compute coherence R(t) at each token position
    D, T = phases.shape
    R_t = np.abs(np.sum(np.exp(1j * phases), axis=0) / D)

    return R_t


def compute_phase_entropy(phases):
    """
    Compute phase entropy as measure of disorder.
    Lower entropy = more ordered/aligned phases
    """
    # Histogram phases to get distribution
    hist, _ = np.histogram(phases, bins=20, range=(-np.pi, np.pi), density=True)
    hist = hist[hist > 0]  # Remove zero bins

    # Shannon entropy
    entropy = -np.sum(hist * np.log(hist))
    return entropy


# ============================================================================
# DEMONSTRATION FUNCTIONS
# ============================================================================

def demo_kuramoto_transition():
    """Show phase transition in Kuramoto model"""
    print("Running Kuramoto simulation...")
    K_vals, R_means = kuramoto_simulation(N=50, T=2000)

    # Theoretical critical coupling
    sigma = 0.1  # Std dev of frequency distribution
    Kc = 2 / (np.pi * np.exp(-0.5) / (np.sqrt(2*np.pi) * sigma))

    plt.figure(figsize=(10, 6))
    plt.plot(K_vals, R_means, '-o', alpha=0.7, label='Simulation')
    plt.axvline(Kc, color='red', linestyle='--', label=f'Critical K = {Kc:.2f}')
    plt.xlabel('Coupling strength K')
    plt.ylabel('Mean coherence R')
    plt.title('Kuramoto Model: Phase Transition to Synchrony')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()

    print(f"Critical coupling (theory): K = {Kc:.2f}")
    print(f"Transition visible in simulation around K ≈ {K_vals[np.argmax(np.array(R_means) > 0.5)]:.2f}")


def demo_gpt2_coherence():
    """Analyze GPT-2 coherence for different prompt types"""
    prompts = {
        "factual": "The capital of France is Paris.",
        "poetic": "Everything arrives in space waiting empty.",
        "rigid": "There are exactly two well-defined categories.",
    }

    results = {}

    print("\nAnalyzing GPT-2 coherence patterns...")
    for prompt_type, prompt in prompts.items():
        hidden_states = get_gpt2_hidden_states(prompt)
        coherence = compute_llm_coherence(hidden_states)
        results[prompt_type] = coherence
        print(f"  {prompt_type}: mean coherence = {np.mean(coherence):.3f}")

    # Plot results
    plt.figure(figsize=(10, 6))
    for prompt_type, coherence in results.items():
        plt.plot(coherence, label=prompt_type, marker='o')

    plt.xlabel('Token index')
    plt.ylabel('Coherence R(t)')
    plt.title('GPT-2 Hidden State Coherence Across Token Positions')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("OSCILLATOR FRAMEWORK DEMONSTRATION")
    print("From toy models to AI system analysis")
    print("=" * 60)

    # Part 1: Kuramoto model
    print("\nPART 1: KURAMOTO OSCILLATORS")
    print("-" * 30)
    demo_kuramoto_transition()

    # Part 2: GPT-2 analysis
    print("\nPART 2: GPT-2 AS OSCILLATOR SYSTEM")
    print("-" * 30)
    demo_gpt2_coherence()

    print("\n" + "=" * 60)
    print("Key insight: Both systems show coherence emerging from coupling")
    print("This framework extends to EEG-LLM cross-substrate analysis")
    print("=" * 60)