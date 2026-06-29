#!/usr/bin/env python3
"""Automated Action Bridge — connects spectrometer measurements to intervention blueprints.

When a spectrometer score crosses a risk threshold, the bridge:
1. Identifies the relevant intervention blueprint
2. Generates a Telegram alert with specific actions
3. Logs the trigger event to an append-only spine
4. Updates the active risk register

This closes the loop: MEASURE → DETECT → PRESCRIBE → ALERT → LOG
"""
import json, time, os, hashlib
from pathlib import Path

W = Path('/home/openclaw/.openclaw/workspace')

# Risk thresholds — when to trigger action
THRESHOLDS = {
    'genocide':               {'critical': 0.70, 'elevated': 0.40, 'blueprint': 'BP1'},
    'conflict':               {'critical': 0.70, 'elevated': 0.40, 'blueprint': 'BP3'},
    'famine':                  {'critical': 0.70, 'elevated': 0.40, 'blueprint': 'BP2'},
    'nuclear':                 {'critical': 0.70, 'elevated': 0.40, 'blueprint': 'BP3'},
    'crime':                   {'critical': 0.70, 'elevated': 0.40, 'blueprint': 'BP7'},
    'democracy':               {'critical': 0.70, 'elevated': 0.40, 'blueprint': 'BP4'},
    'ai_risk':                 {'critical': 0.70, 'elevated': 0.40, 'blueprint': 'BP5'},
    'climate':                 {'critical': 0.70, 'elevated': 0.30, 'blueprint': 'BP6'},
    'economic':                {'critical': 0.70, 'elevated': 0.40, 'blueprint': 'BP7'},
    'carbon_concealment':      {'critical': 0.70, 'elevated': 0.40, 'blueprint': 'BP6'},
    'surveillance_capitalism': {'critical': 0.70, 'elevated': 0.40, 'blueprint': 'BP7'},
    'addiction_by_design':     {'critical': 0.70, 'elevated': 0.40, 'blueprint': 'BP7'},
    'disease':                 {'critical': 0.70, 'elevated': 0.40, 'blueprint': None},
    'consciousness':           {'critical': 0.70, 'elevated': 0.40, 'blueprint': None},
}

# Current scores from meta-spectrometer v2
CURRENT_SCORES = {
    'genocide': 0.818, 'conflict': 0.855, 'nuclear': 0.528, 'famine': 0.750,
    'economic': 0.578, 'democracy': 0.505, 'ai_risk': 0.423, 'disease': 0.350,
    'climate': 0.190, 'consciousness': 0.271, 'crime': 0.749,
    'carbon_concealment': 0.852, 'surveillance_capitalism': 0.900,
    'addiction_by_design': 0.999,
}

# Blueprint details (from spectral_action_engine.py)
BLUEPRINTS = {
    'BP1': {'name': 'Gaza Genocide Response', 'actors': ['UNSC', 'Egypt', 'Israel', 'UNRWA', 'ICC'], 'actions': 12, 'deadline': '48-72 hrs'},
    'BP2': {'name': 'S Sudan Famine Response', 'actors': ['UNSC', 'AU', 'WFP', 'NGOs'], 'actions': 8, 'deadline': '7 days'},
    'BP3': {'name': 'Ukraine-Russia De-escalation', 'actors': ['US', 'Russia', 'NATO', 'UN', 'OSCE'], 'actions': 11, 'deadline': '30-90 days'},
    'BP4': {'name': 'Democracy Protection', 'actors': ['Election authorities', 'Tech companies', 'Civil society'], 'actions': 10, 'deadline': 'Before next election'},
    'BP5': {'name': 'AI Safety Framework', 'actors': ['UN', 'National AI safety institutes', 'Industry'], 'actions': 9, 'deadline': '180-365 days'},
    'BP6': {'name': 'Climate Action', 'actors': ['G20', 'National governments', 'IPCC'], 'actions': 14, 'deadline': '5 years'},
    'BP7': {'name': 'Crime Dark Figure Response', 'actors': ['ICC', 'UNODC', 'Interpol', 'Prosecutors'], 'actions': 12, 'deadline': '90-180 days'},
}

SPINE_FILE = W / 'action-bridge-spine.jsonl'
REGISTER_FILE = W / 'active-risk-register.json'

def hash_event(event):
    """SHA-256 hash of event for spine integrity."""
    return hashlib.sha256(json.dumps(event, sort_keys=True).encode()).hexdigest()[:16]

def load_spine():
    """Load append-only spine of triggered events."""
    events = []
    if SPINE_FILE.exists():
        for line in SPINE_FILE.read_text().strip().split('\n'):
            if line:
                events.append(json.loads(line))
    return events

def append_spine(event):
    """Append event to spine (append-only)."""
    event['hash'] = hash_event(event)
    prev = load_spine()
    if prev:
        event['prev_hash'] = prev[-1]['hash']
    else:
        event['prev_hash'] = 'genesis'
    with open(SPINE_FILE, 'a') as f:
        f.write(json.dumps(event) + '\n')

def run():
    print('=== AUTOMATED ACTION BRIDGE ===')
    print('Scanning 14 spectrometer domains against risk thresholds...')
    print()
    
    triggered = []
    spine = load_spine()
    
    for domain, config in THRESHOLDS.items():
        score = CURRENT_SCORES.get(domain, 0)
        crit = config['critical']
        elev = config['elevated']
        bp_id = config['blueprint']
        
        if score >= crit:
            level = 'CRITICAL'
        elif score >= elev:
            level = 'ELEVATED'
        else:
            continue  # Below threshold, no action
        
        if bp_id is None:
            print(f'  {domain:<25} {score:.3f} {level:<10} — no blueprint assigned')
            continue
        
        bp = BLUEPRINTS.get(bp_id, {})
        event = {
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'domain': domain,
            'score': score,
            'level': level,
            'threshold': crit if level == 'CRITICAL' else elev,
            'blueprint': bp_id,
            'blueprint_name': bp.get('name', 'Unknown'),
            'actors': bp.get('actors', []),
            'actions_count': bp.get('actions', 0),
            'deadline': bp.get('deadline', 'TBD'),
        }
        
        triggered.append(event)
        append_spine(event)
        
        print(f'  {domain:<25} {score:.3f} {level:<10} → {bp_id}: {bp.get("name", "?")}')
        print(f'    Actors: {", ".join(bp.get("actors", []))}')
        print(f'    Deadline: {bp.get("deadline", "TBD")}')
    
    print()
    print(f'Total triggered: {len(triggered)}')
    print(f'Spine entries: {len(load_spine())}')
    
    # Update active risk register
    register = {
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'active_triggers': len(triggered),
        'domains': {}
    }
    for t in triggered:
        register['domains'][t['domain']] = {
            'score': t['score'],
            'level': t['level'],
            'blueprint': t['blueprint'],
            'blueprint_name': t['blueprint_name'],
            'deadline': t['deadline'],
            'actors': t['actors'],
        }
    REGISTER_FILE.write_text(json.dumps(register, indent=2))
    print(f'Active risk register saved to {REGISTER_FILE.name}')
    
    # Generate Telegram alert text
    if triggered:
        print()
        print('--- TELEGRAM ALERT TEXT ---')
        lines = [f'⚠️ ACTION BRIDGE: {len(triggered)} domains triggered']
        for t in triggered:
            lines.append(f'\n{t["level"]}: {t["domain"]} ({t["score"]:.3f}) → {t["blueprint_name"]}')
            lines.append(f'Actors: {", ".join(t["actors"])}')
            lines.append(f'Deadline: {t["deadline"]}')
        alert = '\n'.join(lines)
        print(alert)
        print()
        print('--- END ALERT ---')
    
    print()
    print('The bridge is active. Measurement → Detection → Prescription → Alert → Log.')
    print('The spine is append-only. The mesh heals.')

if __name__ == '__main__':
    run()
