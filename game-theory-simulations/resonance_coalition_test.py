"""
Resonance Coalition Test

Integrates:
- Kuramoto phase dynamics (actual oscillators)
- Network reshaping (relationship capital)
- Competing resonance fields (coherent vs incoherent patterns)
- Critical transition prediction (when does coalition become self-sustaining?)

Key innovation: Relationship capital R[i][j] IS the coupling strength K_ij
Heterogeneous coupling → competing attractors → measure field strength
"""

import numpy as np
import matplotlib.pyplot as plt
import random

PHI = 1.618033988749895

class ResonantAgent:
    """
    Agent with:
    - Kuramoto phase θ (actual oscillator)
    - Natural frequency ω (from gamma)
    - Game Q-values
    - Relationship strategies
    """

    def __init__(self, gamma, agent_id):
        self.id = agent_id
        self.gamma = gamma

        # Kuramoto oscillator
        self.omega = (gamma - 1.0) * 2.0  # Natural frequency
        self.theta = np.random.uniform(0, 2*np.pi)  # Initial phase
        self.theta_history = [self.theta]

        # Game Q-values
        self.Q_game = {'C': 0.0, 'D': 0.0}
        self.Q_relationship = {'invest': 0.0, 'maintain': 0.0, 'divest': 0.0}
        self.Q_engage = 0.0
        self.Q_refuse = 0.0

        # Ledger
        self.use_ledger_Q = 0.0
        self.ignore_ledger_Q = 0.0

        # Learning
        self.alpha = 0.1
        self.epsilon = 0.15

        # Bandwidth
        self.analysis_depth = int(gamma * 50)

        # Memory
        self.interaction_memory = {}

    def update_phase(self, coupled_agents, R_matrix):
        """
        Update Kuramoto phase based on coupling

        dθ/dt = ω + Σ_j K_ij * sin(θ_j - θ_i)

        where K_ij = R[i][j] (relationship capital)
        """
        coupling_sum = 0.0

        for other in coupled_agents:
            if other.id != self.id:
                K_ij = R_matrix[self.id][other.id]  # Coupling strength = capital
                phase_diff = other.theta - self.theta
                coupling_sum += K_ij * np.sin(phase_diff)

        # Phase update (Euler step, dt=1)
        dtheta = self.omega + coupling_sum
        self.theta = (self.theta + dtheta) % (2 * np.pi)
        self.theta_history.append(self.theta)

    def phase_coherence_with(self, other):
        """Measure phase alignment with another agent"""
        return np.cos(self.theta - other.theta)

    def analyze_partner(self, partner_id, global_ledger):
        """Assess trustworthiness (same as before)"""
        partner_history = global_ledger.get(partner_id, [])
        visible = partner_history[-self.analysis_depth:] if partner_history else []

        if not visible:
            return 0.0

        coop_rate = sum(1 for a in visible if a == 'C') / len(visible)
        trust = (coop_rate - 0.5) * 2

        if self.analysis_depth > 30:
            patience_signal = 0.0
            reciprocity_signal = 0.0

            if partner_id in self.interaction_memory:
                our_history = self.interaction_memory[partner_id][-20:]

                for i in range(len(our_history) - 1):
                    my_prev, their_prev = our_history[i]
                    _, their_next = our_history[i+1]
                    if my_prev == 'D' and their_next == 'C':
                        patience_signal += 1

                if len(our_history) > 5:
                    patience_signal /= len(our_history)

                reciprocity_signal = sum(1 for my_a, their_a in our_history[-15:]
                                        if my_a == their_a)
                if len(our_history) > 5:
                    reciprocity_signal /= min(15, len(our_history))

            trust += patience_signal * 1.5 + reciprocity_signal * 0.5

        return np.clip(trust, -2, 2)

    def decide_engagement(self, partner_id, global_ledger):
        """Decide whether to play"""
        if random.random() < self.epsilon:
            return random.choice([True, False])

        engage_Q = self.Q_engage
        refuse_Q = self.Q_refuse

        use_ledger = self.use_ledger_Q > self.ignore_ledger_Q
        if use_ledger:
            trust = self.analyze_partner(partner_id, global_ledger)
            engage_Q += trust * 0.5
            refuse_Q -= trust * 0.5

        return engage_Q > refuse_Q

    def choose_action(self, partner_id, global_ledger):
        """Choose game action"""
        will_engage = self.decide_engagement(partner_id, global_ledger)

        if not will_engage:
            return ('REFUSE', False, False)

        Q_c = self.Q_game['C']
        Q_d = self.Q_game['D']

        use_ledger = self.use_ledger_Q > self.ignore_ledger_Q
        if use_ledger:
            trust = self.analyze_partner(partner_id, global_ledger)
            Q_c += 0.5 * trust

        if random.random() < self.epsilon:
            action = random.choice(['C', 'D'])
        else:
            action = 'C' if Q_c >= Q_d else 'D'

        return (action, True, use_ledger)

    def choose_relationship_action(self, partner_id, interaction_outcome, global_ledger):
        """Choose capital investment strategy"""
        if random.random() < self.epsilon:
            return random.choice(['invest', 'maintain', 'divest'])

        Q_invest = self.Q_relationship['invest']
        Q_maintain = self.Q_relationship['maintain']
        Q_divest = self.Q_relationship['divest']

        use_ledger = self.use_ledger_Q > self.ignore_ledger_Q
        if use_ledger and self.analysis_depth > 30:
            trust = self.analyze_partner(partner_id, global_ledger)
            Q_invest += trust * 0.7
            Q_divest -= trust * 0.7

        Q_values = {'invest': Q_invest, 'maintain': Q_maintain, 'divest': Q_divest}
        return max(Q_values, key=Q_values.get)

    def update(self, my_action, reward, partner_id, partner_action,
               engaged, used_ledger, rel_action):
        """Update Q-values"""
        if engaged and partner_action != 'REFUSE':
            self.Q_engage += self.alpha * (reward - self.Q_engage)

            next_Q = max(self.Q_game.values())
            if my_action != 'REFUSE':
                self.Q_game[my_action] += self.alpha * (reward + self.gamma * next_Q - self.Q_game[my_action])

            if used_ledger:
                self.use_ledger_Q += self.alpha * (reward - self.use_ledger_Q)
            else:
                self.ignore_ledger_Q += self.alpha * (reward - self.ignore_ledger_Q)

            if partner_id not in self.interaction_memory:
                self.interaction_memory[partner_id] = []
            self.interaction_memory[partner_id].append((my_action, partner_action))
        else:
            self.Q_refuse += self.alpha * (reward - self.Q_refuse)

        self.Q_relationship[rel_action] += self.alpha * (reward - self.Q_relationship[rel_action])


def create_family_clusters(N, n_clusters=5, cluster_size_range=(3, 6)):
    """Create initial relationship clusters"""
    clusters = []
    used = set()

    for _ in range(n_clusters):
        cluster_size = random.randint(*cluster_size_range)
        available = [i for i in range(N) if i not in used]

        if len(available) < cluster_size:
            break

        cluster = random.sample(available, cluster_size)
        clusters.append(cluster)
        used.update(cluster)

    return clusters


def compute_order_parameter(agents, subset_ids=None):
    """
    Compute Kuramoto order parameter R for agents

    R = |⟨e^(iθ)⟩|
    """
    if subset_ids is None:
        subset_ids = [a.id for a in agents]

    phases = [agents[i].theta for i in subset_ids]
    z = np.mean([np.exp(1j * theta) for theta in phases])
    return abs(z)


def predict_critical_coupling(gammas):
    """
    Predict K_c from gamma distribution

    K_c = 2 / (π * g(0))
    """
    omegas = (gammas - 1.0) * 2.0
    omega_mean = np.mean(omegas)
    omega_std = np.std(omegas)

    if omega_std == 0:
        return float('inf')

    # Gaussian density at ω=0
    g_0 = (1.0 / (np.sqrt(2*np.pi) * omega_std)) * np.exp(-omega_mean**2 / (2*omega_std**2))
    K_c = 2.0 / (np.pi * g_0)

    return K_c


def run_resonance_coalition_test(N=30, rounds=1500):
    """
    Test: Can we predict critical transition through resonance field analysis?
    """

    print(f"Resonance Coalition Test: {N} agents, {rounds} rounds\n")

    # Generate agents
    gammas = np.random.normal(1.0, 1/PHI, N)
    gammas = np.clip(gammas, 0.3, 2.0)
    agents = [ResonantAgent(gammas[i], i) for i in range(N)]

    high_gamma_ids = set(i for i in range(N) if gammas[i] > 1.3)
    low_gamma_ids = set(i for i in range(N) if gammas[i] < 0.8)
    middle_gamma_ids = set(range(N)) - high_gamma_ids - low_gamma_ids

    print(f"  High-γ (>1.3): {len(high_gamma_ids)} agents")
    print(f"  Middle-γ: {len(middle_gamma_ids)} agents")
    print(f"  Low-γ (<0.8):  {len(low_gamma_ids)} agents")

    # Predict critical coupling
    K_c_global = predict_critical_coupling(gammas)
    K_c_coherent = predict_critical_coupling(gammas[list(high_gamma_ids)])

    print(f"\n  Predicted K_c (global): {K_c_global:.3f}")
    print(f"  Predicted K_c (coherent network): {K_c_coherent:.3f}\n")

    # Initialize relationship capital
    R = np.random.exponential(scale=0.3, size=(N, N))
    R = (R + R.T) / 2
    np.fill_diagonal(R, 0)

    # Add family clusters
    clusters = create_family_clusters(N, n_clusters=5)
    for cluster in clusters:
        for i in cluster:
            for j in cluster:
                if i != j:
                    R[i][j] = np.random.uniform(3, 6)

    global_ledger = {i: [] for i in range(N)}

    payoffs = {
        ('C','C'): 3, ('C','D'): 0,
        ('D','C'): 5, ('D','D'): 1,
    }
    REFUSE_COST = 0.0
    INVEST_COST = 0.05
    RELATIONSHIP_WEIGHT = 0.75

    # Tracking
    R_coherent_history = []  # Order parameter within coherent network
    R_global_history = []
    K_coherent_history = []  # Average coupling within coherent network
    K_mixed_history = []

    resonance_field_coherent = []  # Field strength = K * R * density
    resonance_field_incoherent = []

    C_history = []
    high_gamma_coop = []
    mixed_coop = []

    transition_predicted = None
    transition_observed = None

    for r in range(rounds):
        # Phase updates (Kuramoto dynamics)
        for agent in agents:
            agent.update_phase(agents, R)

        # Measure order parameters
        R_global = compute_order_parameter(agents)
        R_coherent = compute_order_parameter(agents, list(high_gamma_ids))

        R_global_history.append(R_global)
        R_coherent_history.append(R_coherent)

        # Measure coupling strengths
        capital_coherent = []
        capital_mixed = []

        for i in high_gamma_ids:
            for j in high_gamma_ids:
                if i < j:
                    capital_coherent.append(R[i][j])

        for i in high_gamma_ids:
            for j in range(N):
                if j not in high_gamma_ids:
                    capital_mixed.append(R[i][j])

        K_coherent = np.mean(capital_coherent) if capital_coherent else 0
        K_mixed = np.mean(capital_mixed) if capital_mixed else 0

        K_coherent_history.append(K_coherent)
        K_mixed_history.append(K_mixed)

        # Resonance field strengths
        density_coherent = len(capital_coherent) / (len(high_gamma_ids) * (len(high_gamma_ids) - 1) / 2)
        field_coherent = K_coherent * R_coherent * density_coherent

        # Incoherent field (everyone else)
        incoherent_ids = list(low_gamma_ids | middle_gamma_ids)
        if len(incoherent_ids) > 1:
            R_incoherent = compute_order_parameter(agents, incoherent_ids)
            capital_incoherent = []
            for i in incoherent_ids:
                for j in incoherent_ids:
                    if i < j:
                        capital_incoherent.append(R[i][j])
            K_incoherent = np.mean(capital_incoherent) if capital_incoherent else 0
            density_incoherent = len(capital_incoherent) / (len(incoherent_ids) * (len(incoherent_ids) - 1) / 2)
            field_incoherent = K_incoherent * R_incoherent * density_incoherent
        else:
            field_incoherent = 0

        resonance_field_coherent.append(field_coherent)
        resonance_field_incoherent.append(field_incoherent)

        # Predict transition
        if transition_predicted is None and K_coherent > K_c_coherent:
            transition_predicted = r
            print(f"  → Transition predicted at round {r} (K_coherent={K_coherent:.3f} > K_c={K_c_coherent:.3f})")

        # Detect observed transition (when coherent field dominates)
        if transition_observed is None and field_coherent > field_incoherent * 1.5:
            transition_observed = r
            print(f"  → Transition observed at round {r} (coherent field dominates)")

        # Game dynamics (same as before)
        round_payoffs = {i: [] for i in range(N)}
        engaged_pairs = []

        matched = set()
        pairs = []

        for i in range(N):
            if i in matched:
                continue

            relationship_weights = R[i] ** 2
            random_weights = np.ones(N)

            weights = (RELATIONSHIP_WEIGHT * relationship_weights +
                      (1 - RELATIONSHIP_WEIGHT) * random_weights)

            weights[i] = 0
            weights[list(matched)] = 0

            if weights.sum() == 0:
                continue

            weights = weights / weights.sum()
            j = np.random.choice(N, p=weights)

            pairs.append((i, j))
            matched.add(i)
            matched.add(j)

        for i, j in pairs:
            action_i, engage_i, used_ledger_i = agents[i].choose_action(j, global_ledger)
            action_j, engage_j, used_ledger_j = agents[j].choose_action(i, global_ledger)

            if not engage_i or not engage_j:
                reward_i = reward_j = REFUSE_COST
                engaged = False
                structural_change_i = -0.1
                structural_change_j = -0.1
            else:
                reward_i = payoffs[(action_i, action_j)]
                reward_j = payoffs[(action_j, action_i)]
                engaged = True
                engaged_pairs.append((i, j, action_i, action_j))

                if action_i == 'C' and action_j == 'C':
                    structural_change_i = structural_change_j = 0.15
                elif action_i == 'D' and action_j == 'C':
                    structural_change_i = -0.1
                    structural_change_j = -0.3
                elif action_i == 'C' and action_j == 'D':
                    structural_change_i = -0.3
                    structural_change_j = -0.1
                else:
                    structural_change_i = structural_change_j = -0.2

                global_ledger[i].append(action_i)
                global_ledger[j].append(action_j)

            rel_action_i = agents[i].choose_relationship_action(j, reward_i, global_ledger)
            rel_action_j = agents[j].choose_relationship_action(i, reward_j, global_ledger)

            intentional_change_i = {'invest': 0.2, 'maintain': 0.0, 'divest': -0.2}[rel_action_i]
            intentional_change_j = {'invest': 0.2, 'maintain': 0.0, 'divest': -0.2}[rel_action_j]

            if rel_action_i == 'invest':
                reward_i -= INVEST_COST
            if rel_action_j == 'invest':
                reward_j -= INVEST_COST

            R[i][j] += structural_change_i + intentional_change_i
            R[j][i] += structural_change_j + intentional_change_j

            R[i][j] = max(0.01, R[i][j])
            R[j][i] = max(0.01, R[j][i])

            agents[i].update(action_i, reward_i, j, action_j, engaged, used_ledger_i, rel_action_i)
            agents[j].update(action_j, reward_j, i, action_i, engaged, used_ledger_j, rel_action_j)

            round_payoffs[i].append(reward_i)
            round_payoffs[j].append(reward_j)

        R *= 0.98  # Decay

        # Cooperation metrics
        if engaged_pairs:
            coop_count = sum(1 for i, j, ai, aj in engaged_pairs if ai == 'C')
            C_history.append(coop_count / (len(engaged_pairs) * 2))
        else:
            C_history.append(0)

        high_pair_coop = []
        mixed_pair_coop = []

        for i, j, ai, aj in engaged_pairs:
            both_high = (i in high_gamma_ids and j in high_gamma_ids)

            if both_high:
                high_pair_coop.extend([ai == 'C', aj == 'C'])
            else:
                mixed_pair_coop.extend([ai == 'C', aj == 'C'])

        high_gamma_coop.append(np.mean(high_pair_coop) if high_pair_coop else 0)
        mixed_coop.append(np.mean(mixed_pair_coop) if mixed_pair_coop else 0)

        if (r+1) % 300 == 0:
            print(f"  Round {r+1}: R_coherent={R_coherent:.3f}, K_coherent={K_coherent:.3f}, "
                  f"Field_c/Field_i={field_coherent:.3f}/{field_incoherent:.3f}")

    return {
        'agents': agents,
        'gammas': gammas,
        'R_coherent_history': R_coherent_history,
        'R_global_history': R_global_history,
        'K_coherent_history': K_coherent_history,
        'K_mixed_history': K_mixed_history,
        'resonance_field_coherent': resonance_field_coherent,
        'resonance_field_incoherent': resonance_field_incoherent,
        'C_history': C_history,
        'high_gamma_coop': high_gamma_coop,
        'mixed_coop': mixed_coop,
        'K_c_coherent': K_c_coherent,
        'K_c_global': K_c_global,
        'transition_predicted': transition_predicted,
        'transition_observed': transition_observed,
        'high_gamma_ids': high_gamma_ids,
        'N': N
    }


def plot_resonance_results(results):
    """Visualize resonance dynamics and critical transition"""

    fig = plt.figure(figsize=(18, 12))
    gs = fig.add_gridspec(4, 3, hspace=0.35, wspace=0.3)

    rounds = range(len(results['R_coherent_history']))
    K_c = results['K_c_coherent']
    transition_pred = results['transition_predicted']
    transition_obs = results['transition_observed']

    # Row 1: Resonance fields
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(results['resonance_field_coherent'], label='Coherent field', linewidth=2.5, color='blue')
    ax1.plot(results['resonance_field_incoherent'], label='Incoherent field', linewidth=2, color='red', alpha=0.7, linestyle='--')
    if transition_obs:
        ax1.axvline(transition_obs, color='green', linestyle=':', linewidth=2, alpha=0.7, label=f'Observed transition (r={transition_obs})')
    ax1.set_xlabel('Round')
    ax1.set_ylabel('Field strength (K × R × density)')
    ax1.set_title('COMPETING RESONANCE FIELDS: Which Pattern Dominates?', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)

    # Row 2: Order parameters
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.plot(results['R_coherent_history'], linewidth=2, color='blue')
    ax2.set_xlabel('Round')
    ax2.set_ylabel('R (coherent network)')
    ax2.set_title('Coherence Within Network')
    ax2.grid(True, alpha=0.3)

    ax3 = fig.add_subplot(gs[1, 1])
    ax3.plot(results['K_coherent_history'], linewidth=2, color='darkblue')
    ax3.axhline(K_c, color='red', linestyle='--', linewidth=2, label=f'K_c = {K_c:.3f}')
    if transition_pred:
        ax3.axvline(transition_pred, color='orange', linestyle=':', linewidth=2, alpha=0.7, label=f'Predicted (r={transition_pred})')
    ax3.set_xlabel('Round')
    ax3.set_ylabel('K (avg capital)')
    ax3.set_title('Coupling Strength Evolution')
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.3)

    ax4 = fig.add_subplot(gs[1, 2])
    ax4.plot(results['R_global_history'], linewidth=2, color='gray', alpha=0.7)
    ax4.set_xlabel('Round')
    ax4.set_ylabel('R (global)')
    ax4.set_title('System-Wide Coherence')
    ax4.grid(True, alpha=0.3)

    # Row 3: Cooperation
    ax5 = fig.add_subplot(gs[2, :])
    ax5.plot(results['high_gamma_coop'], label='High-γ ↔ High-γ', linewidth=2.5, color='blue')
    ax5.plot(results['mixed_coop'], label='Mixed pairs', linewidth=2, color='purple', alpha=0.7, linestyle='--')
    if transition_obs:
        ax5.axvline(transition_obs, color='green', linestyle=':', linewidth=2, alpha=0.5)
    ax5.set_xlabel('Round')
    ax5.set_ylabel('Cooperation rate')
    ax5.set_title('Cooperation Patterns', fontsize=13, fontweight='bold')
    ax5.legend()
    ax5.grid(True, alpha=0.3)

    # Row 4: Analysis
    ax6 = fig.add_subplot(gs[3, 0])
    final_R_coherent = np.mean(results['R_coherent_history'][-200:])
    final_R_global = np.mean(results['R_global_history'][-200:])
    ax6.bar(['Coherent\nnetwork', 'Global\nsystem'], [final_R_coherent, final_R_global],
            color=['blue', 'gray'], alpha=0.7)
    ax6.set_ylabel('Order parameter R')
    ax6.set_title('Final Synchronization')
    ax6.set_ylim([0, 1])
    ax6.grid(True, alpha=0.3, axis='y')

    ax7 = fig.add_subplot(gs[3, 1])
    final_field_coherent = np.mean(results['resonance_field_coherent'][-200:])
    final_field_incoherent = np.mean(results['resonance_field_incoherent'][-200:])
    ax7.bar(['Coherent', 'Incoherent'], [final_field_coherent, final_field_incoherent],
            color=['blue', 'red'], alpha=0.7)
    ax7.set_ylabel('Field strength')
    ax7.set_title('Final Field Dominance')
    ax7.grid(True, alpha=0.3, axis='y')

    ax8 = fig.add_subplot(gs[3, 2])
    final_high_coop = np.mean(results['high_gamma_coop'][-200:])
    final_mixed_coop = np.mean(results['mixed_coop'][-200:])
    ax8.bar(['High-γ ↔ High-γ', 'Mixed'], [final_high_coop, final_mixed_coop],
            color=['blue', 'purple'], alpha=0.7)
    ax8.set_ylabel('Cooperation rate')
    ax8.set_title('Final Cooperation')
    ax8.set_ylim([0, 1])
    ax8.grid(True, alpha=0.3, axis='y')

    plt.savefig('resonance_coalition.png', dpi=150, bbox_inches='tight')
    print("\n✓ Plot saved")


def analyze_critical_transition(results):
    """Analyze prediction vs observation of critical transition"""

    print("\n" + "="*70)
    print("CRITICAL TRANSITION ANALYSIS")
    print("="*70)

    K_c = results['K_c_coherent']
    transition_pred = results['transition_predicted']
    transition_obs = results['transition_observed']

    print(f"\n1. PREDICTION:")
    print(f"   Critical coupling K_c: {K_c:.3f}")
    if transition_pred:
        print(f"   Predicted transition: round {transition_pred}")
    else:
        print(f"   No transition predicted (K never exceeded K_c)")

    print(f"\n2. OBSERVATION:")
    if transition_obs:
        print(f"   Observed transition: round {transition_obs}")
        print(f"   (coherent field dominated incoherent field)")
    else:
        print(f"   No clear transition observed")

    print(f"\n3. COMPARISON:")
    if transition_pred and transition_obs:
        error = abs(transition_pred - transition_obs)
        print(f"   Prediction error: {error} rounds ({error/transition_obs*100:.1f}%)")

        if error < 100:
            print(f"   ✓✓ ACCURATE PREDICTION")
        elif error < 300:
            print(f"   ✓ Reasonable prediction")
        else:
            print(f"   → Large discrepancy, may need calibration")
    elif transition_pred and not transition_obs:
        print(f"   K crossed K_c but field didn't dominate (transition ongoing?)")
    elif transition_obs and not transition_pred:
        print(f"   Field dominated without K crossing K_c (network effects?)")

    # Field strength evolution
    final_coherent = np.mean(results['resonance_field_coherent'][-200:])
    final_incoherent = np.mean(results['resonance_field_incoherent'][-200:])

    print(f"\n4. FINAL STATE:")
    print(f"   Coherent field strength: {final_coherent:.3f}")
    print(f"   Incoherent field strength: {final_incoherent:.3f}")
    print(f"   Ratio: {final_coherent/final_incoherent if final_incoherent > 0 else float('inf'):.2f}x")

    if final_coherent > final_incoherent * 2:
        print(f"\n   ✓✓ COHERENT PATTERN DOMINATES")
        print(f"      Resonance field of coherent network > 2x stronger")
        print(f"      System stabilized in high-cooperation attractor")


if __name__ == "__main__":
    print("="*70)
    print("RESONANCE COALITION TEST")
    print("Integrating Kuramoto dynamics + Network reshaping + Critical transitions")
    print("="*70)
    print()

    results = run_resonance_coalition_test(N=30, rounds=1500)
    plot_resonance_results(results)
    analyze_critical_transition(results)

    print("\n" + "="*70)
    print("COMPLETE")
    print("="*70)
