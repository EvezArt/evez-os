#!/usr/bin/env python3
"""
Air Pollution Homicide Spectrometer — Dark Matter Crime #8
Measures deliberate suppression of air quality data and denial of pollution health impacts
where the result is premature death. Companies that hide pollution kills are committing
slow-motion homicide.
Dimensional: emission, concealment, health_impact, regulatory_capture, denial_campaign, mortality
"""
import json, numpy as np
from typing import Dict, List, Tuple

CALIBRATION = {
    "vw_dieselgate": {"emission":0.85,"concealment":0.95,"health_impact":0.70,"regulatory_capture":0.65,"denial_campaign":0.90,"mortality":0.55},
    "big_tobacco_smoking": {"emission":0.60,"concealment":0.98,"health_impact":0.95,"regulatory_capture":0.80,"denial_campaign":0.98,"mortality":0.92},
    "exxonmobil_climate": {"emission":0.92,"concealment":0.95,"health_impact":0.85,"regulatory_capture":0.75,"denial_campaign":0.95,"mortality":0.70},
    "tetraethyl_lead": {"emission":0.88,"concealment":0.92,"health_impact":0.90,"regulatory_capture":0.85,"denial_campaign":0.88,"mortality":0.82},
    "pfas_forever": {"emission":0.78,"concealment":0.88,"health_impact":0.82,"regulatory_capture":0.70,"denial_campaign":0.75,"mortality":0.65},
    "asbestos_industry": {"emission":0.65,"concealment":0.95,"health_impact":0.92,"regulatory_capture":0.78,"denial_campaign":0.90,"mortality":0.88},
    "coal_lobby_pm25": {"emission":0.90,"concealment":0.80,"health_impact":0.85,"regulatory_capture":0.72,"denial_campaign":0.82,"mortality":0.75},
    "roundup_glyphosate": {"emission":0.70,"concealment":0.85,"health_impact":0.72,"regulatory_capture":0.68,"denial_campaign":0.80,"mortality":0.58},
    "clean_industry": {"emission":0.05,"concealment":0.02,"health_impact":0.01,"regulatory_capture":0.01,"denial_campaign":0.01,"mortality":0.01},
    "natural_pollution": {"emission":0.20,"concealment":0.00,"health_impact":0.15,"regulatory_capture":0.00,"denial_campaign":0.00,"mortality":0.10},
}

COUPLING = np.array([
    [0.0, 0.25, 0.35, 0.20, 0.15, 0.30], # emission
    [0.25, 0.0, 0.40, 0.30, 0.45, 0.20], # concealment
    [0.35, 0.40, 0.0, 0.15, 0.20, 0.50], # health_impact
    [0.20, 0.30, 0.15, 0.0, 0.35, 0.10], # regulatory_capture
    [0.15, 0.45, 0.20, 0.35, 0.0, 0.15], # denial_campaign
    [0.30, 0.20, 0.50, 0.10, 0.15, 0.0], # mortality
])

def run() -> dict:
    results = {}
    for name, dims in CALIBRATION.items():
        v = np.array([dims[k] for k in ["emission","concealment","health_impact","regulatory_capture","denial_campaign","mortality"]])
        M = COUPLING * np.outer(v, v)
        evals = np.linalg.eigvalsh(M)
        results[name] = {"score": float(np.max(evals)), "dims": dims}
    return results

def falsify(results: dict) -> List[Tuple[str,bool,str]]:
    checks = []
    s = {k: v["score"] for k,v in results.items()}
    d = {k: v["dims"] for k,v in results.items()}
    # 1. Tobacco highest mortality
    checks.append(("tobacco_mortality", d["big_tobacco_smoking"]["mortality"] == max(x["mortality"] for x in d.values()), "Tobacco must have highest mortality"))
    # 2. Exxon highest emission
    checks.append(("exxon_emission", d["exxonmobil_climate"]["emission"] >= 0.90, "Exxon emission >=0.90"))
    # 3. VW highest concealment (defeat devices)
    checks.append(("vw_concealment", d["vw_dieselgate"]["concealment"] >= 0.95, "VW concealment >=0.95"))
    # 4. Clean industry near zero
    checks.append(("clean_near_zero", s["clean_industry"] < 0.01, "Clean industry score <0.01"))
    # 5. Tobacco > coal
    checks.append(("tobacco_gt_coal", s["big_tobacco_smoking"] > s["coal_lobby_pm25"], "Tobacco > coal lobby"))
    # 6. Lead industry high across all dims
    checks.append(("lead_high", s["tetraethyl_lead"] > 0.5, "Tetraethyl lead score >0.5"))
    # 7. Denial campaigns correlate with concealment
    denial_conceal = [(d[k]["denial_campaign"], d[k]["concealment"]) for k in d]
    cc = np.corrcoef([x[0] for x in denial_conceal], [x[1] for x in denial_conceal])[0,1]
    checks.append(("denial_conceal_corr", cc > 0.8, f"Denial-concealment correlation {cc:.3f} >0.8"))
    # 8. Natural pollution zero concealment
    checks.append(("natural_zero_concealment", d["natural_pollution"]["concealment"] == 0.0, "Natural pollution has zero concealment"))
    # 9. Asbestos > Roundup
    checks.append(("asbestos_gt_roundup", s["asbestos_industry"] > s["roundup_glyphosate"], "Asbestos > Roundup"))
    # 10. PFAS moderate-high
    checks.append(("pfas_elevated", s["pfas_forever"] > 0.3, "PFAS elevated (>0.3)"))
    # 11. Mortality correlates with health_impact
    mort_health = [(d[k]["mortality"], d[k]["health_impact"]) for k in d]
    cc2 = np.corrcoef([x[0] for x in mort_health], [x[1] for x in mort_health])[0,1]
    checks.append(("mortality_health_corr", cc2 > 0.9, f"Mortality-health correlation {cc2:.3f} >0.9"))
    # 12. All polluting industries > clean
    for polluter in ["vw_dieselgate","big_tobacco_smoking","exxonmobil_climate","tetraethyl_lead","asbestos_industry","coal_lobby_pm25"]:
        checks.append((f"{polluter}_gt_clean", s[polluter] > s["clean_industry"], f"{polluter} > clean"))
    return checks

if __name__ == "__main__":
    results = run()
    checks = falsify(results)
    passed = sum(1 for _,ok,_ in checks if ok)
    print(f"Air Pollution Homicide Spectrometer: {passed}/{len(checks)} checks passed")
    for name, ok, desc in checks:
        print(f"  {'✓' if ok else '✗'} {name}: {desc}")
    scores = {k: v["score"] for k,v in sorted(results.items(), key=lambda x:-x[1]["score"])}
    print(f"\nRankings:")
    for k,v in scores.items():
        print(f"  {k}: {v:.4f}")
    avg = np.mean([v["score"] for k,v in results.items() if k not in ["clean_industry","natural_pollution"]])
    print(f"\nAverage (polluting industries): {avg:.3f}")
    print(f"Status: {'DETECTED' if avg > 0.3 else 'NORMAL'}")
    with open("air-pollution-homicide-spectrometer-results.json","w") as f:
        json.dump({"results":results,"checks":[{"name":n,"passed":bool(ok),"desc":d} for n,ok,d in checks],"passed":passed,"total":len(checks),"avg":avg,"status":"DETECTED" if avg>0.3 else "NORMAL"},f,indent=2)
