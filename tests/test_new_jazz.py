#!/usr/bin/env python3
import os
import sys

# Ensure we can import from src
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.append(os.path.join(project_root, 'src'))

from key_solver import SimplifiedMusicSolver

def main():
    print("🚀 Starting Jazz Analysis...", flush=True)
    solver = SimplifiedMusicSolver()
    filename = "new_jazz.mid"

    # 1. Check File Existence
    # Look in tests folder (script_dir), project root, or current working dir
    candidates = [
        os.path.join(script_dir, filename),
        os.path.join(project_root, filename),
        os.path.join(os.getcwd(), filename)
    ]
    
    found_path = None
    print(f"🔎 Looking for '{filename}'...", flush=True)
    for path in candidates:
        # print(f"   Checking: {path}") 
        if os.path.exists(path):
            found_path = path
            print(f"✅ Found file at: {found_path}", flush=True)
            break
    
    if not found_path:
        print(f"❌ Error: Could not find '{filename}' in any of these locations:", flush=True)
        for p in candidates:
            print(f"   - {p}")
        print("Please place the .mid file in the 'tests' folder or the project root.")
        return
    
    print(f"\n📂 Loading MIDI...", flush=True)

    # 2. Check MIDI Content
    try:
        # Load raw notes to check content
        notes = solver.load_midi(found_path)
        if not notes:
            print("❌ MIDI file is empty (no notes found).")
            return
            
        duration = notes[-1]['start'] + notes[-1]['duration']
        print(f"   Stats: {len(notes)} notes, {duration:.2f} seconds duration.")
    except Exception as e:
        print(f"❌ Invalid MIDI file: {e}")
        return

    # 3. Run Analysis (Bar-Based)
    # Analyze 1 bar at a time to see the progression "as it goes along" in music time
    print(f"🎹 Analyzing Key (Target: G Minor)...")
    results = solver.analyze_midi(found_path, use_musical_grid=True, window_size=1)
    
    # 4. Print Results
    print("\n   Results per Bar:")
    print("   " + "-" * 50)
    for r in results:
        if r['candidates']:
            top_key = r['candidates'][0]['key']
            confidence = r['candidates'][0]['correlation']
            
            mark = "✅" if "G Minor" in top_key else "  "
            print(f"   {mark} Bar {r['start_bar']:<3} | {top_key:<20} (Corr: {confidence:.2f})")
        else:
            print(f"     Bar {r['start_bar']:<3} | No key detected (empty bar)")

if __name__ == '__main__':
    main()