# Integration with MUSE Music Benchmark

This document explains how the `emb` (Extended Music Benchmark) repository integrates with the `MUSE_music_benchmark` project to provide more sophisticated and verified musical stimuli for benchmarking Audio LLMs.

## Overview

The integration establishes a **Research -> Generate -> Verify -> Deploy** pipeline. While the original MUSE benchmark focuses on human-recorded or manually curated stimuli, `emb` provides the infrastructure to programmatically generate stimuli with precise musical properties (like specific meter shifts or key modulations) and verify them using algorithmic solvers.

## Core Components

### 1. Stimulus Generation (`emb/generate_muse_extension.py`)
This script is the main entry point for the integration. It:
- Programmatically generates MIDI files with specific events (e.g., changing time signatures at specific bars).
- Uses `midi_renderer.py` to convert these MIDI files into high-quality WAV files.
- Automatically deploys the rendered WAVs to the canonical MUSE stimuli directory: `MUSE_music_benchmark/stimuli/emb_extension/`.

### 2. Algorithmic Verification (`emb/src/`)
Unlike simple classification tasks, `emb` uses "involved" solvers to provide ground truth:
- **`TimeSignatureSolver`**: Uses Inter-Onset Interval (IOI) analysis and note accent patterns to "hear" the meter. It can detect changes even without MIDI metadata, ensuring the generated audio actually reflects the intended musical structure.
- **`KeySolver`**: Provides realistic key detection and modulation tracking.

### 3. MUSE Evaluation Runner
A specialized runner was created in the MUSE repository to utilize these extended stimuli:
- **`MUSE_music_benchmark/Gemini/temporal_meter_Gemini_runner.py`**: This script benchmarks the LLM's ability to detect shifts in the musical meter over time.

## Nature of the Extended Tests

The tests created via `emb` move beyond simple multiple-choice classification:
- **Temporal Reasoning**: By varying the "shift bar" (e.g., early vs. late in a 16-bar sequence), we test the LLM's long-term auditory context and attention.
- **Relational Complexity**: The focus is on *transitions* (modulations, meter shifts) rather than static properties.
- **Ground Truth Precision**: Because the stimuli are programmatically generated and algorithmically verified, the "ground truth" includes exact bar and tick numbers for every musical event, allowing for future tasks that ask *when* or *how* a change occurred.

## How to Extend
To add new tests to MUSE via `emb`:
1. Define a new test case in `emb/generate_muse_extension.py`.
2. Implement any necessary verification logic in `emb/src/`.
3. Run `python emb/generate_muse_extension.py` to generate and deploy the stimuli.
4. Update or create a runner in `MUSE_music_benchmark/` to evaluate the new task.
