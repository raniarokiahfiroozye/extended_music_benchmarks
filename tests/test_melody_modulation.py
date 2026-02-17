import sys
import os

# Ensure we can import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from key_solver import SimplifiedMusicSolver

def run_modulation_test():
    solver = SimplifiedMusicSolver()
    
    print("🎵 Generating Melody: Twinkle Twinkle Little Star")
    print("Structure: C Major (Part A) -> Modulation -> E Major (Part A')")
    
    # Part 1: C Major
    # Notes: C C G G A A G | F F E E D D C
    # MIDI: 60 60 67 67 69 69 67 | 65 65 64 64 62 62 60
    c_major_part = [60, 60, 67, 67, 69, 69, 67, 65, 65, 64, 64, 62, 62, 60]
    
    # Part 2: E Major (Transposed up 4 semitones)
    # Notes: E E B B C# C# B | A A G# G# F# F# E
    # MIDI: 64 64 71 71 73 73 71 | 69 69 68 68 66 66 64
    e_major_part = [64, 64, 71, 71, 73, 73, 71, 69, 69, 68, 68, 66, 66, 64]
    
    full_melody = c_major_part + e_major_part
    
    # Run Rolling Search
    # Window size of 7 captures enough context (phrase length)
    window_size = 7 
    results = solver.rolling_key_search(full_melody, window_size=window_size)
    
    print(f"\n🔎 Rolling Window Analysis (Window Size: {window_size})")
    print(f"{'Idx':<4} | {'Window Notes':<25} | {'Detected Candidates'}")
    print("-" * 100)
    
    for i, candidates in results:
        # Get notes for display
        window = full_melody[i : i + window_size]
        readable_notes = "-".join([solver.note_names[n % 12] for n in window])
        
        # Determine expected key based on position
        expected_key = "C Major" if i < len(c_major_part) - window_size else "E Major"
        
        # If we are in the transition zone (window overlaps both parts), expectation is ambiguous
        if i >= len(c_major_part) - window_size and i < len(c_major_part):
            expected_key = "Transition"

        # Create a display string that includes percentages
        display_candidates = []
        for cand in candidates:
            key_name = cand['key']
            percentage = cand['match_percentage']
            if key_name == expected_key:
                display_candidates.append(f"✅ {key_name} ({percentage}%)")
            else:
                display_candidates.append(f"{key_name} ({percentage}%)")
                
        # Truncate for display if too long
        cand_str = ", ".join(display_candidates)
        if len(cand_str) > 60:
            cand_str = cand_str[:57] + "..."
            
        print(f"{i:<4} | {readable_notes:<25} | {cand_str}")

if __name__ == "__main__":
    run_modulation_test()