import os
import sys
import mido
import numpy as np

# Ensure we can import from src
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir, 'src'))

from midi_renderer import MidiRenderer
from time_signature_solver import TimeSignatureSolver

def create_midi(output_path, shift_bar=None, initial_ts=(4,4), final_ts=(3,4), total_bars=16):
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

def main():
    stimuli_dir = "MUSE_music_benchmark/stimuli/emb_extension"
    os.makedirs(stimuli_dir, exist_ok=True)
    
    renderer = MidiRenderer()
    solver = TimeSignatureSolver()
    
    test_cases = [
        {"name": "meter_shift_early", "shift": 5, "label": "Yes"},
        {"name": "meter_shift_late", "shift": 12, "label": "Yes"},
        {"name": "meter_steady_44", "shift": None, "label": "No"},
        {"name": "meter_steady_34", "shift": None, "initial": (3,4), "label": "No"},
    ]
    
    print("Generating stimuli for EMB extension to MUSE...")
    
    for case in test_cases:
        mid_path = f"emb/tests/{case['name']}.mid"
        wav_path = os.path.join(stimuli_dir, f"{case['name']}.wav")
        
        create_midi(
            mid_path, 
            shift_bar=case.get('shift'), 
            initial_ts=case.get('initial', (4,4)),
            total_bars=16
        )
        
        # Verify with solver
        results = solver.detect_time_signature(mid_path)
        print(f"File: {case['name']}, Solver detected: {[r['time_signature'] for r in results]}")
        
        # Render
        renderer.render(mid_path, wav_path)
        print(f"Rendered {wav_path}")

if __name__ == "__main__":
    main()
