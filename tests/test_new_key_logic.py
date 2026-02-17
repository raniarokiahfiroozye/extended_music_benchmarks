import unittest
from src.key_solver import SimplifiedMusicSolver

class TestNewKeyLogic(unittest.TestCase):

    def setUp(self):
        self.solver = SimplifiedMusicSolver()

    def test_perfect_major_scale(self):
        """Tests a perfect C Major scale, which should have two 100% matches (Major and relative Minor)."""
        notes = [60, 62, 64, 65, 67, 69, 71] # C, D, E, F, G, A, B
        result = self.solver.solve_key(notes)
        print(f"\n{self.id()}: {result}")
        self.assertIsInstance(result, list)
        # A major scale and its relative natural minor have the same pitch classes
        self.assertEqual(len(result), 2)
        self.assertTrue(all(r['match_percentage'] == 100.0 for r in result))
        top_keys = {r['key'] for r in result}
        self.assertIn('C Major', top_keys)
        self.assertIn('A Natural Minor', top_keys)

    def test_no_perfect_match_c_major_plus_f_sharp(self):
        """Tests a C Major scale plus an F#, which should have no 100% match."""
        notes = [60, 62, 64, 65, 67, 69, 71, 66] # C Major scale + F#
        result = self.solver.solve_key(notes)
        print(f"\n{self.id()}: {result}")
        
        # There are 8 unique pitch classes.
        # C Major has 7 of them (score=7). 7/8 = 87.5%
        # G Major also has 7 of them (score=7). 7/8 = 87.5%
        self.assertNotEqual(result[0]['match_percentage'], 100.0)
        self.assertEqual(result[0]['match_percentage'], 87.5)
        
        top_keys = {r['key'] for r in result if r['match_percentage'] == 87.5}
        self.assertIn('C Major', top_keys)
        self.assertIn('G Major', top_keys)

    def test_ambiguous_triad(self):
        """Tests a C Major triad which fits perfectly in multiple keys."""
        notes = [60, 64, 67] # C, E, G
        result = self.solver.solve_key(notes)
        print(f"\n{self.id()}: {result}")
        # C, E, G are in C Major, G Major, E Minor, A Minor, etc.
        # All should have 100%
        self.assertGreater(len(result), 1)
        self.assertTrue(all(r['match_percentage'] == 100.0 for r in result))
        top_keys = {r['key'] for r in result}
        self.assertIn('C Major', top_keys)
        self.assertIn('G Major', top_keys)
        self.assertIn('E Natural Minor', top_keys)

    def test_atonal_cluster(self):
        """Tests a chromatic cluster that shouldn't perfectly match any key."""
        notes = [60, 61, 62, 63] # C, C#, D, D#
        result = self.solver.solve_key(notes)
        print(f"\n{self.id()}: {result}")
        # With 4 unique notes, the best matches (C# Maj, C Nat Min) have 3, so 75%
        self.assertNotEqual(result[0]['match_percentage'], 100.0)
        self.assertEqual(result[0]['match_percentage'], 75.0)
        top_keys = {r['key'] for r in result if r['match_percentage'] == 75.0}
        self.assertIn('C# Major', top_keys)
        self.assertIn('C Natural Minor', top_keys)

if __name__ == '__main__':
    unittest.main()