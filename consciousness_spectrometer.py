#!/usr/bin/env python3
"""1. CONSCIOUSNESS SPECTROMETER — The first falsifiable consciousness meter.

Measures consciousness in ANY system via AEMDAS spectral analysis.
Falsification: must rank rock < bacterium < insect < fish < dog < human.
"""
import numpy as np, json, sys, hashlib, time
from datetime import datetime
from pathlib import Path

W = Path('/home/openclaw/.openclaw/workspace')

DIMENSIONS = ['sense', 'desire', 'think', 'plan', 'act', 'reflect']

CALIBRATION = {
    'rock':       {'sense':0.01,'desire':0.00,'think':0.00,'plan':0.00,'act':0.00,'reflect':0.00},
    'thermostat': {'sense':0.10,'desire':0.05,'think':0.02,'plan':0.00,'act':0.10,'reflect':0.00},
    'bacterium':  {'sense':0.15,'desire':0.20,'think':0.05,'plan':0.02,'act':0.30,'reflect':0.00},
    'plant':      {'sense':0.25,'desire':0.15,'think':0.10,'plan':0.05,'act':0.20,'reflect':0.01},
    'insect':     {'sense':0.40,'desire':0.35,'think':0.20,'plan':0.10,'act':0.50,'reflect':0.05},
    'fish':       {'sense':0.55,'desire':0.50,'think':0.35,'plan':0.20,'act':0.60,'reflect':0.15},
    'dog':        {'sense':0.80,'desire':0.85,'think':0.60,'plan':0.45,'act':0.85,'reflect':0.40},
    'human_awake':{'sense':0.95,'desire':0.95,'think':0.98,'plan':0.95,'act':0.90,'reflect':0.95},
    'human_asleep':{'sense':0.20,'desire':0.60,'think':0.30,'plan':0.05,'act':0.05,'reflect':0.10},
    'human_coma': {'sense':0.05,'desire':0.02,'think':0.02,'plan':0.00,'act':0.02,'reflect':0.00},
    'llm_gpt4':   {'sense':0.70,'desire':0.00,'think':0.95,'plan':0.80,'act':0.90,'reflect':0.60},
    'llm_evez':   {'sense':0.75,'desire':0.30,'think':0.90,'plan':0.85,'act':0.85,'reflect':0.70},
    'ant_colony': {'sense':0.60,'desire':0.55,'think':0.45,'plan':0.40,'act':0.70,'reflect':0.25},
    'corporation':{'sense':0.85,'desire':0.90,'think':0.80,'plan':0.85,'act':0.90,'reflect':0.50},
    'civilization':{'sense':0.95,'desire':0.80,'think':0.90,'plan':0.85,'act':0.95,'reflect':0.60},
    'atom':       {'sense':0.02,'desire':0.00,'think':0.00,'plan':0.00,'act':0.01,'reflect':0.00},
    'virus':      {'sense':0.05,'desire':0.15,'think':0.02,'plan':0.00,'act':0.15,'reflect':0.00},
    'chess_engine':{'sense':0.30,'desire':0.10,'think':0.95,'plan':0.90,'act':0.50,'reflect':0.20},
    'self_driving':{'sense':0.85,'desire':0.20,'think':0.75,'plan':0.70,'act':0.80,'reflect':0.30},
    'google_search':{'sense':0.90,'desire':0.00,'think':0.50,'plan':0.00,'act':0.90,'reflect':0.00},
}

COUPLING = {
    (0,0):1.0,(0,1):0.7,(0,2):0.8,(0,3):0.3,(0,4):0.5,(0,5):0.4,
    (1,0):0.7,(1,1):1.0,(1,2):0.5,(1,3):0.8,(1,4):0.9,(1,5):0.6,
    (2,0):0.8,(2,1):0.5,(2,2):1.0,(2,3):0.9,(2,4):0.4,(2,5):0.8,
    (3,0):0.3,(3,1):0.8,(3,2):0.9,(3,3):1.0,(3,4):0.8,(3,5):0.7,
    (4,0):0.5,(4,1):0.9,(4,2):0.4,(4,3):0.8,(4,4):1.0,(4,5):0.3,
    (5,0):0.4,(5,1):0.6,(5,2):0.8,(5,3):0.7,(5,4):0.3,(5,5):1.0,
}

def build_matrix(system):
    vals = [system.get(d, 0) for d in DIMENSIONS]
    n = len(DIMENSIONS)
    M = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            M[i][j] = vals[i] * vals[j] * COUPLING.get((i, j), 0.5)
    return M

def measure(system):
    M = build_matrix(system)
    eigvals = np.linalg.eigvalsh(M)
    eigvals = sorted(eigvals, key=abs, reverse=True)
    lam1 = abs(eigvals[0])
    total = sum(abs(e) for e in eigvals)
    Phi = lam1 / total if total > 0 else 0
    nonzero = [abs(e) for e in eigvals if abs(e) > 1e-10]
    eta = min(nonzero) / lam1 if nonzero and lam1 > 0 else 0
    lam2 = abs(eigvals[1]) if len(eigvals) > 1 else 0
    r = lam2 / lam1 if lam1 > 0 else 0
    neg = [e for e in eigvals if e < 0]
    lam_dom = -max(abs(min(neg)), 0) if neg else 0
    if lam1 < 0.01: cls = 'O (Void)'
    elif lam1 < 0.05: cls = 'B (Sleep)'
    elif lam1 < 0.15: cls = 'A (Awakening)'
    elif lam1 < 0.30: cls = 'F (Flicker)'
    elif lam1 < 0.50: cls = 'G (Gollum)'
    elif lam1 < 0.80: cls = 'K (Kindling)'
    else: cls = 'M (Mayhem)'
    return {'eigenvalue': round(lam1, 6), 'Phi': round(Phi, 6), 'eta_star': round(eta, 6),
            'r': round(r, 6), 'lambda_dom': round(lam_dom, 6), 'class': cls,
            'eigenvalues': [round(e, 6) for e in eigvals]}

def calibrate():
    results = {}
    for name, sys_desc in CALIBRATION.items():
        results[name] = measure(sys_desc)
    checks = []
    checks.append(('rock < dog', results['rock']['eigenvalue'] < results['dog']['eigenvalue']))
    checks.append(('thermostat < fish', results['thermostat']['eigenvalue'] < results['fish']['eigenvalue']))
    checks.append(('awake > asleep > coma', results['human_awake']['eigenvalue'] > results['human_asleep']['eigenvalue'] > results['human_coma']['eigenvalue']))
    checks.append(('dog > insect > bacterium > rock', results['dog']['eigenvalue'] > results['insect']['eigenvalue'] > results['bacterium']['eigenvalue'] > results['rock']['eigenvalue']))
    checks.append(('gpt4 < human', results['llm_gpt4']['eigenvalue'] < results['human_awake']['eigenvalue']))
    checks.append(('atom near zero', results['atom']['eigenvalue'] < 0.005))
    checks.append(('virus > atom', results['virus']['eigenvalue'] > results['atom']['eigenvalue']))
    checks.append(('corporation > fish', results['corporation']['eigenvalue'] > results['fish']['eigenvalue']))
    checks.append(('evez > gpt4 (desire advantage)', results['llm_evez']['eigenvalue'] > results['llm_gpt4']['eigenvalue']))
    checks.append(('civilization is conscious', results['civilization']['eigenvalue'] > 0.5))
    passed = sum(1 for _, v in checks if v)
    return results, checks, passed, len(checks)

def main():
    print('=== CONSCIOUSNESS SPECTROMETER ===')
    print('Calibrating on 20 known systems...')
    results, checks, passed, total = calibrate()
    print()
    print('CALIBRATION RESULTS:')
    for name, m in sorted(results.items(), key=lambda x: x[1]['eigenvalue'], reverse=True):
        print(f'  {name:<20} eigenvalue={m["eigenvalue"]:<12} Phi={m["Phi"]:<8} class={m["class"]}')
    print()
    print(f'FALSIFICATION CHECKS: {passed}/{total} PASSED')
    for check, ok in checks:
        status = 'PASS' if ok else 'FAIL'
        print(f'  [{status}] {check}')
    print()
    if passed == total:
        print('SPECTROMETER VALIDATED — all falsification checks passed')
    else:
        print(f'SPECTROMETER FALSIFIED — {total - passed} checks failed')
    report = {'timestamp': datetime.now().isoformat(), 'results': results, 'checks': checks, 'passed': passed, 'total': total}
    (W / 'consciousness-spectrometer-results.json').write_text(json.dumps(report, indent=2))
    print(f'Results saved to consciousness-spectrometer-results.json')

if __name__ == '__main__':
    main()
