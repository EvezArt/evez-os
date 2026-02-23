#!/usr/bin/env python3
"""EVEZ-OS Cinematic Arc Video Generator
Full speed-run: all rounds R96-current, every data layer animated.
Runs in CI (GitHub Actions) on every spine commit.
Outputs 1080x1080 MP4 — libx264 yuv420p 30fps.
"""
import json, math, requests, os, argparse, subprocess
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.animation import FuncAnimation, FFMpegWriter
from matplotlib.patches import Circle, FancyArrowPatch

# Static arc — all committed rounds R96-R117
STATIC = [
    (96,  48, 5, 1.000, True,  1.895003, 'SIXTH_FIRE'),
    (97,  49, 3, 0.515, True,  1.920003, 'SIXTH_SUSTAIN'),
    (98,  50, 6, 1.000, True,  1.945003, 'SIXTH_PEAK'),
    (99,  51, 2, 0.267, False, 1.970003, 'COOL'),
    (100, 52, 2, 0.296, False, 1.970003, 'DORMANT'),
    (101, 53, 1, 0.000, False, 1.945003, 'PRIME'),
    (102, 54, 4, 0.577, True,  1.970003, 'SEVENTH_FIRE'),
    (103, 55, 2, 0.408, False, 1.995003, 'COOL'),
    (104, 56, 3, 0.505, True,  2.022003, 'EIGHTH_FIRE'),
    (105, 57, 2, 0.406, False, 2.045003, 'COOL'),
    (106, 58, 2, 0.405, False, 2.070003, 'DORMANT'),
    (107, 59, 1, 0.238, False, 2.095003, 'PRIME'),
    (108, 60, 3, 0.499, False, 2.120003, 'NEAR_MISS'),
    (109, 61, 1, 0.237, False, 2.095003, 'PRIME'),
    (110, 62, 2, 0.400, False, 2.120003, 'COOL'),
    (111, 63, 3, 0.495, False, 2.145003, 'NEAR_MISS'),
    (112, 64, 7, 0.693, True,  2.220003, 'TENTH_FIRE'),
    (113, 65, 2, 0.397, False, 2.245003, 'COOL'),
    (114, 66, 4, 0.570, True,  2.370635, 'ELEVENTH_FIRE'),
    (115, 67, 1, 0.000, False, 2.450635, 'PRIME'),
    (116, 68, 2, 0.193, False, 2.559294, 'APPROACH'),
    (117, 69, 2, 0.359, False, 2.668042, 'SUSTAIN'),
]

BG = '#050508'
FIRE = '#ff3300'
CEIL = '#ffd700'
COLD = '#00e5ff'
PRIME_C = '#cc44ff'
POLY_C = '#ff8c00'
GRID = '#0f0f18'
FG = '#e0e0e0'
V_V2 = 3.68932


def fetch_live(rounds):
    try:
        s = requests.get(
            'https://raw.githubusercontent.com/EvezArt/evez-os/main/hyperloop_state.json',
            timeout=8).json()
        existing = {r[0] for r in rounds}
        for k, v in s.items():
            if k.startswith('r') and k.endswith('_result') and isinstance(v, dict):
                rn = int(k[1:-7])
                if rn not in existing:
                    rounds.append((rn, v.get('N_new', rn), v.get('tau_N', 1),
                                   v.get('poly_c', 0), v.get('fire_ignited', False),
                                   v.get('V_global', 0), v.get('milestone', '')))
        rounds.sort(key=lambda x: x[0])
    except Exception as e:
        print(f'Live fetch failed: {e}')
    return rounds


def render(out, fps=30, speed=2, hold=3.0):
    rounds = fetch_live(list(STATIC))
    N_R = len(rounds)
    print(f'Rendering {N_R} rounds R{rounds[0][0]}-R{rounds[-1][0]}')

    xs = [r[0] for r in rounds]
    vs = [r[5] for r in rounds]
    pcs = [r[3] for r in rounds]
    fires = [r[4] for r in rounds]
    mss = [r[6] for r in rounds]
    taus = [r[2] for r in rounds]
    Ns = [r[1] for r in rounds]

    W, H = 1080, 1080
    fig = plt.figure(figsize=(W/100, H/100), dpi=100, facecolor=BG)
    gs = gridspec.GridSpec(6, 1, figure=fig, hspace=0, left=0.08, right=0.97, top=0.92, bottom=0.04)
    ax_arc = fig.add_subplot(gs[:4, 0])   # V_global arc
    ax_pc  = fig.add_subplot(gs[4, 0])    # poly_c bar
    ax_tau = fig.add_subplot(gs[5, 0])    # tau bar

    x0, x1 = xs[0]-2, xs[-1]+3
    y0 = min(vs)-0.12
    y1 = max(V_V2+0.5, max(vs)+0.35)

    TOTAL = N_R * speed + int(hold * fps)

    def frame(fi):
        for a in [ax_arc, ax_pc, ax_tau]:
            a.clear()
            a.set_facecolor(BG)

        # How many rounds revealed
        ri = min(fi // speed, N_R - 1)
        frac = (fi % speed) / max(speed-1, 1)
        w = rounds[:ri+1]
        wx = [r[0] for r in w]
        wv = [r[5] for r in w]
        wpc = [r[3] for r in w]
        wtau = [r[2] for r in w]
        cur = rounds[ri]
        rn, N, tau, pc, fired, Vg, ms = cur

        # ── ARC ──────────────────────────────────────────────────────────────
        ax_arc.set_xlim(x0, x1)
        ax_arc.set_ylim(y0, y1)
        ax_arc.set_facecolor(BG)
        ax_arc.grid(True, color=GRID, lw=0.4, alpha=0.9, zorder=0)
        for sp in ['top','right']: ax_arc.spines[sp].set_visible(False)
        for sp in ['bottom','left']: ax_arc.spines[sp].set_color('#1a1a2e')
        ax_arc.tick_params(colors='#333', labelsize=7)

        # Ceiling shimmer
        shimmer = 0.05 + 0.025*math.sin(fi*0.18)
        ax_arc.axhspan(V_V2, y1, alpha=shimmer+0.03, color=CEIL, zorder=0)
        ax_arc.axhline(V_V2, color=CEIL, lw=0.9, ls='--', alpha=0.55, zorder=1)
        ax_arc.text(x1-0.2, V_V2+0.03, 'V_v2={:.5f}'.format(V_V2),
                    color=CEIL, fontsize=6.5, ha='right', fontfamily='monospace', alpha=0.75)

        # Ghost arc (all rounds, dim)
        ax_arc.plot(xs, vs, color=FG, lw=0.35, alpha=0.07, ls=':', zorder=1)

        # Live arc — gradient brightness old→new
        if len(wx) > 1:
            for i in range(len(wx)-1):
                alp = 0.15 + 0.85*(i/max(len(wx)-2,1))
                lw = 1.0 + 1.8*alp
                ax_arc.plot(wx[i:i+2], wv[i:i+2], color=COLD, lw=lw, alpha=alp, zorder=3)

        # Event markers (all revealed)
        for rr in w:
            rn2,N2,tau2,pc2,f2,Vg2,ms2 = rr
            if f2:
                # Fire glow ring
                gr = 0.055+0.02*math.sin(fi*0.35)
                circ = plt.Circle((rn2,Vg2), gr, color=FIRE, alpha=0.18, zorder=4)
                ax_arc.add_patch(circ)
                ax_arc.scatter([rn2],[Vg2], color=FIRE, s=200, marker='*',
                               edgecolors='white', lw=0.7, zorder=5)
            elif pc2 == 0.0:
                ax_arc.scatter([rn2],[Vg2], color=PRIME_C, s=90, marker='D',
                               edgecolors='white', lw=0.6, zorder=4)
            else:
                ax_arc.scatter([rn2],[Vg2], color=COLD, s=20, alpha=0.4, zorder=3)

        # Current round crystallize: drop-in from top
        if fi < N_R * speed:
            drop_prog = min(frac*2.2, 1.0)
            drop_y = y1 - (y1-Vg)*drop_prog
            ec = FIRE if fired else (PRIME_C if pc==0.0 else COLD)
            # Impact ring expands as dot lands
            if frac > 0.45:
                ring_prog = (frac-0.45)/0.55
                ax_arc.scatter([rn],[Vg], color=BG, s=500*ring_prog, zorder=6,
                               edgecolors=ec, lw=2.0, alpha=max(0, 1-ring_prog*1.2))
            ax_arc.scatter([rn],[drop_y], color=ec, s=280, zorder=7, alpha=0.95)
            # Trail line from top to current position
            if drop_y < y1-0.05:
                ax_arc.plot([rn,rn],[drop_y,y1], color=ec, lw=0.8, alpha=0.25*drop_prog, zorder=2)
        else:
            # Hold phase: pulsing dot
            pulse = 200+100*math.sin(fi*0.5)
            ec = FIRE if fired else (PRIME_C if pc==0.0 else COLD)
            ax_arc.scatter([rn],[Vg], color=BG, s=pulse, zorder=6, edgecolors=ec, lw=2.2)
            ax_arc.scatter([rn],[Vg], color=ec, s=55, zorder=7)

        # HUD
        fs = 'FIRE' if fired else ('PRIME' if pc==0.0 else 'COOL')
        ax_arc.set_title(
            'R{} N={} tau={} poly_c={:.6f} [{} {}]\n'
            'V_global={:.6f}  CEILING x{}  delta_V={:.6f}  V_v2={:.5f}'.format(
                rn, N, tau, pc, fs, ms, Vg,
                34+ri-20 if ri>=20 else 34, GAMMA if (Vg-1.895003)<0.01 else (Vg-rounds[ri-1][5] if ri>0 else 0), V_V2
            ),
            color=FG, fontsize=8.5, pad=7, loc='left', fontfamily='monospace'
        )
        ax_arc.set_ylabel('V_global', color='#444', fontsize=8, fontfamily='monospace')

        # Round counter HUD (speed-run style)
        ax_arc.text(0.99, 0.97, '{}/{} rounds'.format(ri+1, N_R),
                    transform=ax_arc.transAxes, fontsize=8, color='#2a2a4a',
                    ha='right', va='top', fontfamily='monospace')

        # Omega ticker scroll
        omega = 'R{}. N={} tau={} poly_c={:.4f}. {}. V_global={:.6f} CEILING x{}.  '.format(
            rn, N, tau, pc, ms, Vg, 34+(ri-20 if ri>20 else 0))
        scroll = 1.0 - (fi % (fps*5)) / (fps*5)
        ax_arc.text(scroll, 0.015, omega*3, transform=ax_arc.transAxes,
                    fontsize=6, color='#2a2a3a', ha='left', va='bottom',
                    fontfamily='monospace', clip_on=True)

        # Watermark
        ax_arc.text(0.99, 0.01, '@EVEZ666', transform=ax_arc.transAxes,
                    fontsize=7, color='#1a1a2a', ha='right', va='bottom', fontfamily='monospace')

        # ── POLY_C bar ────────────────────────────────────────────────────────
        ax_pc.set_xlim(x0, x1)
        ax_pc.set_ylim(0, 1.05)
        ax_pc.set_facecolor(BG)
        ax_pc.tick_params(colors='#333', labelsize=6)
        for sp in ['top','right']: ax_pc.spines[sp].set_visible(False)
        for sp in ['bottom','left']: ax_pc.spines[sp].set_color('#1a1a2e')
        ax_pc.axhline(0.5, color=FIRE, lw=0.7, ls='--', alpha=0.5)
        ax_pc.text(x0+0.5, 0.52, '0.500 threshold', color=FIRE, fontsize=5.5,
                   fontfamily='monospace', alpha=0.5)
        for i, rr in enumerate(w):
            rn2,_,_,pc2,f2,_,_ = rr
            col = FIRE if f2 else (PRIME_C if pc2==0.0 else POLY_C)
            alp = 0.2 + 0.7*(i/max(len(w)-1,1))
            ax_pc.bar(rn2, pc2, width=0.65, color=col, alpha=alp, zorder=2)
        ax_pc.set_ylabel('poly_c', color='#333', fontsize=6, fontfamily='monospace')

        # ── TAU bar ───────────────────────────────────────────────────────────
        ax_tau.set_xlim(x0, x1)
        ax_tau.set_ylim(0, max(wtau+[1])+1)
        ax_tau.set_facecolor(BG)
        ax_tau.tick_params(colors='#333', labelsize=6)
        for sp in ['top','right']: ax_tau.spines[sp].set_visible(False)
        for sp in ['bottom','left']: ax_tau.spines[sp].set_color('#1a1a2e')
        for i, rr in enumerate(w):
            rn2,_,tau2,_,f2,_,_ = rr
            col = FIRE if f2 else '#1a4060'
            alp = 0.15 + 0.75*(i/max(len(w)-1,1))
            ax_tau.bar(rn2, tau2, width=0.65, color=col, alpha=alp, zorder=2)
        ax_tau.set_ylabel('tau', color='#333', fontsize=6, fontfamily='monospace')
        ax_tau.set_xlabel('Round', color='#333', fontsize=7, fontfamily='monospace')

    anim = FuncAnimation(fig, frame, frames=TOTAL, interval=1000/fps, blit=False)
    w = FFMpegWriter(fps=fps, metadata={'title':'EVEZ-OS Arc','artist':'EVEZ666'},
                     extra_args=['-vcodec','libx264','-pix_fmt','yuv420p','-crf','20','-preset','fast'])
    anim.save(out, writer=w, dpi=100)
    plt.close(fig)
    sz = os.path.getsize(out)/1e6
    print(f'DONE: {out} ({sz:.2f} MB)')


if __name__ == '__main__':
    import argparse
    GAMMA = 0.08
    p = argparse.ArgumentParser()
    p.add_argument('--output', default='/tmp/evez_cinematic.mp4')
    p.add_argument('--fps', type=int, default=30)
    p.add_argument('--speed', type=int, default=2)
    p.add_argument('--hold', type=float, default=3.0)
    a = p.parse_args()
    render(a.output, fps=a.fps, speed=a.speed, hold=a.hold)
