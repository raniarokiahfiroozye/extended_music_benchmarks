import numpy as np
class SimplifiedMusicSolver:
    def __init__(self):
        self.note_names = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
        
        # Krumhansl-Schmuckler Key Profiles (Krumhansl & Kessler, 1982)
        # These represent the stability/importance of each pitch class relative to the tonic.
        self.major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
        self.minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

    def solve_key(self, notes):
        """
        Determines the key using the Krumhansl-Schmuckler key-finding algorithm.
        Calculates the Pearson correlation between the input pitch distribution
        and the standard key profiles.
        
        Args:
            notes: Either a list of integers (MIDI numbers) OR 
                   a list of dicts {'pitch': int, 'duration': float, 'velocity': int}
        """
        if not notes:
            return []

        # 1. Build Pitch Class Distribution (Weighted)
        pc_distribution = np.zeros(12)
        
        if isinstance(notes[0], dict):
            # Rich Input: Weight by Duration * Velocity
            for note in notes:
                pc = note['pitch'] % 12
                weight = note.get('duration', 1.0) * note.get('velocity', 64)
                pc_distribution[pc] += weight
        else:
            # Simple Input: Weight by frequency (count)
            for note in notes:
                pc = note % 12
                pc_distribution[pc] += 1.0

        # Handle silence
        if np.sum(pc_distribution) == 0:
            return []

        # 2. Calculate Correlation with Key Profiles
        candidates = []
        
        # Check all 12 Major Keys
        for i in range(12):
            # Shift the major profile to align with root 'i'
            profile = np.roll(self.major_profile, i)
            corr = np.corrcoef(pc_distribution, profile)[0, 1]
            candidates.append({'key': f"{self.note_names[i]} Major", 'score': corr})
            
        # Check all 12 Minor Keys
        for i in range(12):
            profile = np.roll(self.minor_profile, i)
            corr = np.corrcoef(pc_distribution, profile)[0, 1]
            candidates.append({'key': f"{self.note_names[i]} Minor", 'score': corr})
            
        # 3. Sort by Correlation Score (Descending)
        candidates.sort(key=lambda x: x['score'], reverse=True)
        
        # 4. Return top candidates
        # We return keys that are very close to the best score (e.g., within 0.05 correlation)
        best_score = candidates[0]['score']
        results = []
        
        for c in candidates:
            if c['score'] >= best_score - 0.05:
                results.append({
                    'key': c['key'],
                    'correlation': round(c['score'], 4),
                    # Legacy support: map correlation to a "percentage" for display
                    'match_percentage': round(max(0, c['score']) * 100, 2)
                })
                
        return results

    def load_midi(self, file_path):
        """
        Parses a MIDI file into a list of note dictionaries.
        Requires 'mido' library.
        """
        try:
            import mido
        except ImportError:
            raise ImportError("The 'mido' library is required. Please install it: pip install mido")

        mid = mido.MidiFile(file_path)
        events = []
        active_notes = {} # pitch -> (start_time, velocity)
        current_time = 0.0

        # Merge tracks to handle polyphony correctly across tracks
        for msg in mido.merge_tracks(mid.tracks):
            current_time += msg.time # Accumulate delta time to get absolute time
            
            if msg.type == 'note_on' and msg.velocity > 0:
                # Note Attack
                if msg.note in active_notes:
                    # If note was already on, finish it (re-attack)
                    start, vel = active_notes.pop(msg.note)
                    events.append({'pitch': msg.note, 'start': start, 'duration': current_time - start, 'velocity': vel})
                active_notes[msg.note] = (current_time, msg.velocity)
            
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                # Note Release
                if msg.note in active_notes:
                    start, vel = active_notes.pop(msg.note)
                    events.append({'pitch': msg.note, 'start': start, 'duration': current_time - start, 'velocity': vel})
        
        # Sort by start time
        events.sort(key=lambda x: x['start'])
        return events

    def load_midi_seconds(self, file_path):
        """
        Parses a MIDI file into notes with duration in SECONDS.
        This respects Tempo changes (accelerando/ritardando).
        Notes played slower will have longer durations and thus more weight.
        """
        try:
            import mido
        except ImportError:
            raise ImportError("mido required")

        mid = mido.MidiFile(file_path)
        tpb = mid.ticks_per_beat
        tempo = 500000 # Default 120 BPM (microseconds per beat)
        
        notes = []
        active_notes = {} # pitch -> (start_time_sec, velocity)
        current_time_sec = 0.0
        
        # merge_tracks yields messages with delta_time in TICKS
        for msg in mido.merge_tracks(mid.tracks):
            # Convert delta ticks to delta seconds using current tempo
            # seconds = ticks * (microseconds_per_beat / ticks_per_beat) / 1,000,000
            dt_sec = msg.time * (tempo / tpb) / 1_000_000.0
            current_time_sec += dt_sec
            
            if msg.type == 'set_tempo':
                tempo = msg.tempo
            elif msg.type == 'note_on' and msg.velocity > 0:
                active_notes[msg.note] = (current_time_sec, msg.velocity)
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                if msg.note in active_notes:
                    start, vel = active_notes.pop(msg.note)
                    duration = current_time_sec - start
                    notes.append({'pitch': msg.note, 'start': start, 'duration': duration, 'velocity': vel})
        
        notes.sort(key=lambda x: x['start'])
        return notes

    def rolling_key_search(self, notes, window_size=5):
        """
        Returns a list of (index, candidates) for each window in the note sequence.
        """
        results = []
        for i in range(len(notes) - window_size + 1):
            window = notes[i : i + window_size]
            results.append((i, self.solve_key(window)))
        return results

    def analyze_by_bars(self, file_path, bars_per_window=4, step_bars=1):
        """
        Analyzes the key in sliding windows of musical bars (measures).
        Uses Time Signature and Ticks Per Beat to determine bar boundaries.
        Robust to Tempo changes (BPM does not affect Bar lines).
        """
        try:
            import mido
        except ImportError:
            raise ImportError("mido required")

        mid = mido.MidiFile(file_path)
        tpb = mid.ticks_per_beat
        
        # 1. Extract all events with absolute ticks
        # We need absolute ticks to map against bar boundaries
        abs_events = []
        for track in mid.tracks:
            curr_tick = 0
            for msg in track:
                curr_tick += msg.time
                if msg.type in ['note_on', 'note_off', 'time_signature']:
                    abs_events.append((curr_tick, msg))
        
        # Sort by tick. Ensure time_signature comes before notes at same tick.
        abs_events.sort(key=lambda x: (x[0], 0 if x[1].type == 'time_signature' else 1))
        
        # 2. Parse Notes and Time Signatures
        notes = [] # {'pitch', 'start', 'duration', 'velocity'} (in ticks)
        time_sigs = [] # (tick, num, denom)
        active_notes = {}
        
        for tick, msg in abs_events:
            if msg.type == 'time_signature':
                time_sigs.append((tick, msg.numerator, msg.denominator))
            elif msg.type == 'note_on' and msg.velocity > 0:
                active_notes[msg.note] = (tick, msg.velocity)
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                if msg.note in active_notes:
                    start, vel = active_notes.pop(msg.note)
                    notes.append({'pitch': msg.note, 'start': start, 'duration': tick - start, 'velocity': vel})

        # 3. Define Bar Boundaries
        # Default to 4/4 if no time sig present at start
        if not time_sigs or time_sigs[0][0] > 0:
            time_sigs.insert(0, (0, 4, 4))
            
        bar_boundaries = [] # list of start_ticks
        curr_tick = 0
        max_tick = max([n['start'] + n['duration'] for n in notes]) if notes else 0
        
        # Iterate through time, advancing by bar lengths
        ts_idx = 0
        while curr_tick <= max_tick:
            bar_boundaries.append(curr_tick)
            
            # Check if we passed a time signature change
            # (Use the latest time signature that happened at or before curr_tick)
            while ts_idx + 1 < len(time_sigs) and time_sigs[ts_idx+1][0] <= curr_tick:
                ts_idx += 1
            
            _, num, denom = time_sigs[ts_idx]
            # Calculate ticks per bar based on Time Signature
            # Formula: (TicksPerBeat * Numerator * 4) / Denominator
            # e.g. 3/4 -> 480 * 3 * 4 / 4 = 1440 ticks
            ticks_per_bar = int(tpb * num * 4 / denom)
            curr_tick += ticks_per_bar

        # 4. Bucket Notes into Bars
        # We assign a note to the bar where it STARTS
        bars = [[] for _ in range(len(bar_boundaries))]
        for note in notes:
            # Find which bar this note starts in
            for i in range(len(bar_boundaries) - 1):
                if bar_boundaries[i] <= note['start'] < bar_boundaries[i+1]:
                    bars[i].append(note)
                    break
        
        # 5. Sliding Window Analysis
        results = []
        for i in range(0, len(bars) - bars_per_window + 1, step_bars):
            # Collect all notes in these bars
            window_notes = []
            for b in range(bars_per_window):
                window_notes.extend(bars[i + b])
            
            candidates = self.solve_key(window_notes)
            results.append({
                'start_bar': i + 1,
                'end_bar': i + bars_per_window,
                'candidates': candidates
            })
            
        return results

    def analyze_by_time(self, file_path, window_seconds=5.0, step_seconds=1.0):
        """
        Analyzes key in sliding windows of SECONDS (absolute time).
        
        This is essential for Audio-to-MIDI conversions where the internal 
        tempo map/bar lines might be arbitrary (e.g. fixed 120 BPM) and 
        do not match the actual musical measures.
        """
        notes = self.load_midi_seconds(file_path)
        if not notes:
            return []
            
        # Find total duration based on the end of the last note
        last_note = max(notes, key=lambda x: x['start'] + x['duration'])
        total_duration = last_note['start'] + last_note['duration']
        
        results = []
        current_time = 0.0
        
        while current_time < total_duration:
            window_end = current_time + window_seconds
            
            # Collect notes that sound during this window
            window_notes = []
            for n in notes:
                n_end = n['start'] + n['duration']
                
                # Check for overlap: Note starts before window ends AND ends after window starts
                if n['start'] < window_end and n_end > current_time:
                    # Calculate effective duration within this window for accurate weighting
                    eff_start = max(n['start'], current_time)
                    eff_end = min(n_end, window_end)
                    eff_dur = eff_end - eff_start
                    
                    # Create a temporary note dict with adjusted duration
                    window_notes.append({
                        'pitch': n['pitch'],
                        'velocity': n['velocity'],
                        'duration': eff_dur
                    })
            
            candidates = self.solve_key(window_notes)
            results.append({
                'start_time': round(current_time, 2),
                'end_time': round(window_end, 2),
                'candidates': candidates
            })
            
            current_time += step_seconds
            
        return results

    def analyze_midi(self, file_path, use_musical_grid=False, window_size=None, step_size=None):
        """
        Unified method to analyze a MIDI file.
        
        Args:
            file_path: Path to the MIDI file.
            use_musical_grid: If True, assumes the MIDI has valid bar lines (analyze_by_bars).
                              If False, uses absolute time (analyze_by_time), which is safer
                              for audio-to-midi or unquantized performances.
            window_size: Size of the window. 
                         If grid=True, this is number of bars (default 4).
                         If grid=False, this is number of seconds (default 5.0).
            step_size:   Step size for the sliding window (bars if grid=True, seconds if grid=False).
        """
        if use_musical_grid:
            # Use Bar-Based Analysis (for Scores / Quantized MIDI)
            w = int(window_size) if window_size is not None else 4
            s = int(step_size) if step_size is not None else 1
            return self.analyze_by_bars(file_path, bars_per_window=w, step_bars=s)
        else:
            # Use Time-Based Analysis (Safe Default for Audio-to-MIDI)
            w = float(window_size) if window_size is not None else 5.0
            s = float(step_size) if step_size is not None else 1.0
            return self.analyze_by_time(file_path, window_seconds=w, step_seconds=s)

if __name__ == "__main__":
    # --- QUICK TEST ---
    solver = SimplifiedMusicSolver()
    # Testing your G Major set from earlier: [G, B, D, F#]
    print(solver.solve_key([67, 71, 74, 66]))
