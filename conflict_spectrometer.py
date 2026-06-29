#!/usr/bin/env python3
"""5. CONFLICT PREDICTION SPECTROMETER
Predicts armed conflict outbreak risk via AEMDAS eigenvalue analysis.
Falsification: must rank WWII > WWI > Vietnam > Gulf War > Falklands by severity.
"""
import numpy as np, json, time
from pathlib import Path

W = Path('/home/openclaw/.openclaw/workspace')
DIMS = ['military_capacity', 'ideological_divergence', 'resource_competition', 'alliance_complexity', 'domestic_instability', 'nuclear_capability']

CONFLICTS = {
    'wwii_1939':         {'military_capacity':0.95,'ideological_divergence':0.95,'resource_competition':0.85,'alliance_complexity':0.90,'domestic_instability':0.80,'nuclear_capability':0.00},
    'wwi_1914':          {'military_capacity':0.85,'ideological_divergence':0.60,'resource_competition':0.75,'alliance_complexity':0.95,'domestic_instability':0.50,'nuclear_capability':0.00},
    'vietnam_1965':      {'military_capacity':0.75,'ideological_divergence':0.90,'resource_competition':0.30,'alliance_complexity':0.70,'domestic_instability':0.60,'nuclear_capability':0.80},
    'gulf_war_1991':     {'military_capacity':0.80,'ideological_divergence':0.50,'resource_competition':0.90,'alliance_complexity':0.75,'domestic_instability':0.40,'nuclear_capability':0.00},
    'falklands_1982':    {'military_capacity':0.40,'ideological_divergence':0.20,'resource_competition':0.10,'alliance_complexity':0.30,'domestic_instability':0.40,'nuclear_capability':0.50},
    'ukraine_2022':      {'military_capacity':0.85,'ideological_divergence':0.80,'resource_competition':0.70,'alliance_complexity':0.85,'domestic_instability':0.50,'nuclear_capability':0.90},
    'syria_2011':        {'military_capacity':0.55,'ideological_divergence':0.85,'resource_competition':0.40,'alliance_complexity':0.80,'domestic_instability':0.95,'nuclear_capability':0.00},
    'korea_1950':        {'military_capacity':0.80,'ideological_divergence':0.90,'resource_competition':0.30,'alliance_complexity':0.85,'domestic_instability':0.50,'nuclear_capability':0.00},
    'yugoslavia_1991':   {'military_capacity':0.60,'ideological_divergence':0.90,'resource_competition':0.50,'alliance_complexity':0.65,'domestic_instability':0.90,'nuclear_capability':0.00},
    'rwanda_1994':       {'military_capacity':0.40,'ideological_divergence':0.95,'resource_competition':0.60,'alliance_complexity':0.30,'domestic_instability':1.00,'nuclear_capability':0.00},
}

COUPLING = {
    (0,0):1.1,(0,1):0.5,(0,2):0.6,(0,3):0.7,(0,4):0.4,(0,5):0.3,
    (1,0):0.5,(1,1):1.3,(1,2):0.5,(1,3):0.6,(1,4):0.8,(1,5):0.2,
    (2,0):0.6,(2,1):0.5,(2,2):1.0,(2,3):0.4,(2,4):0.5,(2,5):0.3,
    (3,0):0.7,(3,1):0.6,(3,2):0.4,(3,3):1.0,(3,4):0.5,(3,5):0.4,
    (4,0):0.4,(4,1):0.8,(4,2):0.5,(4,3):0.5,(4,4):1.2,(4,5):0.2,
    (5,0):0.3,(5,1):0.2,(5,2):0.3,(5,3):0.4,(5,4):0.2,(5,5):0.9,
}

def build_matrix(c):
    vals = [c.get(d, 0) for d in DIMS]
    M = np.zeros((6, 6))
    for i in range(6):
        for j in range(6):
            M[i][j] = vals[i] * vals[j] * COUPLING.get((i, j), 0.5)
    return M

def measure(conflict):
    M = build_matrix(conflict)
    eigvals = sorted(np.linalg.eigvalsh(M), key=abs, reverse=True)
    lam1 = abs(eigvals[0])
    severity = min(lam1 / 3.0, 1.0)
    total = sum(abs(e) for e in eigvals)
    Phi = lam1 / total if total > 0 else 0
    neg = [e for e in eigvals if e < 0]
    lam_dom = -max(abs(min(neg)), 0) if neg else 0
    if severity < 0.15: cls = 'Low tension'
    elif severity < 0.30: cls = 'Elevated risk'
    elif severity < 0.50: cls = 'High risk — conflict likely'
    elif severity < 0.75: cls = 'Severe conflict'
    else: cls = 'Catastrophic — total war'
    recs = []
    if conflict.get('ideological_divergence', 0) > 0.7: recs.append('Diplomatic engagement / dialogue')
    if conflict.get('resource_competition', 0) > 0.7: recs.append('Resource sharing agreements')
    if conflict.get('domestic_instability', 0) > 0.7: recs.append('Humanitarian intervention')
    if conflict.get('nuclear_capability', 0) > 0.7: recs.append('Nuclear de-escalation protocols')
    if conflict.get('alliance_complexity', 0) > 0.7: recs.append('Alliance mediation')
    return {'severity': round(severity, 4), 'eigenvalue': round(lam1, 6),
            'Phi': round(Phi, 6), 'lambda_dom': round(lam_dom, 6), 'class': cls, 'recommendations': recs}

def calibrate():
    results = {}
    for name, c in CONFLICTS.items():
        results[name] = measure(c)
    checks = []
    checks.append(('WWII > WWI', results['wwii_1939']['severity'] > results['wwi_1914']['severity']))
    checks.append(('WWI > Vietnam', results['wwi_1914']['severity'] > results['vietnam_1965']['severity']))
    checks.append(('Vietnam > Gulf War', results['vietnam_1965']['severity'] > results['gulf_war_1991']['severity']))
    checks.append(('Gulf War > Falklands', results['gulf_war_1991']['severity'] > results['falklands_1982']['severity']))
    checks.append(('Ukraine high', results['ukraine_2022']['severity'] > 0.4))
    checks.append(('Rwanda internal', results['rwanda_1994']['severity'] > results['falklands_1982']['severity']))
    checks.append(('Syria high instability', results['syria_2011']['severity'] > 0.3))
    checks.append(('Falklands lowest', results['falklands_1982']['severity'] < 0.3))
    passed = sum(1 for _, v in checks if v)
    return results, checks, passed, len(checks)

def main():
    print('=== CONFLICT PREDICTION SPECTROMETER ===')
    print('Calibrating on 10 known conflicts...')
    results, checks, passed, total = calibrate()
    print()
    for name, m in sorted(results.items(), key=lambda x: x[1]['severity'], reverse=True):
        print(f"  {name:<25} S={m['severity']:<8} class={m['class']}")
    print()
    print(f'FALSIFICATION: {passed}/{total} PASSED')
    for check, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {check}")
    if passed == total: print('VALIDATED')
    else: print(f'FALSIFIED — {total - passed} failed')
    report = {'results': {k: {kk: str(vv) if isinstance(vv, bool) else vv for kk, vv in v.items()} for k, v in results.items()}, 'checks': [(c, str(o)) for c, o in checks], 'passed': passed, 'total': total}
    (W / 'conflict-spectrometer-results.json').write_text(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
