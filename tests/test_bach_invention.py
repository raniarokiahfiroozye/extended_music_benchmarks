import sys
import os

# Ensure we can import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from key_solver import SimplifiedMusicSolver

def run_bach_test():
    solver = SimplifiedMusicSolver()
    
    print("🎹 Testing Real-World Modulation: Bach Invention No. 1 (BWV 772)")
    print("Context: Bars 1-6. Expected: C Major -> G Major (Modulation at Bar 5)")
    
    # Bach Invention 1 Right Hand (Approximate Note Sequences)
    # Bar 1: C Major (Contains F natural)
    # Notes: C D E F D E C
    bar1 = [60, 62, 64, 65, 62, 64, 60] 
    
    # Bar 2: Ambiguous (Fits C and G)
    # Notes: G B C D B C A G
    bar2 = [67, 71, 72, 74, 71, 72, 69, 67] 
    
    # Bar 3: Ambiguous (Fits C and G)
    # Notes: G A B C A B G
    bar3 = [67, 69, 71, 72, 69, 71, 67] 
    
    # Bar 4: C Major (Contains F natural)
    # Notes: D E F G E F D
    bar4 = [74, 76, 77, 79, 76, 77, 74] 
    
    # Bar 5: G Major (Contains F# - The Modulation!)
    # Notes: E F# G A F# G E
    bar5 = [76, 78, 79, 81, 78, 79, 76] 
    
    # Bar 6: G Major
    # Notes: B C D E C D B
    bar6 = [71, 72, 74, 76, 72, 74, 71] 
    
    full_melody = bar1 + bar2 + bar3 + bar4 + bar5 + bar6
    
    # Window size of 7 (length of the motif)
    window_size = 7
    results = solver.rolling_key_search(full_melody, window_size=window_size)
    
    print(f"\n🔎 Rolling Window Analysis (Window Size: {window_size})")
    print(f"{'Idx':<4} | {'Window Notes':<30} | {'Detected Candidates'}")
    print("-" * 100)
    
    for i, candidates in results:
        window = full_melody[i : i + window_size]
        readable_notes = " ".join([solver.note_names[n % 12] for n in window])
        
        # Highlight keys for clearer output
        display_str = ""
        found_keys = [k for k in candidates if k in ["C Major", "G Major"]]
        
        if found_keys:
            display_str = " / ".join([f"✅ {k}" for k in found_keys])
        else:
            display_str = ", ".join(candidates[:3])
            
        print(f"{i:<4} | {readable_notes:<30} | {display_str}")

if __name__ == "__main__":
    run_bach_test()