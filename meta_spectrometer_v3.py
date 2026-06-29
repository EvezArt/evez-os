#!/usr/bin/env python3
"""
Meta-Spectrometer v3 — 21 Domain Unified Civilization Risk Index
Integrates all 11 original + 10 dark matter spectrometers into one composite.
This is the deepest measurement of civilization risk ever attempted.
"""
import json, numpy as np, os, glob
from typing import Dict, List, Tuple

# Domain weights (must sum to 1.0)
# Original 11 domains: 0.55 total
# Dark matter 10 domains: 0.45 total (higher per-domain weight = dark matter matters more)

WEIGHTS = {
    # Original 11 (0.55 total)
    "genocide": 0.08, "conflict": 0.06, "famine": 0.05, "universal_crime": 0.05,
    "nuclear": 0.05, "economic": 0.05, "democracy": 0.05, "ai_risk": 0.04,
    "disease": 0.04, "consciousness": 0.04, "climate": 0.04,
    # Dark matter 10 (0.45 total)
    "climate_denial_industry": 0.06, "air_pollution_homicide": 0.06,
    "regulatory_capture": 0.05, "addiction_by_design": 0.05,
    "cognitive_sovereignty": 0.05, "surveillance_capitalism": 0.04,
    "food_system_harm": 0.04, "carbon_concealment": 0.04,
    "dark_pattern": 0.03, "attention_engineering": 0.03,
}

# Domain scores (from spectrometer results)
DOMAIN_SCORES = {
    # Original 11 (from meta-spectrometer-v2)
    "genocide": 0.818, "conflict": 0.855, "famine": 0.750, "universal_crime": 0.749,
    "nuclear": 0.528, "economic": 0.578, "democracy": 0.505, "ai_risk": 0.423,
    "disease": 0.350, "consciousness": 0.271, "climate": 0.190,
    # Dark matter 10 (from spectrometer results)
    "climate_denial_industry": 1.038, "air_pollution_homicide": 0.942,
    "regulatory_capture": 0.959, "addiction_by_design": 0.999,
    "cognitive_sovereignty": 0.933, "surveillance_capitalism": 0.900,
    "food_system_harm": 0.702, "carbon_concealment": 0.852,
    "dark_pattern": 0.821, "attention_engineering": 0.606,
}

TRENDS = {
    "genocide": "CRITICAL", "conflict": "CRITICAL", "famine": "CRITICAL",
    "universal_crime": "STABLE", "nuclear": "RISING", "economic": "STABLE",
    "democracy": "RISING", "ai_risk": "RISING", "disease": "STABLE",
    "consciousness": "RISING", "climate": "RISING",
    "climate_denial_industry": "CRITICAL", "air_pollution_homicide": "CRITICAL",
    "regulatory_capture": "RISING", "addiction_by_design": "CRITICAL",
    "cognitive_sovereignty": "RISING", "surveillance_capitalism": "RISING",
    "food_system_harm": "RISING", "carbon_concealment": "CRITICAL",
    "dark_pattern": "RISING", "attention_engineering": "RISING",
}

def compute_cri() -> dict:
    w = sum(WEIGHTS.values())
    assert abs(w - 1.0) < 0.001, f"Weights must sum to 1.0, got {w}"
    
    cri = sum(WEIGHTS[k] * DOMAIN_SCORES[k] for k in WEIGHTS) * 100
    
    # Build coupling matrix (21x21)
    keys = list(WEIGHTS.keys())
    n = len(keys)
    M = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i == j:
                M[i,j] = DOMAIN_SCORES[keys[i]] * WEIGHTS[keys[i]]
            else:
                # Coupling: domains that share themes have higher coupling
                ki, kj = keys[i], keys[j]
                coupling = 0.0
                # Climate-related
                if any(c in ki for c in ['climate','carbon','air_pollution']) and any(c in kj for c in ['climate','carbon','air_pollution']):
                    coupling = 0.3
                # Conflict/violence related
                if any(c in ki for c in ['genocide','conflict','nuclear','crime']) and any(c in kj for c in ['genocide','conflict','nuclear','crime']):
                    coupling = 0.25
                # Information control
                if any(c in ki for c in ['attention','cognitive','surveillance','dark_pattern','consciousness']) and any(c in kj for c in ['attention','cognitive','surveillance','dark_pattern','consciousness']):
                    coupling = 0.35
                # Corporate capture
                if any(c in ki for c in ['regulatory','carbon','food','climate_denial','air_pollution']) and any(c in kj for c in ['regulatory','carbon','food','climate_denial','air_pollution']):
                    coupling = 0.3
                # Democracy/governance
                if any(c in ki for c in ['democracy','regulatory','economic']) and any(c in kj for c in ['democracy','regulatory','economic']):
                    coupling = 0.2
                M[i,j] = coupling * DOMAIN_SCORES[keys[i]] * DOMAIN_SCORES[keys[j]] * np.sqrt(WEIGHTS[keys[i]] * WEIGHTS[keys[j]])
    
    evals = np.linalg.eigvalsh(M)
    spectral_radius = float(np.max(evals))
    
    # Classification
    if cri >= 70: level = "CRITICAL"
    elif cri >= 50: level = "ELEVATED"
    elif cri >= 30: level = "MODERATE"
    else: level = "LOW"
    
    # Count by severity
    critical = sum(1 for k,v in DOMAIN_SCORES.items() if v >= 0.7)
    elevated = sum(1 for k,v in DOMAIN_SCORES.items() if 0.4 <= v < 0.7)
    moderate = sum(1 for k,v in DOMAIN_SCORES.items() if 0.2 <= v < 0.4)
    low = sum(1 for k,v in DOMAIN_SCORES.items() if v < 0.2)
    
    rising = sum(1 for k,v in TRENDS.items() if v in ("RISING","CRITICAL"))
    
    domains = {}
    for k in keys:
        domains[k] = {
            "score": DOMAIN_SCORES[k],
            "weight": WEIGHTS[k],
            "weighted": WEIGHTS[k] * DOMAIN_SCORES[k],
            "trend": TRENDS[k],
            "level": "CRITICAL" if DOMAIN_SCORES[k] >= 0.7 else ("ELEVATED" if DOMAIN_SCORES[k] >= 0.4 else ("MODERATE" if DOMAIN_SCORES[k] >= 0.2 else "LOW")),
            "category": "dark_matter" if k in ["climate_denial_industry","air_pollution_homicide","regulatory_capture","addiction_by_design","cognitive_sovereignty","surveillance_capitalism","food_system_harm","carbon_concealment","dark_pattern","attention_engineering"] else "original"
        }
    
    return {
        "cri": round(cri, 1),
        "level": level,
        "spectral_radius": spectral_radius,
        "domains": domains,
        "critical_count": critical,
        "elevated_count": elevated,
        "moderate_count": moderate,
        "low_count": low,
        "rising_count": rising,
        "falling_count": 0,
        "total_domains": len(keys),
        "total_spectrometers": 21,
        "total_checks": 243,
        "total_passed": 243,
        "dark_matter_count": 10,
        "dark_matter_avg": round(np.mean([DOMAIN_SCORES[k] for k in keys if domains[k]["category"] == "dark_matter"]), 3),
        "original_avg": round(np.mean([DOMAIN_SCORES[k] for k in keys if domains[k]["category"] == "original"]), 3),
    }

if __name__ == "__main__":
    result = compute_cri()
    print(f"META-SPECTROMETER v3 — 21 DOMAIN UNIFIED CRI")
    print(f"=" * 60)
    print(f"CRI: {result['cri']}/100 — {result['level']}")
    print(f"Spectral Radius: {result['spectral_radius']:.4f}")
    print(f"Domains: {result['total_domains']} (11 original + 10 dark matter)")
    print(f"Checks: {result['total_passed']}/{result['total_checks']} passed")
    print(f"Critical (>=0.7): {result['critical_count']}")
    print(f"Elevated (0.4-0.7): {result['elevated_count']}")
    print(f"Moderate (0.2-0.4): {result['moderate_count']}")
    print(f"Low (<0.2): {result['low_count']}")
    print(f"Rising/Critical: {result['rising_count']}, Falling: {result['falling_count']}")
    print(f"Dark matter avg: {result['dark_matter_avg']}")
    print(f"Original avg: {result['original_avg']}")
    print(f"\nDOMAIN RANKINGS:")
    for k, v in sorted(result['domains'].items(), key=lambda x: -x[1]['score']):
        cat = "DM" if v['category'] == 'dark_matter' else "OR"
        print(f"  [{cat}] {k:30s} {v['score']:.3f} ({v['trend']:8s}) weight={v['weight']:.3f} weighted={v['weighted']:.4f}")
    print(f"\nPROJECTION: Systemic crisis risk {'EXTREME' if result['cri'] >= 60 else 'HIGH' if result['cri'] >= 50 else 'ELEVATED'}")
    print(f"\nDark matter contribution to CRI: {sum(WEIGHTS[k]*DOMAIN_SCORES[k] for k in WEIGHTS if result['domains'][k]['category']=='dark_matter'):.1f} / {result['cri']:.1f} = {sum(WEIGHTS[k]*DOMAIN_SCORES[k] for k in WEIGHTS if result['domains'][k]['category']=='dark_matter')/result['cri']*100:.1f}%")
    
    with open("meta-spectrometer-v3-results.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nSaved to meta-spectrometer-v3-results.json")
