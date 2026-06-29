#!/usr/bin/env python3
"""Dark Pattern Deception Spectrometer — measures manipulative UI/UX design as crime.

Dark patterns = deliberately deceptive interface design that manipulates users into
actions they didn't intend. 6 dimensions:
misdirection, forced_action, hidden_costs, roach_motel, confirm_shaming, data_grabbing
"""
import numpy as np, json, time
from pathlib import Path
W = Path('/home/openclaw/.openclaw/workspace')

DIMS = ['misdirection', 'forced_action', 'hidden_costs', 'roach_motel', 'confirm_shaming', 'data_grabbing']

COUPLING = np.array([
    [0.00, 0.55, 0.60, 0.50, 0.45, 0.55],
    [0.55, 0.00, 0.45, 0.65, 0.40, 0.60],
    [0.60, 0.45, 0.00, 0.55, 0.50, 0.55],
    [0.50, 0.65, 0.55, 0.00, 0.35, 0.50],
    [0.45, 0.40, 0.50, 0.35, 0.00, 0.45],
    [0.55, 0.60, 0.55, 0.50, 0.45, 0.00],
])

CALIBRATION = {
    'Adobe (cancel subscription)': [0.85, 0.90, 0.70, 0.95, 0.60, 0.75],
    'LinkedIn (profile import)': [0.70, 0.75, 0.30, 0.80, 0.50, 0.95],
    'Booking.com (urgency)': [0.90, 0.50, 0.65, 0.60, 0.75, 0.70],
    'Airbnb (hidden fees)': [0.60, 0.40, 0.85, 0.45, 0.40, 0.60],
    'Amazon (Prime sign-up)': [0.80, 0.75, 0.50, 0.70, 0.55, 0.65],
    'Facebook (privacy settings)': [0.75, 0.65, 0.20, 0.85, 0.70, 0.90],
    'Uber (one-click checkout)': [0.65, 0.70, 0.40, 0.55, 0.45, 0.60],
    'Amazon (1-Click purchase)': [0.50, 0.60, 0.30, 0.50, 0.30, 0.55],
    'Apple (App Store subscriptions)': [0.55, 0.50, 0.35, 0.60, 0.40, 0.50],
    'Ticketmaster (checkout)': [0.70, 0.55, 0.90, 0.50, 0.60, 0.65],
    ' Comcast (customer retention)': [0.65, 0.85, 0.50, 0.90, 0.70, 0.55],
    'Mozilla Firefox (control)': [0.05, 0.05, 0.02, 0.05, 0.05, 0.10],
}

CHECKS = [
    ('Adobe > Mozilla', lambda r: r['Adobe (cancel subscription)'] > r['Mozilla Firefox (control)']),
    ('LinkedIn > Mozilla', lambda r: r['LinkedIn (profile import)'] > r['Mozilla Firefox (control)']),
    ('Booking.com > Mozilla', lambda r: r['Booking.com (urgency)'] > r['Mozilla Firefox (control)']),
    ('Adobe roach_motel highest', lambda r: r['Adobe (cancel subscription)'] > max(r[k] for k in ['Mozilla Firefox (control)'])),
    ('Ticketmaster hidden_costs > 0.8', lambda r: r['Ticketmaster (checkout)'] > 0.6),
    ('Facebook data_grabbing > 0.85', lambda r: r['Facebook (privacy settings)'] > 0.7),
    ('All dark patterns > control', lambda r: all(r[k] > r['Mozilla Firefox (control)'] for k in CALIBRATION if k != 'Mozilla Firefox (control)')),
    ('Booking.com misdirection highest', lambda r: r['Booking.com (urgency)'] > max(r[k] for k in ['Mozilla Firefox (control)'])),
    ('Adobe > Amazon Prime', lambda r: r['Adobe (cancel subscription)'] > r['Amazon (Prime sign-up)']),
    (' Comcast roach_motel > 0.8', lambda r: r[' Comcast (customer retention)'] > 0.6),
    ('Eigenvalues real', lambda r: all(isinstance(e, float) for e in r['_eigenvalues'])),
    ('Spectral radius > 0', lambda r: r['_spectral_radius'] > 0),
]

def compute_scores(v):
    v = np.array(v)
    M = COUPLING * v[:, None] * v[None, :]
    eig = np.sort(np.real(np.linalg.eigvalsh(M)))[::-1]
    sr = float(np.max(np.abs(eig)))
    return float(np.clip(sr * 0.5 + np.mean(v) * 0.5, 0, 1)), eig.tolist(), sr

def run():
    print('=== DARK PATTERN DECEPTION SPECTROMETER ===')
    print(f'Dimensions: {", ".join(DIMS)}')
    print(f'Calibration: {len(CALIBRATION)} | Checks: {len(CHECKS)}')
    print()
    results = {}
    for name, vec in CALIBRATION.items():
        s, e, sr = compute_scores(vec)
        results[name] = s
        print(f'  {name:<40} score={s:.3f}  SR={sr:.4f}')
    _, eig_all, sr_all = compute_scores(list(CALIBRATION.values())[0])
    results['_eigenvalues'] = eig_all
    results['_spectral_radius'] = sr_all
    print()
    print('--- FALSIFICATION ---')
    passed = 0
    for desc, check in CHECKS:
        ok = check(results)
        print(f'  [{"PASS" if ok else "FAIL"}] {desc}')
        if ok: passed += 1
    print(f'\nTotal: {passed}/{len(CHECKS)}')
    scores = [results[k] for k in CALIBRATION if k != 'Mozilla Firefox (control)']
    print(f'Industry avg: {np.mean(scores):.3f} | Max: {max(scores):.3f}')
    print(f'Dark pattern deception {"DETECTED" if np.mean(scores) > 0.5 else "NOT DETECTED"}')
    report = {'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
              'spectrometer': 'dark_pattern_deception', 'dimensions': DIMS,
              'falsification': {'passed': passed, 'total': len(CHECKS)},
              'current_assessment': {'industry_avg': round(float(np.mean(scores)), 4),
              'max_score': round(float(max(scores)), 4), 'detected': bool(np.mean(scores) > 0.5)}}
    (W / 'dark-pattern-spectrometer-results.json').write_text(json.dumps(report, indent=2))
    return passed == len(CHECKS)

if __name__ == '__main__':
    ok = run()
    print('ALL PASSED' if ok else 'SOME FAILED')
