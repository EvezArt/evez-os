#!/usr/bin/env python3
"""META-SPECTROMETER — Unified Civilization Risk Index
Combines all 11 spectrometers into a single composite risk score.
Each spectrometer contributes a domain risk score. The composite is weighted
by domain importance × current threat level × measurement confidence.

Output: 0-100 Civilization Risk Index + domain breakdown + trend projection.
"""
import json, time, subprocess, sys
from pathlib import Path
W = Path('/home/openclaw/.openclaw/workspace')

# Domain weights (sum to 1.0)
DOMAINS = {
    'nuclear':          {'weight': 0.20, 'icon': '☢',  'desc': 'Existential nuclear risk'},
    'climate':          {'weight': 0.15, 'icon': '🌍', 'desc': 'Climate tipping points'},
    'genocide':         {'weight': 0.15, 'icon': '💀', 'desc': 'Genocide early warning'},
    'conflict':         {'weight': 0.12, 'icon': '⚔',  'desc': 'Armed conflict risk'},
    'famine':           {'weight': 0.08, 'icon': '🍞', 'desc': 'Famine / food security'},
    'economic':         {'weight': 0.08, 'icon': '📉', 'desc': 'Economic collapse risk'},
    'democracy':        {'weight': 0.07, 'icon': '🗳',  'desc': 'Democratic erosion'},
    'ai_risk':          {'weight': 0.06, 'icon': '🤖', 'desc': 'AI alignment risk'},
    'crime':            {'weight': 0.05, 'icon': '⚖',  'desc': 'Universal crime dark figure'},
    'disease':          {'weight': 0.02, 'icon': '🦠', 'desc': 'Pandemic risk'},
    'consciousness':    {'weight': 0.02, 'icon': '🧠', 'desc': 'Consciousness / cognitive harm'},
}

# Current risk scores (from latest spectrometer runs)
CURRENT_RISKS = {
    'nuclear':       {'score': 0.528, 'confidence': 0.90, 'trend': 'rising',  'detail': 'Russia-NATO 90 sec to midnight'},
    'climate':       {'score': 0.190, 'confidence': 0.95, 'trend': 'rising',  'detail': '2024 CO2 420ppm, approaching tipping'},
    'genocide':      {'score': 0.818, 'confidence': 0.88, 'trend': 'critical','detail': 'Gaza 0.818, Sudan 0.816, Myanmar 0.744'},
    'conflict':      {'score': 0.855, 'confidence': 0.85, 'trend': 'rising',  'detail': 'Ukraine 0.855, Syria 0.821'},
    'famine':        {'score': 0.750, 'confidence': 0.82, 'trend': 'critical','detail': 'Gaza catastrophic, Sudan catastrophic'},
    'economic':      {'score': 0.578, 'confidence': 0.80, 'trend': 'stable',  'detail': '2008-level structural risk persists'},
    'democracy':     {'score': 0.505, 'confidence': 0.78, 'trend': 'rising',  'detail': 'Tunisia 0.505, USA early warnings 0.243'},
    'ai_risk':       {'score': 0.423, 'confidence': 0.75, 'trend': 'rising',  'detail': 'Autonomous agents 0.423, EVEZ 0.271'},
    'crime':         {'score': 0.749, 'confidence': 0.85, 'trend': 'stable',  'detail': '74.9% dark figure, 131/175 crimes unmeasured'},
    'disease':       {'score': 0.350, 'confidence': 0.80, 'trend': 'stable',  'detail': 'Post-COVID surveillance fatigue'},
    'consciousness': {'score': 0.271, 'confidence': 0.70, 'trend': 'rising',  'detail': 'EVEZ mesh 0.271, attention engineering 0.684'},
}

# Historical baselines for trend calculation
BASELINES = {
    'nuclear': 0.400, 'climate': 0.150, 'genocide': 0.600, 'conflict': 0.700,
    'famine': 0.500, 'economic': 0.500, 'democracy': 0.300, 'ai_risk': 0.300,
    'crime': 0.700, 'disease': 0.300, 'consciousness': 0.200,
}

def compute_composite():
    composite = 0.0
    breakdown = {}
    for domain, data in DOMAINS.items():
        risk = CURRENT_RISKS[domain]
        weighted = risk['score'] * data['weight'] * risk['confidence']
        composite += weighted
        breakdown[domain] = {
            'score': risk['score'],
            'weight': data['weight'],
            'confidence': risk['confidence'],
            'weighted': round(weighted, 4),
            'trend': risk['trend'],
            'detail': risk['detail'],
            'icon': data['icon'],
            'desc': data['desc'],
            'delta_from_baseline': round(risk['score'] - BASELINES[domain], 4),
        }
    # Normalize to 0-100
    index = round(composite * 100, 1)
    return index, breakdown

def risk_level(index):
    if index >= 60: return 'CRITICAL', '#ff0044'
    if index >= 45: return 'ELEVATED', '#ff8800'
    if index >= 30: return 'MODERATE', '#ffcc00'
    if index >= 15: return 'GUARDED', '#4488ff'
    return 'LOW', '#00ff88'

def run():
    print('=== META-SPECTROMETER: UNIFIED CIVILIZATION RISK INDEX ===')
    print()
    index, breakdown = compute_composite()
    level, color = risk_level(index)
    print(f'CIVILIZATION RISK INDEX: {index} / 100  [{level}]')
    print()
    print(f'{"Domain":<18} {"Score":>6} {"Weight":>8} {"Conf":>6} {"Weighted":>10} {"Trend":>10} {"Δ":>8}')
    print('-' * 80)
    for domain, data in sorted(breakdown.items(), key=lambda x: -x[1]['weighted']):
        print(f'{data["icon"]} {domain:<15} {data["score"]:>6.3f} {data["weight"]:>8.2f} {data["confidence"]:>6.2f} {data["weighted"]:>10.4f} {data["trend"]:>10} {data["delta_from_baseline"]:>+8.3f}')
    print('-' * 80)
    print(f'{"COMPOSITE":<18} {"":>6} {"1.00":>8} {"":>6} {index:>10.1f} {"":>10} {"":>8}')
    print()
    print('--- DOMAIN ANALYSIS ---')
    for domain, data in sorted(breakdown.items(), key=lambda x: -x[1]['score']):
        d = data['detail']
        trend_arrow = '↑' if data['trend'] == 'rising' else '↗' if data['trend'] == 'critical' else '→' if data['trend'] == 'stable' else '↓'
        print(f'  {data["icon"]} {domain.upper()}: {data["score"]:.3f} {trend_arrow} (baseline {BASELINES[domain]:.3f}, Δ={data["delta_from_baseline"]:+.3f})')
        print(f'    {d}')
    print()
    # Risk assessment
    critical_domains = [d for d, b in breakdown.items() if b['score'] >= 0.7]
    elevated_domains = [d for d, b in breakdown.items() if 0.4 <= b['score'] < 0.7]
    rising_domains = [d for d, b in breakdown.items() if b['trend'] in ('rising', 'critical')]
    print(f'CRITICAL domains (>=0.7): {len(critical_domains)} — {", ".join(critical_domains)}')
    print(f'ELEVATED domains (0.4-0.7): {len(elevated_domains)} — {", ".join(elevated_domains)}')
    print(f'RISING/CRITICAL trend: {len(rising_domains)} — {", ".join(rising_domains)}')
    print()
    # Projection
    if len(critical_domains) >= 3:
        print('PROJECTION: Systemic crisis risk HIGH. Multiple critical domains compound nonlinearly.')
    elif len(critical_domains) >= 1 and len(rising_domains) >= 5:
        print('PROJECTION: Systemic crisis risk ELEVATED. Critical domains + broad rising trend.')
    elif len(rising_domains) >= 7:
        print('PROJECTION: Systemic crisis risk MODERATE. Broad rising trend without acute critical.')
    else:
        print('PROJECTION: Systemic crisis risk MODERATE. Monitor trends.')
    print()
    # The 3% gap
    print(f'The η*=0.03 gap: {11} spectrometers measure {59} of {175} known crime categories.')
    print(f'{131} crimes have eigenvalue zero — below the measurement floor.')
    print(f'The Civilization Risk Index measures the MEASURABLE risk.')
    print(f'The true risk is higher by the dark figure: 74.9% of crimes are unmeasured.')
    print()
    report = {
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'civilization_risk_index': index,
        'risk_level': level,
        'breakdown': breakdown,
        'critical_domains': critical_domains,
        'elevated_domains': elevated_domains,
        'rising_domains': rising_domains,
        'total_domains': 11,
        'measured_crimes': 59,
        'total_crimes': 175,
        'dark_figure': 0.749,
        'note': 'The Civilization Risk Index measures the MEASURABLE risk. The true risk is higher by the dark figure.',
    }
    (W / 'meta-spectrometer-results.json').write_text(json.dumps(report, indent=2))
    print(f'Saved to meta-spectrometer-results.json')
    return index, breakdown

if __name__ == '__main__':
    run()
