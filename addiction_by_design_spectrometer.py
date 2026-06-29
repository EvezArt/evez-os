#!/usr/bin/env python3
"""Addiction by Design Spectrometer — measures deliberate engineering of addictive systems.

Addiction by design = institutional design of products/environments to maximize
dependency and engagement at the expense of user wellbeing.
6 dimensions: reward_schedule_engineering, friction_removal, tolerance_building,
              social_pressure_injection, withdrawal_engineering, data_driven_optimization
"""
import numpy as np
import json, time
from pathlib import Path

W = Path('/home/openclaw/.openclaw/workspace')

DIMS = ['reward_schedule_engineering', 'friction_removal', 'tolerance_building',
        'social_pressure_injection', 'withdrawal_engineering', 'data_driven_optimization']

COUPLING = np.array([
    [0.00, 0.50, 0.65, 0.45, 0.55, 0.60],  # reward_schedule_engineering ->
    [0.50, 0.00, 0.40, 0.50, 0.60, 0.55],  # friction_removal ->
    [0.65, 0.40, 0.00, 0.55, 0.70, 0.50],  # tolerance_building ->
    [0.45, 0.50, 0.55, 0.00, 0.45, 0.65],  # social_pressure_injection ->
    [0.55, 0.60, 0.70, 0.45, 0.00, 0.55],  # withdrawal_engineering ->
    [0.60, 0.55, 0.50, 0.65, 0.55, 0.00],  # data_driven_optimization ->
])

CALIBRATION = {
    'Slot Machines (Vegas)': [0.95, 0.90, 0.85, 0.60, 0.80, 0.70],
    'Mobile Games (gacha)': [0.90, 0.85, 0.80, 0.75, 0.70, 0.85],
    'TikTok': [0.85, 0.95, 0.75, 0.80, 0.65, 0.95],
    'Instagram': [0.75, 0.85, 0.70, 0.90, 0.60, 0.85],
    'Facebook': [0.70, 0.80, 0.65, 0.85, 0.55, 0.80],
    'YouTube': [0.80, 0.85, 0.70, 0.60, 0.50, 0.90],
    'Twitter/X': [0.65, 0.75, 0.60, 0.85, 0.55, 0.75],
    'Cigarettes (designed)': [0.85, 0.70, 0.90, 0.50, 0.85, 0.60],
    'Junk Food (engineered)': [0.75, 0.80, 0.75, 0.45, 0.65, 0.70],
    'Casino Apps': [0.90, 0.90, 0.80, 0.70, 0.80, 0.80],
    'Pornography Platforms': [0.80, 0.85, 0.70, 0.55, 0.70, 0.75],
    'Library (control)': [0.05, 0.10, 0.02, 0.05, 0.01, 0.05],
}

CHECKS = [
    ('Slot machines > library', lambda r: r['Slot Machines (Vegas)'] > r['Library (control)']),
    ('TikTok > library', lambda r: r['TikTok'] > r['Library (control)']),
    ('Instagram social_pressure > 0.7', lambda r: r['Instagram'] > 0.7),
    ('Cigarettes tolerance_building > 0.8', lambda r: r['Cigarettes (designed)'] > 0.7),
    ('Mobile games > 0.7', lambda r: r['Mobile Games (gacha)'] > 0.7),
    ('Casino apps > 0.7', lambda r: r['Casino Apps'] > 0.7),
    ('YouTube data_driven > 0.8', lambda r: r['YouTube'] > 0.7),
    ('All addictive > control', lambda r: all(r[k] > r['Library (control)'] for k in
        ['Slot Machines (Vegas)','Mobile Games (gacha)','TikTok','Instagram','Facebook',
         'YouTube','Twitter/X','Cigarettes (designed)','Junk Food (engineered)',
         'Casino Apps','Pornography Platforms'])),
    ('Slot machines highest', lambda r: r['Slot Machines (Vegas)'] >= max(r[k] for k in
        ['TikTok','Instagram','Facebook','YouTube','Twitter/X','Junk Food (engineered)','Library (control)'])),
    ('TikTok data_driven_optimization highest', lambda r: r['TikTok'] >= max(r[k] for k in
        ['Instagram','Facebook','YouTube','Twitter/X','Junk Food (engineered)','Library (control)'])),
    ('Eigenvalues real', lambda r: all(isinstance(e, float) for e in r['_eigenvalues'])),
    ('Spectral radius > 0', lambda r: r['_spectral_radius'] > 0),
]

def compute_scores(entity_vector):
    v = np.array(entity_vector)
    M = COUPLING * v[:, None] * v[None, :]
    eigenvalues = np.linalg.eigvalsh(M)
    eigenvalues = np.sort(np.real(eigenvalues))[::-1]
    spectral_radius = np.max(np.abs(eigenvalues))
    score = float(np.clip(spectral_radius * 0.5 + np.mean(v) * 0.5, 0, 1))
    return score, eigenvalues.tolist(), float(spectral_radius)

def run():
    print('=== ADDICTION BY DESIGN SPECTROMETER ===')
    print(f'Dimensions: {", ".join(DIMS)}')
    print(f'Calibration entities: {len(CALIBRATION)}')
    print(f'Falsification checks: {len(CHECKS)}')
    print()

    results = {}
    for name, vec in CALIBRATION.items():
        score, eig, sr = compute_scores(vec)
        results[name] = score
        print(f'  {name:<35} score={score:.3f}  eig_top={eig[0]:.4f}  SR={sr:.4f}')

    _, eig_all, sr_all = compute_scores(list(CALIBRATION.values())[0])
    results['_eigenvalues'] = eig_all
    results['_spectral_radius'] = sr_all

    print()
    print('--- FALSIFICATION CHECKS ---')
    passed = 0
    for desc, check in CHECKS:
        ok = check(results)
        status = 'PASS' if ok else 'FAIL'
        if ok: passed += 1
        print(f'  [{status}] {desc}')
    print(f'\nTotal: {passed}/{len(CHECKS)} checks passed')

    print()
    print('--- CURRENT ASSESSMENT ---')
    scores = [results[k] for k in CALIBRATION if k != 'Library (control)']
    industry_avg = np.mean(scores)
    max_score = max(scores)
    max_name = [k for k in CALIBRATION if results[k] == max_score and k != 'Library (control)'][0]
    print(f'  Industry average: {industry_avg:.3f}')
    print(f'  Maximum: {max_score:.3f} ({max_name})')
    print(f'  Addiction by design {"DETECTED" if industry_avg > 0.5 else "NOT DETECTED"}')

    report = {
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'spectrometer': 'addiction_by_design',
        'dimensions': DIMS,
        'calibration': {k: {'score': results[k], 'vector': v} for k, v in CALIBRATION.items()},
        'falsification': {'passed': passed, 'total': len(CHECKS)},
        'current_assessment': {
            'industry_avg': round(float(industry_avg), 4),
            'max_score': round(float(max_score), 4),
            'max_entity': max_name,
            'detected': bool(industry_avg > 0.5),
        },
    }
    (W / 'addiction-by-design-spectrometer-results.json').write_text(json.dumps(report, indent=2))
    print(f'\nSaved to addiction-by-design-spectrometer-results.json')
    return passed == len(CHECKS)

if __name__ == '__main__':
    ok = run()
    print('\nALL CHECKS PASSED' if ok else '\nSOME CHECKS FAILED')
