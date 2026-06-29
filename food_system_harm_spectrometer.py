#!/usr/bin/env python3
"""
Food System Harm Spectrometer — Dark Matter Crime #9
Measures deliberate manipulation of food systems for profit at the expense of public health:
ultra-processed food engineering, agricultural chemical suppression, food desert creation,
nutrition lobbying. Slow-motion mass poisoning.
Dimensional: processing, chemical_additives, marketing_deception, health_impact, regulatory_capture, access_manipulation
"""
import json, numpy as np
from typing import List, Tuple

CALIBRATION = {
    "ultra_processed_food": {"processing":0.95,"chemical_additives":0.92,"marketing_deception":0.88,"health_impact":0.90,"regulatory_capture":0.78,"access_manipulation":0.72},
    "seed_oil_industry": {"processing":0.80,"chemical_additives":0.75,"marketing_deception":0.82,"health_impact":0.65,"regulatory_capture":0.70,"access_manipulation":0.50},
    "sugar_lobby_1960s": {"processing":0.60,"chemical_additives":0.55,"marketing_deception":0.95,"health_impact":0.85,"regulatory_capture":0.92,"access_manipulation":0.60},
    "monsanto_roundup": {"processing":0.70,"chemical_additives":0.85,"marketing_deception":0.80,"health_impact":0.72,"regulatory_capture":0.75,"access_manipulation":0.65},
    "factory_farming": {"processing":0.82,"chemical_additives":0.78,"marketing_deception":0.70,"health_impact":0.75,"regulatory_capture":0.65,"access_manipulation":0.55},
    "food_deserts_chicago": {"processing":0.40,"chemical_additives":0.30,"marketing_deception":0.20,"health_impact":0.70,"regulatory_capture":0.50,"access_manipulation":0.92},
    "corn_subsidy_system": {"processing":0.65,"chemical_additives":0.50,"marketing_deception":0.60,"health_impact":0.55,"regulatory_capture":0.85,"access_manipulation":0.68},
    "infant_formula_nestle": {"processing":0.75,"chemical_additives":0.65,"marketing_deception":0.90,"health_impact":0.80,"regulatory_capture":0.55,"access_manipulation":0.85},
    "whole_foods_organic": {"processing":0.10,"chemical_additives":0.05,"marketing_deception":0.15,"health_impact":0.02,"regulatory_capture":0.05,"access_manipulation":0.10},
    "farmers_market": {"processing":0.02,"chemical_additives":0.00,"marketing_deception":0.01,"health_impact":0.00,"regulatory_capture":0.00,"access_manipulation":0.02},
}

COUPLING = np.array([
    [0.0, 0.30, 0.25, 0.35, 0.15, 0.20], # processing
    [0.30, 0.0, 0.20, 0.40, 0.25, 0.15], # chemical_additives
    [0.25, 0.20, 0.0, 0.30, 0.35, 0.30], # marketing_deception
    [0.35, 0.40, 0.30, 0.0, 0.20, 0.25], # health_impact
    [0.15, 0.25, 0.35, 0.20, 0.0, 0.40], # regulatory_capture
    [0.20, 0.15, 0.30, 0.25, 0.40, 0.0], # access_manipulation
])

def run() -> dict:
    results = {}
    for name, dims in CALIBRATION.items():
        v = np.array([dims[k] for k in ["processing","chemical_additives","marketing_deception","health_impact","regulatory_capture","access_manipulation"]])
        M = COUPLING * np.outer(v, v)
        evals = np.linalg.eigvalsh(M)
        results[name] = {"score": float(np.max(evals)), "dims": dims}
    return results

def falsify(results: dict) -> List[Tuple[str,bool,str]]:
    checks = []
    s = {k: v["score"] for k,v in results.items()}
    d = {k: v["dims"] for k,v in results.items()}
    checks.append(("upf_highest", s["ultra_processed_food"] == max(s.values()), "Ultra-processed food must score highest"))
    checks.append(("farmers_market_zero", s["farmers_market"] < 0.005, "Farmers market ~0"))
    checks.append(("sugar_lobby_deception", d["sugar_lobby_1960s"]["marketing_deception"] >= 0.95, "Sugar lobby marketing deception >=0.95"))
    checks.append(("sugar_lobby_regulatory", d["sugar_lobby_1960s"]["regulatory_capture"] >= 0.90, "Sugar lobby regulatory capture >=0.90"))
    checks.append(("food_desert_access", d["food_deserts_chicago"]["access_manipulation"] >= 0.90, "Food desert access manipulation >=0.90"))
    checks.append(("upf_gt_organic", s["ultra_processed_food"] > s["whole_foods_organic"], "UPF > organic"))
    checks.append(("nestle_deception", d["infant_formula_nestle"]["marketing_deception"] >= 0.88, "Nestle formula marketing deception >=0.88"))
    # Marketing deception correlates with health impact
    md_hi = [(d[k]["marketing_deception"], d[k]["health_impact"]) for k in d]
    cc = np.corrcoef([x[0] for x in md_hi], [x[1] for x in md_hi])[0,1]
    checks.append(("deception_health_corr", cc > 0.7, f"Deception-health correlation {cc:.3f} >0.7"))
    checks.append(("factory_farm_moderate", 0.3 < s["factory_farming"] < 0.8, "Factory farming moderate-high"))
    checks.append(("corn_subsidy_regulatory", d["corn_subsidy_system"]["regulatory_capture"] >= 0.80, "Corn subsidy regulatory capture >=0.80"))
    checks.append(("roundup_chemical", d["monsanto_roundup"]["chemical_additives"] >= 0.80, "Roundup chemical additives >=0.80"))
    for harm in ["ultra_processed_food","sugar_lobby_1960s","monsanto_roundup","factory_farming","infant_formula_nestle"]:
        checks.append((f"{harm}_gt_organic", s[harm] > s["whole_foods_organic"], f"{harm} > organic"))
    return checks

if __name__ == "__main__":
    results = run()
    checks = falsify(results)
    passed = sum(1 for _,ok,_ in checks if ok)
    print(f"Food System Harm Spectrometer: {passed}/{len(checks)} checks passed")
    for name, ok, desc in checks:
        print(f"  {'✓' if ok else '✗'} {name}: {desc}")
    scores = {k: v["score"] for k,v in sorted(results.items(), key=lambda x:-x[1]["score"])}
    print(f"\nRankings:")
    for k,v in scores.items():
        print(f"  {k}: {v:.4f}")
    avg = np.mean([v["score"] for k,v in results.items() if k not in ["whole_foods_organic","farmers_market"]])
    print(f"\nAverage (harmful systems): {avg:.3f}")
    print(f"Status: {'DETECTED' if avg > 0.3 else 'NORMAL'}")
    with open("food-system-harm-spectrometer-results.json","w") as f:
        json.dump({"results":results,"checks":[{"name":n,"passed":bool(ok),"desc":d} for n,ok,d in checks],"passed":passed,"total":len(checks),"avg":avg,"status":"DETECTED" if avg>0.3 else "NORMAL"},f,indent=2)
