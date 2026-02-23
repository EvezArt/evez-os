#!/usr/bin/env python3
"""
EVEZ-OS Inline Video Renderer
Generates arc video from hyperloop_state.json using PIL + ffmpeg.
No external dependencies beyond numpy, Pillow, scipy, ffmpeg.

Usage:
  python gen_video_inline.py --state /path/to/hyperloop_state.json --output /tmp/evez_arc.mp4 --tail 20
"""
import argparse, json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def bar_clr(pc, fire, isp):
    if fire:     return (255, 70, 30)
    if isp:      return (160, 80, 255)
    if pc > 0.45: return (255, 195, 30)
    if pc > 0.35: return (40, 150, 255)
    return (100, 100, 120)

def lc(c1, c2, t):
    return tuple(int(c1[i] + (c2[i]-c1[i]) * t) for i in range(3))

def make_frame(rounds, ridx, t, W=720, H=1280):
    rn, ns, tau, ok, topo, pc, fire, vg, isp = rounds[ridx]
    t = min(1.0, max(0.0, t))
    img = Image.new("RGB", (W, H), (5, 5, 12))
    d   = ImageDraw.Draw(img)
    try:
        BOLD  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        BOLD3 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 44)
        MONO2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 16)
        REG2  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    except:
        BOLD = BOLD3 = MONO2 = REG2 = ImageFont.load_default()

    hc = (255, 70, 30) if fire else ((160, 80, 255) if isp else (255, 195, 30))
    d.rectangle([0,0,W,8], fill=hc)
    d.text((W//2, 52), f"EVEZ-OS  R{rn}", fill=hc, anchor="mm", font=BOLD)
    d.text((W//2, 90), f"N = {ns}", fill=(235,235,245), anchor="mm", font=REG2)

    ey = 118
    dv = 0.08 * 1.0 * pc
    N_int = int(ns.split("=")[0])
    eqs = [
        (f"tau={tau}  omega_k={ok}  topo={topo:.2f}", (70,70,90)),
        (f"poly_c = {topo:.2f}*(1+ln({tau})) / log2({N_int+2})", (235,235,245)),
        (f"       = {pc:.6f}", (255,195,30) if not fire else (255,70,30)),
        (f"threshold 0.500  {'← FIRE' if fire else f'Δ={0.5-pc:.4f}'}", (200,50,50) if fire else (70,70,90)),
        (f"delta_V = 0.08*{pc:.6f} = {dv:.6f}", (50,210,90)),
    ]
    for i,(txt,clr) in enumerate(eqs):
        d.text((38, ey+i*24), txt, fill=clr, font=MONO2)

    by = ey + len(eqs)*24 + 16
    bmax = W - 80
    bw = int(bmax * pc / 0.6 * t)
    bc = bar_clr(pc, fire, isp)
    d.rectangle([40, by, 40+bw, by+26], fill=bc)
    d.rectangle([40, by, 40+bmax, by+26], outline=(100,100,120), width=1)
    tx = 40 + int(bmax * 0.5/0.6)
    d.line([tx, by-4, tx, by+30], fill=(200,50,50), width=2)
    d.text((tx, by-18), "0.500", fill=(180,40,40), font=MONO2, anchor="mm")

    ly = by + 46
    lbl = "FIRE" if fire else ("PRIME BLOCK" if isp else "NO FIRE")
    lc2 = (255,70,30) if fire else ((160,80,255) if isp else (40,150,255))
    d.text((W//2, ly), lbl, fill=lc((5,5,12),lc2,min(1.0,t*2.5)), anchor="mm", font=BOLD3)

    vy = ly + 60
    vf = vg / 6.0
    vbw = int((W-80) * vf * t)
    d.rectangle([40, vy, 40+vbw, vy+18], fill=(50,210,90))
    d.rectangle([40, vy, W-40, vy+18], outline=(100,100,120), width=1)
    d.text((40, vy-20), f"V_global  {vg:.6f} / 6.000  ({vf*100:.1f}%)", fill=(235,235,245), font=MONO2)
    d.text((W-40, vy-20), f"CEILING ×{rn-82}", fill=(255,195,30), anchor="rm", font=MONO2)

    sy = vy + 44
    sh = 130
    sw = W - 80
    d.rectangle([40,sy,40+sw,sy+sh], fill=(10,10,22))
    d.text((40, sy-18), "poly_c history", fill=(70,70,90), font=MONO2)
    tsy = sy + sh - int(sh * 0.5/0.6)
    d.line([40, tsy, 40+sw, tsy], fill=(60,15,15), width=1)
    N_ = len(rounds)
    pts = []
    for i, (rr,_,_,_,_,pci,fi,_,ispi) in enumerate(rounds):
        x = 40 + int(sw*i/(N_-1))
        y = sy + sh - int(sh*pci/0.6)
        pts.append((x,y,bar_clr(pci,fi,ispi),i))
    for i in range(len(pts)-1):
        x1,y1,c1,i1 = pts[i]; x2,y2,c2,i2 = pts[i+1]
        if i1 <= ridx and i2 <= ridx:
            d.line([x1,y1,x2,y2], fill=c2, width=1)
    for (x,y,c,idx) in pts:
        if idx < ridx:   d.ellipse([x-3,y-3,x+3,y+3], fill=c)
        elif idx==ridx:  d.ellipse([x-5,y-5,x+5,y+5], fill=(235,235,245))
        else:            d.ellipse([x-2,y-2,x+2,y+2], fill=tuple(max(0,v//6) for v in c))

    d.rectangle([0,H-36,W,H], fill=(8,8,18))
    d.text((W//2,H-18), f"@EVEZ666  ·  R{rn}  ·  evez-os", fill=(70,70,90), anchor="mm", font=REG2)
    return np.array(img, dtype=np.uint8)

def build_rounds_from_state(state, tail=20):
    rounds = []
    cur = state.get('current_round', 1)
    start = max(1, cur - tail + 1)
    for r in range(start, cur+1):
        key = f"r{r}_result"
        rr = state.get(key, {})
        N = rr.get("N", r)
        ns = rr.get("N_str", str(N))
        tau = rr.get("tau", 1)
        ok = rr.get("omega_k", 1)
        topo = rr.get("topo", 1.0 + 0.15*ok)
        pc = rr.get("poly_c", topo*(1+math.log(tau))/math.log2(N+2) if tau>0 else 0)
        fire = rr.get("fire_ignited", pc >= 0.5)
        vg = rr.get("V_global_new", 0)
        isp = (tau == 1 and ok == 1)
        rounds.append((r, ns or str(N), tau, ok, topo, pc, fire, vg, isp))
    return rounds

def render(state_path, output, tail=20, fps=30, hold=1.5, ramp=0.4):
    state = json.load(open(state_path))
    rounds = build_rounds_from_state(state, tail)
    W, H = 720, 1280
    HOLD = int(hold * fps)
    RAMP = int(ramp * fps)
    cmd = ["ffmpeg","-y","-hide_banner","-loglevel","error",
           "-f","rawvideo","-vcodec","rawvideo","-s",f"{W}x{H}",
           "-pix_fmt","rgb24","-r",str(fps),"-i","pipe:0",
           "-vcodec","libx264","-pix_fmt","yuv420p","-crf","22",
           "-preset","fast","-movflags","+faststart", output]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for ri in range(len(rounds)):
        for f in range(RAMP):
            proc.stdin.write(make_frame(rounds, ri, (f+1)/RAMP, W, H).tobytes())
        for f in range(HOLD):
            proc.stdin.write(make_frame(rounds, ri, 1.0, W, H).tobytes())
    proc.stdin.close(); proc.wait()
    return os.path.getsize(output)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--state", default="workspace/hyperloop_state.json")
    p.add_argument("--output", default="/tmp/evez_arc.mp4")
    p.add_argument("--tail", type=int, default=20)
    p.add_argument("--fps", type=int, default=30)
    p.add_argument("--hold", type=float, default=1.5)
    args = p.parse_args()
    sz = render(args.state, args.output, args.tail, args.fps, args.hold)
    print(f"Rendered: {args.output}  ({sz/1024:.1f} KB)")
