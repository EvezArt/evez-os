#!/usr/bin/env python3
"""
EVEZ-OS CLI — Visual Cognition Layer
Usage: python3 tools/evez.py <command> [options]

Commands:
  play          Run the Play Forever engine (infinite forensic episodes)
  lint          Validate the append-only spine for integrity
  visualize-thought  Generate visual cognition artifacts from spine
  help          Show this message
"""
import sys, os, argparse, json, hashlib, time, random
from pathlib import Path

SPINE_PATH = Path("spine/spine.jsonl")
SPINE_PATH.parent.mkdir(parents=True, exist_ok=True)

LOBBIES = ["DNS", "BGP", "TLS", "CDN", "AUTH", "ROLLBACK", "FUNDING", "MIXED"]
NARRATORS = {
    "PUBLIC_INTERNET": "The world argues about truth at line-rate. You do not get one reality. You get convergence.",
    "FSC_FORGE": "Compression applied. The model cracked first at the boundary of pending vs final.",
    "XRAY_ROOM": "If your resolver lies, your world-map lies. Two vantages or you are worshipping one cache.",
}

def spine_append(entry):
    entry["ts"] = time.time()
    entry["hash"] = hashlib.sha256(json.dumps(entry, sort_keys=True).encode()).hexdigest()[:16]
    with open(SPINE_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry

def cmd_play(args):
    random.seed(args.seed)
    print(f"\n{'='*60}")
    print(f"  EVEZ Play Forever Engine  |  seed={args.seed}  |  steps={args.steps}")
    print(f"  Powered by EVEZ  |  github.com/EvezArt/evez-os")
    print(f"{'='*60}\n")

    for i in range(args.steps):
        lobby = random.choice(LOBBIES)
        narrator = random.choice(list(NARRATORS.keys()))
        claim = f"step_{i:03d}: {lobby} probe — hypothesis pending falsification"
        entry = spine_append({
            "step": i, "lobby": lobby, "narrator": narrator,
            "claim": claim, "truth_plane": "PENDING",
            "powered_by": "EVEZ"
        })
        print(f"[{i:03d}] {lobby:10s} | {narrator:20s} | {entry['hash']}")
        print(f"      \"{NARRATORS[narrator]}\"")
        print()
        time.sleep(0.05)

    print(f"\n✅ {args.steps} spine entries written. Run 'python3 tools/evez.py lint' to verify.")
    manifest = {"powered_by": "EVEZ", "steps": args.steps, "seed": args.seed,
                "spine": str(SPINE_PATH), "version": "1.0.0"}
    with open("manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"📋 manifest.json written.")

def cmd_lint(args):
    if not SPINE_PATH.exists():
        print("No spine found. Run 'python3 tools/evez.py play' first.")
        return
    entries = [json.loads(l) for l in SPINE_PATH.read_text().strip().splitlines() if l.strip()]
    ok = violations = 0
    for e in entries:
        stored_hash = e.pop("hash", None)
        computed = hashlib.sha256(json.dumps(e, sort_keys=True).encode()).hexdigest()[:16]
        e["hash"] = stored_hash
        if stored_hash == computed:
            ok += 1
        else:
            violations += 1
            print(f"  ❌ VIOLATION at step {e.get('step')}: stored={stored_hash} computed={computed}")
    print(f"\nLint: {ok} OK, {violations} violations {'✅' if violations == 0 else '❌'}")

def cmd_visualize(args):
    try:
        import numpy as np
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("Install deps: pip install numpy pillow")
        return

    if not SPINE_PATH.exists():
        print("No spine found. Run play first.")
        return

    entries = [json.loads(l) for l in SPINE_PATH.read_text().strip().splitlines() if l.strip()]
    W, H = 800, 600
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)

    lobby_colors = {
        "DNS": (0,255,128), "BGP": (255,128,0), "TLS": (0,200,255),
        "CDN": (255,0,200), "AUTH": (200,255,0), "ROLLBACK": (255,50,50),
        "FUNDING": (128,0,255), "MIXED": (255,255,255)
    }

    for i, e in enumerate(entries[:50]):
        x = (i % 10) * 75 + 40
        y = (i // 10) * 100 + 40
        color = lobby_colors.get(e.get("lobby", "MIXED"), (200,200,200))
        draw.ellipse([x-20, y-20, x+20, y+20], fill=color, outline=(255,255,255))
        draw.text((x-15, y+25), e.get("lobby","?")[:3], fill=color)

    draw.text((10, H-30), "Powered by EVEZ | github.com/EvezArt/evez-os", fill=(100,100,100))

    out = Path("cognition_map.png")
    img.save(out)
    print(f"✅ Cognition map saved: {out}")

def main():
    parser = argparse.ArgumentParser(description="EVEZ-OS Visual Cognition Layer")
    sub = parser.add_subparsers(dest="cmd")

    p = sub.add_parser("play"); p.add_argument("--seed", type=int, default=42)
    p.add_argument("--steps", type=int, default=14)
    sub.add_parser("lint")
    v = sub.add_parser("visualize-thought"); v.add_argument("--input", default="spine/spine.jsonl")

    args = parser.parse_args()
    if args.cmd == "play": cmd_play(args)
    elif args.cmd == "lint": cmd_lint(args)
    elif args.cmd == "visualize-thought": cmd_visualize(args)
    else: parser.print_help()

if __name__ == "__main__":
    main()
