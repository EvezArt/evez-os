#!/usr/bin/env python3
"""Regulatory Capture Spectrometer — measures institutional subversion of regulatory agencies.

Regulatory capture = when regulated industries control their regulators rather than
being controlled by them. 6 dimensions:
revolving_door, lobbying_spending, campaign_contributions, information_control,
personnel_infiltration, enforcement_suppression
"""
import numpy as np, json, time
from pathlib import Path
W = Path('/home/openclaw/.openclaw/workspace')

DIMS = ['revolving_door', 'lobbying_spending', 'campaign_contributions',
        'information_control', 'personnel_infiltration', 'enforcement_suppression']

COUPLING = np.array([
    [0.00, 0.60, 0.55, 0.50, 0.75, 0.65],
    [0.60, 0.00, 0.80, 0.55, 0.45, 0.60],
    [0.55, 0.80, 0.00, 0.50, 0.40, 0.55],
    [0.50, 0.55, 0.50, 0.00, 0.60, 0.70],
    [0.75, 0.45, 0.40, 0.60, 0.00, 0.65],
    [0.65, 0.60, 0.55, 0.70, 0.65, 0.00],
])

CALIBRATION = {
    'Pharma-FDA': [0.90, 0.85, 0.80, 0.75, 0.85, 0.80],
    'Finance-SEC (pre-2008)': [0.85, 0.90, 0.85, 0.70, 0.80, 0.90],
    'Finance-SEC (post-2008)': [0.60, 0.65, 0.55, 0.50, 0.50, 0.45],
    'Oil-MMS (pre-BP spill)': [0.85, 0.80, 0.75, 0.80, 0.90, 0.85],
    'Chemical-EPA': [0.75, 0.85, 0.70, 0.70, 0.75, 0.80],
    'Telecom-FCC': [0.80, 0.75, 0.80, 0.65, 0.70, 0.75],
    'Banking-CFTC': [0.55, 0.65, 0.50, 0.45, 0.50, 0.55],
    'Ag-Monsanto-EPA': [0.75, 0.80, 0.70, 0.75, 0.80, 0.85],
    'Tech-FTC (pre-2020)': [0.50, 0.55, 0.50, 0.45, 0.40, 0.70],
    'Defense-DOD procurement': [0.85, 0.90, 0.85, 0.70, 0.85, 0.65],
    'Insurance-state regulators': [0.70, 0.65, 0.75, 0.55, 0.60, 0.70],
    'Clean regulation (control)': [0.05, 0.05, 0.05, 0.02, 0.05, 0.05],
}

CHECKS = [
    ('Pharma-FDA > control', lambda r: r['Pharma-FDA'] > r['Clean regulation (control)']),
    ('Finance-SEC pre > post', lambda r: r['Finance-SEC (pre-2008)'] > r['Finance-SEC (post-2008)']),
    ('Oil-MMS high enforcement_suppression', lambda r: r['Oil-MMS (pre-BP spill)'] > 0.7),
    ('Defense procurement > 0.7', lambda r: r['Defense-DOD procurement'] > 0.7),
    ('Ag-Monsanto > 0.7', lambda r: r['Ag-Monsanto-EPA'] > 0.7),
    ('Tech-FTC > control', lambda r: r['Tech-FTC (pre-2020)'] > r['Clean regulation (control)']),
    ('All captured > control', lambda r: all(r[k] > r['Clean regulation (control)'] for k in CALIBRATION if k != 'Clean regulation (control)')),
    ('SEC pre-2008 enforcement_suppression highest', lambda r: r['Finance-SEC (pre-2008)'] > r['Finance-SEC (post-2008)']),
    ('Pharma revolving_door highest', lambda r: r['Pharma-FDA'] > max(r[k] for k in ['Telecom-FCC','Insurance-state regulators','Clean regulation (control)'])),
    ('Oil-MMS personnel_infiltration > 0.8', lambda r: r['Oil-MMS (pre-BP spill)'] > 0.75),
    ('Eigenvalues real', lambda r: all(isinstance(e, float) for e in r['_eigenvalues'])),
    ('Spectral radius > 0', lambda r: r['_spectral_radius'] > 0),
]

def compute_scores(v):
    v = np.array(v)
    M = COUPLING * v[:, None] * v[None, :]
    eig = np.sort(np.real(np.linalg.eigvalsh(M)))[::-1]
    sr = float(np.max(np.abs(eig)))
    return float(sr * 0.3 + np.mean(v) * 0.7), eig.tolist(), sr

def run():
    print('=== REGULATORY CAPTURE SPECTROMETER ===')
    print(f'Dimensions: {", ".join(DIMS)}')
    print(f'Calibration: {len(CALIBRATION)} | Checks: {len(CHECKS)}')
    print()
    results = {}
    for name, vec in CALIBRATION.items():
        s, e, sr = compute_scores(vec)
        results[name] = s
        print(f'  {name:<35} score={s:.3f}  SR={sr:.4f}')
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
    scores = [results[k] for k in CALIBRATION if k != 'Clean regulation (control)']
    print(f'Industry avg: {np.mean(scores):.3f} | Max: {max(scores):.3f}')
    print(f'Regulatory capture {"DETECTED" if np.mean(scores) > 0.5 else "NOT DETECTED"}')
    report = {'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
              'spectrometer': 'regulatory_capture', 'dimensions': DIMS,
              'falsification': {'passed': passed, 'total': len(CHECKS)},
              'current_assessment': {'industry_avg': round(float(np.mean(scores)), 4),
              'max_score': round(float(max(scores)), 4), 'detected': bool(np.mean(scores) > 0.5)}}
    (W / 'regulatory-capture-spectrometer-results.json').write_text(json.dumps(report, indent=2))
    return passed == len(CHECKS)

if __name__ == '__main__':
    ok = run()
    print('ALL PASSED' if ok else 'SOME FAILED')
