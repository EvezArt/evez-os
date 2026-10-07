#!/usr/bin/env python3
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))

from research.weather_flux_theory import (  # noqa: E402
    CouplingHypothesis,
    PhysicalState,
    graph_flux_from_potential,
    kuramoto_order_parameter,
    physical_to_chemical,
    weather_coupled_gain,
)

dry = physical_to_chemical(PhysicalState(25.0, 20.0, 1013.25))
humid = physical_to_chemical(PhysicalState(25.0, 80.0, 1013.25))

assert humid.water_activity > dry.water_activity
assert humid.vapor_pressure_deficit_hpa < dry.vapor_pressure_deficit_hpa
assert humid.relative_water_chemical_potential_j_mol > dry.relative_water_chemical_potential_j_mol

assert graph_flux_from_potential(
    {"a": 1.0, "b": 1.0},
    [("a", "b", 3.0)],
) == {"a": 0.0, "b": 0.0}

forward = graph_flux_from_potential({"a": 2.0, "b": 0.0}, [("a", "b", 3.0)])
reverse = graph_flux_from_potential({"a": 0.0, "b": 2.0}, [("a", "b", 3.0)])
assert forward["a"] == -6.0 and forward["b"] == 6.0
assert reverse["a"] == 6.0 and reverse["b"] == -6.0

theta = [0.0, 0.4, 1.0, 2.2]
shift = 1.7
assert math.isclose(
    kuramoto_order_parameter(theta),
    kuramoto_order_parameter([x + shift for x in theta]),
    rel_tol=1e-12,
    abs_tol=1e-12,
)

gain = weather_coupled_gain(
    0.8,
    CouplingHypothesis(k0=2.0, beta=0.25, z_mean=0.0, z_scale=1.0),
)
assert math.isclose(gain, 2.4)

try:
    physical_to_chemical(PhysicalState(25.0, 101.0, 1013.25))
except ValueError:
    pass
else:
    raise AssertionError("invalid RH accepted")

try:
    graph_flux_from_potential({"a": 1.0, "b": 0.0}, [("a", "b", -0.1)])
except ValueError:
    pass
else:
    raise AssertionError("negative conductance accepted")

print("formal weather/chemistry/network tests: PASS")
