#!/usr/bin/env python3
"""Explore an Alcubierre-style radial shape profile; not a field-equation solver.

Computes only the prescribed shape function and its radial derivative. It does
not compute the Einstein tensor, stress-energy tensor, energy-condition budget,
stability, causal operation, or engineering feasibility.
"""
from __future__ import annotations
import argparse
import json
import math
import sys
from typing import Any


def shape_value(radius_m: float, bubble_radius_m: float, wall_steepness_per_m: float) -> float:
    _validate(radius_m, bubble_radius_m, wall_steepness_per_m)
    sigma = wall_steepness_per_m
    radius = bubble_radius_m
    denominator = 2.0 * math.tanh(sigma * radius)
    return (math.tanh(sigma * (radius_m + radius)) - math.tanh(sigma * (radius_m - radius))) / denominator


def radial_derivative(radius_m: float, bubble_radius_m: float, wall_steepness_per_m: float) -> float:
    _validate(radius_m, bubble_radius_m, wall_steepness_per_m)
    sigma = wall_steepness_per_m
    radius = bubble_radius_m
    denominator = 2.0 * math.tanh(sigma * radius)
    left = 1.0 / math.cosh(sigma * (radius_m + radius)) ** 2 if abs(sigma * (radius_m + radius)) < 350 else 0.0
    right = 1.0 / math.cosh(sigma * (radius_m - radius)) ** 2 if abs(sigma * (radius_m - radius)) < 350 else 0.0
    return sigma * (left - right) / denominator


def _validate(radius_m: float, bubble_radius_m: float, wall_steepness_per_m: float) -> None:
    if not all(math.isfinite(float(v)) for v in (radius_m, bubble_radius_m, wall_steepness_per_m)):
        raise ValueError("all inputs must be finite")
    if radius_m < 0:
        raise ValueError("radius_m must be non-negative")
    if bubble_radius_m <= 0:
        raise ValueError("bubble_radius_m must be positive")
    if wall_steepness_per_m <= 0:
        raise ValueError("wall_steepness_per_m must be positive")
    if bubble_radius_m * wall_steepness_per_m > 1e6:
        raise ValueError("sigma*R exceeds stable input range")


def analyze_profile(bubble_radius_m: float, wall_steepness_per_m: float, samples: int = 401) -> dict[str, Any]:
    if not isinstance(samples, int) or isinstance(samples, bool) or samples < 11 or samples > 100_001:
        raise ValueError("samples must be an integer in [11, 100001]")
    _validate(0.0, bubble_radius_m, wall_steepness_per_m)
    # Dense positive-radius sampling. This is a profile diagnostic, not a spatial
    # discretization suitable for solving Einstein equations.
    r_max = bubble_radius_m + max(8.0 / wall_steepness_per_m, bubble_radius_m * 0.25)
    dr = r_max / (samples - 1)
    points = []
    for i in range(samples):
        r = i * dr
        f = shape_value(r, bubble_radius_m, wall_steepness_per_m)
        df = radial_derivative(r, bubble_radius_m, wall_steepness_per_m)
        points.append({"radius_m": r, "shape": f, "radial_derivative_per_m": df})
    integral = 0.0
    for i in range(1, len(points)):
        integral += 0.5 * (points[i - 1]["radial_derivative_per_m"] ** 2 +
                           points[i]["radial_derivative_per_m"] ** 2) * dr
    peak = max(points, key=lambda p: abs(p["radial_derivative_per_m"]))
    return {
        "model": "Alcubierre-style radial shape ansatz",
        "claim_classification": "speculative",
        "parameters": {"bubble_radius_m": bubble_radius_m, "wall_steepness_per_m": wall_steepness_per_m, "samples": samples},
        "diagnostics": {
            "center_shape": points[0]["shape"],
            "outer_shape": points[-1]["shape"],
            "peak_abs_radial_derivative_per_m": abs(peak["radial_derivative_per_m"]),
            "peak_gradient_radius_m": peak["radius_m"],
            "integral_radial_gradient_squared_dr_per_m": integral,
            "radial_sampling_step_m": dr,
        },
        "profile": points,
        "computed": ["shape function f(r)", "analytic radial derivative df/dr", "sampled radial profile diagnostics"],
        "not_computed": [
            "Einstein tensor or Einstein field equations",
            "stress-energy tensor or energy-condition violations",
            "negative-energy magnitude or sourcing requirements",
            "stability, horizons, causal operation, controllability, or engineering feasibility",
        ],
        "interpretation_limit": "A mathematically specified shape profile is not a spacetime solution, a physical bubble, or evidence of superluminal travel."
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--radius-m", type=float, required=True)
    parser.add_argument("--sigma-per-m", type=float, required=True, help="shape steepness, in inverse meters")
    parser.add_argument("--samples", type=int, default=401)
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    try:
        result = analyze_profile(args.radius_m, args.sigma_per_m, args.samples)
        output = json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as stream:
                stream.write(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
        print(output)
        return 0
    except (ValueError, OSError, OverflowError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, separators=(",", ":")), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
