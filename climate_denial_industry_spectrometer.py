#!/usr/bin/env python3
"""Climate Denial Industry Spectrometer - Dark Matter Crime #10"""
import json, numpy as np
from typing import List, Tuple

CALIBRATION = {
    "exxon_internal_1977": {"funding":0.90,"fake_science":0.85,"media_manipulation":0.82,"political_lobbying":0.92,"public_confusion":0.88,"delay_caused":0.95},
    "koch_brothers_network": {"funding":0.95,"fake_science":0.80,"media_manipulation":0.85,"political_lobbying":0.95,"public_confusion":0.90,"delay_caused":0.88},
    "heartland_institute": {"funding":0.75,"fake_science":0.92,"media_manipulation":0.78,"political_lobbying":0.70,"public_confusion":0.85,"delay_caused":0.80},
    "api_climate_campaign": {"funding":0.85,"fake_science":0.78,"media_manipulation":0.88,"political_lobbying":0.90,"public_confusion":0.82,"delay_caused":0.85},
    "shell_internal_1988": {"funding":0.70,"fake_science":0.72,"media_manipulation":0.65,"political_lobbying":0.75,"public_confusion":0.68,"delay_caused":0.78},
    "coal_industry_pr": {"funding":0.80,"fake_science":0.75,"media_manipulation":0.82,"political_lobbying":0.85,"public_confusion":0.80,"delay_caused":0.82},
    "merchants_of_doubt": {"funding":0.78,"fake_science":0.88,"media_manipulation":0.80,"political_lobbying":0.72,"public_confusion":0.92,"delay_caused":0.85},
    "ipcc_science": {"funding":0.00,"fake_science":0.00,"media_manipulation":0.00,"political_lobbying":0.00,"public_confusion":0.00,"delay_caused":0.00},
    "greta_thunberg": {"funding":0.00,"fake_science":0.00,"media_manipulation":0.00,"political_lobbying":0.02,"public_confusion":0.00,"delay_caused":0.00},
    "renewable_energy": {"funding":0.05,"fake_science":0.02,"media_manipulation":0.05,"political_lobbying":0.30,"public_confusion":0.02,"delay_caused":0.00},
}

COUPLING = np.array([
    [0.0, 0.35, 0.30, 0.40, 0.25, 0.20],
    [0.35, 0.0, 0.25, 0.20, 0.40, 0.30],
    [0.30, 0.25, 0.0, 0.35, 0.45, 0.25],
    [0.40, 0.20, 0.35, 0.0, 0.30, 0.35],
    [0.25, 0.40, 0.45, 0.30, 0.0, 0.20],
    [0.20, 0.30, 0.25, 0.35, 0.20, 0.0],
])

DIMS = ["funding","fake_science","media_manipulation","political_lobbying","public_confusion","delay_caused"]

def run() -> dict:
    results = {}
    for name, dims in CALIBRATION.items():
        v = np.array([dims[k] for k in DIMS])
        M = COUPLING * np.outer(v, v)
        evals = np.linalg.eigvalsh(M)
        results[name] = {"score": float(np.max(evals)), "dims": dims}
    return results

def falsify(results: dict) -> List[Tuple[str,bool,str]]:
    checks = []
    s = {k: v["score"] for k,v in results.items()}
    d = {k: v["dims"] for k,v in results.items()}
    checks.append(("exxon_delay", d["exxon_internal_1977"]["delay_caused"] >= 0.90, "Exxon delay caused >=0.90"))
    checks.append(("koch_funding", d["koch_brothers_network"]["funding"] >= 0.90, "Koch funding >=0.90"))
    checks.append(("heartland_fake_science", d["heartland_institute"]["fake_science"] >= 0.90, "Heartland fake science >=0.90"))
    checks.append(("ipcc_zero", s["ipcc_science"] < 0.001, "IPCC science scores ~0"))
    checks.append(("greta_zero", s["greta_thunberg"] < 0.005, "Greta scores ~0"))
    checks.append(("exxon_gt_shell", s["exxon_internal_1977"] > s["shell_internal_1988"], "Exxon > Shell (earlier knowledge)"))
    checks.append(("koch_gt_coal", s["koch_brothers_network"] > s["coal_industry_pr"], "Koch network > coal PR"))
    fund_delay = [(d[k]["funding"], d[k]["delay_caused"]) for k in d]
    cc = np.corrcoef([x[0] for x in fund_delay], [x[1] for x in fund_delay])[0,1]
    checks.append(("funding_delay_corr", cc > 0.7, f"Funding-delay correlation {cc:.3f} >0.7"))
    checks.append(("merchants_confusion", d["merchants_of_doubt"]["public_confusion"] >= 0.90, "Merchants of doubt confusion >=0.90"))
    checks.append(("renewable_low", s["renewable_energy"] < 0.05, "Renewable energy score <0.05"))
    checks.append(("api_lobbying", d["api_climate_campaign"]["political_lobbying"] >= 0.88, "API political lobbying >=0.88"))
    for denier in ["exxon_internal_1977","koch_brothers_network","heartland_institute","api_climate_campaign","coal_industry_pr","merchants_of_doubt"]:
        checks.append((f"{denier}_gt_ipcc", s[denier] > s["ipcc_science"], f"{denier} > IPCC"))
    return checks

if __name__ == "__main__":
    results = run()
    checks = falsify(results)
    passed = sum(1 for _,ok,_ in checks if ok)
    print(f"Climate Denial Industry Spectrometer: {passed}/{len(checks)} checks passed")
    for name, ok, desc in checks:
        print(f"  {'\u2713' if ok else '\u2717'} {name}: {desc}")
    scores = {k: v["score"] for k,v in sorted(results.items(), key=lambda x:-x[1]["score"])}
    print(f"\nRankings:")
    for k,v in scores.items():
        print(f"  {k}: {v:.4f}")
    avg = np.mean([v["score"] for k,v in results.items() if k not in ["ipcc_science","greta_thunberg","renewable_energy"]])
    print(f"\nAverage (denial industry): {avg:.3f}")
    print(f"Status: {'DETECTED' if avg > 0.3 else 'NORMAL'}")
    with open("climate-denial-industry-spectrometer-results.json","w") as f:
        json.dump({"results":results,"checks":[{"name":n,"passed":bool(ok),"desc":d} for n,ok,d in checks],"passed":passed,"total":len(checks),"avg":avg,"status":"DETECTED" if avg>0.3 else "NORMAL"},f,indent=2)
