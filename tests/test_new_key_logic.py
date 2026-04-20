import sys
import os
import unittest
import numpy as np

# Ensure we can import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from key_solver import SimplifiedMusicSolver

class TestNewKeyLogic(unittest.TestCase):

    def setUp(self):
        self.solver = SimplifiedMusicSolver()

    def test_perfect_major_scale(self):
        """Tests a perfect C Major scale."""
        notes = [60, 62, 64, 65, 67, 69, 71] # C, D, E, F, G, A, B
        result = self.solver.solve_key(notes)
        print(f"\n{self.id()}: {result}")
        self.assertIsInstance(result, list)
        
        # With Krumhansl-Schmuckler, C Major should be the top hit
        self.assertEqual(result[0]['key'], 'C Major')
        # match_percentage is correlation * 100 in this implementation
        self.assertGreater(result[0]['match_percentage'], 70.0)

    def test_c_major_plus_f_sharp(self):
        """Tests a C Major scale plus an F#."""
        notes = [60, 62, 64, 65, 67, 69, 71, 66] # C Major scale + F#
        result = self.solver.solve_key(notes)
        print(f"\n{self.id()}: {result}")
    
        # Should still favor C Major or G Major
        top_keys = {r['key'] for r in result[:2]}
        self.assertIn('C Major', top_keys)
        self.assertIn('G Major', top_keys)

    def test_ambiguous_triad(self):
        """Tests a C Major triad which fits in multiple keys."""
        notes = [60, 64, 67] # C, E, G
        result = self.solver.solve_key(notes)
        print(f"\n{self.id()}: {result}")
        # Top result should be C Major
        self.assertEqual(result[0]['key'], 'C Major')

    def test_atonal_cluster(self):
        """Tests a chromatic cluster."""
        notes = [60, 61, 62, 63] # C, C#, D, D#
        result = self.solver.solve_key(notes)
        print(f"\n{self.id()}: {result}")
        # Correlation should be relatively low for atonal clusters
        self.assertLess(result[0]['match_percentage'], 60.0)

if __name__ == '__main__':
    unittest.main()
