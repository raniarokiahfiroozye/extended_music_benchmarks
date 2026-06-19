import wave
import struct
import numpy as np
import mido

class MidiRenderer:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate

    def midi_to_freq(self, midi_note):
        return 440.0 * (2.0 ** ((midi_note - 69.0) / 12.0))

    def generate_sine_wave(self, freq, duration, amplitude=0.5):
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        wave_data = amplitude * np.sin(2 * np.pi * freq * t)
        return wave_data

    def render(self, midi_path, output_path):
        mid = mido.MidiFile(midi_path)
        tpb = mid.ticks_per_beat
        tempo = 500000 # Default 120 BPM
        
        # First pass: calculate total duration in seconds
        total_ticks = 0
        max_tick = 0
        for msg in mido.merge_tracks(mid.tracks):
            total_ticks += msg.time
            if msg.type == 'note_on' or msg.type == 'note_off':
                max_tick = total_ticks

        # Estimate duration (rough)
        duration_sec = (max_tick / tpb) * (tempo / 1_000_000.0) + 1.0
        audio_buffer = np.zeros(int(self.sample_rate * duration_sec))

        current_tick = 0
        current_time_sec = 0.0
        active_notes = {} # pitch -> start_time_sec

        for msg in mido.merge_tracks(mid.tracks):
            dt_sec = msg.time * (tempo / tpb) / 1_000_000.0
            current_time_sec += dt_sec
            current_tick += msg.time

            if msg.type == 'set_tempo':
                tempo = msg.tempo
            elif msg.type == 'note_on' and msg.velocity > 0:
                active_notes[msg.note] = (current_time_sec, msg.velocity)
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                if msg.note in active_notes:
                    start_time, velocity = active_notes.pop(msg.note)
                    duration = current_time_sec - start_time
                    if duration > 0:
                        freq = self.midi_to_freq(msg.note)
                        # Simple sine wave with a little envelope to avoid clicks
                        samples = self.generate_sine_wave(freq, duration, amplitude=(velocity / 127.0) * 0.3)
                        
                        # Apply simple linear fade-in/out
                        fade_len = int(min(len(samples) // 10, self.sample_rate * 0.01))
                        if fade_len > 0:
                            fade_in = np.linspace(0, 1, fade_len)
                            fade_out = np.linspace(1, 0, fade_len)
                            samples[:fade_len] *= fade_in
                            samples[-fade_len:] *= fade_out

                        start_idx = int(start_time * self.sample_rate)
                        end_idx = start_idx + len(samples)
                        
                        if end_idx > len(audio_buffer):
                            # Resize buffer if needed
                            audio_buffer = np.pad(audio_buffer, (0, end_idx - len(audio_buffer)))
                        
                        audio_buffer[start_idx:end_idx] += samples

        # Normalize and convert to 16-bit PCM
        max_val = np.max(np.abs(audio_buffer))
        if max_val > 0:
            audio_buffer = audio_buffer / max_val * 0.9
        
        pcm_data = (audio_buffer * 32767).astype(np.int16)

        with wave.open(output_path, 'wb') as wav_file:
            wav_file.setnchannels(1) # Mono
            wav_file.setsampwidth(2) # 16-bit
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(pcm_data.tobytes())

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 2:
        renderer = MidiRenderer()
        renderer.render(sys.argv[1], sys.argv[2])
        print(f"Rendered {sys.argv[1]} to {sys.argv[2]}")
