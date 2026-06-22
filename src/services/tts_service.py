#!/usr/bin/env python3
"""EVEZ-OS TTS Pipeline — Free/open-source text-to-speech on port 9125.

Uses the machine_voice 5-stage pipeline for robotic speech synthesis.
No external API keys required — all synthesis is pure math.
"""

import json
import math
import time
import struct
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

SPINE_URL = "http://localhost:9116/append"
VOICE_URL = "http://localhost:9113"

SR = 44100

def spine_log(domain, action, data):
    try:
        requests.post(SPINE_URL, json={"domain": domain, "action": action, "data": data, "timestamp": time.time()}, timeout=2)
    except Exception:
        pass

# ── Audio Helpers ────────────────────────────────────────────────────

def _normalize(samples):
    mx = max(abs(s) for s in samples) or 1.0
    return [s / mx for s in samples]

def samples_to_wav_bytes(samples, sr=SR):
    buf = bytearray()
    data_size = len(samples) * 2
    buf += b'RIFF'
    buf += struct.pack('<I', 36 + data_size)
    buf += b'WAVE'
    buf += b'fmt '
    buf += struct.pack('<IHHIIHH', 16, 1, 1, sr, sr * 2, 2, 16)
    buf += b'data'
    buf += struct.pack('<I', data_size)
    for s in samples:
        val = max(-32768, min(32767, int(s * 32767)))
        buf += struct.pack('<h', val)
    return bytes(buf)

# ── Text-to-Speech Engine (Pure Math) ──────────────────────────────

# Phoneme-to-formant mapping for English-like speech synthesis
PHONEMES = {
    # Vowels: (f1, f2, f3, duration_factor)
    "ah": (700, 1200, 2500, 1.0),
    "ee": (270, 2300, 3000, 0.8),
    "ih": (400, 2000, 2800, 0.7),
    "oh": (500, 800, 2500, 1.0),
    "oo": (300, 700, 2200, 0.9),
    "uh": (600, 1200, 2400, 0.7),
    "ae": (600, 1700, 2500, 0.8),
    "eh": (500, 1800, 2600, 0.8),
    # Consonants: (noise_freq, duration_factor) — simplified
    "s":  (6000, 0.15),
    "sh": (3000, 0.15),
    "t":  (4000, 0.08),
    "k":  (1500, 0.08),
    "p":  (500,  0.06),
    "b":  (200,  0.08),
    "d":  (3000, 0.08),
    "g":  (1000, 0.08),
    "m":  (200,  0.12),
    "n":  (1500, 0.10),
    "r":  (400,  0.12),
    "l":  (500,  0.10),
}

# Simple word-to-phoneme mapping
WORD_PHONEMES = {
    "service": ["s", "uh", "r", "v", "ih", "s"],
    "down": ["d", "ah", "oo", "n"],
    "up": ["uh", "p"],
    "heal": ["h", "ee", "l"],
    "healed": ["h", "ee", "l", "d"],
    "mesh": ["m", "eh", "sh"],
    "alert": ["uh", "l", "uh", "r", "t"],
    "critical": ["k", "r", "ih", "t", "ih", "k", "uh", "l"],
    "warning": ["w", "oo", "r", "n", "ih", "ng"],
    "death": ["d", "eh", "th"],
    "alive": ["uh", "l", "ah", "v"],
    "system": ["s", "ih", "s", "t", "uh", "m"],
    "emergence": ["ih", "m", "uh", "r", "j", "uh", "n", "s"],
    "failed": ["f", "eh", "l", "d"],
    "restarted": ["r", "ee", "s", "t", "ah", "r", "t", "ih", "d"],
    "offline": ["oh", "f", "l", "ah", "y", "n"],
    "online": ["oh", "n", "l", "ah", "y", "n"],
    "error": ["eh", "r", "uh"],
    "ok": ["oh", "k", "eh"],
    "unknown": ["uh", "n", "n", "oh", "n"],
}

def text_to_phonemes(text):
    """Convert text to a list of phoneme symbols."""
    words = text.lower().replace(",", "").replace(".", "").split()
    phonemes = []
    for word in words:
        if word in WORD_PHONEMES:
            phonemes.extend(WORD_PHONEMES[word])
        else:
            # Fallback: use vowel-like sounds for unknown words
            for ch in word:
                if ch in "aeiou":
                    vowel_map = {"a": "ah", "e": "eh", "i": "ih", "o": "oh", "u": "uh"}
                    phonemes.append(vowel_map.get(ch, "uh"))
                elif ch in "sScC":
                    phonemes.append("s")
                elif ch in "tT":
                    phonemes.append("t")
                elif ch in "kK":
                    phonemes.append("k")
                elif ch in "pP":
                    phonemes.append("p")
                elif ch in "bB":
                    phonemes.append("b")
                elif ch in "dD":
                    phonemes.append("d")
                elif ch in "mM":
                    phonemes.append("m")
                elif ch in "nN":
                    phonemes.append("n")
                elif ch in "rR":
                    phonemes.append("r")
                elif ch in "lL":
                    phonemes.append("l")
    return phonemes if phonemes else ["ah"]

def synthesize_phoneme(phoneme, sr=SR):
    """Synthesize a single phoneme as audio samples."""
    n = int(sr * 0.08)  # base duration
    info = PHONEMES.get(phoneme, (500, 1500, 2500, 0.7))

    if phoneme in ("s", "sh", "t", "k", "p"):
        # Consonant: noise burst
        noise_freq = info[0]
        dur_factor = info[1]
        n = int(sr * 0.05 * dur_factor) or int(sr * 0.03)
        import random
        samples = [0.0] * n
        for i in range(n):
            t = i / sr
            noise = random.gauss(0, 1)
            # Filter noise around consonant frequency
            samples[i] = noise * math.exp(-t * 30) * 0.3
            if phoneme in ("s", "sh"):
                samples[i] += 0.2 * math.sin(2 * math.pi * noise_freq * t) * math.exp(-t * 20)
        return samples
    else:
        # Vowel: formant synthesis
        f1, f2, f3, dur_factor = info
        n = int(sr * 0.08 * dur_factor)
        f0 = 120  # fundamental
        samples = [0.0] * n
        for i in range(n):
            t = i / sr
            # Glottal source
            phase = (f0 * t) % 1.0
            pulse = 2.0 * phase - 1.0
            # Formant filtering
            vowel = 0.3 * math.sin(2 * math.pi * f1 * t) + \
                    0.2 * math.sin(2 * math.pi * f2 * t) + \
                    0.1 * math.sin(2 * math.pi * f3 * t)
            # Envelope: smooth attack and release
            env = min(1.0, i / (sr * 0.005)) * min(1.0, (n - i) / (sr * 0.005))
            samples[i] = (0.4 * pulse + 0.6 * vowel) * env * 0.5
        return samples

def synthesize_speech(text, sr=SR):
    """Full TTS: text → phonemes → audio → machine voice pipeline."""
    phonemes = text_to_phonemes(text)

    # Synthesize each phoneme
    all_samples = []
    for ph in phonemes:
        chunk = synthesize_phoneme(ph, sr)
        # Add tiny gap between phonemes
        all_samples.extend(chunk)
        all_samples.extend([0.0] * int(sr * 0.005))

    if not all_samples:
        all_samples = [0.0] * int(sr * 0.1)

    # Apply 5-stage machine voice pipeline
    audio = _normalize(all_samples)

    # Stage 2: Bit-translation (8-bit for robotic character)
    bit_depth = 8
    levels = 2 ** bit_depth
    step = 2.0 / levels
    audio = [max(-1.0, min(1.0, round(s / step) * step)) for s in audio]

    # Stage 3: Ring modulation (subtle)
    ring_freq = 25
    audio = [s * math.sin(2 * math.pi * ring_freq * i / sr) for i, s in enumerate(audio)]

    # Stage 4: Formant shift (slight down for authority)
    shift = -3
    if shift != 0:
        ratio = 2.0 ** (shift / 12.0)
        n = len(audio)
        new_len = int(n / ratio)
        shifted = [0.0] * new_len
        for i in range(new_len):
            src = i * ratio
            idx = int(src)
            frac = src - idx
            if idx + 1 < n:
                shifted[i] = audio[idx] * (1 - frac) + audio[idx + 1] * frac
            elif idx < n:
                shifted[i] = audio[idx]
        while len(shifted) < n:
            shifted.append(0.0)
        audio = shifted[:n]

    # Stage 5: Mechanical resonance
    for i in range(len(audio)):
        t = i / sr
        audio[i] = audio[i] * 0.75 + 0.25 * math.sin(2 * math.pi * 150 * t) * math.sin(2 * math.pi * 3.5 * t)

    audio = _normalize(audio)
    return audio

# ── Alert Voice Generator ──────────────────────────────────────────

def generate_alert_voice(event):
    """Generate alert voice for mesh events. Delegates to machine_voice /alert."""
    event_type = event.get("event_type", "unknown")
    severity = event.get("severity", "info")
    service = event.get("service", "unknown")
    message = event.get("message", "")

    # Try the machine_voice service first
    try:
        r = requests.post(
            f"{VOICE_URL}/alert",
            json=event,
            timeout=5,
        )
        if r.status_code == 200:
            return r.content  # WAV bytes from machine_voice
    except Exception:
        pass

    # Fallback: synthesize locally
    if event_type in ("service_down", "mesh_degraded") or severity == "critical":
        alert_text = f"alert. {service} {event_type}. {message}".strip()
    elif event_type in ("heal", "service_up"):
        alert_text = f"{service} restored. {message}".strip()
    else:
        alert_text = f"mesh update. {message}".strip()

    audio = synthesize_speech(alert_text)
    return samples_to_wav_bytes(audio)

# ── HTTP Handler ─────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):
    def _json(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _wav(self, wav_bytes):
        self.send_response(200)
        self.send_header("Content-Type", "audio/wav")
        self.send_header("Content-Length", str(len(wav_bytes)))
        self.end_headers()
        self.wfile.write(wav_bytes)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length:
            return json.loads(self.rfile.read(length))
        return {}

    def do_GET(self):
        if self.path == "/health":
            self._json(200, {"status": "alive", "service": "tts_service", "port": 9125, "pipeline": "5-stage-machine-voice"})

    def do_POST(self):
        if self.path == "/health":
            self._json(200, {"status": "alive", "service": "tts_service", "port": 9125})
            return

        body = self._read_body()

        if self.path == "/speak":
            text = body.get("text", "")
            if not text:
                self._json(400, {"error": "provide 'text' field"})
                return
            audio = synthesize_speech(text)
            wav = samples_to_wav_bytes(audio)
            spine_log("tts", "speak", {"text": text[:100], "audio_bytes": len(wav)})
            self._wav(wav)
        elif self.path == "/alert":
            # Mesh alert with voice — delegates to machine_voice pipeline
            wav_bytes = generate_alert_voice(body)
            if isinstance(wav_bytes, bytes):
                self._wav(wav_bytes)
            else:
                # Shouldn't happen, but handle gracefully
                self._wav(samples_to_wav_bytes(wav_bytes))
            spine_log("tts", "alert", {"event_type": body.get("event_type", "unknown")})
        else:
            self._json(404, {"error": "not found"})

    def log_message(self, *a):
        pass

if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 9125), Handler)
    print("🔊 TTS Pipeline running on :9125 — 5-stage machine voice, no keys needed")
    server.serve_forever()
