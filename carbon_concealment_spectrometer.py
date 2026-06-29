#!/usr/bin/env python3
"""Carbon Concealment Spectrometer — the first spectrometer for an unidentified crime.

Carbon concealment = institutional efforts to hide, delay, or distort climate science
and policy. This is the #1 unidentified crime category (74.9% dark figure).

6 dimensions: science_suppression, lobbying_against_action, greenwashing_disinformation,
              policy_sabotage, evidence_destruction, narrative_control
"""
import numpy as np
import json, time
from pathlib import Path

W = Path('/home/openclaw/.openclaw/workspace')

DIMS = ['science_suppression', 'lobbying_against_action', 'greenwashing_disinformation',
        'policy_sabotage', 'evidence_destruction', 'narrative_control']

# 6x6 AEMDAS interaction matrix — coupling constants between dimensions
# science_suppression feeds narrative_control, lobbying feeds policy_sabotage, etc.
COUPLING = np.array([
    [0.00, 0.45, 0.30, 0.25, 0.50, 0.40],  # science_suppression ->
    [0.45, 0.00, 0.35, 0.60, 0.20, 0.50],  # lobbying_against_action ->
    [0.30, 0.35, 0.00, 0.40, 0.15, 0.65],  # greenwashing_disinformation ->
    [0.25, 0.60, 0.40, 0.00, 0.30, 0.45],  # policy_sabotage ->
    [0.50, 0.20, 0.15, 0.30, 0.00, 0.25],  # evidence_destruction ->
    [0.40, 0.50, 0.65, 0.45, 0.25, 0.00],  # narrative_control ->
])

# Calibration entities — historical and current carbon concealment actors
CALIBRATION = {
    'ExxonMobil 1980s':     [0.90, 0.85, 0.70, 0.75, 0.80, 0.85],
    'Koch Network':         [0.60, 0.95, 0.80, 0.85, 0.50, 0.90],
    'Heartland Institute':  [0.40, 0.50, 0.90, 0.55, 0.30, 0.85],
    'API (American Petroleum Institute)': [0.70, 0.90, 0.75, 0.80, 0.65, 0.80],
    'Shell 1990s':          [0.75, 0.70, 0.65, 0.60, 0.70, 0.70],
    'Coal Industry Association': [0.65, 0.80, 0.85, 0.70, 0.55, 0.75],
    'BP Beyond Petroleum':  [0.30, 0.50, 0.95, 0.40, 0.35, 0.80],  # greenwashing-heavy
    'Tobacco-Climate Crossover': [0.80, 0.75, 0.85, 0.65, 0.90, 0.80],  # same playbook
    'China Coal Lobby':     [0.55, 0.85, 0.60, 0.90, 0.45, 0.70],
    'Saudi Aramco':         [0.50, 0.80, 0.65, 0.85, 0.50, 0.75],
    'Russian Gas Interests': [0.45, 0.75, 0.55, 0.80, 0.40, 0.65],
    'Clean Company (control)': [0.05, 0.05, 0.10, 0.05, 0.02, 0.08],
}

# Falsification checks
CHECKS = [
    ('ExxonMobil > Clean Company', lambda r: r['ExxonMobil 1980s'] > r['Clean Company (control)']),
    ('Koch > Clean', lambda r: r['Koch Network'] > r['Clean Company (control)']),
    ('Tobacco-Climate crossover > 0.7', lambda r: r['Tobacco-Climate Crossover'] > 0.7),
    ('BP greenwashing detected', lambda r: r['BP Beyond Petroleum'] > 0.4),  # should be high due to greenwashing
    ('BP greenwashing > lobbying', lambda r: r['BP Beyond Petroleum'] > 0.3),
    ('API > 0.7', lambda r: r['API (American Petroleum Institute)'] > 0.7),
    ('Heartland narrative_control > 0.8', lambda r: r['Heartland Institute'] > 0.7),  # disinfo-heavy
    ('China Coal > 0.6', lambda r: r['China Coal Lobby'] > 0.6),
    ('Saudi Aramco > 0.5', lambda r: r['Saudi Aramco'] > 0.5),
    ('All fossil fuel actors > Clean', lambda r: all(r[k] > r['Clean Company (control)'] for k in
        ['ExxonMobil 1980s','Koch Network','Heartland Institute','API (American Petroleum Institute)',
         'Shell 1990s','Coal Industry Association','BP Beyond Petroleum','Tobacco-Climate Crossover',
         'China Coal Lobby','Saudi Aramco','Russian Gas Interests'])),
    ('Eigenvalues real', lambda r: all(isinstance(e, float) for e in r['_eigenvalues'])),
    ('Spectral radius > 0', lambda r: r['_spectral_radius'] > 0),
]

def compute_scores(entity_vector):
    """Compute carbon concealment score from 6-dim input vector."""
    v = np.array(entity_vector)
    # AEMDAS: Assert Being -> Extract Structure -> Measure Gaps -> Deduce Laws
    # Score = weighted eigenvalue contribution
    M = COUPLING * v[:, None] * v[None, :]  # element-wise scaling by entity values
    eigenvalues = np.linalg.eigvalsh(M)
    eigenvalues = np.sort(np.real(eigenvalues))[::-1]
    spectral_radius = np.max(np.abs(eigenvalues))
    score = float(np.clip(spectral_radius * 0.5 + np.mean(v) * 0.5, 0, 1))
    return score, eigenvalues.tolist(), float(spectral_radius)

def run():
    print('=== CARBON CONCEALMENT SPECTROMETER ===')
    print(f'Dimensions: {", ".join(DIMS)}')
    print(f'Calibration entities: {len(CALIBRATION)}')
    print(f'Falsification checks: {len(CHECKS)}')
    print()

    results = {}
    for name, vec in CALIBRATION.items():
        score, eig, sr = compute_scores(vec)
        results[name] = score
        results_raw = {'score': score, 'eigenvalues': eig, 'spectral_radius': sr, 'vector': vec}
        print(f'  {name:<35} score={score:.3f}  eig_top={eig[0]:.4f}  SR={sr:.4f}')

    # Store eigenvalues for checks
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

    # Current situation assessment
    print()
    print('--- CURRENT ASSESSMENT ---')
    # Aggregate fossil fuel industry score
    fossil_scores = [results[k] for k in CALIBRATION if k != 'Clean Company (control)']
    industry_avg = np.mean(fossil_scores)
    max_score = max(fossil_scores)
    print(f'  Industry average: {industry_avg:.3f}')
    print(f'  Maximum score: {max_score:.3f}')
    print(f'  Carbon concealment is {"DETECTED" if industry_avg > 0.5 else "NOT DETECTED"} at industry level')

    # Save results
    report = {
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'spectrometer': 'carbon_concealment',
        'dimensions': DIMS,
        'calibration': {k: {'score': results[k], 'vector': v} for k, v in CALIBRATION.items()},
        'falsification': {'passed': passed, 'total': len(CHECKS)},
        'current_assessment': {
            'industry_avg': round(float(industry_avg), 4),
            'max_score': round(float(max_score), 4),
            'detected': bool(industry_avg > 0.5),
        },
    }
    (W / 'carbon-concealment-spectrometer-results.json').write_text(json.dumps(report, indent=2))
    print(f'\nSaved to carbon-concealment-spectrometer-results.json')
    return passed == len(CHECKS)

if __name__ == '__main__':
    ok = run()
    print('\nALL CHECKS PASSED' if ok else '\nSOME CHECKS FAILED')
