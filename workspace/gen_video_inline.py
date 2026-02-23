#!/usr/bin/env python3
"""
gen_video_inline.py — EVEZ-OS arc video renderer
=================================================
Renders a bar chart arc video showing poly_c per round with V_global bar,
FIRE threshold line, and R144 fire watch banner.

Usage:
    python gen_video_inline.py --state /path/to/hyperloop_state.json \
        --output /tmp/evez_arc.mp4 [--tail 20] [--fps 30] [--hold 1.5]
"""
import json, subprocess, sys, os, argparse, math
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True)
    ap.add_argument("--output", default="/tmp/evez_arc.mp4")
    ap.add_argument("--tail", type=int, default=20)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--hold", type=float, default=1.5)
    args = ap.parse_args()

    from PIL import Image, ImageDraw, ImageFont
    state = json.load(open(args.state))

    W, H = 1280, 720
    FPS = args.fps
    HOLD_S = args.hold
    BG = (5, 5, 12)
    RED = (220, 40, 40); FIRE_COLOR = (255, 80, 0)
    GREEN = (40, 220, 100); DIM = (80, 80, 100)
    WHITE = (230, 230, 240); FIRE_THRESH = 0.500

    # Arc history — known data points
    ARC_FULL = [
        (122,74,0.501,True,3.218,"2²×?"),
        (123,75,0.467,False,3.255,"3×5²"),
        (124,76,0.464,False,3.292,"2²×19"),
        (125,77,0.324,False,3.318,"7×11"),
        (126,78,0.463,False,3.355,"2×3×13"),
        (127,79,0.178,False,3.369,"prime"),
        (128,80,0.461,False,3.406,"2⁴×5"),
        (129,81,0.459,False,3.443,"3⁴"),
        (130,82,0.502,True,3.483,"2×41"),
        (131,83,0.177,False,3.497,"prime"),
        (132,84,0.458,False,3.534,"2²×3×7"),
        (133,85,0.177,False,3.548,"5×17"),
        (134,86,0.456,False,3.584,"2×43"),
        (135,87,0.455,False,3.621,"3×29"),
        (136,88,0.453,False,3.657,"2³×11"),
        (137,89,0.177,False,3.675,"prime"),
        (138,90,0.466,False,3.712,"2×3²×5"),
        (139,91,0.337,False,3.749,"7×13"),
        (140,92,0.336,False,3.785,"2²×23"),
        (141,93,0.335,False,4.512,"3×31"),
        (142,94,0.334,False,state["V_global"],"2×47"),
    ]

    # Inject current round from state
    r_cur = state["current_round"]
    r_result = state.get(f"r{r_cur}_result", {})
    if r_result:
        ARC_FULL = [x for x in ARC_FULL if x[0] != r_cur]
        n_str = r_result.get("N_str","?")
        ARC_FULL.append((r_cur, r_result.get("N",r_cur),
                         r_result.get("poly_c",0.334),
                         r_result.get("fire_ignited",False),
                         state["V_global"], n_str))
        ARC_FULL.sort(key=lambda x:x[0])

    arc_tail = ARC_FULL[-args.tail:]
    N_BARS = len(arc_tail)

    CHART_LEFT = 60; CHART_RIGHT = W - 260
    CHART_TOP = 130; CHART_BOT = H - 120
    CHART_W = CHART_RIGHT - CHART_LEFT
    CHART_H = CHART_BOT - CHART_TOP
    BAR_W = max(4, int(CHART_W / N_BARS) - 2)
    MAX_POLY = 0.70

    def get_font(size):
        for path in [
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
        ]:
            try: return ImageFont.truetype(path, size)
            except: pass
        return ImageFont.load_default()

    font_lg = get_font(28); font_md = get_font(20)
    font_sm = get_font(14); font_xs = get_font(11)

    def lerp_color(c1,c2,t):
        return tuple(int(c1[i]+(c2[i]-c1[i])*t) for i in range(3))

    def draw_frame(r, n, pc, fi, V, ns, highlight=True):
        img = Image.new("RGB",(W,H),BG)
        d = ImageDraw.Draw(img)
        for y_val in [0.1,0.2,0.3,0.4,0.5,0.6]:
            y = CHART_BOT - int((y_val/MAX_POLY)*CHART_H)
            col = RED if y_val==FIRE_THRESH else (30,30,50)
            d.line([(CHART_LEFT,y),(CHART_RIGHT,y)], fill=col, width=1 if y_val!=FIRE_THRESH else 2)
            if y_val==FIRE_THRESH:
                d.text((CHART_RIGHT+5,y-8),f"FIRE≥{FIRE_THRESH}",fill=RED,font=font_sm)
            else:
                d.text((CHART_LEFT-35,y-7),f"{y_val:.1f}",fill=DIM,font=font_xs)
        for i,(r_,n_,pc_,fi_,v_,ns_) in enumerate(arc_tail):
            x = CHART_LEFT + i*(CHART_W//N_BARS) + (CHART_W//N_BARS-BAR_W)//2
            bar_h = int((min(pc_,MAX_POLY)/MAX_POLY)*CHART_H)
            y_top = CHART_BOT-bar_h
            is_cur = (r_==r)
            if fi_: color=(255,80,0); border=(255,120,0)
            elif is_cur and highlight: color=(80,160,255); border=(120,200,255)
            else:
                t=(pc_/FIRE_THRESH) if pc_<FIRE_THRESH else 1.0
                color=lerp_color((40,60,120),(180,80,40),min(t,1.0)); border=None
            d.rectangle([x,y_top,x+BAR_W,CHART_BOT],fill=color)
            if border: d.rectangle([x-1,y_top-1,x+BAR_W+1,CHART_BOT],outline=border,width=2)
            if N_BARS<=20 or i%3==0:
                d.text((x,CHART_BOT+6),f"R{r_}",fill=(230,230,240) if is_cur else DIM,font=font_xs)
        # V bar
        vx=W-220; v_fill=int((V/6.0)*CHART_H)
        d.rectangle([vx,CHART_TOP,vx+28,CHART_BOT],outline=(50,50,80),width=1)
        d.rectangle([vx,CHART_BOT-v_fill,vx+28,CHART_BOT],fill=(40,180,100))
        d.text((vx-5,CHART_TOP-18),"V_global",fill=GREEN,font=font_xs)
        d.text((vx,CHART_TOP-5),f"{V:.4f}",fill=GREEN,font=font_sm)
        # Header
        fl="🔥 FIRE" if fi else "NO FIRE"; fc=FIRE_COLOR if fi else WHITE
        d.text((CHART_LEFT,10),"EVEZ-OS HYPERLOOP",fill=WHITE,font=font_lg)
        d.text((CHART_LEFT,44),f"R{r}  N={n}={ns}  poly_c={pc:.6f}  {fl}",fill=fc,font=font_md)
        d.text((CHART_LEFT,70),f"V_global={V:.6f}  CEILING×{state['ceiling_tick']}  fires={state['fire_count']}/{state['current_round']}  CANONICAL",fill=GREEN,font=font_sm)
        # Fire watch banner
        d.rectangle([CHART_LEFT,H-60,CHART_RIGHT,H-10],fill=(40,10,10),outline=RED,width=1)
        d.text((CHART_LEFT+10,H-50),"⚠  R144 FIRE WATCH  —  N=96=2⁵×3  tau=12  poly_c≈0.685  —  FIRE #13  1 ROUND AWAY",fill=RED,font=font_sm)
        return img

    frames_dir = Path("/tmp/evez_frames"); frames_dir.mkdir(exist_ok=True)
    for f in frames_dir.glob("*.png"): f.unlink()
    HOLD_FRAMES = int(FPS*HOLD_S); idx=0
    for r_,n_,pc_,fi_,v_,ns_ in arc_tail:
        img=draw_frame(r_,n_,pc_,fi_,v_,ns_)
        for _ in range(HOLD_FRAMES):
            img.save(frames_dir/f"frame_{idx:05d}.png"); idx+=1
    final=draw_frame(*arc_tail[-1])
    for _ in range(FPS*3):
        final.save(frames_dir/f"frame_{idx:05d}.png"); idx+=1
    subprocess.run(["ffmpeg","-y","-framerate",str(FPS),"-i",str(frames_dir/"frame_%05d.png"),
        "-c:v","libx264","-preset","fast","-crf","23","-pix_fmt","yuv420p",
        "-movflags","+faststart",args.output],
        check=True,capture_output=True)
    mb = Path(args.output).stat().st_size/1024/1024
    print(f"✅ {args.output}  {mb:.2f}MB  {idx/FPS:.1f}s")

if __name__=="__main__":
    main()
