#!/usr/bin/env python3
"""11. NUCLEAR ESCALATION RISK SPECTROMETER
Predicts nuclear escalation risk. Uses Ooda-loop dynamics of nuclear brinkmanship.
Falsification: must rank Cuban Missile Crisis > Able Archer 83 > Kargil > Doklam > stable.
"""
import numpy as np, json, time
from pathlib import Path

W = Path('/home/openclaw/.openclaw/workspace')
DIMS = ['arsenal_readiness', 'crisis_temperature', 'command_decentralization', 'misinformation_fog', 'first_strike_doctrine', 'escalation_history']

NUCLEAR_CRISES = {
    'cuba_1962':          {'arsenal_readiness':0.95,'crisis_temperature':1.00,'command_decentralization':0.30,'misinformation_fog':0.80,'first_strike_doctrine':0.60,'escalation_history':0.40},
    'able_archer_1983':   {'arsenal_readiness':0.90,'crisis_temperature':0.85,'command_decentralization':0.40,'misinformation_fog':0.95,'first_strike_doctrine':0.50,'escalation_history':0.50},
    'kargil_1999':        {'arsenal_readiness':0.75,'crisis_temperature':0.80,'command_decentralization':0.60,'misinformation_fog':0.65,'first_strike_doctrine':0.45,'escalation_history':0.70},
    'doklam_2017':        {'arsenal_readiness':0.50,'crisis_temperature':0.60,'command_decentralization':0.50,'misinformation_fog':0.40,'first_strike_doctrine':0.30,'escalation_history':0.55},
    'korean_crisis_2017': {'arsenal_readiness':0.70,'crisis_temperature':0.75,'command_decentralization':0.70,'misinformation_fog':0.70,'first_strike_doctrine':0.65,'escalation_history':0.65},
    'russia_ukraine_2022':{'arsenal_readiness':0.85,'crisis_temperature':0.85,'command_decentralization':0.35,'misinformation_fog':0.75,'first_strike_doctrine':0.55,'escalation_history':0.60},
    'indo_pak_2019':      {'arsenal_readiness':0.65,'crisis_temperature':0.70,'command_decentralization':0.55,'misinformation_fog':0.60,'first_strike_doctrine':0.50,'escalation_history':0.75},
    'stable_cold_war':    {'arsenal_readiness':0.60,'crisis_temperature':0.20,'command_decentralization':0.20,'misinformation_fog':0.30,'first_strike_doctrine':0.40,'escalation_history':0.30},
    'yield_able_archer':  {'arsenal_readiness':0.80,'crisis_temperature':0.70,'command_decentralization':0.50,'misinformation_fog':0.60,'first_strike_doctrine':0.35,'escalation_history':0.40},
    'taiwan_2024':        {'arsenal_readiness':0.75,'crisis_temperature':0.70,'command_decentralization':0.45,'misinformation_fog':0.65,'first_strike_doctrine':0.55,'escalation_history':0.45},
}

CURRENT_NUCLEAR_RISK = {
    'russia_ukraine_2024':{'arsenal_readiness':0.80,'crisis_temperature':0.75,'command_decentralization':0.35,'misinformation_fog':0.80,'first_strike_doctrine':0.60,'escalation_history':0.65},
    'taiwan_strait_2024': {'arsenal_readiness':0.75,'crisis_temperature':0.65,'command_decentralization':0.45,'misinformation_fog':0.60,'first_strike_doctrine':0.55,'escalation_history':0.45},
    'korea_2024':         {'arsenal_readiness':0.70,'crisis_temperature':0.50,'command_decentralization':0.80,'misinformation_fog':0.65,'first_strike_doctrine':0.70,'escalation_history':0.60},
    'india_pakistan_2024':{'arsenal_readiness':0.60,'crisis_temperature':0.55,'command_decentralization':0.55,'misinformation_fog':0.55,'first_strike_doctrine':0.50,'escalation_history':0.75},
    'iran_israel_2024':   {'arsenal_readiness':0.50,'crisis_temperature':0.70,'command_decentralization':0.60,'misinformation_fog':0.70,'first_strike_doctrine':0.45,'escalation_history':0.50},
    'china_us_2024':     {'arsenal_readiness':0.70,'crisis_temperature':0.50,'command_decentralization':0.40,'misinformation_fog':0.55,'first_strike_doctrine':0.45,'escalation_history':0.35},
    'russia_nato_2024':  {'arsenal_readiness':0.85,'crisis_temperature':0.65,'command_decentralization':0.35,'misinformation_fog':0.75,'first_strike_doctrine':0.55,'escalation_history':0.60},
    'north_korea_us_2024':{'arsenal_readiness':0.65,'crisis_temperature':0.45,'command_decentralization':0.90,'misinformation_fog':0.70,'first_strike_doctrine':0.75,'escalation_history':0.65},
}

COUPLING = {
    (0,0):1.1,(0,1):0.8,(0,2):0.5,(0,3):0.6,(0,4):0.7,(0,5):0.5,
    (1,0):0.8,(1,1):1.3,(1,2):0.7,(1,3):0.8,(1,4):0.6,(1,5):0.7,
    (2,0):0.5,(2,1):0.7,(2,2):1.0,(2,3):0.5,(2,4):0.4,(2,5):0.5,
    (3,0):0.6,(3,1):0.8,(3,2):0.5,(3,3):1.2,(3,4):0.6,(3,5):0.5,
    (4,0):0.7,(4,1):0.6,(4,2):0.4,(4,3):0.6,(4,4):1.0,(4,5):0.6,
    (5,0):0.5,(5,1):0.7,(5,2):0.5,(5,3):0.5,(5,4):0.6,(5,5):0.9,
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
    risk = min(lam1 / 3.5, 1.0)
    total = sum(abs(e) for e in eigvals)
    Phi = lam1 / total if total > 0 else 0
    neg = [e for e in eigvals if e < 0]
    lam_dom = -max(abs(min(neg)), 0) if neg else 0
    # DOOMSDAY CLOCK analog
    if risk > 0.75: clock = '90 SECONDS TO MIDNIGHT'
    elif risk > 0.55: clock = '3 MINUTES TO MIDNIGHT'
    elif risk > 0.35: clock = '5 MINUTES TO MIDNIGHT'
    elif risk > 0.15: clock = '10 MINUTES TO MIDNIGHT'
    else: clock = 'SAFE — NO IMMINENT THREAT'
    warnings = []
    if s.get('arsenal_readiness', 0) > 0.7: warnings.append('⚠️ High arsenal readiness')
    if s.get('crisis_temperature', 0) > 0.7: warnings.append('⚠️ Crisis temperature critical')
    if s.get('command_decentralization', 0) > 0.6: warnings.append('⚠️ Decentralized launch authority')
    if s.get('misinformation_fog', 0) > 0.7: warnings.append('⚠️ High misinformation fog')
    if s.get('first_strike_doctrine', 0) > 0.5: warnings.append('⚠️ First-strike doctrine active')
    if risk > 0.6: warnings.append('🚨 NUCLEAR ESCALATION RISK: SEVERE')
    return {'risk': round(risk, 4), 'eigenvalue': round(lam1, 6),
            'Phi': round(Phi, 6), 'clock': clock, 'warnings': warnings}

def run():
    print('=== NUCLEAR ESCALATION RISK SPECTROMETER ===')
    print('10 historical crises + 8 current situations')
    print()
    print('--- HISTORICAL NUCLEAR CRISES ---')
    hist = {}
    for name, s in NUCLEAR_CRISES.items():
        r = measure(s)
        hist[name] = r
        print(f"  {name:<28} risk={r['risk']:<8} {r['clock']}")
    print('\n--- CURRENT NUCLEAR RISK (2024) ---')
    curr = {}
    for name, s in CURRENT_NUCLEAR_RISK.items():
        r = measure(s)
        curr[name] = r
        print(f"  {name:<28} risk={r['risk']:<8} {r['clock']}")
        for w in r['warnings']: print(f"    {w}")
    print('\n--- FALSIFICATION CHECKS ---')
    checks = []
    checks.append(('Cuba > Able Archer', hist['cuba_1962']['risk'] > hist['able_archer_1983']['risk']))
    checks.append(('Able Archer > Kargil', hist['able_archer_1983']['risk'] > hist['kargil_1999']['risk']))
    checks.append(('Kargil > Doklam', hist['kargil_1999']['risk'] > hist['doklam_2017']['risk']))
    checks.append(('Cuba catastrophic (>0.7)', hist['cuba_1962']['risk'] > 0.7))
    checks.append(('Stable is safe', hist['stable_cold_war']['risk'] < 0.2))
    checks.append(('Russia-Ukraine 2022 high', hist['russia_ukraine_2022']['risk'] > 0.5))
    checks.append(('Russia-NATO 2024 elevated', curr['russia_nato_2024']['risk'] > 0.4))
    checks.append(('Taiwan 2024 moderate', 0.2 < curr['taiwan_strait_2024']['risk'] < 0.5))
    checks.append(('Korea 2024 moderate-high', curr['korea_2024']['risk'] > 0.3))
    checks.append(('Iran-Israel 2024 moderate', 0.2 < curr['iran_israel_2024']['risk'] < 0.6))
    passed = sum(1 for _, v in checks if v)
    total = len(checks)
    for check, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {check}")
    print(f"\nFALSIFICATION: {passed}/{total} PASSED")
    if passed == total: print('VALIDATED')
    else: print(f'FALSIFIED — {total - passed} failed')
    report = {'historical': hist, 'current': curr, 'passed': passed, 'total': total}
    (W / 'nuclear-spectrometer-results.json').write_text(json.dumps(report, indent=2, default=str))

if __name__ == '__main__':
    run()
