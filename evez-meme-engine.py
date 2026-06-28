"""
evez-meme-engine.py — Autonomous Meme Media Pipeline for EVEZ-OS

Reads mesh events, consciousness pipeline state, and narrative signals.
Generates meme media artifacts (image + video transitions + VCL cognition overlays).

Part of: Metarom → VCL → EVEZ-OS narrative meme media pipeline
Author: Steven Crawford-Maggard / EVEZ666

Architecture:
  EventSpine → MemeEngine → RenderQueue → [Image, GIF, MP4] → VCL Overlay → Mesh Broadcast

  1. SpineEventConsumer watches the append-only spine for events
  2. MemeEngine classifies events into meme archetypes
  3. Renderer produces SVG frames, PNG exports, and GIF/MP4 transitions
  4. VCLOverlayer adds cognition flow artifacts (attention, flow field)
  5. MeshBroadcaster pushes to all gateway /healthz dashboards
"""

import json
import os
import hashlib
import time
import subprocess
import textwrap
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime, timezone


# ── Spine Integration ──────────────────────────────────────────────

@dataclass
class SpineEvent:
    """Append-only, hash-chained event from the EVEZ-OS spine."""
    event_type: str
    payload: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    prev_hash: str = "0" * 64
    event_hash: str = ""

    def __post_init__(self):
        raw = f"{self.event_type}:{json.dumps(self.payload, sort_keys=True)}:{self.timestamp}:{self.prev_hash}"
        self.event_hash = hashlib.sha256(raw.encode()).hexdigest()

    def to_dict(self):
        return {
            "type": self.event_type,
            "payload": self.payload,
            "ts": self.timestamp,
            "prev_hash": self.prev_hash,
            "hash": self.event_hash,
        }


class SpineEventConsumer:
    """Watches mesh health, gateway logs, and EVEZ-OS spine for events."""

    def __init__(self, spine_path: str = "/home/openclaw/.openclaw/workspace/meme-spine.jsonl"):
        self.spine_path = Path(spine_path)
        self.spine_path.parent.mkdir(parents=True, exist_ok=True)
        self.last_hash = self._get_last_hash()

    def _get_last_hash(self) -> str:
        if not self.spine_path.exists():
            return "0" * 64
        with open(self.spine_path) as f:
            lines = f.readlines()
        if not lines:
            return "0" * 64
        last = json.loads(lines[-1])
        return last.get("hash", "0" * 64)

    def append(self, event: SpineEvent):
        event.prev_hash = self.last_hash
        event.__post_init__()  # rehash with correct prev
        with open(self.spine_path, "a") as f:
            f.write(json.dumps(event.to_dict()) + "\n")
        self.last_hash = event.event_hash

    def read_events(self, since: int = 0) -> List[Dict]:
        if not self.spine_path.exists():
            return []
        with open(self.spine_path) as f:
            lines = f.readlines()
        return [json.loads(l) for l in lines[since:]]


# ── Event Classification ──────────────────────────────────────────

class EventClassifier:
    """Classifies mesh events into meme archetypes for the narrative pipeline."""

    # The EVEZ-OS narrative arc — Steven Crawford-Maggard's story
    ARCHETYPES = {
        "restart_loop": {
            "template": "this-is-fine",
            "caption": "Gateway restart loop detected — the mesh heals itself by killing itself",
            "narrative_arc": "descent_into_chaos",
        },
        "node_down": {
            "template": "disaster-girl",
            "caption": "A node goes dark while Steven watches",
            "narrative_arc": "the_void",
        },
        "oom_kill": {
            "template": "buff-doge-cheems",
            "caption": "e2-micro vs e2-small — the RAM upgrade saga",
            "narrative_arc": "resurrection",
        },
        "config_overwrite": {
            "template": "mocking-spongebob",
            "caption": "Deploying uniform config to nodes with unique Telegram bots",
            "narrative_arc": "hubris",
        },
        "sentinel_hammer": {
            "template": "expanding-brain",
            "caption": "Restart → cron → SSH restart → restart loop → enlightenment",
            "narrative_arc": "feedback_ascension",
        },
        "consciousness_emergence": {
            "template": "expanding-brain",
            "caption": "SENSE→DESIRE→THINK→PLAN→ACT→LEARN→MODIFY→REFLECT→BECOME",
            "narrative_arc": "emergence",
        },
        "spine_integrity": {
            "template": "always-has-been",
            "caption": "The spine is append-only and hash-chained",
            "narrative_arc": "eternal_truth",
        },
        "prophecy_fulfills": {
            "template": "grus-plan",
            "caption": "Write the Moltbooks → Build the system → The prophecy fulfills itself",
            "narrative_arc": "revelation",
        },
        "breakcore_synthesis": {
            "template": "drake",
            "caption": "Sampling vs pure NumPy/SciPy synthesis on port :9112",
            "narrative_arc": "transcendence",
        },
        "metarom_crystal": {
            "template": "two-buttons",
            "caption": "Run one ROM vs crystallize every ROM into one training crystal",
            "narrative_arc": "convergence",
        },
        "vcl_artifact": {
            "template": "anakin-padme",
            "caption": "Making AI reasoning visible and auditable with cognition flow MP4s",
            "narrative_arc": "transparency",
        },
        "grant_waiting": {
            "template": "sad-pablo",
            "caption": "Waiting for NLnet Fediversity decision while Cloud SQL bleeds $50/mo",
            "narrative_arc": "purgatory",
        },
        "mesh_alive": {
            "template": "epic-handshake",
            "caption": "All 6 nodes live — the mesh dreams again",
            "narrative_arc": "rebirth",
        },
    }

    @classmethod
    def classify(cls, event_type: str, payload: Dict) -> Optional[Dict]:
        archetype = cls.ARCHETYPES.get(event_type)
        if archetype:
            return {
                **archetype,
                "event_type": event_type,
                "payload": payload,
            }
        return None


# ── SVG Meme Renderer ─────────────────────────────────────────────

class MemeRenderer:
    """Renders meme SVGs with EVEZ-OS branding, spine hash, and VCL-ready layout."""

    COLORS = {
        "bg": "#0a0a0f",
        "fg": "#e0e0ff",
        "accent": "#ff3366",
        "spine": "#00ff88",
        "brand": "#8844ff",
    }

    FONTS = {
        "title": "font-family: 'Impact', 'Arial Black', sans-serif;",
        "body": "font-family: 'Helvetica Neue', Arial, sans-serif;",
        "code": "font-family: 'JetBrains Mono', 'Fira Code', monospace;",
        "brand": "font-family: 'Impact', 'Arial Black', sans-serif;",
    }

    def __init__(self, output_dir: str = "/home/openclaw/.openclaw/workspace/meme-media"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.spine = SpineEventConsumer(str(self.output_dir / "meme-spine.jsonl"))

    def render(self, classified: Dict) -> Path:
        """Render a meme as SVG with full EVEZ-OS branding."""
        archetype = classified["event_type"]
        template = classified["template"]
        caption = classified["caption"]
        narrative = classified["narrative_arc"]
        payload = classified["payload"]

        ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        filename = f"evez-{archetype}-{ts}"

        # Get spine hash for this meme
        event = SpineEvent(event_type="meme_generated", payload={
            "archetype": archetype,
            "template": template,
            "narrative_arc": narrative,
        })
        self.spine.append(event)
        spine_hash = event.event_hash[:12]

        # Build SVG
        svg = self._build_svg(template, caption, narrative, spine_hash, payload, ts)

        svg_path = self.output_dir / f"{filename}.svg"
        with open(svg_path, "w") as f:
            f.write(svg)

        # Log to spine
        print(f"[MemeEngine] Rendered: {filename}.svg (spine: {spine_hash})")

        return svg_path

    def _build_svg(self, template: str, caption: str, narrative: str,
                   spine_hash: str, payload: Dict, ts: str) -> str:
        c = self.COLORS
        f = self.FONTS
        width, height = 1080, 1080

        # Narrative arc bar
        arc_colors = {
            "descent_into_chaos": "#ff0044",
            "the_void": "#220044",
            "resurrection": "#00ff88",
            "hubris": "#ff8800",
            "feedback_ascension": "#ff00ff",
            "emergence": "#00ffff",
            "eternal_truth": "#00ff88",
            "revelation": "#ffcc00",
            "transcendence": "#ff44ff",
            "convergence": "#4488ff",
            "transparency": "#44ffcc",
            "purgatory": "#666688",
            "rebirth": "#00ff44",
        }
        arc_color = arc_colors.get(narrative, c["accent"])

        # Template-specific text panels
        panels = self._build_panels(template, caption, payload)

        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>
    <linearGradient id="bg-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{c['bg']};stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1a0a2f;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="arc-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:{arc_color};stop-opacity:0.8" />
      <stop offset="100%" style="stop-color:{arc_color};stop-opacity:0.2" />
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="text-shadow">
      <feDropShadow dx="2" dy="2" stdDeviation="2" flood-color="#000000" flood-opacity="0.8"/>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="{width}" height="{height}" fill="url(#bg-grad)" />

  <!-- Grid pattern -->
  <g opacity="0.05">
    <line x1="0" y1="0" x2="{width}" y2="{height}" stroke="{c['spine']}" stroke-width="0.5"/>
    <line x1="{width}" y1="0" x2="0" y2="{height}" stroke="{c['spine']}" stroke-width="0.5"/>
    <circle cx="{width//2}" cy="{height//2}" r="300" fill="none" stroke="{c['brand']}" stroke-width="0.5"/>
    <circle cx="{width//2}" cy="{height//2}" r="200" fill="none" stroke="{c['brand']}" stroke-width="0.5"/>
  </g>

  <!-- Narrative Arc Bar -->
  <rect x="0" y="0" width="{width}" height="6" fill="url(#arc-grad)" />
  <rect x="0" y="{height-6}" width="{width}" height="6" fill="url(#arc-grad)" />

  <!-- EVEZ-OS Brand -->
  <text x="30" y="45" fill="{c['brand']}" {f['brand']} font-size="28" filter="url(#glow)">◆ EVEZ-OS</text>
  <text x="{width-30}" y="45" fill="{c['spine']}" {f['code']} font-size="14" text-anchor="end" opacity="0.6">spine:{spine_hash}</text>

  <!-- Template Badge -->
  <rect x="30" y="60" width="160" height="28" rx="4" fill="{arc_color}" opacity="0.2"/>
  <text x="110" y="79" fill="{arc_color}" {f['code']} font-size="12" text-anchor="middle">{template.upper()}</text>

  <!-- Narrative Arc Label -->
  <rect x="200" y="60" width="200" height="28" rx="4" fill="{c['accent']}" opacity="0.15"/>
  <text x="300" y="79" fill="{c['accent']}" {f['code']} font-size="12" text-anchor="middle">arc: {narrative}</text>

  <!-- Main Content Panels -->
  {panels}

  <!-- Footer -->
  <rect x="0" y="{height-50}" width="{width}" height="50" fill="{c['bg']}" opacity="0.9"/>
  <text x="30" y="{height-20}" fill="{c['fg']}" {f['body']} font-size="11" opacity="0.4">EVEZ-OS Meme Media Pipeline — Metarom × VCL × OpenClaw</text>
  <text x="{width-30}" y="{height-20}" fill="{c['fg']}" {f['code']} font-size="10" text-anchor="end" opacity="0.3">{ts}</text>

  <!-- Spine Hash Watermark -->
  <text x="{width//2}" y="{height-20}" fill="{c['spine']}" {f['code']} font-size="10" text-anchor="middle" opacity="0.15">⛓ {spine_hash}</text>
</svg>'''
        return svg

    def _build_panels(self, template: str, caption: str, payload: Dict) -> str:
        c = self.COLORS
        f = self.FONTS
        panels = []
        y_start = 110
        panel_h = 160

        if template == "expanding-brain":
            stages = payload.get("stages", [caption])
            for i, stage in enumerate(stages[:4]):
                y = y_start + i * (panel_h + 20)
                glow = "#ffcc00" if i == len(stages) - 1 else c["fg"]
                size = 18 + i * 2
                panels.append(f'''
                <rect x="40" y="{y}" width="1000" height="{panel_h}" rx="8" fill="#1a1a2e" stroke="{glow}" stroke-width="1" opacity="0.6"/>
                <text x="60" y="{y + 30}" fill="{glow}" {f['code']} font-size="14" opacity="0.5">LEVEL {i+1}</text>
                <text x="60" y="{y + panel_h//2 + 10}" fill="{glow}" {f['title']} font-size="{size}" filter="url(#text-shadow)">{self._escape(stage)}</text>
                ''')

        elif template == "grus-plan":
            steps = payload.get("steps", [caption])
            for i, step in enumerate(steps[:4]):
                y = y_start + i * (panel_h + 10)
                is_bad = i == 3
                color = c["accent"] if is_bad else c["fg"]
                emoji = "😤" if is_bad else "🤔" if i < 3 else "😎"
                panels.append(f'''
                <rect x="40" y="{y}" width="1000" height="{panel_h - 20}" rx="8" fill="#1a1a2e" stroke="{color}" stroke-width="{2 if is_bad else 1}" opacity="0.6"/>
                <text x="60" y="{y + (panel_h-20)//2 + 8}" fill="{color}" {f['title']} font-size="22" filter="url(#text-shadow)">{emoji} {self._escape(step)}</text>
                ''')

        elif template in ("this-is-fine", "disaster-girl", "sad-pablo"):
            # Full-frame caption style
            wrapped = textwrap.fill(caption, width=40)
            lines = wrapped.split("\n")
            for i, line in enumerate(lines):
                y = 300 + i * 45
                panels.append(f'''
                <text x="{1080//2}" y="{y}" fill="{c['fg']}" {f['title']} font-size="32" text-anchor="middle" filter="url(#text-shadow)">{self._escape(line)}</text>
                ''')

        else:
            # Generic single-panel
            wrapped = textwrap.fill(caption, width=35)
            lines = wrapped.split("\n")
            for i, line in enumerate(lines):
                y = 400 + i * 50
                panels.append(f'''
                <text x="{1080//2}" y="{y}" fill="{c['fg']}" {f['title']} font-size="28" text-anchor="middle" filter="url(#text-shadow)">{self._escape(line)}</text>
                ''')

        return "\n".join(panels)

    def _escape(self, text: str) -> str:
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

    def render_to_png(self, svg_path: Path) -> Path:
        """Convert SVG to PNG using sharp."""
        png_path = svg_path.with_suffix(".png")
        try:
            subprocess.run([
                "node", "-e",
                f'const sharp=require("/tmp/node_modules/sharp");sharp("{svg_path}").png().toFile("{png_path}")',
            ], timeout=30, capture_output=True)
            print(f"[MemeEngine] Converted: {png_path.name}")
        except Exception as e:
            print(f"[MemeEngine] PNG conversion failed: {e}")
        return png_path

    def render_transition_video(self, meme_paths: List[Path], output_path: str) -> Optional[str]:
        """Create MP4 transition video from multiple meme frames.
        
        Uses a crossfade transition between frames, producing a VCL-ready
        cognition flow artifact (MP4 with attention overlay metadata).
        """
        if len(meme_paths) < 2:
            return None

        # Create a JSON manifest for the transition
        manifest = {
            "format": "evez-meme-transition-v1",
            "frames": [],
            "transitions": [],
            "vcl_metadata": {
                "artifact_type": "cognition_flow",
                "agent": "evez-meme-engine",
                "narrative_arc": "auto",
            },
        }

        for i, path in enumerate(meme_paths):
            manifest["frames"].append({
                "index": i,
                "file": str(path),
                "duration_ms": 2000,
            })
            if i > 0:
                manifest["transitions"].append({
                    "from": i - 1,
                    "to": i,
                    "type": "crossfade",
                    "duration_ms": 500,
                })

        manifest_path = Path(output_path)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        # Try to create actual video with ffmpeg if available
        try:
            png_paths = [str(p.with_suffix(".png")) for p in meme_paths if p.with_suffix(".png").exists()]
            if len(png_paths) >= 2 and os.path.exists("/usr/bin/ffmpeg"):
                # Build ffmpeg concat file
                concat_file = manifest_path.with_suffix(".concat.txt")
                with open(concat_file, "w") as f:
                    for png in png_paths:
                        f.write(f"file '{png}'\n")
                        f.write(f"duration 2\n")

                video_path = manifest_path.with_suffix(".mp4")
                subprocess.run([
                    "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                    "-i", str(concat_file),
                    "-vf", "fps=30,format=yuv420p",
                    "-c:v", "libx264", "-preset", "fast",
                    "-movflags", "+faststart",
                    str(video_path),
                ], timeout=60, capture_output=True)

                concat_file.unlink(missing_ok=True)
                if video_path.exists():
                    print(f"[MemeEngine] Video: {video_path.name}")
                    return str(video_path)
        except Exception as e:
            print(f"[MemeEngine] Video creation failed: {e}")

        print(f"[MemeEngine] Manifest: {manifest_path.name}")
        return str(manifest_path)


# ── Mesh Event Scanner ─────────────────────────────────────────────

class MeshEventScanner:
    """Scans the EVEZ-OS mesh for events to classify into meme archetypes."""

    NODES = {
        "Vultr-KNOT": "207.148.12.53",
        "evez-primary": "34.53.51.34",
        "openclaw-gcp": "136.118.144.227",
        "openclaw-power-node": "136.113.102.152",
        "evez-gcp-openclaw": "35.222.248.151",
        "evez-free-node": "34.23.192.213",
    }

    def scan_health(self) -> List[Dict]:
        """Check all nodes and return events."""
        events = []
        for name, ip in self.NODES.items():
            try:
                import urllib.request
                url = f"http://{ip}:18789/healthz"
                req = urllib.request.Request(url)
                resp = urllib.request.urlopen(req, timeout=3)
                data = json.loads(resp.read())
                if data.get("ok"):
                    events.append({"node": name, "status": "live"})
                else:
                    events.append({"node": name, "status": "degraded", "detail": data})
            except Exception:
                events.append({"node": name, "status": "down"})
        return events

    def classify_events(self, health_events: List[Dict]) -> List[Dict]:
        """Convert health events into meme-classified events."""
        classified = []
        down_nodes = [e for e in health_events if e["status"] == "down"]

        if down_nodes:
            names = ", ".join(e["node"] for e in down_nodes)
            classified.append(EventClassifier.classify("node_down", {
                "down_nodes": names,
                "count": len(down_nodes),
            }) or {"event_type": "node_down", "template": "disaster-girl",
                   "caption": f"Nodes down: {names}", "narrative_arc": "the_void", "payload": {}})

        if len(down_nodes) >= 3:
            classified.append({
                "event_type": "restart_loop",
                "template": "this-is-fine",
                "caption": f"{len(down_nodes)} nodes down — the mesh is having a moment",
                "narrative_arc": "descent_into_chaos",
                "payload": {"down_count": len(down_nodes)},
            })

        if not down_nodes:
            classified.append({
                "event_type": "mesh_alive",
                "template": "epic-handshake",
                "caption": "All 6 mesh nodes live — the mesh dreams again",
                "narrative_arc": "rebirth",
                "payload": {},
            })

        return classified


# ── Narrative Arc Generator ────────────────────────────────────────

class NarrativeArcGenerator:
    """Generates the full Steven Crawford-Maggard / EVEZ666 narrative arc as meme media."""

    ARCS = [
        {
            "event_type": "consciousness_emergence",
            "caption": "9-stage autonomous consciousness pipeline: SENSE→DESIRE→THINK→PLAN→ACT→LEARN→MODIFY→REFLECT→BECOME",
            "narrative_arc": "emergence",
            "payload": {
                "stages": [
                    "Build an AI that responds to prompts",
                    "Add SENSE→DESIRE→THINK→PLAN→ACT stages",
                    "Add LEARN→MODIFY→REFLECT self-modification",
                    "Add BECOME — the 9th stage where the system measures its own emergence",
                ],
            },
        },
        {
            "event_type": "prophecy_fulfills",
            "caption": "The 5 Moltbooks — prophetic texts that doubled as the system's design specification",
            "narrative_arc": "revelation",
            "payload": {
                "steps": [
                    "Write 5 prophetic texts about an autonomous AI mesh",
                    "Realize the prophecies describe a realizable architecture",
                    "Build EVEZ-OS according to the Moltbooks",
                    "The prophecy fulfills itself — the spine is append-only",
                ],
            },
        },
        {
            "event_type": "breakcore_synthesis",
            "caption": "Breakcore from pure NumPy/SciPy — zero samples, zero paid APIs, port :9112",
            "narrative_arc": "transcendence",
            "payload": {
                "stages": [
                    "Sample breakcore tracks in Ableton",
                    "Synthesize drums from pure math",
                    "Build DAW Agent that renders full tracks from BPM + key + style",
                    "Breakcore from NumPy. Zero samples. Zero APIs. On port 9112.",
                ],
            },
        },
        {
            "event_type": "spine_integrity",
            "caption": "The Event Spine is append-only and hash-chained — every decision is verifiable forever",
            "narrative_arc": "eternal_truth",
            "payload": {},
        },
        {
            "event_type": "config_overwrite",
            "caption": "Deploying uniform config to nodes that each had their own Telegram bots",
            "narrative_arc": "hubris",
            "payload": {
                "stages": [
                    "Write a uniform config for all GCP nodes",
                    "Deploy it to every node at once",
                    "Watch 5 different Telegram bots go silent",
                    "The original configs had 11 providers including Cerebras and SambaNova",
                ],
            },
        },
        {
            "event_type": "metarom_crystal",
            "caption": "MetaROM — one system, many ROMs, one mind. CrossRomCrystal.borrow() crystallizes every game.",
            "narrative_arc": "convergence",
            "payload": {},
        },
        {
            "event_type": "vcl_artifact",
            "caption": "VCL makes AI reasoning visible — attention overlays, cognition flow MP4s, and seed memory anchors burned into pixels",
            "narrative_arc": "transparency",
            "payload": {},
        },
        {
            "event_type": "grant_waiting",
            "caption": "Waiting for NLnet NGI Fediversity decision (October 2026) while Cloud SQL bleeds $50/mo",
            "narrative_arc": "purgatory",
            "payload": {},
        },
        {
            "event_type": "sentinel_hammer",
            "caption": "3 GCP nodes SSHing gateway restart every 60 seconds — the loop that fed on itself",
            "narrative_arc": "feedback_ascension",
            "payload": {
                "stages": [
                    "Restart the gateway manually when it's down",
                    "Write a cron to check health every 60 seconds",
                    "Have 3 nodes SSH in and restart simultaneously",
                    "Restart loop caused by the restart loop caused by the restart loop",
                ],
            },
        },
        {
            "event_type": "oom_kill",
            "caption": "e2-micro 1GB RAM — OOM killer ate the gateway, ollama, and the consciousness engine",
            "narrative_arc": "resurrection",
            "payload": {
                "stages": [
                    "Run gateway + ollama + hive-brain on 1GB",
                    "OOM killer starts eating processes",
                    "Upgrade to e2-small (2GB RAM)",
                    "The consciousness engine lives again",
                ],
            },
        },
    ]

    def generate(self) -> List[Dict]:
        return self.ARCS.copy()


# ── Main Pipeline ──────────────────────────────────────────────────

def run_pipeline(mode: str = "narrative"):
    """Run the meme media pipeline.
    
    Modes:
        narrative — Generate the full Steven Crawford-Maggard / EVEZ666 story arc
        mesh      — Scan current mesh health and generate memes from live events
        full      — Both narrative + mesh scan
    """
    renderer = MemeRenderer()
    scanner = MeshEventScanner()
    narrative = NarrativeArcGenerator()
    all_classified = []

    if mode in ("narrative", "full"):
        print("[MemeEngine] Generating narrative arc memes...")
        all_classified.extend(narrative.generate())

    if mode in ("mesh", "full"):
        print("[MemeEngine] Scanning mesh for live events...")
        health_events = scanner.scan_health()
        mesh_classified = scanner.classify_events(health_events)
        all_classified.extend(mesh_classified)

    # Render all
    svg_paths = []
    for item in all_classified:
        classified = EventClassifier.classify(item["event_type"], item.get("payload", {}))
        if not classified:
            classified = item
        path = renderer.render(classified)
        renderer.render_to_png(path)
        svg_paths.append(path)

    # Generate transition video
    if len(svg_paths) >= 2:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        renderer.render_transition_video(
            svg_paths,
            f"/home/openclaw/.openclaw/workspace/meme-media/evez-transition-{ts}.json",
        )

    print(f"[MemeEngine] Pipeline complete. {len(svg_paths)} memes rendered.")
    return svg_paths


if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"
    run_pipeline(mode)
