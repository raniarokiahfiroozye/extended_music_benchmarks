import os
import sys
import mido

# Ensure we can import from src
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.append(os.path.join(project_root, 'src'))

from time_signature_solver import TimeSignatureSolver

def create_test_midi(file_path):
    """Creates a MIDI file with 4/4 followed by 3/4 and no metadata."""
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)
    tpb = 480
    
    # 4 bars of 4/4
    for bar in range(4):
        for beat in range(4):
            velocity = 100 if beat == 0 else 60
            track.append(mido.Message('note_on', note=60, velocity=velocity, time=0))
            track.append(mido.Message('note_off', note=60, velocity=0, time=tpb))
            
    # 4 bars of 3/4
    for bar in range(4):
        for beat in range(3):
            velocity = 100 if beat == 0 else 60
            track.append(mido.Message('note_on', note=60, velocity=velocity, time=0))
            track.append(mido.Message('note_off', note=60, velocity=0, time=tpb))
            
    mid.save(file_path)

def test_performance_time_signature_detection():
    solver = TimeSignatureSolver()
    test_file = os.path.join(script_dir, "temp_test_perf.mid")
    
    try:
        create_test_midi(test_file)
        results = solver.detect_time_signature(test_file)
        
        print("\n--- Performance TS Detection Results ---")
        if results:
            for res in results:
                print(f"Bar {res['bar']}: {res['time_signature']} (at tick {res['tick']})")
        else:
            print("No results found.")
            
        # Assertions
        assert len(results) >= 2, f"Should detect at least two time signatures, got {len(results)}"
        assert results[0]['time_signature'] == "4/4", f"Initial TS should be 4/4, got {results[0]['time_signature']}"
        assert any(r['time_signature'] == "3/4" for r in results), "Should detect 3/4 change"
        
        # Find 3/4 start
        ts_3_4 = [r for r in results if r['time_signature'] == "3/4"][0]
        # Should be Bar 5
        print(f"✅ Found 3/4 at Bar {ts_3_4['bar']}")
        assert 4 <= ts_3_4['bar'] <= 6, f"3/4 should start around Bar 5, got Bar {ts_3_4['bar']}"
        
        print("\n✅ Performance TS test passed!")
        
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)

if __name__ == '__main__':
    test_performance_time_signature_detection()
