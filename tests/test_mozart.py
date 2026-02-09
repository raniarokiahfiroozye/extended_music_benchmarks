import sys
import os

# Ensure we can import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from key_solver import SimplifiedMusicSolver

def run_mozart_test():
    solver = SimplifiedMusicSolver()
    
    print("🎹 Testing Real-World Melody: Mozart Sonata No. 16 (K.545) - Mvt 1")
    print("Context: Opening Theme (Bars 1-8). Expected Key: C Major")
    
    # Mozart K.545 Right Hand Melody (MIDI Note Numbers)
    # Bar 1: C5, E5, G5
    # Bar 2: B4, C5, D5, C5
    # Bar 3: A4, G4, C5
    # Bar 4: G4, F4, E4, F4
    # Bar 5: E4, F4, G4, E4
    # Bar 6: D4, E4, F4, D4
    # Bar 7: C4, D4, E4, C4
    # Bar 8: D4, G4, B4, D5 (G Major Arpeggio, but notes still diatonic to C)
    
    mozart_melody = [
        72, 76, 79,             # Bar 1
        71, 72, 74, 72,         # Bar 2
        69, 67, 72,             # Bar 3
        67, 65, 64, 65,         # Bar 4
        64, 65, 67, 64,         # Bar 5
        62, 64, 65, 62,         # Bar 6
        60, 62, 64, 60,         # Bar 7
        62, 67, 71, 74          # Bar 8
    ]
    
    # We use a slightly wider window (8) for stability since we have a longer stream
    window_size = 8
    results = solver.rolling_key_search(mozart_melody, window_size=window_size)
    
    print(f"\n🔎 Rolling Window Analysis (Window Size: {window_size})")
    print(f"{'Idx':<4} | {'Window Notes':<30} | {'Detected Candidates'}")
    print("-" * 100)
    
    for i, candidates in results:
        window = mozart_melody[i : i + window_size]
        readable_notes = " ".join([solver.note_names[n % 12] for n in window])
        
        # Format candidates
        # We expect C Major to be present in almost all windows
        display_str = ""
        if "C Major" in candidates:
            display_str = "✅ C Major"
            # Show others if they exist, but keep it clean
            others = [c for c in candidates if c != "C Major"]
            if others:
                display_str += f" (+ {len(others)} others)"
        else:
            display_str = ", ".join(candidates[:3])
            
        print(f"{i:<4} | {readable_notes:<30} | {display_str}")

if __name__ == "__main__":
    run_mozart_test()
