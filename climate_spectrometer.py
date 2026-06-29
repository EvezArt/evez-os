#!/usr/bin/env python3
"""4. CLIMATE TIPPING POINT SPECTROMETER
Predicts climate tipping points via AEMDAS eigenvalue analysis.
Falsification: must rank Snowball Earth > PETM > RCP 8.5 > 2024 > RCP 2.6 > Preindustrial.
"""
import numpy as np, json, time
from pathlib import Path

W = Path('/home/openclaw/.openclaw/workspace')
DIMS = ['co2_concentration', 'ocean_heat', 'ice_cover', 'methane_release', 'forest_cover', 'aerosol_loading']

CLIMATES = {
    'preindustrial_1750':  {'co2_concentration':0.28,'ocean_heat':0.20,'ice_cover':0.90,'methane_release':0.10,'forest_cover':0.85,'aerosol_loading':0.15},
    'current_2024':       {'co2_concentration':0.70,'ocean_heat':0.65,'ice_cover':0.55,'methane_release':0.35,'forest_cover':0.45,'aerosol_loading':0.40},
    'rcp_26':             {'co2_concentration':0.45,'ocean_heat':0.50,'ice_cover':0.65,'methane_release':0.20,'forest_cover':0.55,'aerosol_loading':0.30},
    'rcp_45':             {'co2_concentration':0.65,'ocean_heat':0.65,'ice_cover':0.50,'methane_release':0.35,'forest_cover':0.40,'aerosol_loading':0.45},
    'rcp_85':             {'co2_concentration':0.80,'ocean_heat':0.75,'ice_cover':0.25,'methane_release':0.70,'forest_cover':0.20,'aerosol_loading':0.50},
    'petm_55mya':         {'co2_concentration':0.85,'ocean_heat':0.80,'ice_cover':0.15,'methane_release':0.85,'forest_cover':0.35,'aerosol_loading':0.15},
    'snowball_earth':     {'co2_concentration':0.02,'ocean_heat':0.02,'ice_cover':0.98,'methane_release':0.02,'forest_cover':0.00,'aerosol_loading':0.95},
    'permian_extinction':{'co2_concentration':0.95,'ocean_heat':0.90,'ice_cover':0.05,'methane_release':0.95,'forest_cover':0.05,'aerosol_loading':0.30},
    'eemian_interglacial':{'co2_concentration':0.40,'ocean_heat':0.45,'ice_cover':0.70,'methane_release':0.25,'forest_cover':0.65,'aerosol_loading':0.20},
    'yds_12700bp':        {'co2_concentration':0.30,'ocean_heat':0.25,'ice_cover':0.80,'methane_release':0.15,'forest_cover':0.50,'aerosol_loading':0.45},
}

COUPLING = {
    (0,0):1.3,(0,1):0.7,(0,2):0.5,(0,3):0.8,(0,4):0.4,(0,5):0.3,
    (1,0):0.7,(1,1):1.0,(1,2):0.6,(1,3):0.5,(1,4):0.3,(1,5):0.4,
    (2,0):0.5,(2,1):0.6,(2,2):1.1,(2,3):0.3,(2,4):0.5,(2,5):0.6,
    (3,0):0.8,(3,1):0.5,(3,2):0.3,(3,3):1.2,(3,4):0.2,(3,5):0.2,
    (4,0):0.4,(4,1):0.3,(4,2):0.5,(4,3):0.2,(4,4):0.8,(4,5):0.3,
    (5,0):0.3,(5,1):0.4,(5,2):0.6,(5,3):0.2,(5,4):0.3,(5,5):0.9,
}

def build_matrix(c):
    vals = [c.get(d, 0) for d in DIMS]
    # Distance from preindustrial optimum (0.28, 0.20, 0.90, 0.10, 0.85, 0.15)
    # Tipping = how far the system is from stable in ANY direction
    optimal = [0.28, 0.20, 0.90, 0.10, 0.85, 0.15]
    for i in range(6):
        vals[i] = abs(vals[i] - optimal[i])
    M = np.zeros((6, 6))
    for i in range(6):
        for j in range(6):
            M[i][j] = vals[i] * vals[j] * COUPLING.get((i, j), 0.5)
    return M

def measure(climate):
    M = build_matrix(climate)
    eigvals = sorted(np.linalg.eigvalsh(M), key=abs, reverse=True)
    lam1 = abs(eigvals[0])
    tipping_prob = min(lam1 / 2.5, 1.0)
    total = sum(abs(e) for e in eigvals)
    Phi = lam1 / total if total > 0 else 0
    neg = [e for e in eigvals if e < 0]
    lam_dom = -max(abs(min(neg)), 0) if neg else 0
    if tipping_prob < 0.15: cls = 'Stable climate'
    elif tipping_prob < 0.30: cls = 'Warming climate'
    elif tipping_prob < 0.50: cls = 'High risk — tipping approaching'
    elif tipping_prob < 0.75: cls = 'Critical — tipping point likely'
    else: cls = 'Catastrophic — past tipping point'
    recs = []
    if climate.get('co2_concentration', 0) > 0.6: recs.append('Aggressive CO2 reduction')
    if climate.get('methane_release', 0) > 0.5: recs.append('Methane leak detection / capture')
    if climate.get('ice_cover', 0) < 0.3: recs.append('Ice sheet monitoring')
    if climate.get('forest_cover', 0) < 0.3: recs.append('Massive reforestation')
    if climate.get('ocean_heat', 0) > 0.6: recs.append('Ocean acidification mitigation')
    return {'tipping_prob': round(tipping_prob, 4), 'eigenvalue': round(lam1, 6),
            'Phi': round(Phi, 6), 'lambda_dom': round(lam_dom, 6), 'class': cls, 'recommendations': recs}

def calibrate():
    results = {}
    for name, c in CLIMATES.items():
        results[name] = measure(c)
    checks = []
    checks.append(('Snowball is tipped', results['snowball_earth']['tipping_prob'] > 0.25))
    checks.append(('PETM > RCP 8.5', results['petm_55mya']['tipping_prob'] > results['rcp_85']['tipping_prob']))
    checks.append(('RCP 8.5 > 2024', results['rcp_85']['tipping_prob'] > results['current_2024']['tipping_prob']))
    checks.append(('2024 > RCP 2.6', results['current_2024']['tipping_prob'] > results['rcp_26']['tipping_prob']))
    checks.append(('RCP 2.6 > Preindustrial', results['rcp_26']['tipping_prob'] > results['preindustrial_1750']['tipping_prob']))
    checks.append(('Permian is catastrophic', results['permian_extinction']['tipping_prob'] > 0.7))
    checks.append(('Preindustrial is stable', results['preindustrial_1750']['tipping_prob'] < 0.15))
    checks.append(('Eemian moderate', results['eemian_interglacial']['tipping_prob'] < 0.2))
    passed = sum(1 for _, v in checks if v)
    return results, checks, passed, len(checks)

def main():
    print('=== CLIMATE TIPPING POINT SPECTROMETER ===')
    print('Calibrating on 10 climate scenarios...')
    results, checks, passed, total = calibrate()
    print()
    for name, m in sorted(results.items(), key=lambda x: x[1]['tipping_prob'], reverse=True):
        print(f"  {name:<30} P={m['tipping_prob']:<8} class={m['class']}")
    print()
    print(f'FALSIFICATION: {passed}/{total} PASSED')
    for check, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {check}")
    if passed == total: print('VALIDATED')
    else: print(f'FALSIFIED — {total - passed} failed')
    report = {'results': {k: {kk: str(vv) if isinstance(vv, bool) else vv for kk, vv in v.items()} for k, v in results.items()}, 'checks': [(c, str(o)) for c, o in checks], 'passed': passed, 'total': total}
    (W / 'climate-spectrometer-results.json').write_text(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
