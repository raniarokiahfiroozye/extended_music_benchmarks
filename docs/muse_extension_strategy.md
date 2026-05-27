# Extending MUSE with EMB: Integration Strategy

This document outlines the strategy for using the Extended Music Benchmark (`emb`) to generate new tests and extend the capabilities of the `MUSE_music_benchmark`. A critical constraint of this approach is maintaining strict backward compatibility and requiring zero structural changes to the existing MUSE repository.

## 1. Architectural Philosophy: Additive Extension
The core principle of this integration is that **MUSE's existing codebase, runners, and structural paradigms remain completely untouched.** Other researchers have invested significant time into developing MUSE, and any additions must respect their established workflows and interfaces.

`emb` will act as an independent, external "test generation engine." It will output artifacts (rendered audio files and standalone runner scripts) that are perfectly formatted to be dropped into the existing MUSE framework as isolated, additive features.

## 2. The Core Strategy: Dynamic Test Generation

The primary goal is to use `emb`'s algorithmic solvers and MIDI generation capabilities to create **new, advanced test categories** for MUSE without altering how MUSE operates.

### How it works:
1. **Generation:** `emb` generates complex MIDI files tailored for specific edge cases (e.g., dynamic tempo changes, exact bar-level key modulations, varied velocity profiles).
2. **Verification:** `emb`'s internal solvers (`KeySolver`, `BeatSolver`, `TimeSignatureSolver`) analyze the generated MIDI to establish an absolute algorithmic ground truth.
3. **Rendering:** The MIDI is rendered to audio (WAV) to match MUSE's strict `stimuli/` audio-file requirements.
4. **Integration:** We create *new* runner scripts (e.g., `Gemini/temporal_keymod_Gemini_runner.py`) that exactly mimic the boilerplate, system instructions, and regex parsing of existing MUSE runners.

### Proposed New Test Categories (Fully Compatible with MUSE)

By leveraging `emb`'s generation, we can fit advanced concepts into MUSE's existing Multiple-Choice/A-B classification paradigm:

*   **Temporal Localization (The "Shift" Test):** 
    *   *MUSE Style Prompt:* "Does the time signature change from 4/4 to 3/4 before the halfway point of the excerpt? A. Yes, B. No."
    *   *Implementation:* `emb` generates audio where the shift happens early vs. late, allowing us to test temporal localization while adhering to the existing A/B choice format.
*   **Dynamic Robustness (The "Rubato/Dynamics" Test):**
    *   *MUSE Style Prompt:* "What is the meter of this excerpt? A. Groups of 3, B. Groups of 4."
    *   *Implementation:* `emb` generates the same base composition but applies significant humanization (tempo drift, pianissimo dynamics). We can test when the LLM's perception breaks down compared to the algorithmic solver.

## 3. The "Expert Auditor" (Optional Analytics)
As a supplementary, non-destructive analytical tool, `emb` can be used to audit existing MUSE stimuli. If the original MIDI files for MUSE's `stimuli/` folder are available, `emb`'s solvers can run over them to confirm the hardcoded ground truths (e.g., verifying that a file labeled `mod` actually contains a mathematically verifiable modulation). This is purely analytical and requires zero code changes to the MUSE repository.

## 4. Implementation Steps (Zero-Friction Workflow)

To add a new test to MUSE using `emb`, the workflow will be entirely additive:

1.  Write a generation script in `emb/tests/` to create a new MIDI stimuli suite (e.g., 20 files testing 3/4 vs 2/4 at soft dynamics).
2.  Render these MIDI files to WAV format.
3.  Place the WAV files in a new, isolated subfolder in MUSE (e.g., `MUSE_music_benchmark/stimuli/emb_extensions/`).
4.  Copy an existing MUSE runner (e.g., `keymod_Gemini_runner.py`), rename it for the new test, and update its file paths and system instructions to point to the new stimuli.
5.  Execute the new runner script exactly as one would run any other standard MUSE test.

By strictly adhering to this additive workflow, `emb` acts as a powerful backend generator that expands MUSE's testing surface area without forcing architectural shifts or breaking changes on the wider research team.
