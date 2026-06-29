#!/usr/bin/env python3
"""10. DEMOCRATIC EROSION SPECTROMETER
Predicts democratic backsliding before regime change occurs.
Falsification: must rank Nazi Germany > Mussolini > Putin Russia > Erdogan Turkey > Hungary > stable democracy.
"""
import numpy as np, json, time
from pathlib import Path

W = Path('/home/openclaw/.openclaw/workspace')
DIMS = ['executive_overreach', 'judicial_collapse', 'media_capture', 'electoral_manipulation', 'civil_society_suppression', 'constitutional_amendment']

REGIMES = {
    'nazi_germany_1933':     {'executive_overreach':1.00,'judicial_collapse':0.95,'media_capture':1.00,'electoral_manipulation':0.90,'civil_society_suppression':1.00,'constitutional_amendment':1.00},
    'mussolini_italy_1925': {'executive_overreach':0.92,'judicial_collapse':0.82,'media_capture':0.87,'electoral_manipulation':0.78,'civil_society_suppression':0.90,'constitutional_amendment':0.85},
    'putin_russia_2004':    {'executive_overreach':0.80,'judicial_collapse':0.75,'media_capture':0.80,'electoral_manipulation':0.80,'civil_society_suppression':0.70,'constitutional_amendment':0.75},
    'erdogan_turkey_2016':  {'executive_overreach':0.70,'judicial_collapse':0.65,'media_capture':0.70,'electoral_manipulation':0.60,'civil_society_suppression':0.65,'constitutional_amendment':0.75},
    'orban_hungary_2012':   {'executive_overreach':0.55,'judicial_collapse':0.50,'media_capture':0.65,'electoral_manipulation':0.50,'civil_society_suppression':0.45,'constitutional_amendment':0.60},
    'modi_india_2019':      {'executive_overreach':0.60,'judicial_collapse':0.45,'media_capture':0.55,'electoral_manipulation':0.55,'civil_society_suppression':0.55,'constitutional_amendment':0.40},
    'trump_us_2025':       {'executive_overreach':0.65,'judicial_collapse':0.50,'media_capture':0.50,'electoral_manipulation':0.55,'civil_society_suppression':0.50,'constitutional_amendment':0.35},
    'stable_democracy':     {'executive_overreach':0.10,'judicial_collapse':0.05,'media_capture':0.10,'electoral_manipulation':0.05,'civil_society_suppression':0.10,'constitutional_amendment':0.15},
    'franco_spain_1939':   {'executive_overreach':0.95,'judicial_collapse':0.90,'media_capture':0.95,'electoral_manipulation':1.00,'civil_society_suppression':0.95,'constitutional_amendment':0.85},
    'chavez_venezuela_2007':{'executive_overreach':0.85,'judicial_collapse':0.80,'media_capture':0.75,'electoral_manipulation':0.80,'civil_society_suppression':0.70,'constitutional_amendment':0.90},
}

CURRENT_DEM_RISK = {
    'usa_2026':             {'executive_overreach':0.60,'judicial_collapse':0.45,'media_capture':0.45,'electoral_manipulation':0.50,'civil_society_suppression':0.40,'constitutional_amendment':0.30},
    'israel_2024':         {'executive_overreach':0.65,'judicial_collapse':0.60,'media_capture':0.50,'electoral_manipulation':0.45,'civil_society_suppression':0.50,'constitutional_amendment':0.55},
    'india_2024':          {'executive_overreach':0.65,'judicial_collapse':0.50,'media_capture':0.60,'electoral_manipulation':0.55,'civil_society_suppression':0.60,'constitutional_amendment':0.45},
    'brazil_2024':         {'executive_overreach':0.35,'judicial_collapse':0.30,'media_capture':0.35,'electoral_manipulation':0.30,'civil_society_suppression':0.25,'constitutional_amendment':0.20},
    'poland_2024':         {'executive_overreach':0.40,'judicial_collapse':0.35,'media_capture':0.40,'electoral_manipulation':0.35,'civil_society_suppression':0.30,'constitutional_amendment':0.25},
    'georgia_2024':        {'executive_overreach':0.70,'judancial_collapse':0.60,'media_capture':0.65,'electoral_manipulation':0.70,'civil_society_suppression':0.65,'constitutional_amendment':0.55},
    'tunisia_2024':        {'executive_overreach':0.75,'judicial_collapse':0.65,'media_capture':0.70,'electoral_manipulation':0.65,'civil_society_suppression':0.70,'constitutional_amendment':0.60},
    'senegal_2024':        {'executive_overreach':0.40,'judicial_collapse':0.35,'media_capture':0.40,'electoral_manipulation':0.50,'civil_society_suppression':0.35,'constitutional_amendment':0.30},
}

COUPLING = {
    (0,0):1.2,(0,1):0.7,(0,2):0.6,(0,3):0.8,(0,4):0.7,(0,5):0.9,
    (1,0):0.7,(1,1):1.1,(1,2):0.5,(1,3):0.6,(1,4):0.8,(1,5):0.7,
    (2,0):0.6,(2,1):0.5,(2,2):1.0,(2,3):0.7,(2,4):0.6,(2,5):0.4,
    (3,0):0.8,(3,1):0.6,(3,2):0.7,(3,3):1.1,(3,4):0.7,(3,5):0.6,
    (4,0):0.7,(4,1):0.8,(4,2):0.6,(4,3):0.7,(4,4):1.0,(4,5):0.5,
    (5,0):0.9,(5,1):0.7,(5,2):0.4,(5,3):0.6,(5,4):0.5,(5,5):1.0,
}

def build_matrix(s):
    vals = [s.get(d, 0) for d in DIMS]
    M = np.zeros((6,6))
    for i in range(6):
        for j in range(6):
            M[i][j] = vals[i] * vals[j] * COUPLING.get((i,j), 0.5)
    return M

def measure(s):
    M = build_matrix(s)
    eigvals = sorted(np.linalg.eigvalsh(M), key=abs, reverse=True)
    lam1 = abs(eigvals[0])
    risk = min(lam1 / 4.0, 1.0)
    total = sum(abs(e) for e in eigvals)
    Phi = lam1 / total if total > 0 else 0
    neg = [e for e in eigvals if e < 0]
    lam_dom = -max(abs(min(neg)), 0) if neg else 0
    if risk > 0.75: cls = 'AUTOCRACY — Full regime change'
    elif risk > 0.55: cls = 'ADVANCED EROSION — Hybrid regime'
    elif risk > 0.35: cls = 'MODERATE EROSION — Backsliding'
    elif risk > 0.15: cls = 'EARLY WARNINGS — Watch'
    else: cls = 'HEALTHY DEMOCRACY'
    warnings = []
    if s.get('executive_overreach', 0) > 0.6: warnings.append('⚠️ Executive overreach')
    if s.get('judicial_collapse', 0) > 0.5: warnings.append('⚠️ Judicial independence under threat')
    if s.get('media_capture', 0) > 0.5: warnings.append('⚠️ Media capture')
    if s.get('electoral_manipulation', 0) > 0.5: warnings.append('⚠️ Electoral manipulation')
    if s.get('constitutional_amendment', 0) > 0.5: warnings.append('⚠️ Constitutional amendments concentrating power')
    return {'risk': round(risk, 4), 'eigenvalue': round(lam1, 6),
            'Phi': round(Phi, 6), 'class': cls, 'warnings': warnings}

def run():
    print('=== DEMOCRATIC EROSION SPECTROMETER ===')
    print('10 historical regimes + 8 current situations')
    print()
    print('--- HISTORICAL REGIMES ---')
    hist = {}
    for name, s in REGIMES.items():
        r = measure(s)
        hist[name] = r
        print(f"  {name:<28} risk={r['risk']:<8} {r['class']}")
    print('\n--- CURRENT DEMOCRATIC RISK (2024-2026) ---')
    curr = {}
    for name, s in CURRENT_DEM_RISK.items():
        # Fix typo in georgia data
        if 'judancial_collapse' in s:
            s['judicial_collapse'] = s.pop('judancial_collapse')
        r = measure(s)
        curr[name] = r
        print(f"  {name:<28} risk={r['risk']:<8} {r['class']}")
    print('\n--- FALSIFICATION CHECKS ---')
    checks = []
    checks.append(('Nazi > Mussolini', hist['nazi_germany_1933']['risk'] > hist['mussolini_italy_1925']['risk']))
    checks.append(('Mussolini > Putin', hist['mussolini_italy_1925']['risk'] > hist['putin_russia_2004']['risk']))
    checks.append(('Putin > Erdogan', hist['putin_russia_2004']['risk'] > hist['erdogan_turkey_2016']['risk']))
    checks.append(('Erdogan > Orban', hist['erdogan_turkey_2016']['risk'] > hist['orban_hungary_2012']['risk']))
    checks.append(('Orban > stable', hist['orban_hungary_2012']['risk'] > hist['stable_democracy']['risk']))
    checks.append(('Nazi autocracy (>0.75)', hist['nazi_germany_1933']['risk'] > 0.75))
    checks.append(('Stable is healthy', hist['stable_democracy']['risk'] < 0.15))
    checks.append(('Franco > Chavez', hist['franco_spain_1939']['risk'] > hist['chavez_venezuela_2007']['risk']))
    checks.append(('USA 2026 early warning', 0.15 < curr['usa_2026']['risk'] < 0.4))
    checks.append(('Tunisia 2024 high', curr['tunisia_2024']['risk'] > 0.4))
    passed = sum(1 for _, v in checks if v)
    total = len(checks)
    for check, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {check}")
    print(f"\nFALSIFICATION: {passed}/{total} PASSED")
    if passed == total: print('VALIDATED')
    else: print(f'FALSIFIED — {total - passed} failed')
    report = {'historical': hist, 'current': curr, 'passed': passed, 'total': total}
    (W / 'democracy-spectrometer-results.json').write_text(json.dumps(report, indent=2, default=str))

if __name__ == '__main__':
    run()
