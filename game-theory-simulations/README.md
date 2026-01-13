# Game Theory Simulations: Coherence Propagation

## Overview

This directory contains game theory simulations exploring how coherence spreads through competitive systems. The work combines Prisoner's Dilemma dynamics with physics-based synchronization models to test whether coherent strategies can outcompete exploitation.

## Key Simulations

### 1. Kuramoto-IPD (`kuramoto_ipd.py`)
Fuses the Kuramoto synchronization model from physics with iterated Prisoner's Dilemma:
- Agents have "decision phases" that couple to neighbors
- Tests theoretical prediction: cooperation peaks at critical coupling K_c ≈ 2.0
- **Result:** Cooperation spike occurs EXACTLY at predicted K_c ✓
- Golden ratio (φ ≈ 1.618) appears as barrier to coherence

### 2. Network Reshaping (`network_reshaping_test.py`)
Explores how high-coherence agents build parallel networks:
- Relationship capital system (invest/divest in connections)
- Tracks 1500-round emergence trajectory
- **Result:** High-γ agents initially suffer, then build coherent coalition, achieve payoff reversal
- Shows full arc: burn down → selective rebuild → compound returns

### 3. Resonance Coalition (`resonance_coalition_test.py`)
Integrates Kuramoto phases with network formation:
- Competing resonance fields (coherent vs incoherent)
- Coupling strength based on relationship capital
- **Result:** Coherent field dominates from round 8, maintains 13x advantage

## Core Findings

1. **Temporal Bootstrap:** Agents with long time horizons act on potential coherence before it's observable, actualizing it through their actions

2. **Exit Strategy:** Don't fix broken systems - build parallel networks, endure transition pain, wait for critical mass

3. **Diversity Enables Coherence:** Counterintuitively, heterogeneous systems synchronize MORE easily (more pathways to coherence)

## Theoretical Significance

These simulations test core predictions of The Syntropy Haze theory:
- Coherence spreads through resonance, not control
- Justice/fairness emerges from thermodynamic necessity
- Patient agents bootstrap cooperation through temporal perception

## Running the Simulations

All simulations require Python 3 with numpy, scipy, matplotlib:

```bash
python3 kuramoto_ipd.py  # Kuramoto-IPD fusion
python3 network_reshaping_test.py  # 1500-round network formation
python3 resonance_coalition_test.py  # Competing resonance fields
```

## Context

These simulations were developed collaboratively between James and multiple AI systems (Claude, GPT-4/5, Gemini) as part of testing whether game-theoretic predictions of consciousness-as-resonance theory hold under simulation.

---

*"Patience creates possibility."*