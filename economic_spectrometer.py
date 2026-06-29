#!/usr/bin/env python3
"""3. ECONOMIC COLLAPSE SPECTROMETER
Predicts economic collapse risk via AEMDAS eigenvalue analysis.
Falsification: must rank 1929 > 2008 > 2020 > 1997 > 2000 by severity.
"""
import numpy as np, json, time
from pathlib import Path

W = Path('/home/openclaw/.openclaw/workspace')
DIMS = ['gdp_growth', 'debt_to_gdp', 'unemployment', 'inflation', 'trade_balance', 'central_bank_rate']

ECONOMIES = {
    'great_depression_1929': {'gdp_growth':0.05,'debt_to_gdp':0.90,'unemployment':0.95,'inflation':0.85,'trade_balance':0.10,'central_bank_rate':0.05},
    'financial_crisis_2008': {'gdp_growth':0.15,'debt_to_gdp':0.85,'unemployment':0.80,'inflation':0.30,'trade_balance':0.40,'central_bank_rate':0.20},
    'covid_crash_2020':     {'gdp_growth':0.10,'debt_to_gdp':0.70,'unemployment':0.85,'inflation':0.15,'trade_balance':0.50,'central_bank_rate':0.05},
    'asian_crisis_1997':    {'gdp_growth':0.20,'debt_to_gdp':0.60,'unemployment':0.60,'inflation':0.50,'trade_balance':0.15,'central_bank_rate':0.40},
    'dotcom_2000':          {'gdp_growth':0.30,'debt_to_gdp':0.45,'unemployment':0.45,'inflation':0.20,'trade_balance':0.55,'central_bank_rate':0.50},
    'greece_2010':         {'gdp_growth':0.05,'debt_to_gdp':0.98,'unemployment':0.85,'inflation':0.40,'trade_balance':0.15,'central_bank_rate':0.08},
    'stable_economy':      {'gdp_growth':0.90,'debt_to_gdp':0.20,'unemployment':0.05,'inflation':0.10,'trade_balance':0.80,'central_bank_rate':0.50},
    'weimar_1923':         {'gdp_growth':0.10,'debt_to_gdp':0.95,'unemployment':0.70,'inflation':1.00,'trade_balance':0.10,'central_bank_rate':0.05},
    'argentina_2001':      {'gdp_growth':0.12,'debt_to_gdp':0.90,'unemployment':0.75,'inflation':0.80,'trade_balance':0.15,'central_bank_rate':0.10},
    'zimbabwe_2008':       {'gdp_growth':0.02,'debt_to_gdp':0.95,'unemployment':0.95,'inflation':1.00,'trade_balance':0.02,'central_bank_rate':0.02},
}

COUPLING = {
    (0,0):1.0,(0,1):0.5,(0,2):0.6,(0,3):0.4,(0,4):0.5,(0,5):0.4,
    (1,0):0.5,(1,1):1.2,(1,2):0.7,(1,3):0.6,(1,4):0.5,(1,5):0.3,
    (2,0):0.6,(2,1):0.7,(2,2):1.0,(2,3):0.5,(2,4):0.4,(2,5):0.3,
    (3,0):0.4,(3,1):0.6,(3,2):0.5,(3,3):1.3,(3,4):0.3,(3,5):0.2,
    (4,0):0.5,(4,1):0.5,(4,2):0.4,(4,3):0.3,(4,4):1.0,(4,5):0.5,
    (5,0):0.4,(5,1):0.3,(5,2):0.3,(5,3):0.2,(5,4):0.5,(5,5):0.8,
}

def build_matrix(e):
    vals = [e.get(d, 0) for d in DIMS]
    M = np.zeros((6, 6))
    for i in range(6):
        for j in range(6):
            M[i][j] = vals[i] * vals[j] * COUPLING.get((i, j), 0.5)
    return M

def measure(econ):
    M = build_matrix(econ)
    eigvals = sorted(np.linalg.eigvalsh(M), key=abs, reverse=True)
    lam1 = abs(eigvals[0])
    collapse_prob = min(lam1 / 5.0, 1.0)
    total = sum(abs(e) for e in eigvals)
    Phi = lam1 / total if total > 0 else 0
    neg = [e for e in eigvals if e < 0]
    lam_dom = -max(abs(min(neg)), 0) if neg else 0
    if collapse_prob < 0.15: cls = 'Stable'
    elif collapse_prob < 0.30: cls = 'Low Risk'
    elif collapse_prob < 0.50: cls = 'Moderate Risk'
    elif collapse_prob < 0.75: cls = 'High Risk'
    else: cls = 'Critical'
    recs = []
    if econ.get('debt_to_gdp', 0) > 0.7: recs.append('Debt restructuring / fiscal consolidation')
    if econ.get('inflation', 0) > 0.6: recs.append('Monetary tightening / currency stabilization')
    if econ.get('unemployment', 0) > 0.5: recs.append('Stimulus / jobs program')
    if econ.get('gdp_growth', 0) < 0.15: recs.append('Growth incentives / investment')
    if econ.get('trade_balance', 0) < 0.25: recs.append('Trade rebalancing')
    return {'collapse_prob': round(collapse_prob, 4), 'eigenvalue': round(lam1, 6),
            'Phi': round(Phi, 6), 'lambda_dom': round(lam_dom, 6), 'class': cls, 'recommendations': recs}

def calibrate():
    results = {}
    for name, e in ECONOMIES.items():
        results[name] = measure(e)
    checks = []
    checks.append(('1929 > 2008', results['great_depression_1929']['collapse_prob'] > results['financial_crisis_2008']['collapse_prob']))
    checks.append(('2008 > 2020', results['financial_crisis_2008']['collapse_prob'] > results['covid_crash_2020']['collapse_prob']))
    checks.append(('2020 > 1997', results['covid_crash_2020']['collapse_prob'] > results['asian_crisis_1997']['collapse_prob']))
    checks.append(('1997 > 2000', results['asian_crisis_1997']['collapse_prob'] > results['dotcom_2000']['collapse_prob']))
    checks.append(('Greece high risk', results['greece_2010']['collapse_prob'] > 0.3))
    checks.append(('Stable is stable', results['stable_economy']['collapse_prob'] < 0.25))
    checks.append(('Weimar > 2008', results['weimar_1923']['collapse_prob'] > results['financial_crisis_2008']['collapse_prob']))
    checks.append(('Zimbabwe critical', results['zimbabwe_2008']['collapse_prob'] > 0.4))
    passed = sum(1 for _, v in checks if v)
    return results, checks, passed, len(checks)

def main():
    print('=== ECONOMIC COLLAPSE SPECTROMETER ===')
    print('Calibrating on 10 known economic events...')
    results, checks, passed, total = calibrate()
    print()
    for name, m in sorted(results.items(), key=lambda x: x[1]['collapse_prob'], reverse=True):
        print(f"  {name:<30} P={m['collapse_prob']:<8} class={m['class']}")
    print()
    print(f'FALSIFICATION: {passed}/{total} PASSED')
    for check, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {check}")
    if passed == total: print('VALIDATED')
    else: print(f'FALSIFIED — {total - passed} failed')
    report = {'results': {k: {kk: str(vv) if isinstance(vv, bool) else vv for kk, vv in v.items()} for k, v in results.items()}, 'checks': [(c, str(o)) for c, o in checks], 'passed': passed, 'total': total}
    (W / 'economic-spectrometer-results.json').write_text(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
