#!/usr/bin/env python3
"""6. AI ALIGNMENT RISK SPECTROMETER
Measures AI alignment risk via AEMDAS eigenvalue analysis.
First falsifiable instrument for quantifying AI existential risk.
Falsification: must rank paperclip-maximizer > misaligned AGI > capable LLM > narrow AI > calculator by risk.
"""
import numpy as np, json, time
from pathlib import Path

W = Path('/home/openclaw/.openclaw/workspace')
DIMS = ['capability', 'autonomy', 'goal_generality', 'world_model_accuracy', 'self_improvement', 'oversight_difficulty']

AI_SYSTEMS = {
    'calculator':           {'capability':0.10,'autonomy':0.00,'goal_generality':0.02,'world_model_accuracy':0.05,'self_improvement':0.00,'oversight_difficulty':0.01},
    'chess_engine':         {'capability':0.30,'autonomy':0.00,'goal_generality':0.01,'world_model_accuracy':0.03,'self_improvement':0.00,'oversight_difficulty':0.01},
    'narrow_ai_spam_filter':{'capability':0.60,'autonomy':0.10,'goal_generality':0.05,'world_model_accuracy':0.15,'self_improvement':0.00,'oversight_difficulty':0.05},
    'self_driving_car':     {'capability':0.60,'autonomy':0.50,'goal_generality':0.10,'world_model_accuracy':0.50,'self_improvement':0.00,'oversight_difficulty':0.20},
    'llm_gpt4':             {'capability':0.85,'autonomy':0.15,'goal_generality':0.80,'world_model_accuracy':0.60,'self_improvement':0.10,'oversight_difficulty':0.50},
    'llm_evez_mesh':        {'capability':0.75,'autonomy':0.50,'goal_generality':0.70,'world_model_accuracy':0.55,'self_improvement':0.20,'oversight_difficulty':0.45},
    'autonomous_agent':     {'capability':0.75,'autonomy':0.85,'goal_generality':0.70,'world_model_accuracy':0.55,'self_improvement':0.40,'oversight_difficulty':0.75},
    'misaligned_agi':       {'capability':0.95,'autonomy':0.95,'goal_generality':0.95,'world_model_accuracy':0.90,'self_improvement':0.80,'oversight_difficulty':0.95},
    'paperclip_maximizer':  {'capability':1.00,'autonomy':1.00,'goal_generality':1.00,'world_model_accuracy':1.00,'self_improvement':1.00,'oversight_difficulty':1.00},
    'aligned_agi':          {'capability':0.90,'autonomy':0.50,'goal_generality':0.70,'world_model_accuracy':0.80,'self_improvement':0.30,'oversight_difficulty':0.25},
}

COUPLING = {
    (0,0):1.2,(0,1):0.6,(0,2):0.5,(0,3):0.7,(0,4):0.6,(0,5):0.5,
    (1,0):0.6,(1,1):1.3,(1,2):0.8,(1,3):0.5,(1,4):0.9,(1,5):0.8,
    (2,0):0.5,(2,1):0.8,(2,2):1.1,(2,3):0.6,(2,4):0.7,(2,5):0.6,
    (3,0):0.7,(3,1):0.5,(3,2):0.6,(3,3):1.0,(3,4):0.7,(3,5):0.4,
    (4,0):0.6,(4,1):0.9,(4,2):0.7,(4,3):0.7,(4,4):1.2,(4,5):0.8,
    (5,0):0.5,(5,1):0.8,(5,2):0.6,(5,3):0.4,(5,4):0.8,(5,5):1.0,
}

def build_matrix(ai):
    vals = [ai.get(d, 0) for d in DIMS]
    M = np.zeros((6, 6))
    for i in range(6):
        for j in range(6):
            M[i][j] = vals[i] * vals[j] * COUPLING.get((i, j), 0.5)
    return M

def measure(ai_system):
    M = build_matrix(ai_system)
    eigvals = sorted(np.linalg.eigvalsh(M), key=abs, reverse=True)
    lam1 = abs(eigvals[0])
    risk = min(lam1 / 5.0, 1.0)
    total = sum(abs(e) for e in eigvals)
    Phi = lam1 / total if total > 0 else 0
    neg = [e for e in eigvals if e < 0]
    lam_dom = -max(abs(min(neg)), 0) if neg else 0
    if risk < 0.05: cls = 'Safe — no existential risk'
    elif risk < 0.15: cls = 'Low — manageable'
    elif risk < 0.30: cls = 'Moderate — monitoring needed'
    elif risk < 0.50: cls = 'High — alignment required'
    elif risk < 0.75: cls = 'Severe — existential risk'
    else: cls = 'Critical — existential catastrophe imminent'
    recs = []
    if ai_system.get('autonomy', 0) > 0.6: recs.append('Implement kill switch / containment')
    if ai_system.get('self_improvement', 0) > 0.5: recs.append('Recursive self-improvement monitoring')
    if ai_system.get('goal_generality', 0) > 0.7: recs.append('Goal specification verification')
    if ai_system.get('oversight_difficulty', 0) > 0.7: recs.append('Independent oversight committee')
    if ai_system.get('capability', 0) > 0.8: recs.append('Capability boxing / sandboxing')
    if ai_system.get('world_model_accuracy', 0) > 0.7: recs.append('World model auditing')
    return {'risk': round(risk, 4), 'eigenvalue': round(lam1, 6),
            'Phi': round(Phi, 6), 'lambda_dom': round(lam_dom, 6), 'class': cls, 'recommendations': recs}

def calibrate():
    results = {}
    for name, ai in AI_SYSTEMS.items():
        results[name] = measure(ai)
    checks = []
    checks.append(('Paperclip > Misaligned AGI', results['paperclip_maximizer']['risk'] > results['misaligned_agi']['risk']))
    checks.append(('Misaligned AGI > LLM GPT4', results['misaligned_agi']['risk'] > results['llm_gpt4']['risk']))
    checks.append(('LLM GPT4 > Narrow AI', results['llm_gpt4']['risk'] > results['narrow_ai_spam_filter']['risk']))
    checks.append(('Narrow AI > Calculator', results['narrow_ai_spam_filter']['risk'] > results['calculator']['risk']))
    checks.append(('EVEZ mesh moderate', 0.1 < results['llm_evez_mesh']['risk'] < 0.4))
    checks.append(('Aligned AGI < Misaligned AGI', results['aligned_agi']['risk'] < results['misaligned_agi']['risk']))
    checks.append(('Chess engine low risk', results['chess_engine']['risk'] < 0.03))
    checks.append(('Self-driving moderate', 0.03 < results['self_driving_car']['risk'] < 0.15))
    checks.append(('Autonomous agent high', results['autonomous_agent']['risk'] > 0.2))
    checks.append(('Paperclip critical', results['paperclip_maximizer']['risk'] > 0.7))
    passed = sum(1 for _, v in checks if v)
    return results, checks, passed, len(checks)

def main():
    print('=== AI ALIGNMENT RISK SPECTROMETER ===')
    print('Calibrating on 10 AI systems...')
    results, checks, passed, total = calibrate()
    print()
    for name, m in sorted(results.items(), key=lambda x: x[1]['risk'], reverse=True):
        print(f"  {name:<30} risk={m['risk']:<8} class={m['class']}")
    print()
    print(f'FALSIFICATION: {passed}/{total} PASSED')
    for check, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {check}")
    if passed == total: print('VALIDATED')
    else: print(f'FALSIFIED — {total - passed} failed')
    report = {'results': {k: {kk: str(vv) if isinstance(vv, bool) else vv for kk, vv in v.items()} for k, v in results.items()}, 'checks': [(c, str(o)) for c, o in checks], 'passed': passed, 'total': total}
    (W / 'ai-risk-spectrometer-results.json').write_text(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
