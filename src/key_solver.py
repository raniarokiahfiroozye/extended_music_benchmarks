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
        # 1. Simplify to Pitch Classes and handle empty input
        input_pcs = set([n % 12 for n in notes])
        num_input_notes = len(input_pcs)

        if num_input_notes == 0:
            return []

        best_percentage = 0.0
        candidates = []

        for root in range(12):
            for mode_name, intervals in self.templates.items():
                scale_pcs = set([(root + i) % 12 for i in intervals])
                
                # Calculate how many input notes match the current scale
                score = len(input_pcs.intersection(scale_pcs))
                
                # Avoid division by zero and calculate match percentage
                match_percentage = (score / num_input_notes) * 100 if num_input_notes > 0 else 0
                
                key_name = f"{self.note_names[root]} {mode_name}"

                # If this key is a better fit, it becomes the new sole best candidate
                if match_percentage > best_percentage:
                    best_percentage = match_percentage
                    rounded_percentage = round(best_percentage, 2)
                    candidates = [{'key': key_name, 'match_percentage': rounded_percentage}]
                # If it's an equally good fit, add it to the list of top candidates
                elif match_percentage == best_percentage and best_percentage > 0:
                    rounded_percentage = round(match_percentage, 2)
                    candidates.append({'key': key_name, 'match_percentage': rounded_percentage})

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
