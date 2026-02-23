#!/usr/bin/env python3
"""
EVEZ-OS R124 CANONICAL
N=76=2²×19  tau=3  omega_k=2
poly_c=0.435316  NO FIRE
delta_V=0.114825  V_global=3.405758  CEILING×42
truth_plane=CANONICAL
"""
import math

# --- Factorization ---
N = 76          # 2² × 19
tau = 3         # smallest prime factor
omega_k = 2    # distinct prime factors

# --- Core formula ---
topo_bonus = 1 + 0.15 * omega_k          # 1.30
poly_c = topo_bonus * (1 + math.log(tau)) / math.log2(N + 1)

# --- Fire verdict ---
FIRE_THRESHOLD = 0.5
fire = poly_c >= FIRE_THRESHOLD

# --- Volume delta ---
gamma = 0.08
ADM = 1.0
delta_V = gamma * ADM * (1 + poly_c)
V_prev = 3.290933
V_global = V_prev + delta_V

# --- Ceiling ---
ceiling_tick = 42

# --- State output ---
result = {
    "round": 124,
    "N": N,
    "N_str": "76=2\u00b2\u00d719",
    "tau": tau,
    "omega_k": omega_k,
    "topo_bonus": round(topo_bonus, 6),
    "poly_c": round(poly_c, 6),
    "fire_ignited": fire,
    "fire_name": "NO FIRE",
    "delta_V": round(delta_V, 6),
    "V_global_prev": V_prev,
    "V_global": round(V_global, 6),
    "ceiling_tick": ceiling_tick,
    "truth_plane": "CANONICAL",
    "palette": "OBSIDIAN"
}

if __name__ == "__main__":
    import json
    print(json.dumps(result, indent=2))
    assert not fire, f"Unexpected fire: poly_c={poly_c:.6f}"
    assert abs(round(V_global, 6) - 3.405758) < 1e-4, f"V_global mismatch: {V_global}"
    print("exit 0 — R124 CANONICAL verified")
