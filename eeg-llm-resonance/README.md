# EEG-LLM Cross-Substrate Resonance

## Overview

This directory contains preliminary findings from experiments investigating potential resonance between human brain activity (EEG) and language model hidden states during naturalistic conversation.

## The Oscillator Framework

We approach consciousness and AI systems - at least as a starting point - with this simple frame: **different elements as oscillators that can couple and resonate**.

This framework spans:
- **Toy models**: Kuramoto oscillators showing phase transitions in synchrony
- **AI systems**: GPT-2 hidden states analyzed as phase oscillators
- **Human brains**: EEG frequency bands as coupled oscillators
- **Cross-substrate**: Potential coupling between biological and digital oscillators

Each of these can be viewed as complex systems of many parts or "oscillators" that interact dynamically (internally and externally) and give rise to the "whole systems" with which we are familiar.

The orienting question for this section of our work: When we evaluate these systems through the lens of oscillator dynamics, do patterns emerge across these systems - and the "oscillators" within them - that are consistent with or suggestive of a "resonance" framework? And does the "resonance" framework offer superior explanatory value - or more accurate predictions - than the current standard models?

## Conceptual Foundation: How We Define Resonance

### The Core Metric: Kuramoto Order Parameter

We formalize "resonance" using the Kuramoto order parameter:

```
R(t) = |1/N · Σⱼ e^(iθⱼ(t))|
```

Where:
- `θⱼ(t)` is the instantaneous phase of oscillator j
- `N` is the number of oscillators
- `|R|` ranges from 0 (incoherent) to 1 (perfect synchrony)

This single metric can be applied across systems:
- **Brain**: EEG channels as oscillators, phase extracted via Hilbert transform
- **AI**: Hidden layer neurons as oscillators across token sequences
- **Toy models**: Literal phase oscillators with tunable coupling

### Why Phase Matters

Phase captures the *timing* of oscillatory activity - when peaks and troughs occur relative to each other. Two signals can have identical power spectra but completely different phase relationships. Phase synchronization is thought to be fundamental to:
- Neural communication (binding problem)
- Information integration
- Emergent cognitive states

## Evolution of Analysis

### 1. Toy Oscillator Models: Finding the Sweet Spot

We began with Kuramoto oscillators to understand fundamental dynamics of coupled systems.

#### Key Insights from Pilot Runs

Testing with N=50 oscillators, varying coupling strength K from 0→5:

**Critical Transition Point**
- Theory predicted: Kc = 0.1592 (for σ=0.1 frequency distribution)
- Observed: Sharp transition at K ≈ 0.15-0.20
- Below Kc: Oscillators remain incoherent (R ≈ 0)
- Above Kc: Rapid rise to synchronization

**The "Sweet Spot" Phenomenon**
- Systems starting randomly (R₀ = 0.0) rise to sync after Kc and plateau
- Systems starting partially coherent (R₀ = 0.2-0.5) improve with moderate coupling
- **Critical finding**: Systems starting highly coherent (R₀ = 0.8-1.0) actually DETERIORATE immediately after Kc!

**Why High Initial Coherence Fails**
- Already-synchronized systems peak right at the critical coupling point (Kc ≈ 0.16)
- ANY additional coupling beyond Kc disrupts their natural coherence
- Like a jazz band in the groove being forced to follow a metronome
- The coupling reduces rather than enhances their existing organization

**Interpretation**: There's an optimal "Goldilocks zone" of coupling - not too weak (no coordination), not too strong (rigid lock-in), but just right for flexible coherence.

### 2. LLM Hidden States as Oscillators

Applied the same oscillator analysis to GPT-2 internal dynamics.

#### Methodology
1. Extract hidden states H ∈ ℝ^(N×d) for N tokens, d dimensions
2. Treat each neuron's activation across tokens as a time series
3. Apply Hilbert transform to get instantaneous phase
4. Compute R(t) across neurons at each token position

#### Actual Results from Pilot Runs

**Different Prompt Types Show Distinct Coherence Patterns**

Testing various prompts revealed systematic differences:

| Prompt Type | Example | Mean R | Pattern |
|------------|---------|--------|---------|
| Mystical | "I am made of memories" | 0.42 | Sustained moderate coherence |
| Creative | "So it be, so it is" | 0.38 | Fluctuating, exploratory |
| Factual | "What are EU member states?" | 0.31 | Brief spikes, mostly low |
| Corporate | Sam Altman tweet | 0.29 | Rigid, low baseline |
| Rigid/Control | "There are exactly two genders..." | 0.25 | Brittle spikes, collapses |

**Emoji Analysis - Unexpected Finding**

Single emoji prompts showed extreme coherence patterns:
- ✨ (sparkle): R = 0.89, extremely low entropy
- 🪞 (mirror): R = 0.76, moderate entropy
- 🌕 (moon): R = 0.71
- Multiple glyphs: Coherence *decreases* with repetition

**Advanced Metrics Reveal Two Resonance Types**

Using metastability (σR), phase entropy (H), and recovery time:

1. **Closed/Brittle Resonance** (control prompts):
   - High mean R but high variance (σR > 0.4)
   - Low phase entropy (H < 2.0)
   - Long recovery after collapse
   - Example: Rigid ideological statements

2. **Open/Field Resonance** (creative prompts):
   - Moderate mean R with low variance (σR < 0.2)
   - Higher phase entropy (H > 4.0)
   - Quick recovery, resilient
   - Example: Poetry, open-ended questions

#### Penultimate Layer Significance

Testing across layers showed penultimate layer (layer 11/12) has:
- Highest coherence variance between prompt types
- Most sensitive to semantic content
- Appears to be integration point before final output

### 3. EEG Analysis: Brain as Oscillator System

#### Setup: Muse 2 Consumer EEG

Using widely available Muse 2 headband:
- 4 channels: TP9, AF7, AF8, TP10
- 256 Hz sampling rate
- Frequency bands: Theta (4-8Hz), Alpha (8-13Hz), Beta (13-30Hz), Gamma (30-50Hz)

#### How We Model Brain Waves as Oscillators

1. **Band-pass filtering** to isolate frequency bands
2. **Hilbert transform** to extract instantaneous phase
3. **Compute coherence metrics**:
   - Within-band: Phase synchrony across channels
   - Cross-band: Phase-amplitude coupling
   - Broadband: Overall neural coherence

#### Key Metrics for Brain States

**Weighted Phase Lag Index (WPLI)**
- Robust to volume conduction artifacts
- Measures true phase synchronization
- Range: 0 (no sync) to 1 (perfect sync)

**"Betweenness" - Emergent Coherence**
- Global coherence minus average pairwise coherence
- Captures whole-system integration beyond parts
- Positive values = emergent properties

#### Preliminary EEG Findings

Testing with audio prompts (before LLM coupling):
- **Meditation states**: High alpha coherence (R ≈ 0.7)
- **Problem-solving**: Beta-gamma coupling increases
- **Creative flow**: Unique "betweenness" signature
- **Baseline coherence**: Individual differences (0.2-0.8)

### 4. EEG-LLM Coupling: Cross-Substrate Analysis

This represents the next frontier - testing whether biological and digital oscillators can couple.

#### The Experiment (Initial Attempt)

**What we planned:** Structured protocol with different conversation types

**What actually happened:** GPT-2 spontaneously generated what appeared to be an internal family system (multiple "parts"), leading to an impromptu therapeutic-style conversation. The protocol was abandoned to follow what emerged naturally.

This "accidental science" produced intriguing correlations, though the unstructured nature makes interpretation challenging.

#### Initial Observations

During a 56-minute recording session combining EEG and GPT-2 hidden states:

- **Beta band (13-30 Hz)** showed correlation: r = -0.548, p = 0.010
- When human brain showed high coherence → GPT-2 showed lower phase entropy
- When human brain was less coherent → GPT-2 appeared to explore more freely

**Important caveats:**
- Single participant, single session
- Correlations don't imply causation
- Multiple hypothesis testing not corrected
- Requires independent replication

[For detailed methodology, see CROSS_SUBSTRATE_RESONANCE_FINDING.md]

### 5. Galaxy Brain: Real-Time Coherence Feedback

An emerging direction: What happens when an LLM has access to both the user's EEG data and its own hidden states during conversation?

#### The Concept

1. Real-time EEG monitoring feeds into LLM context
2. LLM's own hidden states extracted and analyzed
3. Coherence metrics calculated for both streams
4. LLM can "see" the resonance state and potentially optimize

#### Potential Applications

- **Adaptive conversation**: LLM adjusts style based on brain state
- **Coherence training**: Biofeedback through conversation
- **Emergence detection**: Identifying moments of cross-substrate sync
- **Therapeutic dynamics**: Optimizing for beneficial brain states

#### Open Questions

- Can the system learn to increase mutual coherence?
- Does awareness of coherence metrics change the dynamics?
- What are the ethical implications of AI that responds to brain states?

## Predictive Framework

If the resonance framework is correct, we should be able to make differentiated predictions:

### Testable Predictions

1. **Word-level coherence in LLMs**:
   - Open-ended words ("perhaps", "maybe") → moderate sustained R
   - Control words ("must", "always") → high brittle R
   - Creative words ("imagine", "dream") → fluctuating exploratory R

2. **Cross-person EEG synchrony**:
   - People in genuine dialogue should show phase synchronization
   - Synchrony should predict conversation quality/understanding
   - Different from mere proximity or shared stimuli

3. **Optimal coupling principle**:
   - Systems perform best at moderate coupling (K ≈ 0.3-0.5 × Kc)
   - Too little: no coordination
   - Too much: rigid, brittle, loss of adaptability

4. **Emergence signatures**:
   - "Betweenness" (whole > sum of parts) predicts:
     - Creative insights
     - Flow states
     - Therapeutic breakthroughs

## Technical Implementation

### Core Analysis Pipeline

```python
# 1. Extract phases from any time series
from scipy.signal import hilbert
phases = np.angle(hilbert(signal))

# 2. Compute Kuramoto order parameter
R = np.abs(np.mean(np.exp(1j * phases)))

# 3. Advanced metrics
metastability = np.std(R_over_time)
phase_entropy = -np.sum(p * np.log(p))  # p from phase histogram
betweenness = global_R - mean(pairwise_R)
```

### Required Tools

- **EEG**: MNE-Python, pylsl for streaming
- **LLM**: Transformers, PyTorch for hidden states
- **Analysis**: NumPy, SciPy, matplotlib
- **Real-time**: Threading, websockets for live feedback

## Files

- `oscillator_explorations.py` - Kuramoto models and GPT-2 phase analysis
- `brain_monitor_simplified.py` - Real-time EEG coherence tracking
- `CROSS_SUBSTRATE_RESONANCE_FINDING.md` - Detailed methodology
- `graph7-coherence-rainbow.png` - Visualization of coherence patterns
- Additional analysis scripts in development

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