import sys
import os

# Ensure we can import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import random
from key_solver import SimplifiedMusicSolver # Assuming the previous logic is in key_solver.py

def run_advanced_test_suite():
    solver = SimplifiedMusicSolver()
    gen = StimulusGenerator()
    
    # 1. Define our 6 Scrambled Scales (7-8 notes each)
    suite = [
        ("C Major Scrambled", gen.generate_scrambled_scale("C", "Major"), "C Major"),
        ("Eb Natural Minor Scrambled", gen.generate_scrambled_scale("Eb", "Natural Minor"), "Eb Natural Minor"),
        ("A Harmonic Minor Scrambled", gen.generate_scrambled_scale("A", "Harmonic Minor"), "A Harmonic Minor"),
        ("F# Melodic Minor Asc Scrambled", gen.generate_scrambled_scale("F#", "Melodic Minor Asc"), "F# Melodic Minor Asc"),
        ("G Major Scrambled", gen.generate_scrambled_scale("G", "Major"), "G Major"),
        ("B Natural Minor Scrambled", gen.generate_scrambled_scale("B", "Natural Minor"), "B Natural Minor"),
    ]
    
    # 2. Add Dissonant Groupings
    suite.append(("Atonal Cluster A", gen.generate_dissonant_cluster(8), "No Match (Atonal/Dissonant)"))
    suite.append(("Atonal Cluster B", [60, 61, 62, 63, 64, 65, 66], "No Match (Atonal/Dissonant)"))

    print(f"{'Test Description':<30} | {'Status':<10} | {'Result'}")
    print("-" * 80)

    for desc, notes, expected in suite:
        actual = solver.solve_key(notes)
        
        # Logic check for Indeterminate: if expected is in the indeterminate string, it's a soft pass
        if expected in actual or actual == expected:
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            
        print(f"{desc:<30} | {status:<10} | {actual}")

    
class StimulusGenerator:
    def __init__(self):
        self.note_names = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
        self.scales = {
            'Major': [0, 2, 4, 5, 7, 9, 11],
            'Natural Minor': [0, 2, 3, 5, 7, 8, 10],
            'Harmonic Minor': [0, 2, 3, 5, 7, 8, 11],
            'Melodic Minor Asc': [0, 2, 3, 5, 7, 9, 11]
        }

    def generate_scrambled_scale(self, root_name, scale_type):
        root_pc = self.note_names.index(root_name)
        intervals = self.scales[scale_type]
        
        # Create a full octave scale + the octave repeat (8 notes)
        pcs = [(root_pc + i) % 12 for i in intervals]
        pcs.append(root_pc) # Add the octave
        
        # Scramble across different octaves (MIDI 36 to 84)
        midi_notes = []
        for pc in pcs:
            octave = random.choice([3, 4, 5, 6])
            midi_notes.append(pc + (octave * 12))
            
        random.shuffle(midi_notes)
        return midi_notes

    def generate_dissonant_cluster(self, num_notes=8):
        # Generates a chromatic cluster that fits no standard western scale
        all_midi = list(range(48, 72))
        cluster = random.sample(all_midi, num_notes)
        random.shuffle(cluster)
        return cluster

# Initialize
# gen = StimulusGenerator()

if __name__ == "__main__":
    run_advanced_test_suite()


