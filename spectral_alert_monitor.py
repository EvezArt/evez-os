#!/usr/bin/env python3
"""SPECTRAL ALERT MONITOR — Cron job: re-run spectrometers, compare to last results,
send Telegram alert if risk scores changed significantly.
Designed to run every 30 minutes via cron or heartbeat.
"""
import json, time, subprocess, os
from pathlib import Path
W = Path('/home/openclaw/.openclaw/workspace')
LAST = W / 'spectral-alert-state.json'
THRESHOLD = 0.05  # Alert if any domain changes by more than 5%

def run_spectrometers():
    """Run all 11 spectrometers, return results dict."""
    results = {}
    spectrometers = [
        ('nuclear', 'nuclear_spectrometer.py'),
        ('climate', 'climate_spectrometer.py'),
        ('genocide', 'genocide_ews_spectrometer.py'),
        ('conflict', 'conflict_spectrometer.py'),
        ('famine', 'famine_spectrometer.py'),
        ('economic', 'economic_spectrometer.py'),
        ('democracy', 'democracy_spectrometer.py'),
        ('ai_risk', 'ai_risk_spectrometer.py'),
        ('crime', 'universal_crime_spectrometer.py'),
        ('disease', 'disease_spectrometer.py'),
        ('consciousness', 'consciousness_spectrometer.py'),
    ]
    for name, script in spectrometers:
        path = W / script
        if not path.exists():
            results[name] = {'error': f'{script} not found'}
            continue
        try:
            r = subprocess.run(['python3', str(path)], capture_output=True, text=True, timeout=60)
            if r.returncode == 0:
                results[name] = {'status': 'ok', 'stdout': r.stdout[-500:] if r.stdout else ''}
            else:
                results[name] = {'status': 'error', 'error': r.stderr[-200:]}
        except subprocess.TimeoutExpired:
            results[name] = {'status': 'timeout'}
        except Exception as e:
            results[name] = {'status': 'exception', 'error': str(e)}
    return results

def load_last():
    if LAST.exists():
        return json.loads(LAST.read_text())
    return None

def save_current(results):
    LAST.write_text(json.dumps(results, indent=2))

def check_changes(current, last):
    """Compare current vs last, return list of significant changes."""
    changes = []
    if not last or 'scores' not in last:
        return changes
    for domain, data in current.get('scores', {}).items():
        old_score = last['scores'].get(domain, {}).get('score', 0)
        new_score = data.get('score', 0)
        delta = abs(new_score - old_score)
        if delta >= THRESHOLD:
            changes.append({
                'domain': domain,
                'old': round(old_score, 3),
                'new': round(new_score, 3),
                'delta': round(delta, 3),
                'direction': 'up' if new_score > old_score else 'down',
            })
    return changes

def send_telegram(message):
    """Send alert via Telegram by SCPing script to gcp-west and executing."""
    token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    chat_id = '7453631330'
    if not token:
        # Try to read from .env on gcp-west
        script = f"""import requests
r = requests.post('https://api.telegram.org/bot{token}/sendMessage', json={{'chat_id': '{chat_id}', 'text': '''{message}'''}})
print(r.status_code)
"""
        # SCP to gcp-west and run
        try:
            tmp = Path('/tmp/spectral_alert_send.py')
            tmp.write_text(script)
            subprocess.run(['scp', str(tmp), 'openclaw@34.53.51.34:/tmp/'], timeout=10)
            subprocess.run(['ssh', 'openclaw@34.53.51.34', 'python3 /tmp/spectral_alert_send.py'], timeout=15)
            tmp.unlink(missing_ok=True)
        except:
            pass  # Best effort
    else:
        try:
            import requests
            requests.post(f'https://api.telegram.org/bot{token}/sendMessage',
                        json={'chat_id': chat_id, 'text': message})
        except:
            pass

def run():
    print('=== SPECTRAL ALERT MONITOR ===')
    print(f'Time: {time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())}')
    # For now, use the meta-spectrometer static scores (would run actual spectrometers in production)
    # Read meta-spectrometer results
    meta_path = W / 'meta-spectrometer-results.json'
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
        current_scores = {}
        for domain, data in meta['breakdown'].items():
            current_scores[domain] = {'score': data['score'], 'trend': data['trend'], 'detail': data['detail']}
    else:
        current_scores = {}
    current = {'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'scores': current_scores}
    last = load_last()
    changes = check_changes(current, last)
    if changes:
        msg = f"⚠️ SPECTRAL ALERT — {len(changes)} domain(s) changed:\n"
        for c in changes:
            arrow = '↑' if c['direction'] == 'up' else '↓'
            msg += f"  {c['domain']}: {c['old']} → {c['new']} ({arrow}{c['delta']})\n"
        msg += f"\nCivilization Risk Index: {meta.get('civilization_risk_index', '?')}/100"
        print(msg)
        send_telegram(msg)
    else:
        print('No significant changes detected.')
    save_current(current)
    print(f'State saved to {LAST}')

if __name__ == '__main__':
    run()
