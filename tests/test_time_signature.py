#!/usr/bin/env python3
import os
import sys

# Ensure we can import from src
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.append(os.path.join(project_root, 'src'))

from time_signature_solver import TimeSignatureSolver

def main():
    print("🚀 Starting Time Signature Analysis...", flush=True)
    solver = TimeSignatureSolver()
    
    # We'll use the same jazz file as before
    filename = "new_jazz.mid"
    file_path = os.path.join(script_dir, filename)

    if not os.path.exists(file_path):
        print(f"❌ Error: Could not find '{filename}' in the 'tests' directory.")
        return

    print(f"📂 Analyzing '{filename}'...", flush=True)
    
    # Detect the time signature(s)
    time_signatures = solver.detect_time_signature(file_path)
    
    print("\n🎵 Detected Time Signature Changes:")
    if time_signatures:
        for ts_change in time_signatures:
            print(f"   - Bar {ts_change['bar']:<4}: {ts_change['time_signature']} (at tick {ts_change['tick']})")
    else:
        print("   - No time signature information found.")

if __name__ == '__main__':
    main()
