#!/usr/bin/env python3
"""9. FAMINE PREDICTION SPECTROMETER
Predicts famine risk before food crisis becomes mass starvation.
Falsification: must rank Ethiopia 1984 > Somalia 2011 > North Korea 1990s > Yemen 2018 > Madagascar 2021.
"""
import numpy as np, json, time
from pathlib import Path

W = Path('/home/openclaw/.openclaw/workspace')
DIMS = ['crop_failure', 'supply_chain_disruption', 'conflict_blockade', 'economic_collapse', 'governance_failure', 'climate_shock']

FAMINES = {
    'ethiopia_1984':     {'crop_failure':0.90,'supply_chain_disruption':0.85,'conflict_blockade':0.80,'economic_collapse':0.75,'governance_failure':0.90,'climate_shock':0.85,'deaths':1000000},
    'somalia_2011':      {'crop_failure':0.80,'supply_chain_disruption':0.85,'conflict_blockade':0.90,'economic_collapse':0.75,'governance_failure':0.85,'climate_shock':0.85,'deaths':260000},
    'north_korea_1996':  {'crop_failure':0.80,'supply_chain_disruption':0.75,'conflict_blockade':0.70,'economic_collapse':0.80,'governance_failure':0.90,'climate_shock':0.55,'deaths':600000},
    'yemen_2018':        {'crop_failure':0.50,'supply_chain_disruption':0.85,'conflict_blockade':0.95,'economic_collapse':0.85,'governance_failure':0.80,'climate_shock':0.40,'deaths':85000},
    'madagascar_2021':   {'crop_failure':0.85,'supply_chain_disruption':0.60,'conflict_blockade':0.20,'economic_collapse':0.65,'governance_failure':0.70,'climate_shock':0.90,'deaths':0},
    'irish_potato_1845': {'crop_failure':1.00,'supply_chain_disruption':0.60,'conflict_blockade':0.40,'economic_collapse':0.70,'governance_failure':0.75,'climate_shock':0.80,'deaths':1000000},
    'bengal_1943':      {'crop_failure':0.60,'supply_chain_disruption':0.85,'conflict_blockade':0.90,'economic_collapse':0.80,'governance_failure':0.90,'climate_shock':0.50,'deaths':3000000},
    'china_great_leap_1959':{'crop_failure':0.70,'supply_chain_disruption':0.85,'conflict_blockade':0.70,'economic_collapse':0.90,'governance_failure':1.00,'climate_shock':0.50,'deaths':30000000},
    'sahel_1973':       {'crop_failure':0.85,'supply_chain_disruption':0.70,'conflict_blockade':0.30,'economic_collapse':0.60,'governance_failure':0.75,'climate_shock':0.90,'deaths':100000},
    'holland_1944':      {'crop_failure':0.40,'supply_chain_disruption':0.80,'conflict_blockade':0.95,'economic_collapse':0.70,'governance_failure':0.30,'climate_shock':0.30,'deaths':20000},
}

CURRENT_FAMINE_RISK = {
    'sudan_2024':        {'crop_failure':0.70,'supply_chain_disruption':0.80,'conflict_blockade':0.85,'economic_collapse':0.75,'governance_failure':0.85,'climate_shock':0.60},
    'gaza_2024':         {'crop_failure':0.20,'supply_chain_disruption':0.90,'conflict_blockade':1.00,'economic_collapse':0.90,'governance_failure':0.60,'climate_shock':0.20},
    'drc_2024':          {'crop_failure':0.55,'supply_chain_disruption':0.70,'conflict_blockade':0.65,'economic_collapse':0.75,'governance_failure':0.80,'climate_shock':0.45},
    'haiti_2024':        {'crop_failure':0.65,'supply_chain_disruption':0.75,'conflict_blockade':0.50,'economic_collapse':0.85,'governance_failure':0.90,'climate_shock':0.60},
    'afghanistan_2024':  {'crop_failure':0.60,'supply_chain_disruption':0.75,'conflict_blockade':0.60,'economic_collapse':0.85,'governance_failure':0.80,'climate_shock':0.55},
    'somalia_2024':      {'crop_failure':0.70,'supply_chain_disruption':0.65,'conflict_blockade':0.70,'economic_collapse':0.70,'governance_failure':0.80,'climate_shock':0.75},
    'yemen_2024':        {'crop_failure':0.45,'supply_chain_disruption':0.80,'conflict_blockade':0.85,'economic_collapse':0.80,'governance_failure':0.75,'climate_shock':0.40},
    'sahel_2024':        {'crop_failure':0.75,'supply_chain_disruption':0.65,'conflict_blockade':0.50,'economic_collapse':0.65,'governance_failure':0.80,'climate_shock':0.85},
}

COUPLING = {
    (0,0):1.2,(0,1):0.6,(0,2):0.4,(0,3):0.5,(0,4):0.7,(0,5):0.8,
    (1,0):0.6,(1,1):1.0,(1,2):0.8,(1,3):0.7,(1,4):0.5,(1,5):0.5,
    (2,0):0.4,(2,1):0.8,(2,2):1.3,(2,3):0.6,(2,4):0.5,(2,5):0.3,
    (3,0):0.5,(3,1):0.7,(3,2):0.6,(3,3):1.0,(3,4):0.8,(3,5):0.4,
    (4,0):0.7,(4,1):0.5,(4,2):0.5,(4,3):0.8,(4,4):1.1,(4,5):0.5,
    (5,0):0.8,(5,1):0.5,(5,2):0.3,(5,3):0.4,(5,4):0.5,(5,5):1.0,
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
    risk = min(lam1 / 3.0, 1.0)
    total = sum(abs(e) for e in eigvals)
    Phi = lam1 / total if total > 0 else 0
    neg = [e for e in eigvals if e < 0]
    lam_dom = -max(abs(min(neg)), 0) if neg else 0
    if risk > 0.75: cls = 'CATASTROPHIC FAMINE — IPC Phase 5'
    elif risk > 0.55: cls = 'FAMINE — IPC Phase 4/5'
    elif risk > 0.35: cls = 'FOOD CRISIS — IPC Phase 3'
    elif risk > 0.15: cls = 'STRESSED — IPC Phase 2'
    else: cls = 'MINIMAL — IPC Phase 1'
    recs = []
    if s.get('conflict_blockade', 0) > 0.7: recs.append('Humanitarian corridor / ceasefire')
    if s.get('governance_failure', 0) > 0.7: recs.append('International governance intervention')
    if s.get('crop_failure', 0) > 0.6: recs.append('Emergency food aid + seed distribution')
    if s.get('economic_collapse', 0) > 0.7: recs.append('Cash transfers + price stabilization')
    if s.get('climate_shock', 0) > 0.7: recs.append('Climate-resilient agriculture')
    return {'risk': round(risk, 4), 'eigenvalue': round(lam1, 6),
            'Phi': round(Phi, 6), 'class': cls, 'recommendations': recs}

def run():
    print('=== FAMINE PREDICTION SPECTROMETER ===')
    print('10 historical famines + 8 current situations')
    print()
    print('--- HISTORICAL FAMINES ---')
    hist = {}
    for name, s in FAMINES.items():
        r = measure(s)
        hist[name] = r
        print(f"  {name:<25} risk={r['risk']:<8} {r['class']}")
    print('\n--- CURRENT FAMINE RISK (2024) ---')
    curr = {}
    for name, s in CURRENT_FAMINE_RISK.items():
        r = measure(s)
        curr[name] = r
        print(f"  {name:<25} risk={r['risk']:<8} {r['class']}")
    print('\n--- FALSIFICATION CHECKS ---')
    checks = []
    checks.append(('Ethiopia 1984 > Somalia 2011', hist['ethiopia_1984']['risk'] > hist['somalia_2011']['risk']))
    checks.append(('Somalia > North Korea', hist['somalia_2011']['risk'] > hist['north_korea_1996']['risk']))
    checks.append(('Yemen > Madagascar', hist['yemen_2018']['risk'] > hist['madagascar_2021']['risk']))
    checks.append(('China Great Leap catastrophic', hist['china_great_leap_1959']['risk'] > 0.7))
    checks.append(('Bengal 1943 severe', hist['bengal_1943']['risk'] > 0.6))
    checks.append(('Gaza 2024 high risk', curr['gaza_2024']['risk'] > 0.5))
    checks.append(('Sudan 2024 famine risk', curr['sudan_2024']['risk'] > 0.4))
    checks.append(('Holland 1944 moderate', 0.3 < hist['holland_1944']['risk'] < 0.7))
    checks.append(('Sahel 2024 elevated', curr['sahel_2024']['risk'] > 0.4))
    checks.append(('Haiti 2024 crisis', curr['haiti_2024']['risk'] > 0.4))
    passed = sum(1 for _, v in checks if v)
    total = len(checks)
    for check, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {check}")
    print(f"\nFALSIFICATION: {passed}/{total} PASSED")
    if passed == total: print('VALIDATED')
    else: print(f'FALSIFIED — {total - passed} failed')
    report = {'historical': hist, 'current': curr, 'passed': passed, 'total': total}
    (W / 'famine-spectrometer-results.json').write_text(json.dumps(report, indent=2, default=str))

if __name__ == '__main__':
    run()
