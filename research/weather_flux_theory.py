#!/usr/bin/env python3
"""Formal weather/chemistry/network coupling model.

Three typed state spaces are kept separate:
P = physical thermodynamic state
C = chemical-potential proxy state
I = information/phase state

The P->C map is physically interpretable under stated equilibrium assumptions.
The C->I map is a hypothesis-bearing abstraction and is not evidence for a
biological neural mechanism.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Mapping, Sequence

R_GAS = 8.31446261815324  # J mol^-1 K^-1


@dataclass(frozen=True)
class PhysicalState:
    temperature_c: float
    relative_humidity_pct: float
    pressure_hpa: float


@dataclass(frozen=True)
class ChemicalState:
    temperature_k: float
    water_activity: float
    relative_water_chemical_potential_j_mol: float
    vapor_pressure_deficit_hpa: float


@dataclass(frozen=True)
class CouplingHypothesis:
    k0: float
    beta: float
    z_mean: float = 0.0
    z_scale: float = 1.0


def _finite(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def saturation_vapor_pressure_hpa(temperature_c: float) -> float:
    t = _finite("temperature_c", temperature_c)
    return 6.112 * math.exp((17.67 * t) / (t + 243.5))


def physical_to_chemical(state: PhysicalState) -> ChemicalState:
    t = _finite("temperature_c", state.temperature_c)
    rh = _finite("relative_humidity_pct", state.relative_humidity_pct)
    p = _finite("pressure_hpa", state.pressure_hpa)

    if not 0.0 <= rh <= 100.0:
        raise ValueError("relative_humidity_pct must be in [0,100]")
    if p <= 0.0:
        raise ValueError("pressure_hpa must be positive")

    t_k = t + 273.15
    es = saturation_vapor_pressure_hpa(t)
    e = es * rh / 100.0
    vpd = max(0.0, es - e)

    if rh == 0.0:
        mu = float("-inf")
    else:
        aw = rh / 100.0
        mu = R_GAS * t_k * math.log(aw)

    return ChemicalState(
        temperature_k=t_k,
        water_activity=rh / 100.0,
        relative_water_chemical_potential_j_mol=mu,
        vapor_pressure_deficit_hpa=vpd,
    )


def normalize_covariate(value: float, mean: float, scale: float) -> float:
    x = _finite("value", value)
    m = _finite("mean", mean)
    s = _finite("scale", scale)
    if s <= 0.0:
        raise ValueError("scale must be positive")
    return (x - m) / s


def weather_coupled_gain(z: float, hypothesis: CouplingHypothesis) -> float:
    z_norm = normalize_covariate(z, hypothesis.z_mean, hypothesis.z_scale)
    return hypothesis.k0 * (1.0 + hypothesis.beta * z_norm)


def kuramoto_order_parameter(theta: Sequence[float]) -> float:
    if not theta:
        raise ValueError("theta cannot be empty")
    real = sum(math.cos(x) for x in theta) / len(theta)
    imag = sum(math.sin(x) for x in theta) / len(theta)
    return math.hypot(real, imag)


def graph_flux_from_potential(
    potentials: Mapping[str, float],
    edges: Sequence[tuple[str, str, float]],
) -> dict[str, float]:
    out = {node: 0.0 for node in potentials}
    for source, target, conductance in edges:
        k = _finite("conductance", conductance)
        if k < 0.0:
            raise ValueError("conductance must be nonnegative")
        if source not in potentials or target not in potentials:
            raise KeyError("edge endpoint is not in potentials")
        j = k * (float(potentials[source]) - float(potentials[target]))
        out[source] -= j
        out[target] += j
    return out


def identifiability_conditions() -> dict[str, list[str]]:
    return {
        "H1_weather_to_chemistry": [
            "temperature, RH, and pressure are independently measured",
            "equilibrium assumptions are declared before deriving water activity",
            "thermodynamic quantities are recomputed from raw observations",
        ],
        "H2_chemistry_to_transport": [
            "network topology is fixed or topology change is independently measured",
            "conductances are estimated independently of the response variable",
            "source and sink boundary conditions are recorded",
        ],
        "H3_chemistry_to_information": [
            "information signal is independently measured",
            "phase/coherence metric is predeclared",
            "time-lagged null model survives",
            "weather covariate improves out-of-sample prediction over nulls",
        ],
    }
