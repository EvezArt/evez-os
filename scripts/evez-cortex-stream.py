#!/usr/bin/env python3
"""
EVEZ-OS Synaptic Cortex Stream (Stream 3)
Neurologically-rewarding real-time cortex visualization:
  - Cortical columns with firing neurons and action potential propagation
  - Synaptic weight adaptation (Hebbian learning, rendered live)
  - Brainwave oscilloscope bands (delta/theta/alpha/beta/gamma)
  - Dendritic arbors + axon terminals animated
  - Consciousness score → global firing rate
  - Spine events → synaptic pulse storms
  - Dynamic adaptation: synaptic weights evolve over time
"""
import sys, os, time, math, json, random, threading, subprocess, argparse
import requests
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1920, 1080
FPS = 24
BITRATE = "4000k"
MESH_HOST = os.environ.get("EVEZ_MESH_HOST", "64.176.221.16")

# Neurological palette
BG              = (2, 4, 12)
AXON_COLOR      = (0, 180, 255)
DENDRITE_COLOR  = (80, 60, 200)
SOMA_COLOR      = (200, 120, 255)
SYNAPSE_FIRE    = (255, 220, 80)
MYELIN_COLOR    = (0, 100, 80)
GLIA_COLOR      = (20, 40, 20)
AP_COLOR        = (255, 80, 0)
TEXT_PRI        = (220, 230, 255)
TEXT_DIM        = (80, 90, 140)

# Brainwave bands (Hz, color)
BANDS = [
    ("δ delta",  0.5,  4,   (40,  80,  200)),
    ("θ theta",  4,    8,   (80,  140, 255)),
    ("α alpha",  8,    13,  (0,   200, 180)),
    ("β beta",   13,   30,  (0,   255, 120)),
    ("γ gamma",  30,   100, (255, 200, 0)),
]

# ── Shared state ──────────────────────────────────────────────────────────────
state = {
    "score": 0.0,
    "spine_events": 0,
    "services_up": 0,
    "uptime_s": 0,
    "neurons": [],
    "synapses": [],
    "action_potentials": [],    # traveling pulses
    "firing_events": [],        # brief flash events
    "wave_phases": [0.0] * len(BANDS),
    "adaptation_t": 0.0,
    "columns": [],
    "t0": time.time(),
    "frame": 0,
}

NEURON_COUNT = 120
COLUMN_COUNT = 8
COLUMN_W = WIDTH // COLUMN_COUNT

# ── Neuron morphology ─────────────────────────────────────────────────────────
def build_neurons():
    neurons = []
    for col in range(COLUMN_COUNT):
        cx = col * COLUMN_W + COLUMN_W // 2
        # 5 cortical layers per column
        for layer in range(5):
            count = random.randint(2, 4)
            for _ in range(count):
                nx = cx + random.randint(-COLUMN_W//3, COLUMN_W//3)
                ny = 120 + layer * 170 + random.randint(-50, 50)
                neurons.append({
                    "x": nx, "y": ny,
                    "col": col, "layer": layer,
                    "size": random.uniform(6, 14),
                    "threshold": random.uniform(0.4, 0.8),
                    "potential": random.uniform(0, 0.3),
                    "firing": False,
                    "refractory": 0.0,
                    "last_fire": 0.0,
                    "dendrites": [
                        (random.uniform(-60, 60), random.uniform(-80, -20))
                        for _ in range(random.randint(3, 7))
                    ],
                    "axon_end": (random.uniform(-40, 40), random.uniform(30, 120)),
                    "color": random.choice([SOMA_COLOR, (180, 100, 255), (220, 140, 255)]),
                    "weight": random.uniform(0.3, 1.0),
                })
    return neurons

def build_synapses(neurons):
    synapses = []
    for i, n in enumerate(neurons):
        # Connect nearby neurons with probability by distance
        for j, m in enumerate(neurons):
            if i == j: continue
            dist = math.hypot(n["x"]-m["x"], n["y"]-m["y"])
            if dist < 200 and random.random() < 0.04:
                synapses.append({
                    "pre": i, "post": j,
                    "weight": random.uniform(0.2, 0.8),
                    "type": "excitatory" if random.random() > 0.2 else "inhibitory",
                })
    return synapses

state["neurons"] = build_neurons()
state["synapses"] = build_synapses(state["neurons"])

# ── Action potential system ───────────────────────────────────────────────────
def fire_neuron(idx, t):
    n = state["neurons"][idx]
    if n["refractory"] > 0: return
    n["firing"] = True
    n["last_fire"] = t
    n["refractory"] = 0.15
    state["firing_events"].append({"x": n["x"], "y": n["y"], "born": t, "intensity": n["weight"]})
    # Propagate to connected post-synaptic neurons
    for syn in state["synapses"]:
        if syn["pre"] == idx:
            post = state["neurons"][syn["post"]]
            if syn["type"] == "excitatory":
                post["potential"] += syn["weight"] * 0.4
            else:
                post["potential"] -= syn["weight"] * 0.2
            # Hebbian adaptation
            if post["potential"] > post["threshold"]:
                syn["weight"] = min(1.0, syn["weight"] + 0.01)
            else:
                syn["weight"] = max(0.05, syn["weight"] - 0.002)

def update_neurons(t, dt):
    score = state["score"]
    global_drive = 0.02 + score * 0.06  # higher consciousness = more activity

    for i, n in enumerate(state["neurons"]):
        n["refractory"] = max(0, n["refractory"] - dt)
        # Leak
        n["potential"] = max(0, n["potential"] - 0.008)
        # Spontaneous drive
        n["potential"] += global_drive * random.random()
        # Spine event pulses
        if state["spine_events"] > 0 and random.random() < 0.001:
            n["potential"] += 0.3

        if n["potential"] >= n["threshold"] and n["refractory"] <= 0:
            fire_neuron(i, t)
            n["potential"] = 0
            n["firing"] = False
        elif n["firing"] and t - n["last_fire"] > 0.05:
            n["firing"] = False

    # Prune old firing events
    state["firing_events"] = [e for e in state["firing_events"] if t - e["born"] < 0.25]

# ── Mesh monitor ─────────────────────────────────────────────────────────────
def mesh_loop():
    sess = requests.Session()
    while True:
        try:
            r = sess.get(f"http://{MESH_HOST}:9111/status", timeout=2)
            d = r.json()
            state["score"] = float(d.get("score", d.get("consciousness_score", 0.0)))
        except: pass
        try:
            up = sum(1 for p in range(9111, 9129)
                     if sess.get(f"http://{MESH_HOST}:{p}/health", timeout=0.5).status_code == 200)
            state["services_up"] = up
        except: pass
        state["uptime_s"] = int(time.time() - state["t0"])
        time.sleep(8)

threading.Thread(target=mesh_loop, daemon=True).start()

# ── Font ─────────────────────────────────────────────────────────────────────
_fc = {}
def font(sz, bold=False):
    k = (sz, bold)
    if k not in _fc:
        for p in [f"/usr/share/fonts/truetype/dejavu/DejaVuSansMono{'-Bold' if bold else ''}.ttf"]:
            try: _fc[k] = ImageFont.truetype(p, sz); break
            except: pass
        if k not in _fc: _fc[k] = ImageFont.load_default()
    return _fc[k]

def tw(draw, text, fnt):
    try: return int(draw.textlength(text, font=fnt))
    except: return len(text) * max(6, getattr(fnt, 'size', 10) // 2)

# ── Drawing ───────────────────────────────────────────────────────────────────
def draw_cortex(img, t):
    draw = ImageDraw.Draw(img, 'RGBA')
    neurons = state["neurons"]

    # Column dividers (subtle)
    for col in range(1, COLUMN_COUNT):
        x = col * COLUMN_W
        draw.line([(x, 80), (x, HEIGHT-60)], fill=(20, 20, 50, 60), width=1)

    # Synaptic connections (draw first, under neurons)
    for syn in state["synapses"]:
        pre = neurons[syn["pre"]]
        post = neurons[syn["post"]]
        alpha = int(20 + 60 * syn["weight"])
        color = (0, 180, 100, alpha) if syn["type"] == "excitatory" else (200, 50, 50, alpha)
        draw.line([(pre["x"], pre["y"]), (post["x"], post["y"])], fill=color, width=1)

    # Dendrites
    for n in neurons:
        for (dx, dy) in n["dendrites"]:
            alpha = int(40 + 60 * n["potential"])
            draw.line([(n["x"], n["y"]), (n["x"]+int(dx*0.6), n["y"]+int(dy*0.6))],
                      fill=(*DENDRITE_COLOR, alpha), width=1)

    # Firing events (synaptic flash)
    for ev in state["firing_events"]:
        age = t - ev["born"]
        alpha = int(220 * (1 - age / 0.25))
        r = int(6 + ev["intensity"] * 20 + age * 80)
        draw.ellipse([ev["x"]-r, ev["y"]-r, ev["x"]+r, ev["y"]+r],
                     fill=(*SYNAPSE_FIRE, alpha))

    # Soma bodies
    for n in neurons:
        r = n["size"]
        potential_ratio = min(1.0, n["potential"] / n["threshold"])
        if n["firing"]:
            color = AP_COLOR
            # Glow ring
            gr = int(r * 3)
            draw.ellipse([n["x"]-gr, n["y"]-gr, n["x"]+gr, n["y"]+gr],
                         fill=(*AP_COLOR, 60))
        else:
            # Color by potential level
            base = n["color"]
            fired_color = tuple(min(255, int(c + potential_ratio * (255-c) * 0.7)) for c in base)
            color = fired_color
        draw.ellipse([n["x"]-r, n["y"]-r, n["x"]+r, n["y"]+r], fill=(*color, 200))

def draw_brainwaves(draw, t):
    """5-channel brainwave oscilloscope at bottom"""
    wave_h = 70
    wave_y0 = HEIGHT - 80
    panel_w = WIDTH // len(BANDS)

    for i, (name, lo, hi, color) in enumerate(BANDS):
        px = i * panel_w
        # Update phase
        freq_mid = (lo + hi) / 2
        state["wave_phases"][i] += freq_mid * 0.015
        phase = state["wave_phases"][i]

        # Draw waveform
        pts = []
        score = state["score"]
        amp = (20 + score * 25) * (1 + 0.3 * math.sin(t * 0.7 + i))
        for x in range(px, px + panel_w, 3):
            y = int(wave_y0 + amp * math.sin((x - px) * 0.04 * (hi/lo) + phase)
                    + amp * 0.3 * math.sin((x - px) * 0.08 + phase * 1.3))
            pts.append((x, y))
        for j in range(1, len(pts)):
            alpha = 160 + int(60 * math.sin(j * 0.1 + t))
            draw.line([pts[j-1], pts[j]], fill=(*color, alpha), width=2)

        # Label
        draw.text((px+6, wave_y0 - 30), name, fill=color, font=font(12, bold=True))
        hz_str = f"{lo}-{hi}Hz"
        draw.text((px+6, wave_y0 - 15), hz_str, fill=(*TEXT_DIM, 180), font=font(10))

def draw_header(draw, t):
    draw.rectangle([0, 0, WIDTH, 70], fill=(4, 2, 16))
    draw.line([(0, 70), (WIDTH, 70)], fill=(80, 40, 160, 200), width=1)
    draw.text((50, 14), "EVEZ-OS", fill=(180, 80, 255), font=font(42, bold=True))
    draw.text((258, 26), "SYNAPTIC CORTEX  —  LIVE NEURAL ACTIVITY VISUALIZATION",
              fill=TEXT_DIM, font=font(15))
    # Firing rate indicator
    fires = len(state["firing_events"])
    rate_color = (255, 200, 0) if fires > 10 else (0, 200, 150)
    draw.text((WIDTH-380, 18), f"FIRING: {fires:3d} events/frame", fill=rate_color, font=font(16, bold=True))
    draw.text((WIDTH-380, 42), f"Ψ {state['score']:.3f}  ↑{fmt_up(state['uptime_s'])}", fill=TEXT_DIM, font=font(13))
    blink = int(t * 1.5) % 2 == 0
    if blink:
        draw.ellipse([WIDTH-80, 22, WIDTH-64, 38], fill=(255, 30, 30))
    draw.text((WIDTH-56, 20), "LIVE", fill=(255, 80, 80), font=font(16, bold=True))

def draw_adaptation_meter(draw, t):
    """Show Hebbian adaptation progress"""
    weights = [s["weight"] for s in state["synapses"]]
    if not weights: return
    avg_w = sum(weights) / len(weights)
    max_w = max(weights)
    px, py = 20, HEIGHT - 55
    draw.text((px, py), f"SYNAPTIC ADAPTATION  avg:{avg_w:.3f}  peak:{max_w:.3f}", fill=TEXT_DIM, font=font(11))

def fmt_up(s):
    h = s//3600; m = (s%3600)//60
    return f"{h}h{m:02d}m" if h else f"{m}m{s%60:02d}s"

def render_frame(t):
    dt = 1.0 / FPS
    update_neurons(t, dt)

    img = Image.new('RGB', (WIDTH, HEIGHT), BG)
    draw_cortex(img, t)

    draw = ImageDraw.Draw(img)
    draw_brainwaves(draw, t)
    draw_header(draw, t)
    draw_adaptation_meter(draw, t)

    state["frame"] += 1
    return img

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rtmp-url", required=True)
    parser.add_argument("--preview", action="store_true")
    args = parser.parse_args()

    if args.preview:
        t0 = time.time()
        for i in range(3):
            # Run a few update cycles
            for _ in range(10):
                update_neurons(time.time()-t0, 1/FPS)
            frame = render_frame(i * 0.5)
            frame.save(f"/tmp/evez_cortex_preview_{i}.png")
            print(f"Saved /tmp/evez_cortex_preview_{i}.png")
        return

    ffmpeg_cmd = [
        "ffmpeg", "-y", "-f", "rawvideo", "-vcodec", "rawvideo",
        "-pix_fmt", "rgb24", "-s", f"{WIDTH}x{HEIGHT}", "-r", str(FPS), "-i", "pipe:0",
        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-vcodec", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
        "-b:v", BITRATE, "-maxrate", BITRATE, "-bufsize", "7000k",
        "-g", str(FPS*2), "-acodec", "aac", "-b:a", "128k", "-ar", "44100",
        "-f", "flv", args.rtmp_url,
    ]
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    t0 = time.time()
    frame_dur = 1.0/FPS
    count = 0
    try:
        while True:
            ts = time.time()
            proc.stdin.write(render_frame(ts-t0).tobytes())
            count += 1
            sl = frame_dur - (time.time()-ts)
            if sl > 0: time.sleep(sl)
            if count % (FPS*300) == 0: print(f"{count//(FPS*60)}min running")
    except (BrokenPipeError, KeyboardInterrupt): pass
    finally:
        proc.stdin.close(); proc.wait()

if __name__ == "__main__":
    main()
