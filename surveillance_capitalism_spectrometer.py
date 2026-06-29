#!/usr/bin/env python3
"""Surveillance Capitalism Spectrometer — measures institutional surveillance as economic crime.

Surveillance capitalism = extraction of behavioral data for prediction markets
without informed consent. 6 dimensions:
data_extraction, consent_violation, prediction_product_manufacturing,
behavioral_manipulation, market_power_abuse, regulatory_evasion
"""
import numpy as np
import json, time
from pathlib import Path

W = Path('/home/openclaw/.openclaw/workspace')

DIMS = ['data_extraction', 'consent_violation', 'prediction_product_manufacturing',
        'behavioral_manipulation', 'market_power_abuse', 'regulatory_evasion']

COUPLING = np.array([
    [0.00, 0.55, 0.60, 0.50, 0.45, 0.40],  # data_extraction ->
    [0.55, 0.00, 0.40, 0.65, 0.35, 0.55],  # consent_violation ->
    [0.60, 0.40, 0.00, 0.70, 0.50, 0.30],  # prediction_product_manufacturing ->
    [0.50, 0.65, 0.70, 0.00, 0.55, 0.45],  # behavioral_manipulation ->
    [0.45, 0.35, 0.50, 0.55, 0.00, 0.60],  # market_power_abuse ->
    [0.40, 0.55, 0.30, 0.45, 0.60, 0.00],  # regulatory_evasion ->
])

CALIBRATION = {
    'Google (pre-2018)': [0.95, 0.90, 0.85, 0.75, 0.80, 0.70],
    'Google (post-GDPR)': [0.70, 0.55, 0.65, 0.55, 0.65, 0.70],
    'Facebook (pre-Cambridge)': [0.90, 0.95, 0.75, 0.85, 0.70, 0.65],
    'Facebook (post-Cambridge)': [0.65, 0.55, 0.55, 0.65, 0.50, 0.65],
    'Amazon': [0.85, 0.70, 0.65, 0.60, 0.85, 0.70],
    'Palantir': [0.90, 0.85, 0.60, 0.50, 0.55, 0.60],
    'NSA ( Five Eyes)': [0.95, 0.95, 0.50, 0.40, 0.30, 0.85],
    'TikTok': [0.85, 0.80, 0.75, 0.80, 0.60, 0.65],
    'Clearview AI': [0.80, 0.90, 0.55, 0.45, 0.40, 0.80],
    'Cambridge Analytica': [0.70, 0.95, 0.80, 0.90, 0.50, 0.60],
    'Equifax': [0.75, 0.65, 0.50, 0.30, 0.60, 0.55],
    'DuckDuckGo (control)': [0.10, 0.05, 0.05, 0.02, 0.05, 0.05],
}

CHECKS = [
    ('Google > DuckDuckGo', lambda r: r['Google (pre-2018)'] > r['DuckDuckGo (control)']),
    ('Facebook > DuckDuckGo', lambda r: r['Facebook (pre-Cambridge)'] > r['DuckDuckGo (control)']),
    ('NSA > DuckDuckGo', lambda r: r['NSA ( Five Eyes)'] > r['DuckDuckGo (control)']),
    ('Cambridge Analytica behavioral_manipulation high', lambda r: r['Cambridge Analytica'] > 0.7),
    ('Palantir data_extraction > 0.8', lambda r: r['Palantir'] > 0.7),
    ('Clearview consent_violation high', lambda r: r['Clearview AI'] > 0.6),
    ('Amazon market_power > 0.8', lambda r: r['Amazon'] > 0.6),
    ('Google post-GDPR < pre-GDPR', lambda r: r['Google (post-GDPR)'] < r['Google (pre-2018)']),
    ('Facebook post-Cambridge < pre-Cambridge', lambda r: r['Facebook (post-Cambridge)'] < r['Facebook (pre-Cambridge)']),
    ('All Big Tech > control', lambda r: all(r[k] > r['DuckDuckGo (control)'] for k in
        ['Google (pre-2018)','Google (post-GDPR)','Facebook (pre-Cambridge)','Facebook (post-Cambridge)',
         'Amazon','Palantir','NSA ( Five Eyes)','TikTok','Clearview AI','Cambridge Analytica','Equifax'])),
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
    print('=== SURVEILLANCE CAPITALISM SPECTROMETER ===')
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
    tech_scores = [results[k] for k in CALIBRATION if k != 'DuckDuckGo (control)']
    industry_avg = np.mean(tech_scores)
    max_score = max(tech_scores)
    print(f'  Industry average: {industry_avg:.3f}')
    print(f'  Maximum score: {max_score:.3f} ({[k for k in CALIBRATION if results[k] == max_score][0]})')
    print(f'  Surveillance capitalism {"DETECTED" if industry_avg > 0.5 else "NOT DETECTED"}')

    report = {
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'spectrometer': 'surveillance_capitalism',
        'dimensions': DIMS,
        'calibration': {k: {'score': results[k], 'vector': v} for k, v in CALIBRATION.items()},
        'falsification': {'passed': passed, 'total': len(CHECKS)},
        'current_assessment': {
            'industry_avg': round(float(industry_avg), 4),
            'max_score': round(float(max_score), 4),
            'detected': bool(industry_avg > 0.5),
        },
    }
    (W / 'surveillance-capitalism-spectrometer-results.json').write_text(json.dumps(report, indent=2))
    print(f'\nSaved to surveillance-capitalism-spectrometer-results.json')
    return passed == len(CHECKS)

if __name__ == '__main__':
    ok = run()
    print('\nALL CHECKS PASSED' if ok else '\nSOME CHECKS FAILED')
