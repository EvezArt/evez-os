#!/usr/bin/env python3
"""Special-relativistic spacetime interval calculator in flat Minkowski spacetime.

This is a kinematic baseline for classifying separations, not a warp-bubble
solver and not evidence of communication or propulsion faster than light.
"""
from __future__ import annotations
import argparse
import json
import math
import sys
from typing import Any

SPEED_OF_LIGHT_M_S = 299_792_458.0


def classify_interval(delta_t_seconds: float, delta_x_meters: float, *, relative_tolerance: float = 1e-12) -> dict[str, Any]:
    if any(not math.isfinite(float(v)) for v in (delta_t_seconds, delta_x_meters, relative_tolerance)):
        raise ValueError("inputs must be finite numbers")
    if relative_tolerance < 0 or relative_tolerance >= 1:
        raise ValueError("relative_tolerance must be in [0, 1)")
    ct = SPEED_OF_LIGHT_M_S * delta_t_seconds
    ct_sq, dx_sq = ct * ct, delta_x_meters * delta_x_meters
    interval_sq = ct_sq - dx_sq
    tolerance = relative_tolerance * max(ct_sq, dx_sq, 1.0)
    if delta_t_seconds == 0 and delta_x_meters == 0:
        kind = "COINCIDENT_EVENT"
    elif interval_sq > tolerance:
        kind = "TIMELIKE"
    elif interval_sq < -tolerance:
        kind = "SPACELIKE"
    else:
        kind = "LIGHTLIKE_OR_WITHIN_TOLERANCE"
    beta = None if delta_t_seconds == 0 else delta_x_meters / (SPEED_OF_LIGHT_M_S * delta_t_seconds)
    return {
        "calculation": "flat_minkowski_1d_interval",
        "metric_convention": "(+,-)",
        "delta_t_seconds": delta_t_seconds,
        "delta_x_meters": delta_x_meters,
        "speed_of_light_m_s": SPEED_OF_LIGHT_M_S,
        "c_delta_t_meters": ct,
        "interval_squared_m2": interval_sq,
        "numerical_tolerance_m2": tolerance,
        "classification": kind,
        "coordinate_beta": beta,
        "coordinate_speed_exceeds_c": None if beta is None else abs(beta) > 1 + relative_tolerance,
        "scope": "Flat-spacetime kinematics only; no signal transfer or warp-bubble feasibility is inferred."
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--delta-t-seconds", type=float, required=True)
    parser.add_argument("--delta-x-meters", type=float, required=True)
    parser.add_argument("--relative-tolerance", type=float, default=1e-12)
    args = parser.parse_args(argv)
    try:
        result = classify_interval(args.delta_t_seconds, args.delta_x_meters, relative_tolerance=args.relative_tolerance)
    except ValueError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, separators=(",", ":")), file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
