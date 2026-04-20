import mido
import numpy as np
from collections import Counter

class BeatSolver:
    def detect_beats(self, file_path, accent_threshold=95):
        """
        Detects beats in a MIDI file based on note accents and inter-onset intervals.
        """
        try:
            mid = mido.MidiFile(file_path)
        except Exception as e:
            print(f"Error loading MIDI file: {e}")
            return []

        tpb = mid.ticks_per_beat if mid.ticks_per_beat > 0 else 480
        
        note_events = []
        current_tick = 0
        for msg in mido.merge_tracks(mid.tracks):
            current_tick += msg.time
            if msg.type == 'note_on' and msg.velocity > 0:
                note_events.append({'tick': current_tick, 'velocity': msg.velocity})

        if not note_events:
            return []

        beats = self._estimate_beats(note_events, tpb, accent_threshold)
        return beats

    def _estimate_beats(self, notes, tpb, accent_threshold):
        """
        Estimates beat locations from a list of note events.
        """
        if len(notes) < 4:
            return []

        all_ticks = np.array([n['tick'] for n in notes])
        
        # Determine Primary Beat (Pulse) based on most common Inter-Onset Interval (IOI)
        iois = np.diff(all_ticks)
        ioi_counts = Counter(iois)
        
        most_common_iois = [ioi for ioi, count in ioi_counts.most_common(10) if ioi > tpb / 4] # Filter out very short IOIs
        if not most_common_iois:
            beat_guess = tpb # Default to a quarter note if no good IOI is found
        else:
            beat_guess = most_common_iois[0]

        # Find the start of the first beat
        # A simple approach is to assume the first note is on a beat
        first_beat_tick = all_ticks[0]

        # Generate beat ticks
        beats = []
        current_beat_tick = first_beat_tick
        max_tick = all_ticks[-1]
        
        while current_beat_tick <= max_tick:
            beats.append(current_beat_tick)
            current_beat_tick += beat_guess
            
        return beats

if __name__ == '__main__':
    print("BeatSolver class created in 'src/beat_solver.py'")
