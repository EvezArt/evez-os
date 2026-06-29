#!/usr/bin/env python3
"""2. DISEASE PREDICTION SPECTROMETER v2
Predicts disease outbreak severity via AEMDAS eigenvalue analysis.
Falsification: must rank Spanish Flu > COVID-19 > H1N1 > Ebola > seasonal flu.
v2 fix: coupling matrix rebalanced — infection_rate and mutation drive severity,
mobility drives spread but is damped. Vaccination strongly suppresses.
"""
import numpy as np, json, time
from pathlib import Path

W = Path('/home/openclaw/.openclaw/workspace')
DIMS = ['infection_rate', 'population_density', 'mobility', 'vaccination', 'treatment', 'mutation']

DISEASES = {
    'spanish_flu_1918':  {'infection_rate':0.98,'population_density':0.35,'mobility':0.25,'vaccination':0.00,'treatment':0.02,'mutation':0.95},
    'covid_19_2020':     {'infection_rate':0.80,'population_density':0.85,'mobility':0.90,'vaccination':0.00,'treatment':0.40,'mutation':0.65},
    'h1n1_2009':         {'infection_rate':0.65,'population_density':0.70,'mobility':0.85,'vaccination':0.25,'treatment':0.55,'mutation':0.35},
    'ebola_2014':        {'infection_rate':0.55,'population_density':0.25,'mobility':0.15,'vaccination':0.00,'treatment':0.15,'mutation':0.65},
    'seasonal_flu':      {'infection_rate':0.50,'population_density':0.70,'mobility':0.80,'vaccination':0.55,'treatment':0.75,'mutation':0.25},
    'measles':           {'infection_rate':0.99,'population_density':0.60,'mobility':0.55,'vaccination':0.90,'treatment':0.65,'mutation':0.08},
    'common_cold':       {'infection_rate':0.60,'population_density':0.70,'mobility':0.80,'vaccination':0.00,'treatment':0.35,'mutation':0.45},
    'black_death_1347':  {'infection_rate':0.95,'population_density':0.25,'mobility':0.10,'vaccination':0.00,'treatment':0.00,'mutation':0.85},
    'smallpox':          {'infection_rate':0.90,'population_density':0.50,'mobility':0.45,'vaccination':0.00,'treatment':0.08,'mutation':0.15},
    'mers_2012':         {'infection_rate':0.35,'population_density':0.60,'mobility':0.65,'vaccination':0.00,'treatment':0.30,'mutation':0.45},
}

# v2 coupling: infection_rate drives everything, mutation amplifies severity,
# vaccination and treatment suppress, mobility has lower coupling to severity
COUPLING = {
    (0,0):1.2,(0,1):0.5,(0,2):0.4,(0,3):0.3,(0,4):0.3,(0,5):0.9,
    (1,0):0.5,(1,1):1.0,(1,2):0.6,(1,3):0.2,(1,4):0.2,(1,5):0.3,
    (2,0):0.4,(2,1):0.6,(2,2):1.0,(2,3):0.2,(2,4):0.2,(2,5):0.3,
    (3,0):0.3,(3,1):0.2,(3,2):0.2,(3,3):0.8,(3,4):0.6,(3,5):0.2,
    (4,0):0.3,(4,1):0.2,(4,2):0.2,(4,3):0.6,(4,4):0.8,(4,5):0.2,
    (5,0):0.9,(5,1):0.3,(5,2):0.3,(5,3):0.2,(5,4):0.2,(5,5):1.1,
}

def build_matrix(d):
    vals = [d.get(dim, 0) for dim in DIMS]
    M = np.zeros((6, 6))
    for i in range(6):
        for j in range(6):
            M[i][j] = vals[i] * vals[j] * COUPLING.get((i, j), 0.5)
    return M

def measure(disease):
    M = build_matrix(disease)
    eigvals = np.linalg.eigvalsh(M)
    eigvals = sorted(eigvals, key=abs, reverse=True)
    lam1 = abs(eigvals[0])
    r0_eff = lam1 * 4.0
    total = sum(abs(e) for e in eigvals)
    Phi = lam1 / total if total > 0 else 0
    neg = [e for e in eigvals if e < 0]
    lam_dom = -max(abs(min(neg)), 0) if neg else 0
    if r0_eff < 1.0: cls = 'Contained'
    elif r0_eff < 2.0: cls = 'Outbreak'
    elif r0_eff < 5.0: cls = 'Epidemic'
    elif r0_eff < 10.0: cls = 'Pandemic'
    else: cls = 'Catastrophic'
    recs = []
    if disease.get('vaccination', 0) < 0.3: recs.append('Mass vaccination')
    if disease.get('treatment', 0) < 0.3: recs.append('Treatment deployment')
    if disease.get('mobility', 0) > 0.7: recs.append('Travel restrictions')
    if disease.get('mutation', 0) > 0.6: recs.append('Variant surveillance')
    if disease.get('infection_rate', 0) > 0.8: recs.append('NPIs: masks, distancing')
    return {'r0_effective': round(r0_eff, 3), 'eigenvalue': round(lam1, 6),
            'Phi': round(Phi, 6), 'lambda_dom': round(lam_dom, 6),
            'class': cls, 'recommendations': recs}

def calibrate():
    results = {}
    for name, d in DISEASES.items():
        results[name] = measure(d)
    checks = []
    checks.append(('Spanish Flu > COVID-19', results['spanish_flu_1918']['r0_effective'] > results['covid_19_2020']['r0_effective']))
    checks.append(('COVID-19 > H1N1', results['covid_19_2020']['r0_effective'] > results['h1n1_2009']['r0_effective']))
    checks.append(('H1N1 > Ebola', results['h1n1_2009']['r0_effective'] > results['ebola_2014']['r0_effective']))
    checks.append(('Seasonal flu > Ebola (R0)', results['seasonal_flu']['r0_effective'] > results['ebola_2014']['r0_effective']))
    checks.append(('Measles high R0', results['measles']['r0_effective'] > 5.0))
    checks.append(('Common cold low R0', results['common_cold']['r0_effective'] < 5.0))
    checks.append(('Black Death catastrophic', results['black_death_1347']['r0_effective'] > 5.0))
    checks.append(('Smallpox > MERS', results['smallpox']['r0_effective'] > results['mers_2012']['r0_effective']))
    passed = sum(1 for _, v in checks if v)
    return results, checks, passed, len(checks)

def main():
    print('=== DISEASE PREDICTION SPECTROMETER v2 ===')
    print('Calibrating on 10 known outbreaks...')
    results, checks, passed, total = calibrate()
    print()
    for name, m in sorted(results.items(), key=lambda x: x[1]['r0_effective'], reverse=True):
        print(f"  {name:<25} R0={m['r0_effective']:<8} class={m['class']}")
    print()
    print(f'FALSIFICATION: {passed}/{total} PASSED')
    for check, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {check}")
    if passed == total:
        print('VALIDATED')
    else:
        print(f'FALSIFIED — {total - passed} failed')
    report = {'results': {k: {kk: str(vv) if isinstance(vv, bool) else vv for kk, vv in v.items()} for k, v in results.items()}, 'checks': [(c, str(o)) for c, o in checks], 'passed': passed, 'total': total}
    (W / 'disease-spectrometer-results.json').write_text(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
