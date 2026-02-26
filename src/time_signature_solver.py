import mido

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
        
        # Default to 4/4 if no time signature message is present at the beginning
        current_ts = (4, 4)
        has_initial_ts = False

        # Pass 1: Find all time signature events first
        for msg in mido.merge_tracks(mid.tracks):
            if msg.type == 'time_signature':
                if msg.time == 0: # A time signature at the very start
                    current_ts = (msg.numerator, msg.denominator)
                    has_initial_ts = True
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


if __name__ == '__main__':
    print("TimeSignatureSolver class created in 'src/time_signature_solver.py'")
    print("To use it:")
    print("1. from time_signature_solver import TimeSignatureSolver")
    print("2. solver = TimeSignatureSolver()")
    print("3. results = solver.detect_time_signature('path/to/your/midi.mid')")
    print("4. print(results)")
