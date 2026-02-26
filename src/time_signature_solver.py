import mido
import numpy as np
from collections import Counter

class TimeSignatureSolver:
    def detect_time_signature(self, file_path):
        """
        Detects the time signature(s) from a MIDI file by reading time_signature meta messages.
        
        Args:
            file_path: Path to the MIDI file.
            
        Returns:
            A list of dictionaries, where each dictionary contains:
            - 'time_signature': The time signature as a string (e.g., "4/4").
            - 'bar': The bar number where the change occurs.
            - 'tick': The absolute tick where the change occurs.
        """
        try:
            mid = mido.MidiFile(file_path)
        except Exception as e:
            print(f"Error loading MIDI file: {e}")
            return []

        tpb = mid.ticks_per_beat if mid.ticks_per_beat > 0 else 480

        time_signature_changes = []
        
        has_initial_ts = False
        for msg in mido.merge_tracks(mid.tracks):
            if msg.type == 'time_signature':
                has_initial_ts = True
                break
        
        if not has_initial_ts:
            return self._detect_from_performance(mid)

        # Pass 1: Find all time signature events first
        current_ts = (4, 4)
        for msg in mido.merge_tracks(mid.tracks):
            if msg.type == 'time_signature':
                if msg.time == 0: # A time signature at the very start
                    current_ts = (msg.numerator, msg.denominator)
                break # Often we only care about the first one for simple cases

        # Add the definitive starting time signature
        time_signature_changes.append({
            'time_signature': f"{current_ts[0]}/{current_ts[1]}",
            'bar': 1,
            'tick': 0
        })

        current_tick = 0
        current_bar = 1
        ticks_per_bar = (tpb * current_ts[0] * 4) / current_ts[1]

        # Pass 2: Iterate through events to find where TS changes occur in bar numbers
        for msg in mido.merge_tracks(mid.tracks):
            
            # Calculate current bar based on ticks passed
            ticks_passed = msg.time
            while ticks_passed > 0 and ticks_per_bar > 0:
                if ticks_passed >= ticks_per_bar:
                    ticks_passed -= ticks_per_bar
                    current_bar += 1
                else:
                    break # Not enough ticks to make a full bar
            
            current_tick += msg.time

            if msg.type == 'time_signature':
                new_ts = (msg.numerator, msg.denominator)
                
                # If this is a new time signature not at the start
                if new_ts != current_ts and current_tick > 0:
                    current_ts = new_ts
                    ticks_per_bar = (tpb * current_ts[0] * 4) / current_ts[1]
                    
                    time_signature_changes.append({
                        'time_signature': f"{new_ts[0]}/{new_ts[1]}",
                        'bar': current_bar,
                        'tick': current_tick
                    })

        # Post-process to remove potential duplicates if multiple were at tick 0
        final_changes = []
        if time_signature_changes:
            final_changes.append(time_signature_changes[0])
            for i in range(1, len(time_signature_changes)):
                if time_signature_changes[i]['tick'] > time_signature_changes[i-1]['tick']:
                    final_changes.append(time_signature_changes[i])

        return final_changes

    def _detect_from_performance(self, mid, accent_threshold=95, ioi_tolerance=0.1):
        """
        Analyzes the MIDI performance to detect the time signature based on note accents.
        """
        tpb = mid.ticks_per_beat if mid.ticks_per_beat > 0 else 480
        
        note_events = []
        current_tick = 0
        for msg in mido.merge_tracks(mid.tracks):
            current_tick += msg.time
            if msg.type == 'note_on' and msg.velocity > 0:
                note_events.append({'tick': current_tick, 'velocity': msg.velocity})

        if not note_events:
            return [{'time_signature': "4/4", 'bar': 1, 'tick': 0}] # Default if no notes

        # Find accented notes
        accented_notes = [n for n in note_events if n['velocity'] > accent_threshold]

        if len(accented_notes) < 4: # Not enough data for a reliable guess
            return [{'time_signature': "4/4", 'bar': 1, 'tick': 0}] # Default

        # Calculate Inter-Onset Intervals (IOIs) in ticks
        iois = np.diff([n['tick'] for n in accented_notes])

        if len(iois) == 0:
            return [{'time_signature': "4/4", 'bar': 1, 'tick': 0}]

        # Find the most common IOI (the beat)
        ioi_counts = Counter(iois)
        most_common_ioi = ioi_counts.most_common(1)[0][0]

        # Try to fit to common time signatures
        for beats_per_bar in [4, 3, 2]:
            bar_duration = most_common_ioi * beats_per_bar
            
            # Count how many IOIs match a multiple of the bar duration
            matches = 0
            for ioi in iois:
                if abs(ioi % bar_duration) < (bar_duration * ioi_tolerance):
                    matches +=1
            
            # If a significant number of IOIs align with the bar grid, we have a match
            if matches / len(iois) > 0.5: # Heuristic: more than 50% of accents align
                return [{'time_signature': f"{beats_per_bar}/4", 'bar': 1, 'tick': 0}]
        
        # Fallback if no clear pattern emerges
        return [{'time_signature': "4/4", 'bar': 1, 'tick': 0}]


if __name__ == '__main__':
    print("TimeSignatureSolver class created in 'src/time_signature_solver.py'")
    print("To use it:")
    print("1. from time_signature_solver import TimeSignatureSolver")
    print("2. solver = TimeSignatureSolver()")
    print("3. results = solver.detect_time_signature('path/to/your/midi.mid')")
    print("4. print(results)")
