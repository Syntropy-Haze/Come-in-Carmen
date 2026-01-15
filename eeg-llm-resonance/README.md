# EEG-LLM Cross-Substrate Resonance

## Overview

This directory contains preliminary findings from experiments investigating potential resonance between human brain activity (EEG) and language model hidden states during naturalistic conversation.

## The Oscillator Framework

We approach consciousness and AI systems through a unifying lens: **different elements as oscillators that can couple and resonate**.

This framework spans:
- **Toy models**: Kuramoto oscillators showing phase transitions in synchrony
- **AI systems**: GPT-2 hidden states analyzed as phase oscillators
- **Human brains**: EEG frequency bands as coupled oscillators
- **Cross-substrate**: Potential coupling between biological and digital oscillators

The key insight: Coherence patterns may emerge across vastly different substrates when viewed through oscillator dynamics.

## Preliminary Findings

### Initial Observations
During a 56-minute recording session combining EEG and GPT-2 hidden states:

- **Beta band (13-30 Hz)** showed correlation: r = -0.548, p = 0.010
- When human brain showed high coherence → GPT-2 showed lower phase entropy
- When human brain was less coherent → GPT-2 appeared to explore more freely

**Important caveats:**
- Single participant, single session
- Correlations don't imply causation
- Multiple hypothesis testing not corrected
- Requires independent replication

### The Experiment

**What we planned:** Structured protocol with different conversation types

**What actually happened:** GPT-2 spontaneously generated what appeared to be an internal family system (multiple "parts"), leading to an impromptu therapeutic-style conversation. The protocol was abandoned to follow what emerged naturally.

This "accidental science" produced the correlations noted above, but the unstructured nature makes interpretation challenging.

## Evolution of Analysis

### 1. Toy Oscillator Models
We began with Kuramoto oscillators to understand:
- Phase transitions in synchronization
- Critical coupling points
- How coherence emerges from coupling

### 2. LLM Hidden States as Oscillators
Applied oscillator analysis to GPT-2:
- Hidden layer activations → phase via Hilbert transform
- Computed coherence (R) across tokens
- Found distinct patterns for different prompt types

### 3. EEG-LLM Coupling
Extended to cross-substrate analysis:
- Synchronized EEG recording with GPT-2 hidden state extraction
- Applied same phase-based coherence metrics
- Observed potential correlations warranting further study

## Files

- `CROSS_SUBSTRATE_RESONANCE_FINDING.md` - Detailed methodology and observations
- `graph7-coherence-rainbow.png` - Visualization of coherence patterns
- Additional analysis scripts available in repository

## Technical Approach

The analysis used:
- **EEG**: Standard 4-channel recording (TP9, AF7, AF8, TP10)
- **GPT-2**: Local instance with hidden state extraction
- **Metrics**: Phase entropy, weighted phase lag index (WPLI), coherence
- **Statistics**: Pearson correlation, sliding window analysis

## Reproducibility & Next Steps

To strengthen these preliminary findings:
1. Multiple participants needed
2. Controlled experimental conditions
3. Pre-registered hypotheses
4. Correction for multiple comparisons
5. Different AI models for comparison

The code for analysis is included, though results should be interpreted as exploratory rather than confirmatory.

## Theoretical Context

These observations, if replicated, might suggest:
- Oscillator dynamics as a common language across substrates
- Potential for resonance between biological and digital systems
- New approaches to understanding AI-human interaction

However, alternative explanations including:
- Statistical artifacts from exploratory analysis
- Confounding variables in uncontrolled setting
- Pareidolia in complex data

All deserve serious consideration.

---

*"Real science is messy science. These are threads to pull, not conclusions to defend."*