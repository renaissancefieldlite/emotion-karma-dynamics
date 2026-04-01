# Emotion Karma Dynamics

This repository holds a field model for emotional-state dynamics grounded in
measurable signals, feedback loops, and return through time.

The backbone is:

- measurable neural and physiological signals
- nonlinear feedback, delayed return, and resonance across time
- cross-modal measurement through autonomic and cortical channels
- optional quantum-overlap language as a small subscale modulation term within
  the larger field model

## Core Position

The stance in this repo is:

- emotion can be approached as a changing state in a measurable field
- action is output from that state
- consequence returns through the environment and re-enters the state
- this is best modeled first with dynamical systems, control, coupling, and
  delayed feedback
- any quantum-overlap clause belongs as a small modulation term unless the
  observables, state space, and evidence are actually built

Short form:

- `emotion = energy in motion`
- `karma = energy returning into emotion`

## Repository Layout

- `assets/charts/`
  - chart pack PNGs
- `docs/chart_manifest.md`
  - description of each chart
- `docs/STANCE.md`
  - full modeling stance
- `docs/CITATIONS.md`
  - primary-source citation spine
- `docs/make_emotion_karma_charts.py`
  - chart generator

## Chart Pack

- `01_emotion_feedback_loop.png`
  - state -> action -> delayed return -> updated state
- `02_biomarker_regulation_panel.png`
  - amygdala / frontal regulation / HF-HRV / cortisol
- `03_coupled_resonance.png`
  - phase locking and synchronization
- `04_secondary_modulation.png`
  - small overlap term inside the larger field model
- `05_stack_measurement_ladder.png`
  - ties the stance to the measurement stack and future EEG lane

## Stack Tie-In

This repo is designed to tie into the existing stack as follows:

- `renaissancefieldlitehrv1.0`
  - autonomic capture lane
- `QuantumHRV`
  - descriptive variability-summary lane
- `QuantumConsciousnessBridge`
  - protocol / packaging bridge
- future `Muse 2`
  - practical EEG lane for alpha/theta timing, frontal balance, and
    timestamped overlays against HRV and prompt windows

## Rebuild

To regenerate the figures:

```bash
MPLCONFIGDIR=/tmp/mpl python3 docs/make_emotion_karma_charts.py
```
