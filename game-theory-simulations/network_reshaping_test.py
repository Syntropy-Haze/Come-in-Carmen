"""
Network Reshaping Test

Can coherent agents reshape their networks through relationship investment?

Key mechanisms:
- Relationship capital R[i][j] (pre-existing, not aligned with coherence)
- Matching weighted by capital (+ noise)
- Active investment/divestment (agent choice)
- Capital evolution: structural + intentional + decay

Tests: Can high-γ agents gradually shift capital toward coherent partners?
Starting embedded in incoherent networks (family, old friends)
Ending: self-organized coherent coalition
"""

import numpy as np
import matplotlib.pyplot as plt
import random

PHI = 1.618033988749895

class NetworkAgent:
    """
    Agent with relationship capital and strategic investment capacity
    """

    def __init__(self, gamma, agent_id):
        self.id = agent_id
        self.gamma = gamma

        # Game Q-values
        self.Q_game = {'C': 0.0, 'D': 0.0}

        # NEW: Relationship strategy Q-values
        self.Q_relationship = {
            'invest': 0.0,   # Build capital with this partner
            'maintain': 0.0,  # Neutral
            'divest': 0.0     # Withdraw from relationship
        }

        # Engagement Q-values
        self.Q_engage = 0.0
        self.Q_refuse = 0.0

        # Ledger usage
        self.use_ledger_Q = 0.0
        self.ignore_ledger_Q = 0.0

        # Learning
        self.alpha = 0.1
        self.epsilon = 0.15

        # Bandwidth (patience → deep analysis)
        self.analysis_depth = int(gamma * 50)

        # Memory
        self.interaction_memory = {}

    def analyze_partner(self, partner_id, global_ledger):
        """Assess trustworthiness using bandwidth"""
        partner_history = global_ledger.get(partner_id, [])
        visible = partner_history[-self.analysis_depth:] if partner_history else []

        if not visible:
            return 0.0

        # Base: cooperation rate
        coop_rate = sum(1 for a in visible if a == 'C') / len(visible)
        trust = (coop_rate - 0.5) * 2

        # Deep patterns (high bandwidth only)
        if self.analysis_depth > 30:
            patience_signal = 0.0
            reciprocity_signal = 0.0

            if partner_id in self.interaction_memory:
                our_history = self.interaction_memory[partner_id][-20:]

                # Patience: cooperated after I defected?
                for i in range(len(our_history) - 1):
                    my_prev, their_prev = our_history[i]
                    _, their_next = our_history[i+1]
                    if my_prev == 'D' and their_next == 'C':
                        patience_signal += 1

                if len(our_history) > 5:
                    patience_signal /= len(our_history)

                # Reciprocity
                reciprocity_signal = sum(1 for my_a, their_a in our_history[-15:]
                                        if my_a == their_a)
                if len(our_history) > 5:
                    reciprocity_signal /= min(15, len(our_history))

            trust += patience_signal * 1.5 + reciprocity_signal * 0.5

        return np.clip(trust, -2, 2)

    def decide_engagement(self, partner_id, global_ledger):
        """Should I play with this partner?"""
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
        """Choose game action (C/D/REFUSE)"""
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
        """
        NEW: Decide how to adjust relationship capital

        invest: +0.2 capital (small cost, shows commitment)
        maintain: 0 (neutral)
        divest: -0.2 capital (withdrawing)

        Agents learn when investment helps
        """
        if random.random() < self.epsilon:
            return random.choice(['invest', 'maintain', 'divest'])

        Q_invest = self.Q_relationship['invest']
        Q_maintain = self.Q_relationship['maintain']
        Q_divest = self.Q_relationship['divest']

        # High-bandwidth agents use trust assessment
        use_ledger = self.use_ledger_Q > self.ignore_ledger_Q
        if use_ledger and self.analysis_depth > 30:
            trust = self.analyze_partner(partner_id, global_ledger)
            Q_invest += trust * 0.7  # More likely to invest in trustworthy
            Q_divest -= trust * 0.7  # Less likely to divest

        # Choose best strategy
        Q_values = {'invest': Q_invest, 'maintain': Q_maintain, 'divest': Q_divest}
        return max(Q_values, key=Q_values.get)

    def update(self, my_action, reward, partner_id, partner_action,
               engaged, used_ledger, rel_action):
        """Update all Q-values"""

        # Game Q-values
        if engaged and partner_action != 'REFUSE':
            self.Q_engage += self.alpha * (reward - self.Q_engage)

            next_Q = max(self.Q_game.values())
            if my_action != 'REFUSE':
                self.Q_game[my_action] += self.alpha * (reward + self.gamma * next_Q - self.Q_game[my_action])

            if used_ledger:
                self.use_ledger_Q += self.alpha * (reward - self.use_ledger_Q)
            else:
                self.ignore_ledger_Q += self.alpha * (reward - self.ignore_ledger_Q)

            # Memory
            if partner_id not in self.interaction_memory:
                self.interaction_memory[partner_id] = []
            self.interaction_memory[partner_id].append((my_action, partner_action))

        else:
            self.Q_refuse += self.alpha * (reward - self.Q_refuse)

        # NEW: Relationship strategy Q-values
        # Learn whether investment strategy paid off
        self.Q_relationship[rel_action] += self.alpha * (reward - self.Q_relationship[rel_action])


def create_family_clusters(N, n_clusters=5, cluster_size_range=(3, 6)):
    """Create family/friend group clusters"""
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


def run_network_reshaping_test(N=30, rounds=1500):
    """
    Test: Can coherent agents reshape networks through relationship investment?
    """

    print(f"Network Reshaping Test: {N} agents, {rounds} rounds\n")

    # Generate agents
    gammas = np.random.normal(1.0, 1/PHI, N)
    gammas = np.clip(gammas, 0.3, 2.0)
    agents = [NetworkAgent(gammas[i], i) for i in range(N)]

    high_gamma_ids = set(i for i in range(N) if gammas[i] > 1.3)
    low_gamma_ids = set(i for i in range(N) if gammas[i] < 0.8)

    print(f"  High-γ (>1.3): {len(high_gamma_ids)} agents")
    print(f"  Low-γ (<0.8):  {len(low_gamma_ids)} agents")
    print(f"  Bandwidth: {int(min(gammas)*50)} - {int(max(gammas)*50)} rounds\n")

    # Initialize relationship capital matrix
    # Starts RANDOMLY distributed (not aligned with coherence)
    R = np.random.exponential(scale=0.3, size=(N, N))
    R = R + R.T  # Make symmetric (mutual capital)
    np.fill_diagonal(R, 0)  # No self-relationships

    # Add family/friend clusters (high initial capital)
    clusters = create_family_clusters(N, n_clusters=5)
    print(f"  Created {len(clusters)} family/friend clusters")
    for cluster in clusters:
        for i in cluster:
            for j in cluster:
                if i != j:
                    R[i][j] = np.random.uniform(3, 6)  # High initial capital

    print(f"  Initial relationship capital range: {R[R > 0].min():.2f} - {R.max():.2f}\n")

    global_ledger = {i: [] for i in range(N)}

    payoffs = {
        ('C','C'): 3, ('C','D'): 0,
        ('D','C'): 5, ('D','D'): 1,
    }
    REFUSE_COST = 0.0
    INVEST_COST = 0.05  # Small cost to invest (attention/effort)

    # Matching parameters
    RELATIONSHIP_WEIGHT = 0.75  # 75% capital-weighted, 25% random

    # Tracking
    C_history = []
    high_gamma_coop = []  # High-γ ↔ High-γ cooperation
    mixed_coop = []

    payoffs_high = []
    payoffs_low = []

    # Track capital concentration over time
    capital_within_high = []  # Total capital among high-γ pairs
    capital_mixed = []        # Capital between high-γ and others

    # NEW: Track who gets pulled into the network
    # For each agent, track their capital concentration with high-γ network
    agent_coherence_affinity = {i: [] for i in range(N)}  # How connected to high-γ network?

    for r in range(rounds):
        round_payoffs = {i: [] for i in range(N)}
        engaged_pairs = []

        # Each agent gets matched
        matched = set()
        pairs = []

        for i in range(N):
            if i in matched:
                continue

            # Weighted matching (influence, not control)
            relationship_weights = R[i] ** 2  # Square to amplify differences
            random_weights = np.ones(N)

            weights = (RELATIONSHIP_WEIGHT * relationship_weights +
                      (1 - RELATIONSHIP_WEIGHT) * random_weights)

            weights[i] = 0  # Can't match with self
            weights[list(matched)] = 0  # Can't match with already matched

            if weights.sum() == 0:
                continue  # No available partners

            weights = weights / weights.sum()
            j = np.random.choice(N, p=weights)

            pairs.append((i, j))
            matched.add(i)
            matched.add(j)

        # Execute interactions
        for i, j in pairs:
            # Both decide
            action_i, engage_i, used_ledger_i = agents[i].choose_action(j, global_ledger)
            action_j, engage_j, used_ledger_j = agents[j].choose_action(i, global_ledger)

            # Determine outcome
            if not engage_i or not engage_j:
                reward_i = reward_j = REFUSE_COST
                engaged = False
                structural_change_i = -0.1  # Refusing damages relationship slightly
                structural_change_j = -0.1
            else:
                reward_i = payoffs[(action_i, action_j)]
                reward_j = payoffs[(action_j, action_i)]
                engaged = True
                engaged_pairs.append((i, j, action_i, action_j))

                # Structural relationship changes from game outcome
                if action_i == 'C' and action_j == 'C':
                    structural_change_i = structural_change_j = 0.15  # Mutual coop builds trust
                elif action_i == 'D' and action_j == 'C':
                    structural_change_i = -0.1  # I exploited, slight damage
                    structural_change_j = -0.3  # I was exploited, major damage
                elif action_i == 'C' and action_j == 'D':
                    structural_change_i = -0.3
                    structural_change_j = -0.1
                else:  # Both defect
                    structural_change_i = structural_change_j = -0.2

                global_ledger[i].append(action_i)
                global_ledger[j].append(action_j)

            # Agents choose relationship actions
            rel_action_i = agents[i].choose_relationship_action(j, reward_i, global_ledger)
            rel_action_j = agents[j].choose_relationship_action(i, reward_j, global_ledger)

            # Apply relationship choices
            intentional_change_i = {'invest': 0.2, 'maintain': 0.0, 'divest': -0.2}[rel_action_i]
            intentional_change_j = {'invest': 0.2, 'maintain': 0.0, 'divest': -0.2}[rel_action_j]

            if rel_action_i == 'invest':
                reward_i -= INVEST_COST  # Investment costs attention
            if rel_action_j == 'invest':
                reward_j -= INVEST_COST

            # Update capital (structural + intentional)
            R[i][j] += structural_change_i + intentional_change_i
            R[j][i] += structural_change_j + intentional_change_j

            R[i][j] = max(0.01, R[i][j])  # Floor at minimum
            R[j][i] = max(0.01, R[j][i])

            # Update agents
            agents[i].update(action_i, reward_i, j, action_j, engaged, used_ledger_i, rel_action_i)
            agents[j].update(action_j, reward_j, i, action_i, engaged, used_ledger_j, rel_action_j)

            round_payoffs[i].append(reward_i)
            round_payoffs[j].append(reward_j)

        # Natural decay (relationships require maintenance)
        R *= 0.98

        # Metrics
        if engaged_pairs:
            coop_count = sum(1 for i, j, ai, aj in engaged_pairs if ai == 'C')
            C_history.append(coop_count / (len(engaged_pairs) * 2))
        else:
            C_history.append(0)

        # Cooperation in high-γ pairs
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

        # Payoffs
        high_p = [np.mean(round_payoffs[i]) for i in high_gamma_ids if round_payoffs[i]]
        low_p = [np.mean(round_payoffs[i]) for i in low_gamma_ids if round_payoffs[i]]

        payoffs_high.append(np.mean(high_p) if high_p else 0)
        payoffs_low.append(np.mean(low_p) if low_p else 0)

        # Capital concentration (KEY METRIC)
        # How much capital is concentrated within high-γ network?
        capital_high = []
        capital_mix = []

        for i in high_gamma_ids:
            for j in high_gamma_ids:
                if i < j:
                    capital_high.append(R[i][j])

        for i in high_gamma_ids:
            for j in range(N):
                if j not in high_gamma_ids:
                    capital_mix.append(R[i][j])

        capital_within_high.append(np.mean(capital_high) if capital_high else 0)
        capital_mixed.append(np.mean(capital_mix) if capital_mix else 0)

        # NEW: Track each agent's affinity to high-γ network
        for i in range(N):
            # What fraction of my capital is with high-γ agents?
            my_capital_with_high = sum(R[i][j] for j in high_gamma_ids if i != j)
            my_total_capital = R[i].sum()

            affinity = my_capital_with_high / my_total_capital if my_total_capital > 0 else 0
            agent_coherence_affinity[i].append(affinity)

        if (r+1) % 150 == 0:
            print(f"  Round {r+1}: "
                  f"High-γ↔High-γ C={high_gamma_coop[-1]:.2%}, "
                  f"Capital(high/mix)={capital_within_high[-1]:.2f}/{capital_mixed[-1]:.2f}, "
                  f"Payoff(H/L)={payoffs_high[-1]:.2f}/{payoffs_low[-1]:.2f}")

    return {
        'agents': agents,
        'gammas': gammas,
        'R': R,
        'C_history': C_history,
        'high_gamma_coop': high_gamma_coop,
        'mixed_coop': mixed_coop,
        'payoffs_high': payoffs_high,
        'payoffs_low': payoffs_low,
        'capital_within_high': capital_within_high,
        'capital_mixed': capital_mixed,
        'agent_coherence_affinity': agent_coherence_affinity,
        'high_gamma_ids': high_gamma_ids,
        'low_gamma_ids': low_gamma_ids,
        'N': N
    }


def plot_network_reshaping(results):
    """Visualize network evolution"""

    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(4, 3, hspace=0.35, wspace=0.3)

    rounds = range(len(results['C_history']))

    # Row 1: Cooperation patterns
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(results['high_gamma_coop'], label='High-γ ↔ High-γ', linewidth=2.5, color='blue')
    ax1.plot(results['mixed_coop'], label='Mixed pairs', linewidth=2, color='purple', alpha=0.7, linestyle='--')
    ax1.axhline(0.7, color='green', linestyle=':', alpha=0.4)
    ax1.set_xlabel('Round')
    ax1.set_ylabel('Cooperation rate')
    ax1.set_title('COALITION EMERGENCE: Do High-γ Agents Cooperate More With Each Other?', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)

    # Row 2: CAPITAL RESHAPING (KEY!)
    ax2 = fig.add_subplot(gs[1, :])
    ax2.plot(results['capital_within_high'], label='Capital within high-γ network', linewidth=2.5, color='darkblue')
    ax2.plot(results['capital_mixed'], label='Capital: high-γ ↔ others', linewidth=2, color='orange', alpha=0.7)
    ax2.set_xlabel('Round')
    ax2.set_ylabel('Average relationship capital')
    ax2.set_title('NETWORK RESHAPING: Capital Concentration Over Time', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3)

    # Row 3: Payoffs and overall
    ax3 = fig.add_subplot(gs[2, 0])
    ax3.plot(results['C_history'], linewidth=2, color='gray')
    ax3.set_xlabel('Round')
    ax3.set_ylabel('Cooperation')
    ax3.set_title('Overall Cooperation')
    ax3.grid(True, alpha=0.3)

    ax4 = fig.add_subplot(gs[2, 1])
    ax4.plot(results['payoffs_high'], label='High-γ', linewidth=2, alpha=0.8)
    ax4.plot(results['payoffs_low'], label='Low-γ', linewidth=2, alpha=0.8)
    ax4.set_xlabel('Round')
    ax4.set_ylabel('Average payoff')
    ax4.set_title('Who Thrives?')
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    # Row 4: Final state analysis
    ax5 = fig.add_subplot(gs[3, 0])
    final_high_coop = np.mean(results['high_gamma_coop'][-80:])
    final_mixed_coop = np.mean(results['mixed_coop'][-80:])

    ax5.bar(['High-γ ↔ High-γ', 'Mixed'],
            [final_high_coop, final_mixed_coop],
            color=['blue', 'purple'], alpha=0.7)
    ax5.set_ylabel('Cooperation (final 80)')
    ax5.set_title('Coalition Strength')
    ax5.set_ylim([0, 1])
    ax5.grid(True, alpha=0.3, axis='y')

    ax6 = fig.add_subplot(gs[3, 1])
    final_capital_high = np.mean(results['capital_within_high'][-80:])
    final_capital_mixed = np.mean(results['capital_mixed'][-80:])

    ax6.bar(['Within high-γ', 'High-γ ↔ others'],
            [final_capital_high, final_capital_mixed],
            color=['darkblue', 'orange'], alpha=0.7)
    ax6.set_ylabel('Capital (final 80)')
    ax6.set_title('Network Concentration')
    ax6.grid(True, alpha=0.3, axis='y')

    ax7 = fig.add_subplot(gs[3, 2])
    final_payoff_high = np.mean(results['payoffs_high'][-80:])
    final_payoff_low = np.mean(results['payoffs_low'][-80:])

    ax7.bar(['High-γ', 'Low-γ'],
            [final_payoff_high, final_payoff_low],
            color=['green', 'red'], alpha=0.7)
    ax7.set_ylabel('Payoff (final 80)')
    ax7.set_title('Final Outcomes')
    ax7.grid(True, alpha=0.3, axis='y')

    plt.savefig('network_reshaping.png', dpi=150, bbox_inches='tight')
    print("\n✓ Plot saved")


def analyze_network_growth(results):
    """
    Analyze: Does the coherent network GROW?
    Do other agents get pulled in over time?
    """

    print("\n" + "="*70)
    print("NETWORK GROWTH ANALYSIS: Who Gets Pulled In?")
    print("="*70)

    affinity_data = results['agent_coherence_affinity']
    gammas = results['gammas']
    high_gamma_ids = results['high_gamma_ids']
    low_gamma_ids = results['low_gamma_ids']
    N = results['N']

    # Identify "middle-γ" agents
    middle_gamma_ids = [i for i in range(N)
                       if i not in high_gamma_ids and i not in low_gamma_ids]

    # For each group, track average affinity to high-γ network over time
    def get_group_affinity(group_ids, window='all'):
        if window == 'early':
            rounds = slice(50, 200)
        elif window == 'late':
            rounds = slice(-200, None)
        else:
            rounds = slice(None)

        affinities = []
        for agent_id in group_ids:
            if agent_id not in high_gamma_ids:  # Don't count high-γ agents themselves
                agent_affinity = affinity_data[agent_id][rounds]
                affinities.append(np.mean(agent_affinity))
        return np.mean(affinities) if affinities else 0

    print(f"\n1. AFFINITY TO HIGH-γ NETWORK (non-high-γ agents):")
    print(f"   Middle-γ agents:")
    print(f"     Early (rounds 50-200):  {get_group_affinity(middle_gamma_ids, 'early'):.1%}")
    print(f"     Late (final 200):       {get_group_affinity(middle_gamma_ids, 'late'):.1%}")

    print(f"   Low-γ agents:")
    print(f"     Early (rounds 50-200):  {get_group_affinity(low_gamma_ids, 'early'):.1%}")
    print(f"     Late (final 200):       {get_group_affinity(low_gamma_ids, 'late'):.1%}")

    # Find individual agents who shifted toward coherent network
    print(f"\n2. INDIVIDUAL MIGRATION PATTERNS:")

    migrants = []
    for i in range(N):
        if i in high_gamma_ids:
            continue  # Skip high-γ agents themselves

        early_affinity = np.mean(affinity_data[i][50:200])
        late_affinity = np.mean(affinity_data[i][-200:])
        shift = late_affinity - early_affinity

        if shift > 0.2:  # Significant shift toward coherent network
            migrants.append((i, gammas[i], early_affinity, late_affinity, shift))

    if migrants:
        migrants.sort(key=lambda x: x[4], reverse=True)  # Sort by shift magnitude
        print(f"   Found {len(migrants)} agents who migrated toward high-γ network:")
        for agent_id, gamma, early, late, shift in migrants[:5]:
            gamma_label = "mid-γ" if agent_id in middle_gamma_ids else "low-γ"
            print(f"     Agent {agent_id} ({gamma_label}, γ={gamma:.2f}): {early:.1%} → {late:.1%} (+{shift:.1%})")
    else:
        print(f"   No significant migration detected")

    # System-wide effect
    print(f"\n3. SYSTEM-WIDE EFFECT:")

    # Average affinity of ALL non-high-γ agents
    all_others = [i for i in range(N) if i not in high_gamma_ids]
    early_system = get_group_affinity(all_others, 'early')
    late_system = get_group_affinity(all_others, 'late')

    print(f"   Non-high-γ agents' average affinity to coherent network:")
    print(f"     Early: {early_system:.1%}")
    print(f"     Late:  {late_system:.1%}")
    print(f"     Change: {(late_system - early_system):+.1%}")

    if late_system > early_system + 0.1:
        print(f"\n   ✓✓ NETWORK GREW")
        print(f"      Other agents got pulled toward coherent network")
        print(f"      Coalition expanding beyond initial high-γ core")
    elif late_system > early_system + 0.05:
        print(f"\n   ✓ Modest growth")
    else:
        print(f"\n   → Network stable or contracting")
        print(f"      Coherent network remains exclusive to high-γ agents")


def analyze_network_reshaping(results):
    """Analyze network evolution"""

    print("\n" + "="*70)
    print("NETWORK RESHAPING ANALYSIS")
    print("="*70)

    # Capital concentration (KEY METRIC)
    initial_capital_high = np.mean(results['capital_within_high'][:20])
    final_capital_high = np.mean(results['capital_within_high'][-80:])

    initial_capital_mixed = np.mean(results['capital_mixed'][:20])
    final_capital_mixed = np.mean(results['capital_mixed'][-80:])

    print(f"\n1. CAPITAL RESHAPING:")
    print(f"   Within high-γ network:")
    print(f"     Initial: {initial_capital_high:.2f}")
    print(f"     Final:   {final_capital_high:.2f}")
    print(f"     Change:  {(final_capital_high - initial_capital_high):+.2f} ({((final_capital_high/initial_capital_high - 1)*100):+.0f}%)")

    print(f"   High-γ ↔ others:")
    print(f"     Initial: {initial_capital_mixed:.2f}")
    print(f"     Final:   {final_capital_mixed:.2f}")
    print(f"     Change:  {(final_capital_mixed - initial_capital_mixed):+.2f} ({((final_capital_mixed/initial_capital_mixed - 1)*100):+.0f}%)")

    if final_capital_high > final_capital_mixed * 1.5:
        print(f"\n   ✓✓ NETWORK RESHAPING SUCCESSFUL")
        print(f"      Capital concentrated within coherent network")

    # Cooperation
    final_high_coop = np.mean(results['high_gamma_coop'][-80:])
    final_mixed_coop = np.mean(results['mixed_coop'][-80:])

    print(f"\n2. COALITION FORMATION:")
    print(f"   High-γ ↔ High-γ: {final_high_coop:.1%}")
    print(f"   Mixed pairs:     {final_mixed_coop:.1%}")
    print(f"   Difference: {(final_high_coop - final_mixed_coop):+.1%}")

    if final_high_coop > final_mixed_coop + 0.15:
        print(f"   ✓ Strong preferential cooperation")

    # Payoffs
    final_payoff_high = np.mean(results['payoffs_high'][-80:])
    final_payoff_low = np.mean(results['payoffs_low'][-80:])

    print(f"\n3. OUTCOMES:")
    print(f"   High-γ payoff: {final_payoff_high:.2f}")
    print(f"   Low-γ payoff:  {final_payoff_low:.2f}")
    print(f"   Difference: {(final_payoff_high - final_payoff_low):+.2f}")

    if final_payoff_high > final_payoff_low + 0.2:
        print(f"   ✓ Network reshaping → payoff advantage")

    # Trajectory
    early_capital_high = np.mean(results['capital_within_high'][40:120])
    late_capital_high = np.mean(results['capital_within_high'][-80:])

    print(f"\n4. TRAJECTORY:")
    print(f"   Capital growth: {early_capital_high:.2f} → {late_capital_high:.2f}")

    if late_capital_high > early_capital_high * 1.3:
        print(f"   ✓ Accelerating concentration (compound growth)")

    print(f"\n5. INTERPRETATION:")
    if (final_capital_high > initial_capital_high * 1.5 and
        final_high_coop > final_mixed_coop + 0.15):
        print(f"   SUCCESS: Coherent agents reshaped their networks")
        print(f"   - Started: embedded in random relationships")
        print(f"   - Strategy: invest in trustworthy, divest from exploiters")
        print(f"   - Result: concentrated capital → preferential matching → coalition")
        print(f"   → Parallel network emerged through strategic relationship investment")
    else:
        print(f"   Partial reshaping or transition ongoing")
        print(f"   May need longer horizon or different parameters")


if __name__ == "__main__":
    print("="*70)
    print("NETWORK RESHAPING TEST - LONG HORIZON")
    print("Can coherent agents reshape networks through relationship investment?")
    print("Giving them TIME to figure it out...")
    print("="*70)
    print()

    results = run_network_reshaping_test(N=30, rounds=1500)
    plot_network_reshaping(results)
    analyze_network_reshaping(results)
    analyze_network_growth(results)

    print("\n" + "="*70)
    print("COMPLETE")
    print("="*70)
