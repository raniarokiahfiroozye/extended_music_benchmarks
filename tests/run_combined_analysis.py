import sys
import os
import argparse

# Ensure we can import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from beat_solver import BeatSolver
from time_signature_solver import TimeSignatureSolver
import mido

def analyze_file(file_path):
    print("🎼 Running Combined Beat and Time Signature Analysis...")
    beat_solver = BeatSolver()
    ts_solver = TimeSignatureSolver()
    
    if not os.path.exists(file_path):
        print(f"❌ Error: Could not find '{file_path}'")
        return

    print(f"📂 Loading: {file_path}")
    
    # 1. Detect Time Signature Changes
    print("🔎 Detecting time signatures...")
    time_signatures = ts_solver.detect_time_signature(file_path)
    
    if not time_signatures:
        print("Could not determine time signature. Aborting.")
        return

    # 2. Detect all beat ticks
    print("🎶 Detecting beats...")
    beats = beat_solver.detect_beats(file_path)

    if not beats:
        print("Could not detect any beats. Aborting.")
        return

    # Sort time signatures by tick to be safe
    time_signatures.sort(key=lambda x: x['tick'])

    # 3. Group beats into bars based on the Time Signature at that moment
    print("\n" + "="*50)
    print(f"{'Bar':<10} | {'Actual Beats':<20} | {'Time Signature':<20}")
    print("="*50)

    beat_idx = 0
    bar_count = 1
    ts_idx = 0

    while beat_idx < len(beats):
        # Find the TS that applies to the CURRENT beat
        current_tick = beats[beat_idx]
        while ts_idx + 1 < len(time_signatures) and time_signatures[ts_idx+1]['tick'] <= current_tick:
            ts_idx += 1
        
        current_ts_str = time_signatures[ts_idx]['time_signature']
        numerator, denominator = map(int, current_ts_str.split('/'))
        
        # A bar consists of 'numerator' beats
        # We collect them just for reporting/counting
        beats_in_this_bar = []
        for _ in range(numerator):
            if beat_idx < len(beats):
                beats_in_this_bar.append(beats[beat_idx])
                beat_idx += 1
        
        print(f"{bar_count:<10} | {len(beats_in_this_bar):<20} | {current_ts_str:<20}")
        bar_count += 1

def main():
    parser = argparse.ArgumentParser(description="Combined Beat and Time Signature Analysis for MIDI files.")
    parser.add_argument('midi_file', nargs='?', default="new_jazz.mid",
                        help="Path to the MIDI file to analyze.")
    args = parser.parse_args()

    # Smart path searching
    possible_paths = [
        args.midi_file,
        os.path.join(os.path.dirname(__file__), args.midi_file),
        os.path.join(os.path.dirname(__file__), "..", args.midi_file)
    ]
    
    found_path = None
    for p in possible_paths:
        if os.path.exists(p):
            found_path = p
            break
            
    if not found_path:
        print(f"❌ Error: Could not find '{args.midi_file}'")
        return
    
    analyze_file(found_path)

if __name__ == "__main__":
    main()
