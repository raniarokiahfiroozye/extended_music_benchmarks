import os
import sys
import mido

# Ensure we can import from src
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.append(os.path.join(project_root, 'src'))

from time_signature_solver import TimeSignatureSolver

def create_pp_test_midi(file_path):
    """Creates a very soft MIDI file (pianissimo) with 4/4 time."""
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)
    tpb = 480
    
    # 8 bars of very soft 4/4
    # Downbeat: 40, Weak Beats: 38 (only ~5% difference)
    for bar in range(8):
        for beat in range(4):
            velocity = 40 if beat == 0 else 38
            track.append(mido.Message('note_on', note=60, velocity=velocity, time=0))
            track.append(mido.Message('note_off', note=60, velocity=0, time=tpb))
            
    mid.save(file_path)

def test_pp_detection():
    solver = TimeSignatureSolver()
    test_file = os.path.join(script_dir, "temp_pp_test.mid")
    
    try:
        create_pp_test_midi(test_file)
        results = solver.detect_time_signature(test_file)
        
        print("\n--- Pianissimo (pp) TS Detection Results ---")
        if results:
            for res in results:
                print(f"Bar {res['bar']}: {res['time_signature']} (at tick {res['tick']})")
        else:
            print("No results found.")
            
        assert len(results) >= 1
        assert results[0]['time_signature'] == "4/4", f"Should detect 4/4 even at low velocity, got {results[0]['time_signature']}"
        print("\n✅ Pianissimo detection test passed!")
        
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)

if __name__ == '__main__':
    test_pp_detection()
