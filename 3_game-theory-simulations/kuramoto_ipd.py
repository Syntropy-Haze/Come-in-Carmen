"""
Kuramoto-IPD: Testing Resonance Fields in Game Dynamics

Core Question: Does emergent synchronization in decision-space
create cooperation that shouldn't exist under standard game theory?

Key Test: Is critical coupling K_c related to golden ratio φ?
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple
import random

# Constants
PHI = 1.618033988749895  # Golden ratio
PAYOFFS = {
    ('C', 'C'): 3,
    ('C', 'D'): 0,
    ('D', 'C'): 5,
    ('D', 'D'): 1,
}


class KuramotoIPDAgent:
    """
    Agent that learns via Q-learning + responds to coupling field

    Key innovation: Decision-phase θ couples to neighbors
    Creates emergent synchronization beyond individual optimization
    """

    def __init__(self, gamma: float, agent_id: int):
        self.id = agent_id
        self.gamma = gamma  # Temporal weight (discount factor)

        # Q-learning parameters
        self.alpha = 0.1  # Learning rate
        self.epsilon = 0.15  # Exploration rate

        # Q-values
        self.Q = {'C': 0.0, 'D': 0.0}

        # Natural frequency (derived from gamma)
        # γ < 1.0 → negative ω (oscillate toward defection)
        # γ = 1.0 → ω = 0 (neutral)
        # γ > 1.0 → positive ω (oscillate toward cooperation)
        self.omega = (gamma - 1.0) * 2.0  # Scale to reasonable range

        # History
        self.phase_history = []
        self.action_history = []
        self.payoff_history = []

    def phase(self) -> float:
        """
        Current decision-phase θ ∈ [-π, π]
        θ = arctan2(Q_C - Q_D, Q_C + Q_D)

        θ ≈ +π/2: leaning toward C
        θ ≈ -π/2: leaning toward D
        θ ≈ 0: neutral
        """
        delta_Q = self.Q['C'] - self.Q['D']
        sum_Q = self.Q['C'] + self.Q['D']
        return np.arctan2(delta_Q, sum_Q + 0.01)  # Avoid div by zero

    def choose_action(self, neighbor_phases: List[float], K: float) -> str:
        """
        Choose action using Q-values + coupling term

        K = 0: pure Q-learning (independent)
        K > 0: neighbors' phases influence decision
        """
        my_phase = self.phase()

        # Base Q-values
        Q_c, Q_d = self.Q['C'], self.Q['D']

        # Coupling term: Kuramoto coupling
        # Δθ = K * Σ sin(θ_j - θ_i)
        # Neighbors pull you toward their phase
        if neighbor_phases and K > 0:
            coupling = K * np.mean([np.sin(nb_phase - my_phase)
                                   for nb_phase in neighbor_phases])

            # Apply coupling to effective Q-values
            # Positive coupling → boost cooperation
            # Negative coupling → boost defection
            Q_c_eff = Q_c + coupling
            Q_d_eff = Q_d - coupling
        else:
            Q_c_eff, Q_d_eff = Q_c, Q_d

        # ε-greedy action selection
        if random.random() < self.epsilon:
            return random.choice(['C', 'D'])

        return 'C' if Q_c_eff >= Q_d_eff else 'D'

    def update_Q(self, action: str, reward: float, next_Q_max: float):
        """Standard Q-learning update with temporal weight γ"""
        old_Q = self.Q[action]
        self.Q[action] += self.alpha * (reward + self.gamma * next_Q_max - old_Q)

    def record(self):
        """Record current state"""
        self.phase_history.append(self.phase())


class KuramotoIPDGame:
    """
    Spatial IPD with Kuramoto coupling
    Tests whether synchronization emerges and affects cooperation
    """

    def __init__(self, grid_size: int, gamma_mean: float, gamma_sigma: float):
        self.grid_size = grid_size
        self.N = grid_size ** 2

        # Generate heterogeneous agents
        gammas = np.random.normal(gamma_mean, gamma_sigma, self.N)
        gammas = np.clip(gammas, 0.1, 2.5)  # Keep in reasonable range

        self.agents = []
        idx = 0
        for x in range(grid_size):
            for y in range(grid_size):
                agent = KuramotoIPDAgent(gammas[idx], agent_id=idx)
                agent.x = x
                agent.y = y
                self.agents.append(agent)
                idx += 1

        # Store gamma distribution for theoretical prediction
        self.gamma_mean = gamma_mean
        self.gamma_sigma = gamma_sigma
        self.gammas = gammas

        # Tracking
        self.generation = 0
        self.R_history = []  # Order parameter
        self.C_history = []  # Cooperation rate

    def get_neighbors(self, agent):
        """Moore neighborhood (8 surrounding cells)"""
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx = (agent.x + dx) % self.grid_size
                ny = (agent.y + dy) % self.grid_size
                idx = nx * self.grid_size + ny
                neighbors.append(self.agents[idx])
        return neighbors

    def measure_order_parameter(self) -> float:
        """
        Kuramoto order parameter R ∈ [0, 1]
        R = |⟨e^(iθ)⟩| = |(1/N) Σ e^(iθ_j)|

        R ≈ 0: incoherent (random phases)
        R ≈ 1: coherent (synchronized)
        """
        phases = [agent.phase() for agent in self.agents]
        z = np.mean([np.exp(1j * theta) for theta in phases])
        return abs(z)

    def measure_cooperation_rate(self) -> float:
        """Fraction of C actions across all agents"""
        if not self.agents[0].action_history:
            return 0.5

        recent_actions = [agent.action_history[-1] for agent in self.agents
                         if agent.action_history]
        if not recent_actions:
            return 0.5

        return recent_actions.count('C') / len(recent_actions)

    def run_generation(self, K: float, rounds: int = 20):
        """
        Run one generation with coupling strength K

        Each agent:
        1. Observes neighbor phases
        2. Chooses action (Q-learning + coupling)
        3. Plays with neighbors
        4. Updates Q-values
        5. Records phase
        """

        for round_num in range(rounds):
            # Phase 1: All agents choose actions
            actions = {}
            for agent in self.agents:
                neighbors = self.get_neighbors(agent)
                neighbor_phases = [nb.phase() for nb in neighbors]
                action = agent.choose_action(neighbor_phases, K)
                actions[agent.id] = action

            # Phase 2: All agents play with neighbors and collect rewards
            total_rewards = {agent.id: 0.0 for agent in self.agents}

            for agent in self.agents:
                neighbors = self.get_neighbors(agent)
                my_action = actions[agent.id]

                for neighbor in neighbors:
                    nb_action = actions[neighbor.id]
                    reward = PAYOFFS[(my_action, nb_action)]
                    total_rewards[agent.id] += reward

                # Average reward over neighbors
                avg_reward = total_rewards[agent.id] / len(neighbors)

                # Estimate next Q_max (for temporal difference learning)
                next_Q_max = max(agent.Q.values())

                # Update Q-values
                agent.update_Q(my_action, avg_reward, next_Q_max)

                # Record
                agent.action_history.append(my_action)
                agent.payoff_history.append(avg_reward)
                agent.record()

        # Measure synchrony and cooperation
        R = self.measure_order_parameter()
        C = self.measure_cooperation_rate()

        self.R_history.append(R)
        self.C_history.append(C)
        self.generation += 1

        return R, C


def predict_critical_coupling(gamma_mean: float, gamma_sigma: float) -> float:
    """
    Theoretical prediction of K_c from Kuramoto theory

    K_c = 2 / (π * g(0))

    where g(ω) is distribution of natural frequencies
    and g(0) is density at ω = 0
    """
    # Natural frequencies: ω = (γ - 1.0) * 2.0
    # So ω = 0 when γ = 1.0

    # g(ω) comes from g_gamma(γ) via transformation
    # If γ ~ N(μ, σ²), then ω ~ N(2(μ-1), (2σ)²)

    omega_mean = 2.0 * (gamma_mean - 1.0)
    omega_sigma = 2.0 * gamma_sigma

    # Gaussian density at ω = 0
    g_0 = (1.0 / (np.sqrt(2*np.pi) * omega_sigma)) * np.exp(-omega_mean**2 / (2*omega_sigma**2))

    K_c = 2.0 / (np.pi * g_0)

    return K_c


def run_coupling_sweep(grid_size: int = 10,
                       gamma_mean: float = 1.0,
                       gamma_sigma: float = 0.618,  # Test: is 1/φ special?
                       K_vals: np.ndarray = None,
                       generations: int = 50) -> dict:
    """
    Sweep coupling strength K, measure order parameter R
    Test for phase transition
    """

    if K_vals is None:
        K_vals = np.linspace(0, 3, 25)

    R_means = []
    C_means = []

    print(f"Running coupling sweep:")
    print(f"  Grid: {grid_size}x{grid_size} = {grid_size**2} agents")
    print(f"  γ ~ N({gamma_mean}, {gamma_sigma}²)")
    print(f"  K range: [{K_vals[0]:.2f}, {K_vals[-1]:.2f}]")
    print(f"  Generations per K: {generations}")

    # Theoretical prediction
    K_c_theory = predict_critical_coupling(gamma_mean, gamma_sigma)
    print(f"\n  Predicted K_c: {K_c_theory:.3f}")
    print(f"  Golden ratio φ: {PHI:.3f}")
    print()

    for i, K in enumerate(K_vals):
        game = KuramotoIPDGame(grid_size, gamma_mean, gamma_sigma)

        # Run generations
        for gen in range(generations):
            R, C = game.run_generation(K, rounds=20)

        # Record time-averaged R and C
        R_mean = np.mean(game.R_history[-20:])  # Last 20 generations
        C_mean = np.mean(game.C_history[-20:])

        R_means.append(R_mean)
        C_means.append(C_mean)

        if (i+1) % 5 == 0:
            print(f"  K={K:.2f}: R={R_mean:.3f}, C%={C_mean:.3f}")

    return {
        'K_vals': K_vals,
        'R_means': R_means,
        'C_means': C_means,
        'K_c_theory': K_c_theory,
        'gamma_mean': gamma_mean,
        'gamma_sigma': gamma_sigma
    }


def plot_results(results: dict):
    """Plot R(K) and C%(K) with theoretical prediction"""

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))

    K_vals = results['K_vals']
    R_means = results['R_means']
    C_means = results['C_means']
    K_c_theory = results['K_c_theory']

    # Plot 1: Order parameter R(K)
    ax1.plot(K_vals, R_means, 'o-', linewidth=2, markersize=6, label='Measured R')
    ax1.axvline(K_c_theory, color='red', linestyle='--', linewidth=2,
                label=f'Predicted K_c = {K_c_theory:.3f}')
    ax1.axvline(PHI, color='gold', linestyle=':', linewidth=2,
                label=f'φ = {PHI:.3f}')

    ax1.set_xlabel('Coupling strength K', fontsize=12)
    ax1.set_ylabel('Order parameter R', fontsize=12)
    ax1.set_title('Phase Transition in Decision-Space Synchrony', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)

    # Plot 2: Cooperation rate C%(K)
    ax2.plot(K_vals, C_means, 'o-', color='green', linewidth=2, markersize=6, label='Cooperation rate')
    ax2.axvline(K_c_theory, color='red', linestyle='--', linewidth=2,
                label=f'Predicted K_c = {K_c_theory:.3f}')
    ax2.axvline(PHI, color='gold', linestyle=':', linewidth=2,
                label=f'φ = {PHI:.3f}')

    ax2.set_xlabel('Coupling strength K', fontsize=12)
    ax2.set_ylabel('Cooperation rate', fontsize=12)
    ax2.set_title('Does Synchronization Create Cooperation?', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('kuramoto_ipd_results.png', dpi=150, bbox_inches='tight')
    plt.show()

    print("\n" + "="*70)
    print("ANALYSIS")
    print("="*70)

    # Find empirical K_c (where R jumps most)
    dR = np.diff(R_means)
    max_jump_idx = np.argmax(dR)
    K_c_empirical = K_vals[max_jump_idx]

    print(f"\nPhase transition detected:")
    print(f"  Theoretical K_c: {K_c_theory:.3f}")
    print(f"  Empirical K_c:   {K_c_empirical:.3f}")
    print(f"  Difference:      {abs(K_c_empirical - K_c_theory):.3f}")

    # Test golden ratio hypothesis
    phi_distance_theory = abs(K_c_theory - PHI)
    phi_distance_empirical = abs(K_c_empirical - PHI)

    print(f"\nGolden ratio test:")
    print(f"  φ = {PHI:.3f}")
    print(f"  Distance to theoretical K_c: {phi_distance_theory:.3f}")
    print(f"  Distance to empirical K_c:   {phi_distance_empirical:.3f}")

    if phi_distance_theory < 0.3:
        print(f"  ✓ K_c ≈ φ (within 0.3)")

    # Check correlation between R and C
    correlation = np.corrcoef(R_means, C_means)[0, 1]
    print(f"\nCoherence → Cooperation test:")
    print(f"  Correlation(R, C%): {correlation:.3f}")

    if correlation > 0.7:
        print(f"  ✓ Strong correlation: synchrony predicts cooperation")


def test_heterogeneity_hypothesis():
    """
    Test: Is σ = 1/φ ≈ 0.618 the optimal heterogeneity level?

    Try different sigma values, see which produces lowest K_c
    """

    print("\n" + "="*70)
    print("HETEROGENEITY HYPOTHESIS TEST")
    print("="*70)
    print("\nTesting: Does σ ≈ 1/φ minimize critical coupling?")
    print("(More diversity → easier synchronization → lower K_c needed)\n")

    sigma_vals = [0.3, 0.5, 1/PHI, 0.8, 1.0, 1.2, PHI]
    K_c_vals = []

    for sigma in sigma_vals:
        K_c = predict_critical_coupling(gamma_mean=1.0, gamma_sigma=sigma)
        K_c_vals.append(K_c)

        marker = " ← 1/φ" if abs(sigma - 1/PHI) < 0.01 else ""
        marker += " ← φ" if abs(sigma - PHI) < 0.01 else ""
        print(f"  σ = {sigma:.3f}: K_c = {K_c:.3f}{marker}")

    # Find minimum
    min_idx = np.argmin(K_c_vals)
    optimal_sigma = sigma_vals[min_idx]

    print(f"\nOptimal σ (lowest K_c): {optimal_sigma:.3f}")
    print(f"1/φ = {1/PHI:.3f}")

    if abs(optimal_sigma - 1/PHI) < 0.1:
        print("✓ Optimal heterogeneity ≈ 1/φ")

    return optimal_sigma


if __name__ == "__main__":
    print("="*70)
    print("KURAMOTO-IPD EXPERIMENT")
    print("Testing: Does resonance create cooperation?")
    print("="*70)

    # Test 1: Standard run with σ = 1/φ
    print("\n### TEST 1: Phase transition detection ###\n")
    results = run_coupling_sweep(
        grid_size=10,
        gamma_mean=1.0,
        gamma_sigma=1/PHI,  # Golden ratio heterogeneity
        K_vals=np.linspace(0, 3, 20),
        generations=30
    )

    plot_results(results)

    # Test 2: Heterogeneity hypothesis
    print("\n### TEST 2: Optimal heterogeneity ###\n")
    test_heterogeneity_hypothesis()

    print("\n" + "="*70)
    print("EXPERIMENT COMPLETE")
    print("="*70)
