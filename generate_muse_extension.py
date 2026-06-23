import os
import sys
import mido
import numpy as np

# Ensure we can import from src
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir, 'src'))

from midi_renderer import MidiRenderer
from time_signature_solver import TimeSignatureSolver
from key_solver import SimplifiedMusicSolver

def create_meter_midi(output_path, shift_bar=None, initial_ts=(4,4), final_ts=(3,4), total_bars=16):
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)
    tpb = 480
    
    # Add initial time signature meta message
    track.append(mido.MetaMessage('time_signature', numerator=initial_ts[0], denominator=initial_ts[1], time=0))
    
    curr_ts = initial_ts
    for bar in range(1, total_bars + 1):
        if shift_bar and bar == shift_bar:
            curr_ts = final_ts
            track.append(mido.MetaMessage('time_signature', numerator=final_ts[0], denominator=final_ts[1], time=0))
        
        num = curr_ts[0]
        for beat in range(num):
            velocity = 100 if beat == 0 else 60
            track.append(mido.Message('note_on', note=60, velocity=velocity, time=0))
            track.append(mido.Message('note_off', note=60, velocity=0, time=tpb))
            
    mid.save(output_path)
    return output_path

def create_key_midi(output_path, shift_bar=None, initial_key="C", final_key="G", total_bars=16):
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)
    tpb = 480
    
    # 4/4 time signature
    track.append(mido.MetaMessage('time_signature', numerator=4, denominator=4, time=0))
    
    # Define chord progressions (I - IV - V - I)
    c_chords = [
        [60, 64, 67], # C (C-E-G)
        [65, 69, 72], # F (F-A-C)
        [67, 71, 74], # G (G-B-D)
        [60, 64, 67]  # C (C-E-G)
    ]
    g_chords = [
        [67, 71, 74], # G (G-B-D)
        [72, 76, 79], # C (C-E-G)
        [74, 78, 81], # D (D-F#-A)
        [67, 71, 74]  # G (G-B-D)
    ]
    
    curr_key = initial_key
    for bar in range(1, total_bars + 1):
        if shift_bar and bar == shift_bar:
            curr_key = final_key
            
        chord_idx = (bar - 1) % 4
        if curr_key == "C":
            notes = c_chords[chord_idx]
        else:
            notes = g_chords[chord_idx]
            
        for note in notes:
            track.append(mido.Message('note_on', note=note, velocity=80, time=0))
        
        track.append(mido.Message('note_off', note=notes[0], velocity=0, time=tpb * 4))
        for note in notes[1:]:
            track.append(mido.Message('note_off', note=note, velocity=0, time=0))
            
    mid.save(output_path)
    return output_path

def main():
    stimuli_dir = "MUSE_music_benchmark/stimuli/emb_extension"
    os.makedirs(stimuli_dir, exist_ok=True)
    
    renderer = MidiRenderer()
    ts_solver = TimeSignatureSolver()
    key_solver = SimplifiedMusicSolver()
    
    # 1. Meter test cases
    meter_cases = [
        {"name": "meter_shift_early", "shift": 5, "label": "Yes"},
        {"name": "meter_shift_late", "shift": 12, "label": "Yes"},
        {"name": "meter_steady_44", "shift": None, "label": "No"},
        {"name": "meter_steady_34", "shift": None, "initial": (3,4), "label": "No"},
    ]
    
    print("Generating Meter Stimuli for EMB extension to MUSE...")
    for case in meter_cases:
        mid_path = f"emb/tests/{case['name']}.mid"
        wav_path = os.path.join(stimuli_dir, f"{case['name']}.wav")
        
        create_meter_midi(
            mid_path, 
            shift_bar=case.get('shift'), 
            initial_ts=case.get('initial', (4,4)),
            total_bars=16
        )
        
        # Verify with solver
        results = ts_solver.detect_time_signature(mid_path)
        print(f"File: {case['name']}, Solver detected: {[r['time_signature'] for r in results]}")
        
        # Render
        renderer.render_fluidsynth(mid_path, wav_path)
        print(f"Rendered {wav_path} (via FluidSynth)")
        
    # 2. Key test cases
    key_cases = [
        {"name": "key_shift_early", "shift": 5, "initial": "C", "final": "G", "label": "Yes"},
        {"name": "key_shift_late", "shift": 12, "initial": "C", "final": "G", "label": "Yes"},
        {"name": "key_steady_c", "shift": None, "initial": "C", "label": "No"},
        {"name": "key_steady_g", "shift": None, "initial": "G", "label": "No"},
    ]
    
    print("\nGenerating Key Modulation Stimuli for EMB extension to MUSE...")
    for case in key_cases:
        mid_path = f"emb/tests/{case['name']}.mid"
        wav_path = os.path.join(stimuli_dir, f"{case['name']}.wav")
        
        create_key_midi(
            mid_path,
            shift_bar=case.get('shift'),
            initial_key=case.get('initial', "C"),
            final_key=case.get('final', "G"),
            total_bars=16
        )
        
        # Verify with solver
        results = key_solver.analyze_by_bars(mid_path, bars_per_window=4, step_bars=4)
        detected_keys = []
        for r in results:
            if r['candidates']:
                detected_keys.append(f"{r['start_bar']}-{r['end_bar']}:{r['candidates'][0]['key']}")
        print(f"File: {case['name']}, Solver detected: {detected_keys}")
        
        # Render
        renderer.render_fluidsynth(mid_path, wav_path)
        print(f"Rendered {wav_path} (via FluidSynth)")

if __name__ == "__main__":
    main()
