import numpy as np
class SimplifiedMusicSolver:
    def __init__(self):
        self.note_names = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
        self.templates = {
            'Major': [0, 2, 4, 5, 7, 9, 11],
            'Natural Minor': [0, 2, 3, 5, 7, 8, 10],
            'Harmonic Minor': [0, 2, 3, 5, 7, 8, 11],
            'Melodic Minor Asc': [0, 2, 3, 5, 7, 9, 11]
        }

    def solve_key(self, notes):
        # 1. Simplify everything to the 12 basic notes (Pitch Classes)
        # This handles different octaves automatically (60 % 12 = 0, 72 % 12 = 0)
        input_pcs = set([n % 12 for n in notes])
        
        candidates = []

        for root in range(12):
            for mode_name, intervals in self.templates.items():
                scale_pcs = set([(root + i) % 12 for i in intervals])
                
                # Logic: Is every note the user gave me inside THIS scale?
                if input_pcs.issubset(scale_pcs):
                    candidates.append(f"{self.note_names[root]} {mode_name}")

        # 2. Determine the result
        if len(candidates) == 0:
            return ["No Match (Atonal/Dissonant)"]
        
        return candidates

    def rolling_key_search(self, notes, window_size=5):
        """
        Returns a list of (index, candidates) for each window in the note sequence.
        """
        results = []
        for i in range(len(notes) - window_size + 1):
            window = notes[i : i + window_size]
            results.append((i, self.solve_key(window)))
        return results

if __name__ == "__main__":
    # --- QUICK TEST ---
    solver = SimplifiedMusicSolver()
    # Testing your G Major set from earlier: [G, B, D, F#]
    print(solver.solve_key([67, 71, 74, 66]))
