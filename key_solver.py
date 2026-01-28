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
            return "No Match (Atonal/Dissonant)"
        if len(candidates) > 1:
            return f"Indeterminate (Could be: {', '.join(candidates[:3])}...)"
        
        return candidates[0]
# --- QUICK TEST ---
solver = SimplifiedMusicSolver()
# Testing your G Major set from earlier: [G, B, D, F#]
print(solver.solve_key([67, 71, 74, 66]))




# class MusicLogicSolver:
#     def __init__(self):
#         # 0=C, 1=C#, 2=D, 3=Eb, 4=E, 5=F, 6=F#, 7=G, 8=Ab, 9=A, 10=Bb, 11=B
#         self.note_names = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
        
#         # Scale Templates (Intervals relative to root)
#         self.templates = {
#             'Major': [0, 2, 4, 5, 7, 9, 11],
#             'Minor': [0, 2, 3, 5, 7, 8, 10],  # Natural Minor
#             'Harmonic Minor': [0, 2, 3, 5, 7, 8, 11],      # Raised 7th (e.g., G# in A minor)
#             'Melodic Minor Asc': [0, 2, 3, 5, 7, 9, 11]    # Ascending only - Raised 6th & 7th (e.g., F#, G# in A minor)
#             }

#     def get_pitch_class(self, note):
#         """Converts MIDI or Note Names to a 0-11 integer."""
#         name_to_pc = {
#             'C': 0, 'C#': 1, 'DB': 1, 'D': 2, 'D#': 3, 'EB': 3, 'E': 4, 
#             'F': 5, 'F#': 6, 'GB': 6, 'G': 7, 'G#': 8, 'AB': 8, 'A': 9, 
#             'A#': 10, 'BB': 10, 'B': 11
#         }
#         if isinstance(note, int):
#             return note % 12
#         if isinstance(note, str):
#             return name_to_pc.get(note.upper().replace('♯', '#').replace('♭', 'B'), 0)
#         return note

#     def solve_key(self, note_sequence):
#         """
#         Identifies the key that best fits the input notes.
#         Modeled on MUSE solver logic.
#         """
#         # 1. Deduplicate and normalize to pitch classes (0-11)
#         input_pcs = set([self.get_pitch_class(n) for n in note_sequence])
        
#         best_key = None
#         max_score = -1
        
#         # 2. Iterate through all 12 roots
#         for root in range(12):
#             # 3. Check both Major and Minor templates
#             for mode, intervals in self.templates.items():
#                 scale_pcs = set([(root + i) % 12 for i in intervals])
                
#                 # Calculate how many input notes are actually in this scale
#                 matches = input_pcs.intersection(scale_pcs)
#                 score = len(matches)
                
#                 # Tie-breaker: prefer keys where the root is actually present in the input
#                 if root in input_pcs:
#                     score += 0.1 

#                 if score > max_score:
#                     max_score = score
#                     best_key = f"{self.note_names[root]} {mode}"
        
#         return best_key

# --- HOW TO USE IN YOUR BENCHMARK ---
# solver = MusicLogicSolver()
# llm_transcription = [60, 64, 67, 65, 71] # C, E, G, F, B
# result = solver.solve_key(llm_transcription)
# print(f"Detected Key: {result}") # Output: C Major