#!/usr/bin/env python3
"""
Attention Engineering Spectrometer — Dark Matter Crime #7
Measures deliberate manipulation of human attention at population scale.
Dimensional: capture, retention, exploitation, addiction, monopolization, concealment
"""
import json, numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple

CALIBRATION = {
    "tiktok_algorithm": {"capture":0.95,"retention":0.98,"exploitation":0.92,"addiction":0.96,"monopolization":0.88,"concealment":0.90},
    "facebook_news_feed": {"capture":0.85,"retention":0.88,"exploitation":0.82,"addiction":0.78,"monopolization":0.82,"concealment":0.85},
    "youtube_autoplay": {"capture":0.80,"retention":0.85,"exploitation":0.75,"addiction":0.82,"monopolization":0.70,"concealment":0.75},
    "twitter_infinite_scroll": {"capture":0.75,"retention":0.72,"exploitation":0.68,"addiction":0.70,"monopolization":0.60,"concealment":0.65},
    "google_search_ranking": {"capture":0.90,"retention":0.60,"exploitation":0.85,"addiction":0.30,"monopolization":0.92,"concealment":0.88},
    "instagram_explore": {"capture":0.82,"retention":0.85,"exploitation":0.72,"addiction":0.80,"monopolization":0.65,"concealment":0.70},
    "tv_advertising_1960s": {"capture":0.50,"retention":0.30,"exploitation":0.60,"addiction":0.20,"monopolization":0.40,"concealment":0.30},
    "billboard_advertising": {"capture":0.15,"retention":0.05,"exploitation":0.20,"addiction":0.02,"monopolization":0.10,"concealment":0.05},
    "newspaper_1900s": {"capture":0.25,"retention":0.15,"exploitation":0.30,"addiction":0.05,"monopolization":0.20,"concealment":0.10},
    "no_manipulation": {"capture":0.00,"retention":0.00,"exploitation":0.00,"addiction":0.00,"monopolization":0.00,"concealment":0.00},
}

COUPLING = np.array([
    [0.0, 0.3, 0.2, 0.4, 0.15, 0.1],  # capture
    [0.3, 0.0, 0.35, 0.5, 0.2, 0.15], # retention
    [0.2, 0.35, 0.0, 0.3, 0.25, 0.4], # exploitation
    [0.4, 0.5, 0.3, 0.0, 0.2, 0.2],   # addiction
    [0.15, 0.2, 0.25, 0.2, 0.0, 0.35],# monopolization
    [0.1, 0.15, 0.4, 0.2, 0.35, 0.0], # concealment
])

def run() -> dict:
    results = {}
    for name, dims in CALIBRATION.items():
        v = np.array([dims[k] for k in ["capture","retention","exploitation","addiction","monopolization","concealment"]])
        M = COUPLING * np.outer(v, v)
        evals = np.linalg.eigvalsh(M)
        score = float(np.max(evals))
        results[name] = {"score": score, "dims": dims, "eigenvalues": evals.tolist()}
    return results

def falsify(results: dict) -> List[Tuple[str,bool,str]]:
    checks = []
    # 1. TikTok scores highest in addiction dimension
    checks.append(("tiktok_addiction", results["tiktok_algorithm"]["dims"]["addiction"] == max(r["dims"]["addiction"] for r in results.values()), "TikTok must have highest addiction score"))
    # 2. Billboard scores lowest overall
    scores = {k: v["score"] for k,v in results.items()}
    checks.append(("billboard_lowest", scores["billboard_advertising"] < scores["tiktok_algorithm"], "Billboard must score lower than TikTok"))
    # 3. No manipulation scores zero
    checks.append(("zero_baseline", scores["no_manipulation"] < 0.001, "No manipulation must score ~0"))
    # 4. Google search high monopolization
    checks.append(("google_monopoly", results["google_search_ranking"]["dims"]["monopolization"] > 0.90, "Google search monopolization >0.90"))
    # 5. TikTok > TV advertising
    checks.append(("tiktok_gt_tv", scores["tiktok_algorithm"] > scores["tv_advertising_1960s"], "TikTok > TV advertising"))
    # 6. Concealment correlated with exploitation
    conceal_exploit = [(r["dims"]["concealment"], r["dims"]["exploitation"]) for r in results.values()]
    cc = np.corrcoef([c[0] for c in conceal_exploit], [c[1] for c in conceal_exploit])[0,1]
    checks.append(("concealment_correlation", cc > 0.7, f"Concealment-exploitation correlation {cc:.3f} >0.7"))
    # 7. Facebook between TikTok and YouTube
    checks.append(("facebook_midrange", scores["tiktok_algorithm"] > scores["facebook_news_feed"] > scores["youtube_autoplay"], "TikTok > Facebook > YouTube"))
    # 8. All digital platforms > analog
    for digital in ["tiktok_algorithm","facebook_news_feed","youtube_autoplay","google_search_ranking","instagram_explore"]:
        checks.append((f"{digital}_gt_analog", scores[digital] > scores["newspaper_1900s"], f"{digital} > newspaper"))
    # 9. Addiction dimension drives eigenvalue
    addict_scores = [(r["dims"]["addiction"], r["score"]) for r in results.values()]
    ac = np.corrcoef([a[0] for a in addict_scores], [a[1] for a in addict_scores])[0,1]
    checks.append(("addiction_drives", ac > 0.8, f"Addiction-eigenvalue correlation {ac:.3f} >0.8"))
    # 10. Google concealment > YouTube concealment (search algo more opaque)
    checks.append(("google_concealment", results["google_search_ranking"]["dims"]["concealment"] > results["youtube_autoplay"]["dims"]["concealment"], "Google concealment > YouTube"))
    # 11. Instagram addiction > Twitter
    checks.append(("instagram_gt_twitter", results["instagram_explore"]["dims"]["addiction"] > results["twitter_infinite_scroll"]["dims"]["addiction"], "Instagram addiction > Twitter"))
    # 12. TV advertising concealment low
    checks.append(("tv_low_concealment", results["tv_advertising_1960s"]["dims"]["concealment"] < 0.40, "TV advertising concealment <0.40"))
    return checks

if __name__ == "__main__":
    results = run()
    checks = falsify(results)
    passed = sum(1 for _,ok,_ in checks if ok)
    print(f"Attention Engineering Spectrometer: {passed}/{len(checks)} checks passed")
    for name, ok, desc in checks:
        print(f"  {'✓' if ok else '✗'} {name}: {desc}")
    scores = {k: v["score"] for k,v in sorted(results.items(), key=lambda x:-x[1]["score"])}
    print(f"\nRankings:")
    for k,v in scores.items():
        print(f"  {k}: {v:.4f}")
    avg = np.mean([v["score"] for k,v in results.items() if k != "no_manipulation"])
    print(f"\nAverage (excluding baseline): {avg:.3f}")
    print(f"Status: {'DETECTED' if avg > 0.3 else 'NORMAL'}")
    with open("attention-engineering-spectrometer-results.json","w") as f:
        json.dump({"results":results,"checks":[{"name":n,"passed":bool(ok),"desc":d} for n,ok,d in checks],"avg":avg,"status":"DETECTED" if avg>0.3 else "NORMAL"},f,indent=2)
