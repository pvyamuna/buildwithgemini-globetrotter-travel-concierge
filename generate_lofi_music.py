"""Synthesizes an upbeat lo-fi background music track in Python."""

import numpy as np
from scipy.io import wavfile

SAMPLE_RATE = 44100
DURATION = 35.0  # seconds
NUM_SAMPLES = int(SAMPLE_RATE * DURATION)
BPM = 85.0
BEAT_DUR = 60.0 / BPM  # ~0.7058s per beat


def generate_lofi_track(filename="lofi_track.wav"):
    t = np.linspace(0, DURATION, NUM_SAMPLES, endpoint=False)
    audio = np.zeros(NUM_SAMPLES, dtype=np.float32)

    # 1. Warm Chord Progression (Cmaj7 -> Am7 -> Dm7 -> G7)
    chords = [
        [261.63, 329.63, 392.00, 493.88],  # Cmaj7
        [220.00, 261.63, 329.63, 392.00],  # Am7
        [293.66, 349.23, 440.00, 523.25],  # Dm7
        [196.00, 246.94, 293.66, 349.23],  # G7
    ]
    bar_dur = BEAT_DUR * 4.0  # 4 beats per bar

    pad_layer = np.zeros(NUM_SAMPLES, dtype=np.float32)
    for i in range(NUM_SAMPLES):
        cur_t = t[i]
        bar_idx = int(cur_t / bar_dur) % len(chords)
        chord_freqs = chords[bar_idx]

        # Combine warm sine/triangle waves with gentle vibrato & lowpass
        vibrato = 1.0 + 0.003 * np.sin(2 * np.pi * 4.5 * cur_t)
        note_val = 0.0
        for f in chord_freqs:
            freq = f * vibrato
            note_val += 0.25 * np.sin(2 * np.pi * freq * cur_t)
            # Add subtle second harmonic
            note_val += 0.08 * np.sin(2 * np.pi * freq * 2.0 * cur_t)

        # Soft bar swell envelope
        bar_t = cur_t % bar_dur
        bar_env = np.sin(np.pi * (bar_t / bar_dur)) ** 0.5
        pad_layer[i] = note_val * bar_env

    # 2. Chill Lo-Fi Drums (Kick, Snare, Hi-Hat)
    drums = np.zeros(NUM_SAMPLES, dtype=np.float32)
    total_beats = int(DURATION / BEAT_DUR)

    np.random.seed(42)
    noise = np.random.normal(0, 0.1, NUM_SAMPLES).astype(np.float32)

    for b in range(total_beats):
        beat_start_t = b * BEAT_DUR
        start_idx = int(beat_start_t * SAMPLE_RATE)

        # Kick on beats 1 and 3 (0 and 2 in 0-indexed 4-beat bar)
        if b % 4 in [0, 2]:
            kick_dur = int(0.18 * SAMPLE_RATE)
            end_idx = min(start_idx + kick_dur, NUM_SAMPLES)
            length = end_idx - start_idx
            if length > 0:
                kt = np.linspace(0, 0.18, length)
                # Pitch drop sine sweep 110Hz -> 45Hz
                kick_freq = 110.0 * np.exp(-18.0 * kt) + 45.0
                kick_env = np.exp(-12.0 * kt)
                kick_wave = 0.6 * np.sin(2 * np.pi * kick_freq * kt) * kick_env
                drums[start_idx:end_idx] += kick_wave

        # Snare/Rimshot on beats 2 and 4 (1 and 3 in bar)
        if b % 4 in [1, 3]:
            snare_dur = int(0.15 * SAMPLE_RATE)
            end_idx = min(start_idx + snare_dur, NUM_SAMPLES)
            length = end_idx - start_idx
            if length > 0:
                st = np.linspace(0, 0.15, length)
                snare_env = np.exp(-22.0 * st)
                snare_tone = 0.25 * np.sin(2 * np.pi * 180.0 * st)
                snare_noise = 0.35 * noise[start_idx:end_idx]
                drums[start_idx:end_idx] += (snare_tone + snare_noise) * snare_env

        # Hi-hat on every beat and offbeat (eighth notes)
        for sub in [0.0, 0.5]:
            hh_start_t = (b + sub) * BEAT_DUR
            hh_idx = int(hh_start_t * SAMPLE_RATE)
            hh_dur = int(0.05 * SAMPLE_RATE)
            end_idx = min(hh_idx + hh_dur, NUM_SAMPLES)
            length = end_idx - hh_idx
            if length > 0:
                ht = np.linspace(0, 0.05, length)
                hh_env = np.exp(-60.0 * ht)
                # High-frequency noise
                hh_noise = 0.12 * noise[hh_idx:end_idx] * hh_env
                drums[hh_idx:end_idx] += hh_noise

    # 3. Vinyl Crackle & Soft Hiss Noise
    crackle = np.random.choice([0.0, 0.0, 0.0, 0.05, -0.05], size=NUM_SAMPLES) * np.random.binomial(1, 0.002, NUM_SAMPLES)
    hiss = 0.015 * np.random.normal(0, 1, NUM_SAMPLES)

    # Combine all layers
    audio = 0.45 * pad_layer + 0.5 * drums + crackle + hiss

    # Normalize audio to peak at -1.5 dB (0.85)
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = (audio / max_val) * 0.85

    # Convert to 16-bit PCM WAV
    audio_int16 = (audio * 32767).astype(np.int16)
    wavfile.write(filename, SAMPLE_RATE, audio_int16)
    print(f"Generated upbeat lo-fi track: {filename} ({DURATION}s)")


if __name__ == "__main__":
    generate_lofi_track()
