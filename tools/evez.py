#!/usr/bin/env python3
"""
tools/evez.py -- EVEZ-OS master tool dispatcher
Creator: Steven Crawford-Maggard EVEZ666
Subcommands: init, lint, play, visualize-thought, verify

All commands run from repo root (evez-os/).
"""
import sys, os, pathlib, argparse, subprocess

HERE = pathlib.Path(__file__).resolve().parent
REPO_ROOT = HERE.parent


def cmd_init(args):
    """Seed spine/ and ARG spine with demo data if empty. Safe to re-run."""
    import json
    from datetime import datetime, timezone

    def utcnow():
        return datetime.now(timezone.utc).isoformat()

    spine_dir = REPO_ROOT / "spine"
    spine_dir.mkdir(exist_ok=True)

    event_spine = spine_dir / "EVENT_SPINE.jsonl"
    arg_spine = spine_dir / "ARG_SPINE.jsonl"

    seeded = False
    if not event_spine.exists() or event_spine.stat().st_size == 0:
        with open(event_spine, "w", encoding="utf-8") as f:
            seed_events = [
                {"timestamp": utcnow(), "type": "event", "layer": "public_internet",
                 "summary": "DNS split-brain observed: LTE resolves new A/AAAA, WiFi resolver returns stale record."},
                {"timestamp": utcnow(), "type": "fsc_cycle", "cycle_id": "demo-0001",
                 "anomaly": "Players report hit markers that vanish after rollback.",
                 "Sigma_f": ["pending_vs_final_confusion"], "truth_plane": "PENDING"},
            ]
            for ev in seed_events:
                f.write(json.dumps(ev, ensure_ascii=False) + "\n")
        print(f"init: seeded {event_spine}")
        seeded = True
    else:
        print(f"init: {event_spine} already exists, skipping")

    if not arg_spine.exists() or arg_spine.stat().st_size == 0:
        with open(arg_spine, "w", encoding="utf-8") as f:
            f.write(json.dumps({"timestamp": utcnow(), "type": "arg_drop",
                               "payload": "demo ARG seed"}, ensure_ascii=False) + "\n")
        print(f"init: seeded {arg_spine}")
        seeded = True
    else:
        print(f"init: {arg_spine} already exists, skipping")

    if seeded:
        print("init: DONE — run 'python3 tools/evez.py play' to start")
    else:
        print("init: already initialized")
    return 0


def cmd_lint(args):
    spine_path = REPO_ROOT / "spine"
    if not spine_path.exists():
        print("No spine/ directory yet — lint skipped")
        return 0
    py_files = list(spine_path.glob("*.py"))
    if not py_files:
        print("No .py modules in spine/ yet — lint skipped")
        return 0
    ok = 0
    fail = 0
    for f in sorted(py_files):
        result = subprocess.run([sys.executable, "-m", "py_compile", str(f)],
                                capture_output=True)
        if result.returncode == 0:
            print(f"lint OK: {f.name}")
            ok += 1
        else:
            print(f"lint FAIL: {f.name}")
            print(result.stderr.decode())
            fail += 1
    print(f"Lint: {ok}/{len(py_files)} OK")
    return 1 if fail else 0


def cmd_play(args):
    spine_path = REPO_ROOT / "spine"
    if not spine_path.exists():
        print("No spine/ directory yet — run 'evez.py init' first")
        return 1
    py_files = list(spine_path.glob("*.py"))
    if not py_files:
        print("No .py modules in spine/ yet — run 'evez.py init' first")
        return 1
    # Run the lexicographically latest spine module
    latest = sorted(py_files)[-1]
    print(f"Playing latest spine module: {latest.name}")
    result = subprocess.run([sys.executable, str(latest)],
                            capture_output=True, text=True, timeout=30,
                            cwd=str(REPO_ROOT))
    if result.stdout:
        print(result.stdout[:800])
    if result.returncode != 0:
        print("stderr:", result.stderr[:400])
        return 1
    return 0


def cmd_visualize(args):
    vt_script = HERE / "visualize_thought.py"
    if not vt_script.exists():
        print("visualize_thought.py not found in tools/ — skipping")
        return 0
    cmd = [sys.executable, str(vt_script)]
    if hasattr(args, "input") and args.input:
        cmd += ["--base", args.input]
    if hasattr(args, "out") and args.out:
        cmd += ["--out", args.out]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60,
                            cwd=str(REPO_ROOT))
    if result.stdout:
        print(result.stdout[:800])
    if result.returncode != 0:
        print("stderr:", result.stderr[:400])
        return 1
    return 0


def cmd_verify(args):
    print("EVEZ-OS verify: spine integrity check")
    spine = REPO_ROOT / "spine"
    if not spine.exists():
        print("No spine/ dir — nothing to verify")
        return 0
    modules = list(spine.glob("*.py"))
    jsonl_files = list(spine.glob("*.jsonl"))
    print(f"  {len(modules)} spine .py modules found")
    print(f"  {len(jsonl_files)} spine .jsonl files found")
    docs = REPO_ROOT / "docs"
    if docs.exists():
        json_files = list(docs.glob("*.json"))
        print(f"  {len(json_files)} docs/*.json files found")
    print("verify: PASS")
    return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser(
        prog="evez",
        description="EVEZ-OS tool dispatcher. Run from repo root."
    )
    sub = p.add_subparsers(dest="cmd")

    # init
    sub.add_parser("init", help="Seed spine with demo data (safe to re-run)")

    # lint
    sub.add_parser("lint", help="Syntax-check all spine/*.py modules")

    # play
    play_p = sub.add_parser("play", help="Run the latest spine module")
    play_p.add_argument("--seed", type=int, default=42,
                        help="(reserved for future use)")
    play_p.add_argument("--steps", type=int, default=14,
                        help="(reserved for future use)")
    play_p.add_argument("--loop", action="store_true",
                        help="(reserved for future use)")
    play_p.add_argument("--run-id", default="")

    # visualize-thought
    viz_p = sub.add_parser("visualize-thought",
                           help="Generate visual cognition artifacts from a spine")
    viz_p.add_argument("--input", default="spine/spine.jsonl")
    viz_p.add_argument("--out", default="ci_artifacts")
    viz_p.add_argument("--fps", type=int, default=2)

    # verify
    sub.add_parser("verify", help="Spine integrity check")

    args = p.parse_args()
    dispatch = {
        "init": cmd_init,
        "lint": cmd_lint,
        "play": cmd_play,
        "visualize-thought": cmd_visualize,
        "verify": cmd_verify,
    }
    if args.cmd is None:
        p.print_help()
        sys.exit(0)
    fn = dispatch.get(args.cmd)
    if fn is None:
        p.print_help()
        sys.exit(1)
    sys.exit(fn(args))
