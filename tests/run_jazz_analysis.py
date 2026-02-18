import sys
import os

# Ensure we can import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from key_solver import SimplifiedMusicSolver

def main():
    print("🎹 Running Jazz Analysis Script...")
    solver = SimplifiedMusicSolver()
    
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
    
    # Analyze 1 bar at a time
    print("🔎 Analyzing Key per Bar...")
    results = solver.analyze_midi(found_path, use_musical_grid=True, window_size=1)
    
    print("\n" + "="*60)
    print(f"{'Bar':<10} | {'Detected Key':<25} | {'Confidence'}")
    print("="*60)
    
    for r in results:
        bar_num = f"{r['start_bar']}"
        if r['candidates']:
            top = r['candidates'][0]
            key = top['key']
            score = top['correlation']
            print(f"{bar_num:<10} | {key:<25} | {score:.2f}")
        else:
            print(f"{bar_num:<10} | {'(Silence/No Notes)':<25} | -")
            
if __name__ == "__main__":
    main()