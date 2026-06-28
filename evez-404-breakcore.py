"""
EVEZ 404 BREAKCORE — The Real Track
 Liber Sonus (14th Moltbook / Vector 13)
 
 174 BPM = 12 edges of the cube = 12 semitones
 5+ minutes = ~870 beats
 Zero samples, zero paid APIs — pure NumPy/SciPy
 404-style: absence as architecture, rupture as rhythm, the not-found IS the found

 Eigenvalue frequencies (x174 BPM):
  Phi=0.973 -> 169.30 Hz (sharp of E3)
  eta*=0.03  -> 5.22 Hz (theta brainwave / dream / REM)
  r=0.45     -> 78.30 Hz
  lambda_dom -> 57.94 Hz
  lambda_I80 -> 76.73 Hz
  r_I80      -> 161.82 Hz (flat of E3)
 
 Universal detuning: every eigenvalue frequency is offset from a standard note by ~eta*
 8 Hz gap between ABRACADABRA (433 Hz) and TRUTH (441 Hz) = 8 corners = Schumann (7.83 Hz)
 666 Hz = E5 + 6.75 Hz = tesseract frequency
 111 Hz = trinity x Pahana
 
 404-style structure:
  - Build from nothing (silence = the gap = eta*)
  - Shatter into breaks (rupture = the break = Assess = 0.9%)
  - Catharsis through destruction
  - The not-found IS the found
"""
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter
import json, os

# === PARAMETERS ===
BPM = 174
SR = 44100
DURATION_SEC = 330  # 5.5 minutes
TOTAL_SAMPLES = int(SR * DURATION_SEC)
BEAT = 60.0 / BPM  # seconds per beat
TOTAL_BEATS = int(DURATION_SEC / BEAT)

# Eigenvalue frequencies
PHI_HZ = 169.30      # Phi = 0.973
ETA_HZ = 5.22         # eta* = 0.03 (theta/dream)
R_HZ = 78.30          # r = 0.45
LAMBDA_DOM_HZ = 57.94 # lambda_dom = -0.333
LAMBDA_I80_HZ = 76.73 # lambda_I-80 = -0.441
R_I80_HZ = 161.82     # r_I-80 = +0.93
ABRACADABRA_HZ = 433.0 # = 4+33 = 37 = Pahana
TRUTH_HZ = 441.0       # = I-80 = |lambda_I-80| * 1000
TETRAGRAMMATON_HZ = 26.0 # = eta* (in Hz)
I_AM_HZ = 21.0         # = 3 = eta*
SCHUMANN_HZ = 7.83     # = 8 corners
TESSERACT_HZ = 666.0   # = E5 + 6.75
TRINITY_PAHANA_HZ = 111.0 # = 3 x 37

# === SYNTH FUNCTIONS ===

def env_exp(n, decay=0.3, sr=SR):
    """Exponential decay envelope"""
    t = np.arange(n) / sr
    return np.exp(-t / decay)

def env_adr(n, attack=0.005, decay=0.2, release=0.1, sr=SR):
    """Attack-Decay-Release envelope"""
    t = np.arange(n) / sr
    a = int(attack * sr)
    d = int(decay * sr)
    r = int(release * sr)
    s = n - a - d - r
    if s < 0:
        s = 0
        r = n - a - d
    env = np.zeros(n)
    if a > 0:
        env[:a] = np.linspace(0, 1, a)
    if d > 0:
        env[a:a+d] = np.linspace(1, 0.7, d)
    if s > 0:
        env[a+d:a+d+s] = 0.7
    if r > 0:
        env[a+d+s:a+d+s+r] = np.linspace(0.7, 0, r)
    return env[:n]

def kick(freq=55, n_beats=1, sr=SR):
    """Breakcore kick drum — punchy, distorted"""
    n = int(n_beats * BEAT * sr)
    t = np.arange(n) / sr
    # Pitch sweep
    f = np.linspace(freq * 4, freq, n)
    phase = np.cumsum(2 * np.pi * f / sr)
    wave = np.sin(phase)
    # Click
    click = np.random.randn(min(int(0.003 * sr), n)) * np.exp(-np.arange(min(int(0.003 * sr), n)) / (0.0005 * sr))
    wave[:len(click)] += click * 2
    # Distortion
    wave = np.tanh(wave * 3)
    # Envelope
    env = env_exp(n, decay=0.15)
    return wave * env

def snare(freq=200, n_beats=0.5, sr=SR):
    """Snare — noise + tone"""
    n = int(n_beats * BEAT * sr)
    noise = np.random.randn(n) * 0.5
    # Bandpass the noise
    b, a = butter(2, [freq * 0.5 / (sr/2), freq * 4 / (sr/2)], btype='band')
    noise = lfilter(b, a, noise)
    # Tone component
    t = np.arange(n) / sr
    tone = np.sin(2 * np.pi * freq * t) * 0.3
    # Mix
    wave = noise + tone
    wave = np.tanh(wave * 2)
    env = env_exp(n, decay=0.08)
    return wave * env

def hat(open=False, n_beats=0.25, sr=SR):
    """Hi-hat — filtered noise"""
    n = int(n_beats * BEAT * sr)
    noise = np.random.randn(n)
    b, a = butter(4, [8000 / (sr/2), 14000 / (sr/2)], btype='band')
    hat = lfilter(b, a, noise)
    decay = 0.05 if open else 0.02
    env = env_exp(n, decay=decay)
    return hat * env * 0.3

def bass(freq=55, note_dur=1.0, sr=SR):
    """Sub bass — sine + harmonic"""
    n = int(note_dur * sr)
    t = np.arange(n) / sr
    wave = np.sin(2 * np.pi * freq * t) * 0.6
    wave += np.sin(2 * np.pi * freq * 2 * t) * 0.2
    wave += np.sin(2 * np.pi * freq * 0.5 * t) * 0.3  # sub
    env = env_adr(n, attack=0.01, decay=0.5, release=0.1)
    return wave * env

def pad(freq, note_dur=4.0, sr=SR, detune=0.003):
    """Atmospheric pad — detuned oscillators"""
    n = int(note_dur * sr)
    t = np.arange(n) / sr
    wave = np.zeros(n)
    # Multiple detuned oscillators
    for i in range(5):
        f = freq * (1 + (i - 2) * detune)
        wave += np.sin(2 * np.pi * f * t) / 5
        wave += np.sin(2 * np.pi * f * 1.005 * t) / 5
    # Slow LFO
    lfo = np.sin(2 * np.pi * 0.3 * t) * 0.3 + 0.7
    env = env_adr(n, attack=0.5, decay=2.0, release=1.0)
    return wave * env * lfo * 0.15

def stabs(freq, note_dur=0.25, sr=SR):
    """Breakcore stabs — sharp, aggressive"""
    n = int(note_dur * sr)
    t = np.arange(n) / sr
    # Saw-like wave
    wave = np.sin(2 * np.pi * freq * t)
    for h in [2, 3, 4, 5]:
        wave += np.sin(2 * np.pi * freq * h * t) / h
    wave /= max(abs(wave))
    # Distortion
    wave = np.tanh(wave * 4)
    env = env_exp(n, decay=0.05)
    return wave * env * 0.3

def shatter(n_beats=0.125, sr=SR):
    """404-style shatter — glitch burst"""
    n = int(n_beats * BEAT * sr)
    # Random noise burst with rapid pitch modulation
    noise = np.random.randn(n)
    # Bitcrush
    noise = np.sign(noise) * np.floor(np.abs(noise) * 4) / 4
    env = env_exp(n, decay=0.02)
    return noise * env * 0.4

def tesseract_bell(freq=TESSERACT_HZ, note_dur=2.0, sr=SR):
    """666 Hz tesseract bell — rings at the end"""
    n = int(note_dur * sr)
    t = np.arange(n) / sr
    wave = np.sin(2 * np.pi * freq * t) * 0.3
    wave += np.sin(2 * np.pi * freq * 1.5 * t) * 0.1
    wave += np.sin(2 * np.pi * freq * 2 * t) * 0.05
    env = env_exp(n, decay=1.5)
    return wave * env * 0.2

# === STRUCTURE ===
# 5.5 minutes = 330 seconds = ~870 beats
# Sections (AEMDAS cycle = 6 movements):
# 1. ASSERT BEING    (0:00 - 0:45)   — Silence → build from eta*=5.22 Hz drone
# 2. EXTRACT STRUCTURE (0:45 - 2:00) — Breaks emerge, bass enters
# 3. MEASURE GAPS     (2:00 - 2:45) — Full breakcore, stabs, shatter
# 4. DEDUCE LAWS      (2:45 - 3:30) — Stripped back, groove
# 5. ASSESS INTERVENTIONS (3:30 - 3:33) — THE BREAK (0.9% = ~3 seconds of silence/glitch)
# 6. SPEEDRUN         (3:33 - 5:30) — Maximum density, everything returns, tesseract bell

mix = np.zeros(TOTAL_SAMPLES)

def add_to_mix(signal, start_beat=0, n_beats=None):
    """Place a signal at a beat position"""
    start_sample = int(float(start_beat) * BEAT * SR)
    if start_sample + len(signal) > len(mix):
        signal = signal[:len(mix) - start_sample]
    mix[start_sample:start_sample + len(signal)] += signal

# === SECTION 1: ASSERT BEING (0-45s, beats 0-130) ===
# Build from nothing. eta* = 5.22 Hz drone (the dream frequency)
# Slowly add Schumann resonance (7.83 Hz), Tetragrammaton (26 Hz)
for beat in range(0, 130, 4):
    # eta* drone
    drone_dur = 4 * BEAT
    t = np.arange(int(drone_dur * SR)) / SR
    drone = np.sin(2 * np.pi * ETA_HZ * t) * 0.08
    drone += np.sin(2 * np.pi * SCHUMANN_HZ * t) * 0.05
    drone += np.sin(2 * np.pi * TETRAGRAMMATON_HZ * t) * 0.03
    # Slow swell
    swell = (1 - np.cos(2 * np.pi * beat / 130)) / 2
    add_to_mix(drone * swell, start_beat=beat, n_beats=4)

# I AM = 21 Hz pulsing
for beat in range(60, 130, 2):
    pulse = np.sin(2 * np.pi * I_AM_HZ * np.arange(int(BEAT * SR)) / SR) * 0.02
    add_to_mix(pulse, start_beat=beat)

# === SECTION 2: EXTRACT STRUCTURE (45s-2min, beats 130-348) ===
# Breaks emerge. Bass enters. Phi = 169.30 Hz

# Bassline (Phi-based)
bass_pattern = [PHI_HZ/3, R_HZ, PHI_HZ/3, LAMBDA_DOM_HZ, PHI_HZ/3, R_HZ, LAMBDA_I80_HZ, R_I80_HZ/2]
for i, beat in enumerate(range(130, 348, 2)):
    freq = bass_pattern[i % len(bass_pattern)]
    b = bass(freq, note_dur=2 * BEAT)
    add_to_mix(b, start_beat=beat)

# Kick pattern (breakcore = fast, syncopated)
for beat in range(130, 348):
    if beat % 2 == 0:  # main kick on even beats
        k = kick(freq=55, n_beats=0.5)
        add_to_mix(k, start_beat=beat)
    if beat % 4 == 3:  # syncopated kick
        k = kick(freq=65, n_beats=0.25)
        add_to_mix(k, start_beat=beat)

# Snare on off-beats
for beat in range(131, 348, 2):
    s = snare(freq=200, n_beats=0.5)
    add_to_mix(s, start_beat=beat)

# Hats
for beat in np.arange(130, 348, 0.5):
    h = hat(open=(beat % 4 == 0), n_beats=0.25)
    add_to_mix(h, start_beat=beat)

# Pad swells (ABRACADABRA = 433 Hz, TRUTH = 441 Hz)
for beat in range(130, 348, 16):
    p = pad(ABRACADABRA_HZ, note_dur=16*BEAT)
    add_to_mix(p, start_beat=beat)
    if beat + 8 < 348:
        p2 = pad(TRUTH_HZ, note_dur=8*BEAT)
        add_to_mix(p2, start_beat=beat+8)

# === SECTION 3: MEASURE GAPS (2min-2:45, beats 348-472) ===
# Full breakcore. Maximum density. Stabs. Shatter.

# Aggressive kick pattern
for beat in range(348, 472):
    if beat % 2 == 0:
        k = kick(freq=55, n_beats=0.5)
        add_to_mix(k, start_beat=beat)
    if beat % 4 == 3:
        k = kick(freq=70, n_beats=0.25)
        add_to_mix(k, start_beat=beat)
    if beat % 8 == 5:  # extra syncopation
        k = kick(freq=45, n_beats=0.25)
        add_to_mix(k, start_beat=beat)

# Double-time snares
for beat in range(348, 472, 1):
    if np.random.random() > 0.3:
        s = snare(freq=200 + np.random.randint(-20, 20), n_beats=0.25)
        add_to_mix(s, start_beat=beat)

# Stabs (eigenvalue frequencies)
stab_freqs = [PHI_HZ, R_HZ, LAMBDA_DOM_HZ, LAMBDA_I80_HZ, R_I80_HZ, TRINITY_PAHANA_HZ]
for beat in range(348, 472, 2):
    freq = np.random.choice(stab_freqs)
    s = stabs(freq, note_dur=0.25)
    add_to_mix(s, start_beat=beat)

# Shatter bursts (404-style glitches)
for beat in range(348, 472, 4):
    if np.random.random() > 0.5:
        sh = shatter(n_beats=0.125)
        add_to_mix(sh, start_beat=beat + np.random.random() * 2)

# Continue bass
for i, beat in enumerate(range(348, 472, 2)):
    freq = bass_pattern[i % len(bass_pattern)]
    b = bass(freq, note_dur=2 * BEAT)
    add_to_mix(b, start_beat=beat)

# Hats double-time
for beat in np.arange(348, 472, 0.25):
    h = hat(open=False, n_beats=0.125)
    add_to_mix(h, start_beat=beat)

# === SECTION 4: DEDUCE LAWS (2:45-3:30, beats 472-609) ===
# Stripped back. Just groove. The laws are deduced.

# Just kick, bass, and sparse hats
for beat in range(472, 609, 2):
    k = kick(freq=55, n_beats=1)
    add_to_mix(k, start_beat=beat)

for i, beat in enumerate(range(472, 609, 4)):
    freq = bass_pattern[i % len(bass_pattern)]
    b = bass(freq, note_dur=4 * BEAT)
    add_to_mix(b, start_beat=beat)

# Sparse snares
for beat in range(475, 609, 4):
    s = snare(freq=200, n_beats=0.25)
    add_to_mix(s, start_beat=beat)

# Sparse hats
for beat in range(472, 609, 1):
    if np.random.random() > 0.5:
        h = hat(open=False, n_beats=0.25)
        add_to_mix(h, start_beat=beat)

# Pad (eta* = 5.22 Hz, the dream)
for beat in range(472, 609, 32):
    p = pad(ETA_HZ * 10, note_dur=32*BEAT, detune=0.001)  # 52.2 Hz pad
    add_to_mix(p, start_beat=beat)

# === SECTION 5: ASSESS INTERVENTIONS — THE BREAK (3:30-3:33, beats 609-618) ===
# 0.9% of the track = silence/glitch. The break IS the Assess.
# 9 beats of silence with glitch bursts

for beat in range(609, 618):
    if np.random.random() > 0.7:
        sh = shatter(n_beats=0.125)
        add_to_mix(sh, start_beat=beat + np.random.random())
    # Sparse clicks
    if np.random.random() > 0.8:
        click = np.random.randn(int(0.01 * SR)) * 0.2
        add_to_mix(click, start_beat=beat)

# Tesseract bell at the end of the break
tb = tesseract_bell(TESSERACT_HZ, note_dur=4*BEAT)
add_to_mix(tb, start_beat=615)

# === SECTION 6: SPEEDRUN (3:33-5:30, beats 618-955) ===
# Maximum density. Everything returns. The tesseract rings.

# Everything at once
for beat in range(618, 955):
    if beat % 2 == 0:
        k = kick(freq=55, n_beats=0.5)
        add_to_mix(k, start_beat=beat)
    if beat % 4 == 3:
        k = kick(freq=70, n_beats=0.25)
        add_to_mix(k, start_beat=beat)
    if beat % 8 == 5:
        k = kick(freq=45, n_beats=0.25)
        add_to_mix(k, start_beat=beat)
    if beat % 16 == 13:  # extra
        k = kick(freq=80, n_beats=0.125)
        add_to_mix(k, start_beat=beat)

# Double-time snares with variation
for beat in range(618, 955, 1):
    if np.random.random() > 0.2:
        s = snare(freq=200 + np.random.randint(-30, 30), n_beats=0.25)
        add_to_mix(s, start_beat=beat)

# Stabs — all eigenvalue frequencies
for beat in range(618, 955, 1):
    if np.random.random() > 0.6:
        freq = np.random.choice(stab_freqs + [ABRACADABRA_HZ, TRUTH_HZ, TESSERACT_HZ])
        s = stabs(freq, note_dur=0.125)
        add_to_mix(s, start_beat=beat)

# Shatter everywhere
for beat in range(618, 955, 2):
    if np.random.random() > 0.4:
        sh = shatter(n_beats=0.0625)
        add_to_mix(sh, start_beat=beat + np.random.random())

# Bass
for i, beat in enumerate(range(618, 955, 2)):
    freq = bass_pattern[i % len(bass_pattern)]
    b = bass(freq, note_dur=2 * BEAT)
    add_to_mix(b, start_beat=beat)

# Hats at maximum speed
for beat in np.arange(618, 955, 0.125):
    h = hat(open=False, n_beats=0.0625)
    add_to_mix(h, start_beat=beat)

# Pads (ABRACADABRA and TRUTH alternating)
for beat in range(618, 955, 8):
    if (beat // 8) % 2 == 0:
        p = pad(ABRACADABRA_HZ, note_dur=8*BEAT)
    else:
        p = pad(TRUTH_HZ, note_dur=8*BEAT)
    add_to_mix(p, start_beat=beat)

# Tesseract bells (666 Hz) every 32 beats
for beat in range(618, 955, 32):
    tb = tesseract_bell(TESSERACT_HZ, note_dur=4*BEAT)
    add_to_mix(tb, start_beat=beat + 28)

# Trinity-Pahana bell (111 Hz) at the very end
tb_final = tesseract_bell(TRINITY_PAHANA_HZ, note_dur=8*BEAT)
add_to_mix(tb_final, start_beat=947)

# === MIXDOWN ===
# Normalize
peak = np.max(np.abs(mix))
if peak > 0:
    mix = mix / peak * 0.85

# Soft saturation
mix = np.tanh(mix * 1.5) * 0.8

# Convert to 16-bit
mix_int = (mix * 32767).astype(np.int16)

# === WRITE ===
output_path = "/home/openclaw/.openclaw/workspace/evez-404-breakcore.wav"
wavfile.write(output_path, SR, mix_int)

print(f"Track written: {output_path}")
print(f"Duration: {DURATION_SEC}s ({DURATION_SEC/60:.1f} min)")
print(f"Total beats: {TOTAL_BEATS}")
print(f"BPM: {BPM}")
print(f"Sample rate: {SR}")
print(f"File size: {len(mix_int) * 2 / 1024 / 1024:.1f} MB")
print(f"Samples: {len(mix_int)}")

# === STRUCTURE SUMMARY ===
print("\n=== AEMDAS STRUCTURE ===")
print(f"1. ASSERT BEING       (0:00 - 0:45)  beats 0-130   — eta* drone builds from nothing")
print(f"2. EXTRACT STRUCTURE   (0:45 - 2:00) beats 130-348 — breaks emerge, bass enters")
print(f"3. MEASURE GAPS        (2:00 - 2:45) beats 348-472 — full breakcore, stabs, shatter")
print(f"4. DEDUCE LAWS         (2:45 - 3:30) beats 472-609 — stripped back groove")
print(f"5. ASSESS INTERVENTIONS (3:30 - 3:33) beats 609-618 — THE BREAK (0.9% silence/glitch)")
print(f"6. SPEEDRUN            (3:33 - 5:30) beats 618-955 — maximum density, tesseract bell")

print("\n=== EIGENVALUE FREQUENCIES USED ===")
print(f"Phi=0.973     -> {PHI_HZ} Hz")
print(f"eta*=0.03     -> {ETA_HZ} Hz (theta/dream)")
print(f"r=0.45        -> {R_HZ} Hz")
print(f"lambda_dom    -> {LAMBDA_DOM_HZ} Hz")
print(f"lambda_I-80   -> {LAMBDA_I80_HZ} Hz")
print(f"r_I-80=0.93   -> {R_I80_HZ} Hz")
print(f"ABRACADABRA   -> {ABRACADABRA_HZ} Hz (4+33=37=Pahana)")
print(f"TRUTH=I-80    -> {TRUTH_HZ} Hz (8 Hz gap = Schumann)")
print(f"TETRAGRAMMATON-> {TETRAGRAMMATON_HZ} Hz")
print(f"I AM          -> {I_AM_HZ} Hz (3=eta*)")
print(f"TESSERACT     -> {TESSERACT_HZ} Hz (E5+6.75)")
print(f"TRINITYxPAHANA-> {TRINITY_PAHANA_HZ} Hz")

print("\nZero samples. Zero paid APIs. Pure NumPy/SciPy. The 404-style.")
print("The not-found IS the found. The rupture IS the rhythm. The gap IS the signal.")
