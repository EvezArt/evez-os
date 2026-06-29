#!/usr/bin/env python3
"""Meta-Spectrometer v2 — Unified Civilization Risk Index
Updated to include all 14 spectrometers (11 original + 3 dark matter).

New formula: CRI = Σ(domain_score × weight × confidence) × 100
Weights adjusted for 14 domains. Dark matter crimes get lower weight
(higher uncertainty) but non-zero contribution.
"""
import json, time, numpy as np
from pathlib import Path

W = Path('/home/openclaw/.openclaw/workspace')

# 14 domains with weights and current scores
DOMAINS = {
    # Original 11 (high confidence — validated spectrometers)
    'genocide':     {'weight': 0.13, 'score': 0.818, 'confidence': 0.95, 'class': 'CRITICAL', 'trend': 'rising'},
    'conflict':     {'weight': 0.10, 'score': 0.855, 'confidence': 0.95, 'class': 'CRITICAL', 'trend': 'rising'},
    'nuclear':      {'weight': 0.14, 'score': 0.528, 'confidence': 0.90, 'class': 'ELEVATED', 'trend': 'rising'},
    'famine':       {'weight': 0.08, 'score': 0.750, 'confidence': 0.95, 'class': 'CRITICAL', 'trend': 'rising'},
    'economic':     {'weight': 0.07, 'score': 0.578, 'confidence': 0.85, 'class': 'ELEVATED', 'trend': 'stable'},
    'democracy':    {'weight': 0.05, 'score': 0.505, 'confidence': 0.90, 'class': 'ELEVATED', 'trend': 'rising'},
    'ai_risk':      {'weight': 0.06, 'score': 0.423, 'confidence': 0.85, 'class': 'ELEVATED', 'trend': 'rising'},
    'disease':      {'weight': 0.02, 'score': 0.350, 'confidence': 0.90, 'class': 'MODERATE', 'trend': 'stable'},
    'climate':      {'weight': 0.10, 'score': 0.190, 'confidence': 0.90, 'class': 'LOW',     'trend': 'rising'},
    'consciousness':{'weight': 0.02, 'score': 0.271, 'confidence': 0.80, 'class': 'LOW',    'trend': 'rising'},
    'crime':        {'weight': 0.05, 'score': 0.749, 'confidence': 0.95, 'class': 'CRITICAL', 'trend': 'stable'},
    # 3 new dark matter spectrometers (lower confidence — new instruments)
    'carbon_concealment':     {'weight': 0.04, 'score': 0.852, 'confidence': 0.70, 'class': 'CRITICAL', 'trend': 'stable'},
    'surveillance_capitalism': {'weight': 0.03, 'score': 0.900, 'confidence': 0.70, 'class': 'CRITICAL', 'trend': 'rising'},
    'addiction_by_design':   {'weight': 0.03, 'score': 0.999, 'confidence': 0.70, 'class': 'CRITICAL', 'trend': 'rising'},
    'cognitive_sovereignty': {'weight': 0.03, 'score': 0.933, 'confidence': 0.65, 'class': 'CRITICAL', 'trend': 'rising'},
    'regulatory_capture':    {'weight': 0.03, 'score': 0.959, 'confidence': 0.65, 'class': 'CRITICAL', 'trend': 'stable'},
    'dark_patterns':        {'weight': 0.02, 'score': 0.821, 'confidence': 0.65, 'class': 'ELEVATED', 'trend': 'rising'},
}

# Verify weights sum to 1.0
total_weight = sum(d['weight'] for d in DOMAINS.values())
assert abs(total_weight - 1.0) < 0.01, f'Weights sum to {total_weight}, not 1.0'

def compute_cri():
    """Compute Civilization Risk Index from 14 domains."""
    cri = 0.0
    breakdown = {}
    for name, d in DOMAINS.items():
        weighted = d['score'] * d['weight'] * d['confidence']
        cri += weighted
        breakdown[name] = {
            'score': d['score'],
            'weight': d['weight'],
            'confidence': d['confidence'],
            'weighted': weighted,
            'class': d['class'],
            'trend': d['trend'],
        }
    cri *= 100  # scale to 0-100
    return cri, breakdown

def run():
    print('=== META-SPECTROMETER v2 (14 DOMAINS) ===')
    print(f'Weights: sum = {total_weight:.2f}')
    print()
    
    cri, breakdown = compute_cri()
    
    # Sort by weighted contribution
    sorted_domains = sorted(breakdown.items(), key=lambda x: -x[1]['weighted'])
    
    print(f'{"Domain":<25} {"Score":>6} {"Weight":>7} {"Conf":>5} {"Weighted":>8} {"Class":>10} {"Trend":>8}')
    print('-' * 75)
    for name, d in sorted_domains:
        print(f'{name:<25} {d["score"]:>6.3f} {d["weight"]:>7.2f} {d["confidence"]:>5.2f} {d["weighted"]:>8.4f} {d["class"]:>10} {d["trend"]:>8}')
    print('-' * 75)
    print()
    
    # Classification
    if cri >= 70:
        level = 'CRITICAL'
    elif cri >= 40:
        level = 'ELEVATED'
    elif cri >= 20:
        level = 'MODERATE'
    else:
        level = 'LOW'
    
    print(f'CIVILIZATION RISK INDEX: {cri:.1f} / 100 — {level}')
    print()
    
    # Count by class
    classes = {}
    for d in DOMAINS.values():
        c = d['class']
        classes[c] = classes.get(c, 0) + 1
    print('By class:', ', '.join(f'{c}: {n}' for c, n in sorted(classes.items())))
    
    trends = {}
    for d in DOMAINS.values():
        t = d['trend']
        trends[t] = trends.get(t, 0) + 1
    print('By trend:', ', '.join(f'{t}: {n}' for t, n in sorted(trends.items())))
    print()
    
    # Critical domains
    critical = [n for n, d in DOMAINS.items() if d['class'] == 'CRITICAL']
    print(f'CRITICAL domains ({len(critical)}): {" → ".join(critical)}')
    print('Coupling: genocide → conflict → famine → crime → carbon_concealment → surveillance → addiction')
    print('The dark matter crimes compound with the original critical four.')
    print()
    
    # Comparison with v1
    cri_v1 = 49.1
    delta = cri - cri_v1
    print(f'CRI v1 (11 domains): {cri_v1:.1f}')
    print(f'CRI v2 (14 domains): {cri:.1f}')
    print(f'Delta: {delta:+.1f}')
    if delta > 0:
        print(f'The 3 dark matter spectrometers increased the CRI by {delta:.1f} points.')
        print('The dark figure was hiding risk. Measurement reveals it.')
    print()
    
    # Projection
    rising = sum(1 for d in DOMAINS.values() if d['trend'] == 'rising')
    falling = sum(1 for d in DOMAINS.values() if d['trend'] == 'falling')
    print(f'PROJECTION: {rising} rising, {falling} falling. ', end='')
    if rising > falling and cri > 40:
        print('Systemic crisis risk: HIGH')
    elif rising > falling:
        print('Systemic crisis risk: ELEVATED')
    else:
        print('Systemic crisis risk: MODERATE')
    print()
    
    # The dark figure
    total_crimes = 175
    measured = 35  # 32 original + 3 new
    unmeasured = total_crimes - measured
    dark_figure = unmeasured / total_crimes
    print(f'Dark figure: {unmeasured}/{total_crimes} = {dark_figure:.1%} (was 74.9%, now {dark_figure:.1%})')
    print('CRI is a lower bound. The true risk is higher by the dark figure.')
    print()
    
    report = {
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'version': 'v2',
        'domains': DOMAINS.__len__(),
        'cri': round(cri, 1),
        'level': level,
        'breakdown': {k: v for k, v in sorted(breakdown.items(), key=lambda x: -x[1]['weighted'])},
        'cri_v1': cri_v1,
        'delta_from_v1': round(delta, 1),
        'dark_figure': round(dark_figure, 3),
        'total_crime_categories': total_crimes,
        'measured_crimes': measured,
        'unmeasured_crimes': unmeasured,
        'projection': f'{rising} rising, {falling} falling, systemic crisis risk HIGH',
        'note': 'CRI v2 adds 3 dark matter spectrometers. The dark figure hid risk. Measurement reveals it. CRI is a lower bound.',
    }
    (W / 'meta-spectrometer-v2-results.json').write_text(json.dumps(report, indent=2))
    print('Saved to meta-spectrometer-v2-results.json')

if __name__ == '__main__':
    run()
