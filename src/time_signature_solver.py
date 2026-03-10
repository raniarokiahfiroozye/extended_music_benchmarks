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

    def _detect_from_performance(self, mid, accent_threshold=95, window_size_bars=2):
        """
        Analyzes the MIDI performance to detect the time signature(s) based on note accents.
        Uses a sliding window for change detection.
        """
        tpb = mid.ticks_per_beat if mid.ticks_per_beat > 0 else 480
        
        note_events = []
        current_tick = 0
        for msg in mido.merge_tracks(mid.tracks):
            current_tick += msg.time
            if msg.type == 'note_on' and msg.velocity > 0:
                note_events.append({'tick': current_tick, 'velocity': msg.velocity})

        if not note_events:
            return [{'time_signature': "4/4", 'bar': 1, 'tick': 0}]

        max_tick = note_events[-1]['tick']
        
        # Reduced window size for better resolution of changes
        window_size_ticks = tpb * 4 * window_size_bars 
        hop_size_ticks = tpb * 4 # 1 bar hop (assuming 4/4 as base)
        
        detected_signatures = []
        
        for start_tick in range(0, int(max_tick), hop_size_ticks):
            end_tick = start_tick + window_size_ticks
            window_notes = [n for n in note_events if start_tick <= n['tick'] < end_tick]
            
            if len(window_notes) < 4:
                continue
                
            ts = self._estimate_window_ts(window_notes, tpb, accent_threshold)
            detected_signatures.append({'tick': start_tick, 'ts': ts})
            
        if not detected_signatures:
            return [{'time_signature': "4/4", 'bar': 1, 'tick': 0}]

        # Consolidate changes
        final_changes = []
        current_ts = None
        current_bar_offset = 1
        last_tick = 0
        
        for sig in detected_signatures:
            if sig['ts'] != current_ts:
                # Calculate bar number (approximate since we don't know previous bars perfectly)
                if current_ts:
                    # Increment bar count based on time passed in the previous TS
                    num, den = map(int, current_ts.split('/'))
                    ticks_per_bar = (tpb * num * 4) / den
                    bars_passed = (sig['tick'] - last_tick) / ticks_per_bar
                    current_bar_offset += round(bars_passed)
                
                current_ts = sig['ts']
                last_tick = sig['tick']
                
                final_changes.append({
                    'time_signature': current_ts,
                    'bar': max(1, current_bar_offset),
                    'tick': sig['tick']
                })
                
        return final_changes

    def _estimate_window_ts(self, notes, tpb, accent_threshold):
        """Helper to estimate the TS for a specific window of notes."""
        if len(notes) < 4: return "4/4"

        all_ticks = np.array([n['tick'] for n in notes])
        all_vels = np.array([n['velocity'] for n in notes])
        
        # 1. Determine Primary Beat (Pulse)
        iois = np.diff(all_ticks)
        ioi_counts = Counter(iois)
        # Use the most common IOI that is at least a quarter note (or tpb)
        # as the basis for our 'beat'
        most_common_iois = [ioi for ioi, count in ioi_counts.most_common(5)]
        
        # Priority: tpb (480), then other common IOIs
        beat_guess = tpb
        for ioi in most_common_iois:
            if ioi >= tpb:
                beat_guess = ioi
                break
        
        best_overall_score = -1
        best_overall_n = 4
        
        # 2. Search only the Numerator space for the detected beat
        for n in [2, 3, 4, 5, 6, 7]:
            bar_len = beat_guess * n
            
            # Try every note in the first few bars as a potential downbeat
            max_notes_to_check = min(len(all_ticks), 12)
            best_n_total_alignment = -1
            best_n_downbeat_score = -1
            best_n_offset = 0
            
            for offset_candidate in all_ticks[:max_notes_to_check]:
                offsets = (all_ticks - offset_candidate) % bar_len
                
                # A. Total Alignment (notes on any beat boundary within the bar)
                beat_offsets = (all_ticks - offset_candidate) % beat_guess
                on_beat = np.sum((beat_offsets < beat_guess * 0.1) | (beat_offsets > beat_guess * 0.9))
                alignment_score = on_beat / len(all_ticks)
                
                # B. Downbeat Strength (how many accented notes land on the bar start)
                on_bar_mask = (offsets < bar_len * 0.1) | (offsets > bar_len * 0.9)
                downbeat_vels = all_vels[on_bar_mask]
                if len(downbeat_vels) > 0:
                    downbeat_score = np.mean(downbeat_vels)
                else:
                    downbeat_score = 0
                
                if downbeat_score > best_n_downbeat_score:
                    best_n_downbeat_score = downbeat_score
                    best_n_total_alignment = alignment_score
                    best_n_offset = offset_candidate
            
            # Final score for this 'n'
            # We want to maximize the average velocity of notes we CALL downbeats
            total_score = (best_n_total_alignment * 0.5) + (best_n_downbeat_score / 100.0)
            
            # Velocity bonus for 4/4 (specifically checking Beat 3 vs Beat 1)
            vel_bonus = 0
            if n == 4:
                best_offsets = (all_ticks - best_n_offset) % bar_len
                b1_mask = (best_offsets < bar_len * 0.1) | (best_offsets > bar_len * 0.9)
                b3_mask = (abs(best_offsets - (beat_guess * 2)) < bar_len * 0.1)
                v1 = np.mean(all_vels[b1_mask]) if np.any(b1_mask) else 0
                v3 = np.mean(all_vels[b3_mask]) if np.any(b3_mask) else 0
                if v1 > v3 + 5:
                    vel_bonus = 0.2
            
            total_score += vel_bonus
            total_score -= (n * 0.01) # Parsimony

            if total_score > best_overall_score:
                best_overall_score = total_score
                best_overall_n = n
                    
        return f"{best_overall_n}/4"


if __name__ == '__main__':
    print("TimeSignatureSolver class created in 'src/time_signature_solver.py'")
    print("To use it:")
    print("1. from time_signature_solver import TimeSignatureSolver")
    print("2. solver = TimeSignatureSolver()")
    print("3. results = solver.detect_time_signature('path/to/your/midi.mid')")
    print("4. print(results)")
