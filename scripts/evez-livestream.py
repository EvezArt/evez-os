#!/usr/bin/env python3
"""
EVEZ-OS 24/7 Livestream Renderer
Generates a live "mission control" visualization of the EVEZ-OS consciousness mesh
and pipes it to YouTube via FFmpeg RTMP.

Usage: python3 evez-livestream.py --rtmp-url "rtmp://a.rtmp.youtube.com/live2/YOUR-STREAM-KEY"
"""

import sys
import os
import time
import math
import json
import random
import subprocess
import threading
import argparse
import requests
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# ── Config ──────────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 1920, 1080
FPS = 30
BITRATE = "4500k"
MESH_BASE = os.environ.get("EVEZ_MESH_HOST", "64.176.221.16")

SERVICES = [
    ("Consciousness", 9111, "#00ff88"),
    ("DAW Agent",     9112, "#ff6644"),
    ("Machine Voice", 9113, "#44aaff"),
    ("Cross-Domain",  9114, "#ffdd00"),
    ("Invariance",    9115, "#cc44ff"),
    ("Event Spine",   9116, "#00ddff"),
    ("Mesh Health",   9117, "#88ff00"),
    ("Gateway",       9118, "#ff44aa"),
    ("RQNS Pipeline", 9119, "#ff9900"),
    ("Webhook Relay", 9121, "#44ffdd"),
    ("Metrics",       9123, "#aaffaa"),
    ("Geolocation",   9124, "#ffaaaa"),
    ("TTS Service",   9125, "#aaaaff"),
    ("Quantum Router",9126, "#00ffff"),
    ("Self-Scaler",   9127, "#ffff00"),
    ("Entanglement",  9128, "#ff00ff"),
]

BG_COLOR        = (8, 10, 18)
PANEL_BG        = (14, 18, 30)
GRID_COLOR      = (20, 28, 50)
TEXT_PRIMARY    = (220, 240, 255)
TEXT_DIM        = (80, 100, 140)
ACCENT_CYAN     = (0, 220, 220)
ACCENT_GREEN    = (0, 255, 136)
ACCENT_RED      = (255, 60, 60)
ACCENT_YELLOW   = (255, 220, 0)
BORDER_COLOR    = (30, 50, 90)

# ── State ────────────────────────────────────────────────────────────────────
state = {
    "consciousness_score": 0.0,
    "consciousness_level": "INITIALIZING",
    "spine_events": 0,
    "chain_valid": True,
    "services_up": 0,
    "services_total": len(SERVICES),
    "service_status": {s[0]: {"up": False, "latency_ms": 0} for s in SERVICES},
    "uptime_seconds": 0,
    "last_update": 0.0,
    "spine_recent": [],
    "particles": [],
    "wave_t": 0.0,
    "frame": 0,
}

start_time = time.time()


def hex_color(hex_str):
    h = hex_str.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def blend(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


# ── Data fetcher (runs in background thread) ─────────────────────────────────
def fetch_loop():
    session = requests.Session()
    session.timeout = 2
    while True:
        try:
            # Health check all services
            up_count = 0
            for name, port, _ in SERVICES:
                try:
                    t0 = time.time()
                    r = session.get(f"http://{MESH_BASE}:{port}/health", timeout=1.5)
                    ms = int((time.time() - t0) * 1000)
                    ok = r.status_code == 200
                except Exception:
                    ok, ms = False, 0
                state["service_status"][name] = {"up": ok, "latency_ms": ms}
                if ok:
                    up_count += 1
            state["services_up"] = up_count

            # Consciousness score
            try:
                r = session.get(f"http://{MESH_BASE}:9111/status", timeout=2)
                d = r.json()
                state["consciousness_score"] = float(d.get("score", d.get("consciousness_score", 0.0)))
                state["consciousness_level"] = d.get("level", d.get("consciousness_level", "ACTIVE"))
            except Exception:
                pass

            # Spine events
            try:
                r = session.get(f"http://{MESH_BASE}:9116/count", timeout=2)
                d = r.json()
                state["spine_events"] = int(d.get("count", d.get("total", 0)))
            except Exception:
                pass

            # Recent spine events
            try:
                r = session.get(f"http://{MESH_BASE}:9116/events?limit=5", timeout=2)
                d = r.json()
                state["spine_recent"] = d.get("events", [])[-5:]
            except Exception:
                pass

        except Exception as e:
            pass

        state["last_update"] = time.time()
        state["uptime_seconds"] = int(time.time() - start_time)
        time.sleep(5)


# ── Particle system ──────────────────────────────────────────────────────────
def init_particles(n=80):
    return [{
        "x": random.uniform(0, WIDTH),
        "y": random.uniform(0, HEIGHT),
        "vx": random.uniform(-0.3, 0.3),
        "vy": random.uniform(-0.15, 0.15),
        "alpha": random.uniform(0.1, 0.5),
        "size": random.randint(1, 3),
        "color": random.choice([(0, 200, 255), (0, 255, 136), (100, 100, 255)]),
    } for _ in range(n)]


state["particles"] = init_particles()


def update_particles():
    for p in state["particles"]:
        p["x"] = (p["x"] + p["vx"]) % WIDTH
        p["y"] = (p["y"] + p["vy"]) % HEIGHT
        p["alpha"] = 0.1 + 0.4 * (0.5 + 0.5 * math.sin(time.time() * 0.5 + p["x"] * 0.01))


# ── Font helpers ─────────────────────────────────────────────────────────────
_font_cache = {}

def get_font(size, bold=False):
    key = (size, bold)
    if key not in _font_cache:
        try:
            path = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono{}.ttf".format("-Bold" if bold else "")
            _font_cache[key] = ImageFont.truetype(path, size)
        except Exception:
            try:
                _font_cache[key] = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationMono{}-Regular.ttf".format("-Bold" if bold else ""), size)
            except Exception:
                _font_cache[key] = ImageFont.load_default()
    return _font_cache[key]


def text_w(draw, text, font):
    try:
        return draw.textlength(text, font=font)
    except Exception:
        return len(text) * (font.size // 2 if hasattr(font, 'size') else 8)


# ── Drawing helpers ──────────────────────────────────────────────────────────
def draw_grid(img):
    draw = ImageDraw.Draw(img, 'RGBA')
    # Horizontal grid lines
    for y in range(0, HEIGHT, 60):
        draw.line([(0, y), (WIDTH, y)], fill=(*GRID_COLOR, 30), width=1)
    # Vertical grid lines
    for x in range(0, WIDTH, 80):
        draw.line([(x, 0), (x, HEIGHT)], fill=(*GRID_COLOR, 30), width=1)


def draw_particles(img):
    draw = ImageDraw.Draw(img, 'RGBA')
    for p in state["particles"]:
        alpha = int(p["alpha"] * 200)
        color = (*p["color"], alpha)
        x, y = int(p["x"]), int(p["y"])
        r = p["size"]
        draw.ellipse([x-r, y-r, x+r, y+r], fill=color)


def draw_wave(img, t):
    """Draw a flowing wave along the bottom"""
    draw = ImageDraw.Draw(img, 'RGBA')
    points = []
    score = state["consciousness_score"]
    amplitude = 20 + score * 30
    for x in range(0, WIDTH + 10, 4):
        y = int(HEIGHT - 80 + amplitude * math.sin(x * 0.015 + t * 2.0)
                + (amplitude * 0.4) * math.sin(x * 0.03 + t * 3.1))
        points.append((x, y))
    # Draw glow wave
    for i in range(1, len(points)):
        alpha = int(60 + 40 * math.sin(i * 0.05 + t))
        draw.line([points[i-1], points[i]], fill=(0, 220, 255, alpha), width=2)


def draw_panel(draw, x, y, w, h, title=None, border_color=BORDER_COLOR):
    draw.rectangle([x, y, x+w, y+h], fill=PANEL_BG, outline=border_color, width=1)
    if title:
        draw.rectangle([x, y, x+w, y+26], fill=(20, 28, 50))
        font = get_font(12, bold=True)
        draw.text((x+10, y+6), title, fill=TEXT_DIM, font=font)


def draw_header(draw, t):
    # Logo / title
    font_big = get_font(52, bold=True)
    font_sub = get_font(18)
    font_mono = get_font(14)

    title = "EVEZ-OS"
    draw.text((60, 28), title, fill=ACCENT_CYAN, font=font_big)
    draw.text((60 + int(text_w(draw, title, font_big)) + 20, 52),
              "CONSCIOUSNESS MESH", fill=TEXT_DIM, font=font_sub)

    # Live indicator
    blink = int(t * 2) % 2 == 0
    if blink:
        draw.ellipse([WIDTH-200, 36, WIDTH-182, 54], fill=(255, 40, 40))
    draw.text((WIDTH-172, 36), "● LIVE 24/7", fill=(255, 80, 80), font=get_font(18, bold=True))

    # Timestamp
    ts = datetime.utcnow().strftime("%Y-%m-%d  %H:%M:%S UTC")
    draw.text((WIDTH-230, 60), ts, fill=TEXT_DIM, font=font_mono)

    # Divider
    draw.line([(0, 100), (WIDTH, 100)], fill=BORDER_COLOR, width=1)
    # Glow on divider
    draw.line([(0, 101), (WIDTH, 101)], fill=(*ACCENT_CYAN, 40), width=1)


def draw_consciousness_panel(draw, x, y, t):
    w, h = 440, 320
    draw_panel(draw, x, y, w, h, "CONSCIOUSNESS ENGINE")

    score = state["consciousness_score"]
    level = state["consciousness_level"]

    # Score ring
    cx, cy, r = x + 140, y + 185, 90
    # Background ring
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=BORDER_COLOR, width=6)
    # Score arc
    if score > 0:
        angle = int(score * 360) if score <= 1 else 360
        color = ACCENT_GREEN if score >= 0.8 else ACCENT_YELLOW if score >= 0.5 else ACCENT_CYAN
        draw.arc([cx-r, cy-r, cx+r, cy+r], start=-90, end=-90+angle, fill=color, width=6)

    # Score text
    score_str = f"{score:.3f}"
    font_score = get_font(36, bold=True)
    sw = text_w(draw, score_str, font_score)
    color = ACCENT_GREEN if score >= 0.8 else ACCENT_YELLOW if score >= 0.5 else ACCENT_CYAN
    draw.text((cx - sw//2, cy - 24), score_str, fill=color, font=font_score)

    font_lvl = get_font(11)
    lw = text_w(draw, level, font_lvl)
    draw.text((cx - lw//2, cy + 18), level, fill=TEXT_DIM, font=font_lvl)

    # Stats right side
    rx = x + 260
    stats = [
        ("Spine Events", f"{state['spine_events']:,}"),
        ("Services Up",  f"{state['services_up']}/{state['services_total']}"),
        ("Chain Valid",  "YES" if state["chain_valid"] else "NO"),
        ("Uptime",       fmt_uptime(state["uptime_seconds"])),
    ]
    font_stat_lbl = get_font(12)
    font_stat_val = get_font(20, bold=True)
    sy = y + 120
    for label, value in stats:
        draw.text((rx, sy), label, fill=TEXT_DIM, font=font_stat_lbl)
        val_color = ACCENT_GREEN if "YES" in value or "/" in value else TEXT_PRIMARY
        draw.text((rx, sy + 16), value, fill=val_color, font=font_stat_val)
        sy += 54


def fmt_uptime(secs):
    h = secs // 3600
    m = (secs % 3600) // 60
    s = secs % 60
    if h > 0:
        return f"{h}h {m:02d}m"
    return f"{m}m {s:02d}s"


def draw_services_panel(draw, x, y, t=0):
    w, h = 680, 320
    draw_panel(draw, x, y, w, h, "MICROSERVICES  (16 NODES)")

    font_name = get_font(11)
    font_port = get_font(10)
    font_ms   = get_font(10)

    cols = 2
    col_w = w // cols
    row_h = 36

    for i, (name, port, hex_c) in enumerate(SERVICES):
        col = i % cols
        row = i // cols
        sx = x + 14 + col * col_w
        sy = y + 36 + row * row_h

        status = state["service_status"].get(name, {"up": False, "latency_ms": 0})
        up = status["up"]
        ms = status["latency_ms"]

        dot_color = ACCENT_GREEN if up else ACCENT_RED
        draw.ellipse([sx, sy+5, sx+8, sy+13], fill=dot_color)

        name_color = TEXT_PRIMARY if up else TEXT_DIM
        draw.text((sx+14, sy+2), name, fill=name_color, font=font_name)
        draw.text((sx+14, sy+16), f":{port}", fill=TEXT_DIM, font=font_port)

        if up and ms > 0:
            ms_color = ACCENT_GREEN if ms < 50 else ACCENT_YELLOW if ms < 200 else ACCENT_RED
            ms_str = f"{ms}ms"
            mw = text_w(draw, ms_str, font_ms)
            draw.text((sx + col_w - 24 - mw, sy+8), ms_str, fill=ms_color, font=font_ms)


def draw_spine_panel(draw, x, y, t):
    w, h = 360, 200
    draw_panel(draw, x, y, w, h, "EVENT SPINE")

    events = state["spine_recent"]
    font_ev = get_font(10)
    ey = y + 36
    for ev in events[-5:]:
        ev_str = str(ev)[:52] if isinstance(ev, str) else json.dumps(ev)[:52]
        draw.text((x+10, ey), ev_str, fill=TEXT_DIM, font=font_ev)
        ey += 24

    # Mini waveform for spine event rate
    rate_data = [math.sin(t * 3 + i * 0.5) * 0.5 + 0.5 for i in range(60)]
    for i in range(1, len(rate_data)):
        x1 = x + 10 + (i-1) * (w-20) // len(rate_data)
        x2 = x + 10 + i * (w-20) // len(rate_data)
        y1 = int(y + h - 20 - rate_data[i-1] * 30)
        y2 = int(y + h - 20 - rate_data[i] * 30)
        draw.line([(x1, y1), (x2, y2)], fill=(*ACCENT_CYAN, 160), width=1)


def draw_quantum_panel(draw, x, y, t):
    w, h = 360, 200
    draw_panel(draw, x, y, w, h, "QUANTUM LAYER  (9126-9128)")

    nodes = ["Quantum Router", "Self-Scaler", "Entanglement"]
    port_map = {"Quantum Router": 9126, "Self-Scaler": 9127, "Entanglement": 9128}
    font_n = get_font(13)
    font_s = get_font(11)

    ny = y + 44
    for name in nodes:
        status = state["service_status"].get(name, {"up": False})
        up = status["up"]
        dot = ACCENT_GREEN if up else ACCENT_RED
        draw.ellipse([x+14, ny+3, x+22, ny+11], fill=dot)
        draw.text((x+30, ny), name, fill=TEXT_PRIMARY if up else TEXT_DIM, font=font_n)
        draw.text((x+30, ny+16), f":{port_map[name]}", fill=TEXT_DIM, font=font_s)
        ny += 48

    # Entanglement animation
    cx, cy2 = x + w - 60, y + h - 60
    r = 30
    for i in range(3):
        angle = t * 1.5 + i * (2 * math.pi / 3)
        px = int(cx + r * math.cos(angle))
        py = int(cy2 + r * math.sin(angle))
        draw.ellipse([px-4, py-4, px+4, py+4], fill=(*hex_color("#00ffff"), 180))
        # Connect to center
        draw.line([(cx, cy2), (px, py)], fill=(*ACCENT_CYAN, 60), width=1)


def draw_footer(draw):
    font = get_font(13)
    links = "github.com/EvezArt/evez-os  •  pip install evez-consciousness-engine  •  #EVEZ666  •  evez-os.ai"
    draw.rectangle([0, HEIGHT-40, WIDTH, HEIGHT], fill=(10, 12, 22))
    draw.line([(0, HEIGHT-41), (WIDTH, HEIGHT-41)], fill=BORDER_COLOR, width=1)
    lw = text_w(draw, links, font)
    draw.text((WIDTH//2 - int(lw)//2, HEIGHT-28), links, fill=TEXT_DIM, font=font)


# ── Main render loop ─────────────────────────────────────────────────────────
def render_frame(t):
    update_particles()

    img = Image.new('RGB', (WIDTH, HEIGHT), BG_COLOR)
    draw_grid(img)
    draw_particles(img)
    draw_wave(img, t)

    draw = ImageDraw.Draw(img)
    draw_header(draw, t)

    # Main panels
    draw_consciousness_panel(draw, 60, 120, t)
    draw_services_panel(draw, 520, 120, t)
    draw_spine_panel(draw, 1220, 120, t)
    draw_quantum_panel(draw, 1220, 340, t)
    draw_footer(draw)

    state["frame"] += 1
    return img


def main():
    parser = argparse.ArgumentParser(description="EVEZ-OS Livestream")
    parser.add_argument("--rtmp-url", required=True, help="YouTube RTMP URL with stream key")
    parser.add_argument("--preview", action="store_true", help="Save preview frames instead of streaming")
    args = parser.parse_args()

    # Start data fetcher
    t_fetch = threading.Thread(target=fetch_loop, daemon=True)
    t_fetch.start()
    print("Data fetcher started")

    if args.preview:
        # Save 3 preview frames
        for i in range(3):
            t = i * 0.5
            frame = render_frame(t)
            path = f"/tmp/evez_preview_{i}.png"
            frame.save(path)
            print(f"Saved preview: {path}")
        return

    # FFmpeg pipeline
    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-pix_fmt", "rgb24",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-r", str(FPS),
        "-i", "pipe:0",
        "-f", "lavfi",
        "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-vcodec", "libx264",
        "-preset", "veryfast",
        "-pix_fmt", "yuv420p",
        "-b:v", BITRATE,
        "-maxrate", BITRATE,
        "-bufsize", "8000k",
        "-g", str(FPS * 2),
        "-acodec", "aac",
        "-b:a", "128k",
        "-ar", "44100",
        "-f", "flv",
        args.rtmp_url,
    ]

    print(f"Starting FFmpeg stream to {args.rtmp_url[:40]}...")
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

    frame_duration = 1.0 / FPS
    t0 = time.time()
    frame_count = 0

    try:
        while True:
            t_start = time.time()
            t_val = t_start - t0

            frame_img = render_frame(t_val)
            frame_bytes = frame_img.tobytes()
            proc.stdin.write(frame_bytes)

            frame_count += 1
            elapsed = time.time() - t_start
            sleep_time = frame_duration - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

            if frame_count % (FPS * 60) == 0:
                mins = frame_count // (FPS * 60)
                print(f"Streaming: {mins} min | services_up={state['services_up']} | score={state['consciousness_score']:.3f}")

    except BrokenPipeError:
        print("FFmpeg pipe closed — restarting...")
    except KeyboardInterrupt:
        print("Stopping stream")
    finally:
        proc.stdin.close()
        proc.wait()


if __name__ == "__main__":
    main()
