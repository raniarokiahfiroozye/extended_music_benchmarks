import os
import sys

# Ensure we can import from src
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.append(os.path.join(project_root, 'src'))

from time_signature_solver import TimeSignatureSolver

def test_without_meta_messages():
    """
    Tests that the time signature is correctly detected from a MIDI file that does not have meta messages.
    """
    solver = TimeSignatureSolver()
    # Path to the MIDI file without meta messages
    file_path = os.path.join(script_dir, "new_jazz_no_ts.mid")
    
    # Detect the time signature
    time_signatures = solver.detect_time_signature(file_path)
    
    print(f"\nDetected time signature for 'new_jazz_no_ts.mid': {time_signatures}")
    
    # Assert that the correct time signature is detected
    assert len(time_signatures) > 0
    assert time_signatures[0]['time_signature'] == "4/4"
    print("\nTest passed!")

if __name__ == '__main__':
    test_without_meta_messages()
