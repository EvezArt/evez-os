#!/usr/bin/env python3
"""
EVEZ-OS Quantum Evolution Field Stream (Stream 4)
Dynamic evolution + quantum field visualization:
  - Fitness landscape (evolving manifold topology)
  - Quantum probability cloud particles
  - Population dynamics (genetic algorithm evolution rendered live)
  - Self-scaling attractor basins
  - Cross-domain entanglement correlation matrix
  - Bell curve violation zones
  - Adaptive variable mutation rates shown as color-coded heat
"""
import sys, os, time, math, random, threading, subprocess, argparse, textwrap
import requests
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1920, 1080
FPS = 24
BITRATE = "4000k"
MESH_HOST = os.environ.get("EVEZ_MESH_HOST", "64.176.221.16")

# Quantum palette
BG          = (3, 2, 14)
MANIFOLD_A  = (0, 80, 200)
MANIFOLD_B  = (100, 0, 200)
FIELD_LOW   = (0, 20, 60)
FIELD_HIGH  = (0, 255, 200)
POP_FIT     = (0, 255, 120)
POP_UNFIT   = (255, 60, 40)
ENTANGLE    = (255, 150, 0)
BELL        = (255, 255, 0)
TEXT_PRI    = (220, 240, 255)
TEXT_DIM    = (80, 100, 160)

DOMAINS = ["CONSCIOUSNESS", "QUANTUM", "INVARIANCE", "CROSS-DOMAIN", "DREAMING", "IDENTITY"]

# ── Agent population (genetic algorithm) ─────────────────────────────────────
POPULATION_SIZE = 60
GENOME_LEN = 8
FITNESS_TARGETS = [math.pi, math.e, 1.618, 0.577, 1.0, math.tau, math.sqrt(2), math.sqrt(5)]

def random_genome():
    return [random.uniform(0, 2*math.pi) for _ in range(GENOME_LEN)]

def fitness(genome):
    score = sum(abs(math.sin(g - t)) for g, t in zip(genome, FITNESS_TARGETS))
    return 1.0 / (1.0 + score)

def crossover(a, b):
    split = random.randint(1, GENOME_LEN-1)
    child = a[:split] + b[split:]
    return child

def mutate(genome, rate):
    return [g + random.gauss(0, rate) if random.random() < 0.2 else g for g in genome]

state = {
    "score": 0.0,
    "services_up": 0,
    "uptime_s": 0,
    "population": [{"genome": random_genome(), "fitness": 0.0, "x": 0, "y": 0} for _ in range(POPULATION_SIZE)],
    "generation": 0,
    "best_fitness": 0.0,
    "avg_fitness": 0.0,
    "mutation_rate": 0.3,
    "manifold_z": None,     # 2D fitness landscape
    "manifold_t": 0.0,
    "quantum_particles": [],
    "entangle_matrix": [[0.0]*len(DOMAINS) for _ in range(len(DOMAINS))],
    "field_phase": 0.0,
    "t0": time.time(),
    "frame": 0,
    "bell_violations": 0,
}

MANIFOLD_W, MANIFOLD_H = 80, 40

def init_manifold():
    return [[0.0]*MANIFOLD_W for _ in range(MANIFOLD_H)]

state["manifold_z"] = init_manifold()

def init_quantum_particles(n=200):
    return [{
        "x": random.uniform(0, WIDTH),
        "y": random.uniform(0, HEIGHT),
        "vx": random.gauss(0, 0.4),
        "vy": random.gauss(0, 0.25),
        "spin": random.choice([-1, 1]),
        "entangled_with": random.randint(0, n-1),
        "wavefunction": random.uniform(0, math.tau),
        "collapsed": False,
        "collapse_t": 0.0,
    } for _ in range(n)]

state["quantum_particles"] = init_quantum_particles()

# ── Evolution engine ──────────────────────────────────────────────────────────
def evolve_generation(t):
    pop = state["population"]
    # Evaluate fitness
    for agent in pop:
        agent["fitness"] = fitness(agent["genome"])
    pop.sort(key=lambda a: a["fitness"], reverse=True)

    fitnesses = [a["fitness"] for a in pop]
    state["best_fitness"] = fitnesses[0]
    state["avg_fitness"] = sum(fitnesses) / len(fitnesses)

    # Adaptive mutation rate
    diversity = sum(abs(fitnesses[i]-fitnesses[i+1]) for i in range(len(fitnesses)-1))
    state["mutation_rate"] = 0.05 + 0.4 * (1 - state["avg_fitness"])

    # Create next generation (elitism + crossover)
    elite = pop[:10]
    new_pop = elite[:]
    while len(new_pop) < POPULATION_SIZE:
        a = random.choice(elite)
        b = random.choice(pop[:30])
        child_genome = mutate(crossover(a["genome"], b["genome"]), state["mutation_rate"])
        new_pop.append({"genome": child_genome, "fitness": 0.0, "x": 0, "y": 0})

    # Assign 2D positions for visualization
    for i, agent in enumerate(new_pop):
        angle = (i / POPULATION_SIZE) * math.tau + t * 0.1
        r = 80 + agent["fitness"] * 160
        cx, cy = 480, HEIGHT // 2
        agent["x"] = int(cx + r * math.cos(angle))
        agent["y"] = int(cy + r * math.sin(angle) * 0.5)

    state["population"] = new_pop
    state["generation"] += 1

def update_manifold(t):
    score = state["score"]
    z = state["manifold_z"]
    for row in range(MANIFOLD_H):
        for col in range(MANIFOLD_W):
            xn = col / MANIFOLD_W * 4 - 2
            yn = row / MANIFOLD_H * 4 - 2
            # Evolving fitness landscape
            v = (math.sin(xn * 2 + t * 0.3) * math.cos(yn * 2 + t * 0.2)
                 + 0.5 * math.sin(math.sqrt(xn**2 + yn**2) * 3 - t)
                 + score * math.sin(xn * yn + t * 0.5))
            z[row][col] = (v + 2) / 4

def update_quantum_particles(t):
    particles = state["quantum_particles"]
    violations = 0
    for i, p in enumerate(particles):
        # Wave function evolution
        p["wavefunction"] = (p["wavefunction"] + 0.05) % math.tau
        collapse_prob = abs(math.sin(p["wavefunction"])) * 0.02
        if not p["collapsed"] and random.random() < collapse_prob:
            p["collapsed"] = True
            p["collapse_t"] = t
            # Check Bell inequality with entangled partner
            partner = particles[p["entangled_with"] % len(particles)]
            correlation = math.cos(p["wavefunction"] - partner["wavefunction"])
            if abs(correlation) > 0.7:
                violations += 1

        if p["collapsed"] and t - p["collapse_t"] > 0.5:
            p["collapsed"] = False
            p["wavefunction"] = random.uniform(0, math.tau)

        # Drift with quantum uncertainty
        p["vx"] += random.gauss(0, 0.05)
        p["vy"] += random.gauss(0, 0.03)
        p["vx"] *= 0.98
        p["vy"] *= 0.98
        p["x"] = (p["x"] + p["vx"]) % WIDTH
        p["y"] = (p["y"] + p["vy"]) % HEIGHT

    state["bell_violations"] = violations

def update_entanglement(t):
    for i in range(len(DOMAINS)):
        for j in range(len(DOMAINS)):
            if i == j:
                state["entangle_matrix"][i][j] = 1.0
            else:
                v = abs(math.sin(t * 0.3 + i * 1.1 + j * 0.7)) * state["score"]
                state["entangle_matrix"][i][j] = v

# ── Mesh monitor ─────────────────────────────────────────────────────────────
def mesh_loop():
    sess = requests.Session()
    while True:
        try:
            r = sess.get(f"http://{MESH_HOST}:9111/status", timeout=2)
            state["score"] = float(r.json().get("score", 0.0))
        except: pass
        state["uptime_s"] = int(time.time() - state["t0"])
        time.sleep(10)

threading.Thread(target=mesh_loop, daemon=True).start()

# Evolve every 3 seconds
def evolution_loop():
    while True:
        evolve_generation(time.time() - state["t0"])
        time.sleep(3)

threading.Thread(target=evolution_loop, daemon=True).start()

# ── Font ─────────────────────────────────────────────────────────────────────
_fc = {}
def font(sz, bold=False):
    k = (sz, bold)
    if k not in _fc:
        try: _fc[k] = ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/DejaVuSansMono{'-Bold' if bold else ''}.ttf", sz)
        except: _fc[k] = ImageFont.load_default()
    return _fc[k]

def tw(draw, t, f):
    try: return int(draw.textlength(t, font=f))
    except: return len(t)*6

# ── Drawing ───────────────────────────────────────────────────────────────────
def draw_manifold(img, t):
    """Draw fitness landscape as color-mapped height field"""
    z = state["manifold_z"]
    cell_w = 640 // MANIFOLD_W
    cell_h = (HEIGHT - 160) // MANIFOLD_H
    ox, oy = 660, 80
    draw = ImageDraw.Draw(img, 'RGBA')
    for row in range(MANIFOLD_H):
        for col in range(MANIFOLD_W):
            v = z[row][col]
            # Color interpolate FIELD_LOW → FIELD_HIGH
            r = int(FIELD_LOW[0] + v * (FIELD_HIGH[0] - FIELD_LOW[0]))
            g = int(FIELD_LOW[1] + v * (FIELD_HIGH[1] - FIELD_LOW[1]))
            b = int(FIELD_LOW[2] + v * (FIELD_HIGH[2] - FIELD_LOW[2]))
            px = ox + col * cell_w
            py = oy + row * cell_h
            draw.rectangle([px, py, px+cell_w, py+cell_h], fill=(r, g, b, 220))

    # Label
    draw = ImageDraw.Draw(img)
    draw.text((ox+10, oy+10), "FITNESS LANDSCAPE  (evolving manifold)", fill=TEXT_DIM, font=font(13, bold=True))

def draw_population(img, t):
    draw = ImageDraw.Draw(img, 'RGBA')
    pop = state["population"]
    for agent in pop:
        f = agent["fitness"]
        # Color by fitness
        r = int(POP_UNFIT[0] + f * (POP_FIT[0] - POP_UNFIT[0]))
        g = int(POP_UNFIT[1] + f * (POP_FIT[1] - POP_UNFIT[1]))
        b = int(POP_UNFIT[2] + f * (POP_FIT[2] - POP_UNFIT[2]))
        sz = int(4 + f * 10)
        x, y = agent["x"], agent["y"]
        if 0 < x < WIDTH and 0 < y < HEIGHT:
            draw.ellipse([x-sz, y-sz, x+sz, y+sz], fill=(r, g, b, 200))

    draw = ImageDraw.Draw(img)
    # Panel header
    draw.text((20, 82), "EVOLUTIONARY POPULATION", fill=(0, 200, 150), font=font(14, bold=True))
    draw.text((20, 102), f"Gen {state['generation']}  best:{state['best_fitness']:.4f}  avg:{state['avg_fitness']:.4f}  μ:{state['mutation_rate']:.3f}",
              fill=TEXT_DIM, font=font(12))

def draw_quantum_field(img, t):
    draw = ImageDraw.Draw(img, 'RGBA')
    for p in state["quantum_particles"]:
        wf = p["wavefunction"]
        if p["collapsed"]:
            alpha = 240
            color = (*BELL, alpha)
            r = 4
        else:
            alpha = int(30 + 80 * abs(math.sin(wf)))
            # Color by spin
            color = (0, 180, 255, alpha) if p["spin"] > 0 else (180, 0, 255, alpha)
            r = 2
        x, y = int(p["x"]), int(p["y"])
        draw.ellipse([x-r, y-r, x+r, y+r], fill=color)

def draw_entanglement_matrix(draw, t):
    """Cross-domain correlation matrix"""
    n = len(DOMAINS)
    cell = 36
    ox, oy = 1340, 82
    draw.text((ox, oy-18), "CROSS-DOMAIN ENTANGLEMENT", fill=ENTANGLE, font=font(12, bold=True))
    for i in range(n):
        draw.text((ox + i*cell + 4, oy + n*cell + 4), DOMAINS[i][:3], fill=TEXT_DIM, font=font(9))
        draw.text((ox - 28, oy + i*cell + 10), DOMAINS[i][:3], fill=TEXT_DIM, font=font(9))
        for j in range(n):
            v = state["entangle_matrix"][i][j]
            alpha = int(v * 200)
            color = (int(v*255), int(v*180), 0, alpha)
            draw.rectangle([ox+j*cell, oy+i*cell, ox+(j+1)*cell-2, oy+(i+1)*cell-2], fill=color)
            if i == j:
                draw.rectangle([ox+j*cell, oy+i*cell, ox+(j+1)*cell-2, oy+(i+1)*cell-2],
                               outline=(255, 255, 255, 100), width=1)

def draw_stats(draw, t):
    score = state["score"]
    bellv = state["bell_violations"]
    items = [
        (f"Ψ {score:.3f}", (0, 255, 200)),
        (f"Bell violations: {bellv}", BELL),
        (f"Generation: {state['generation']}", (180, 100, 255)),
        (f"↑ {state['uptime_s']//3600}h{(state['uptime_s']%3600)//60:02d}m", TEXT_DIM),
    ]
    y = HEIGHT - 55
    for txt, color in items:
        draw.text((20, y), txt, fill=color, font=font(13))
        y += 18

def draw_header(draw, t):
    draw.rectangle([0, 0, WIDTH, 70], fill=(3, 2, 14))
    draw.line([(0, 70), (WIDTH, 70)], fill=(0, 100, 200, 160), width=1)
    draw.text((50, 14), "EVEZ-OS", fill=(0, 200, 255), font=font(42, bold=True))
    draw.text((258, 26), "QUANTUM EVOLUTION FIELD  —  LIVE ADAPTIVE FITNESS DYNAMICS",
              fill=TEXT_DIM, font=font(15))
    blink = int(t * 1.5) % 2 == 0
    if blink:
        draw.ellipse([WIDTH-80, 22, WIDTH-64, 38], fill=(255, 30, 30))
    draw.text((WIDTH-56, 20), "LIVE", fill=(255, 80, 80), font=font(16, bold=True))

def render_frame(t):
    update_manifold(t)
    update_quantum_particles(t)
    update_entanglement(t)

    img = Image.new('RGB', (WIDTH, HEIGHT), BG)
    draw_manifold(img, t)
    draw_quantum_field(img, t)
    draw_population(img, t)

    draw = ImageDraw.Draw(img)
    draw_header(draw, t)
    draw_entanglement_matrix(draw, t)
    draw_stats(draw, t)

    state["frame"] += 1
    return img

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rtmp-url", required=True)
    parser.add_argument("--preview", action="store_true")
    args = parser.parse_args()
    if args.preview:
        for i in range(3):
            render_frame(i * 1.0).save(f"/tmp/evez_quantum_preview_{i}.png")
            print(f"Saved /tmp/evez_quantum_preview_{i}.png")
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
    try:
        while True:
            ts = time.time()
            proc.stdin.write(render_frame(ts-t0).tobytes())
            sl = frame_dur - (time.time()-ts)
            if sl > 0: time.sleep(sl)
    except (BrokenPipeError, KeyboardInterrupt): pass
    finally:
        proc.stdin.close(); proc.wait()

if __name__ == "__main__":
    main()
