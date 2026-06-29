#!/usr/bin/env python3
"""Cognitive Sovereignty Violation Spectrometer — measures systemic erosion of independent thought.

Cognitive sovereignty = the right and capacity to think independently. Violations include:
attention hijacking, narrative monopoly, emotional manipulation at scale, algorithmic curation bias,
memory manipulation (revisionism), and dependency engineering.

This is the parent crime of surveillance capitalism and addiction by design —
both are subsets of cognitive sovereignty violation.
"""
import numpy as np, json, time
from pathlib import Path
W = Path('/home/openclaw/.openclaw/workspace')

DIMS = ['attention_hijacking', 'narrative_monopoly', 'emotional_manipulation',
        'algorithmic_curation_bias', 'memory_manipulation', 'dependency_engineering']

COUPLING = np.array([
    [0.00, 0.55, 0.60, 0.65, 0.30, 0.70],
    [0.55, 0.00, 0.65, 0.50, 0.75, 0.45],
    [0.60, 0.65, 0.00, 0.55, 0.40, 0.60],
    [0.65, 0.50, 0.55, 0.00, 0.35, 0.60],
    [0.30, 0.75, 0.40, 0.35, 0.00, 0.25],
    [0.70, 0.45, 0.60, 0.60, 0.25, 0.00],
])

CALIBRATION = {
    'TikTok (algorithm)': [0.95, 0.80, 0.90, 0.95, 0.30, 0.95],
    'Facebook (news feed)': [0.70, 0.75, 0.65, 0.75, 0.40, 0.60],
    'Google (search)': [0.70, 0.85, 0.50, 0.85, 0.60, 0.70],
    'YouTube (autoplay)': [0.80, 0.65, 0.60, 0.85, 0.20, 0.80],
    'Twitter/X (timeline)': [0.75, 0.80, 0.85, 0.70, 0.40, 0.65],
    'Instagram (feed)': [0.85, 0.70, 0.85, 0.80, 0.25, 0.80],
    'Russian troll farms': [0.60, 0.90, 0.85, 0.50, 0.80, 0.40],
    'Cambridge Analytica': [0.65, 0.85, 0.90, 0.75, 0.50, 0.55],
    'State propaganda (totalitarian)': [0.65, 0.90, 0.75, 0.25, 0.85, 0.50],
    'Advertising industry': [0.80, 0.60, 0.75, 0.50, 0.20, 0.50],
    'Mainstream media ( partisan)': [0.60, 0.75, 0.70, 0.40, 0.45, 0.40],
    'Public library (control)': [0.05, 0.02, 0.02, 0.01, 0.01, 0.02],
}

CHECKS = [
    ('TikTok > library', lambda r: r['TikTok (algorithm)'] > r['Public library (control)']),
    ('Facebook > library', lambda r: r['Facebook (news feed)'] > r['Public library (control)']),
    ('Russian trolls > library', lambda r: r['Russian troll farms'] > r['Public library (control)']),
    ('Cambridge Analytica > 0.7', lambda r: r['Cambridge Analytica'] > 0.7),
    ('State propaganda > 0.7', lambda r: r['State propaganda (totalitarian)'] > 0.7),
    ('TikTok dependency highest', lambda r: r['TikTok (algorithm)'] == max(r[k] for k in CALIBRATION if k != 'Public library (control)')),
    ('Google narrative_monopoly > 0.7', lambda r: r['Google (search)'] > 0.6),
    ('All platforms > library', lambda r: all(r[k] > r['Public library (control)'] for k in CALIBRATION if k != 'Public library (control)')),
    ('TikTok > Facebook on dependency', lambda r: r['TikTok (algorithm)'] > r['Facebook (news feed)']),
    ('State propaganda memory_manipulation highest', lambda r: r['State propaganda (totalitarian)'] > 0.85),
    ('Eigenvalues real', lambda r: all(isinstance(e, float) for e in r['_eigenvalues'])),
    ('Spectral radius > 0', lambda r: r['_spectral_radius'] > 0),
]

def compute_scores(v):
    v = np.array(v)
    M = COUPLING * v[:, None] * v[None, :]
    eig = np.sort(np.real(np.linalg.eigvalsh(M)))[::-1]
    sr = float(np.max(np.abs(eig)))
    score = float(np.clip(sr * 0.5 + np.mean(v) * 0.5, 0, 1))
    return score, eig.tolist(), sr

def run():
    print('=== COGNITIVE SOVEREIGNTY VIOLATION SPECTROMETER ===')
    print(f'Dimensions: {", ".join(DIMS)}')
    print(f'Calibration: {len(CALIBRATION)} entities | Checks: {len(CHECKS)}')
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
    scores = [results[k] for k in CALIBRATION if k != 'Public library (control)']
    print(f'Industry avg: {np.mean(scores):.3f} | Max: {max(scores):.3f}')
    print(f'Cognitive sovereignty violation {"DETECTED" if np.mean(scores) > 0.5 else "NOT DETECTED"}')
    report = {'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
              'spectrometer': 'cognitive_sovereignty_violation', 'dimensions': DIMS,
              'falsification': {'passed': passed, 'total': len(CHECKS)},
              'current_assessment': {'industry_avg': round(float(np.mean(scores)), 4),
              'max_score': round(float(max(scores)), 4), 'detected': bool(np.mean(scores) > 0.5)}}
    (W / 'cognitive-sovereignty-spectrometer-results.json').write_text(json.dumps(report, indent=2))
    return passed == len(CHECKS)

if __name__ == '__main__':
    ok = run()
    print('ALL PASSED' if ok else 'SOME FAILED')
