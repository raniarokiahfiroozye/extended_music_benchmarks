import sys
import os

# Ensure we can import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from beat_solver import BeatSolver

def main():
    print("🥁 Running Beat Analysis Script...")
    solver = BeatSolver()
    
    # Try to find the file
    filename = "new_jazz.mid"
    possible_paths = [
        filename,
        os.path.join(os.path.dirname(__file__), filename),
        os.path.join(os.path.dirname(__file__), "..", filename)
    ]
    
    found_path = None
    for p in possible_paths:
        if os.path.exists(p):
            found_path = p
            break
            
    if not found_path:
        print(f"❌ Error: Could not find '{filename}'")
        return

    print(f"📂 Loading: {found_path}")
    
    # Detect beats
    print("🎶 Detecting Beats...")
    beats = solver.detect_beats(found_path)
    
    print("\n" + "="*30)
    print(f"{'Beat Number':<15} | {'Tick'}")
    print("="*30)
    
    if beats:
        for i, tick in enumerate(beats):
            print(f"{i+1:<15} | {tick}")
    else:
        print("No beats detected.")
            
if __name__ == "__main__":
    main()
