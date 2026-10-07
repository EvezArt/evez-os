#!/usr/bin/env python3
"""Deterministic weather -> chemistry -> transport model.

This is a computational translation layer, not a claim that weather directly
causes biological or neural activity. Weather variables are transformed into
well-defined thermodynamic quantities; those quantities can then drive an
abstract graph-transport model inspired by mycelial and synaptic connectivity.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from typing import Iterable, Mapping


@dataclass(frozen=True)
class WeatherObservation:
    temperature_c: float
    relative_humidity_pct: float
    pressure_hpa: float = 1013.25


@dataclass(frozen=True)
class ChemicalSubstrate:
    saturation_vapor_pressure_hpa: float
    vapor_pressure_hpa: float
    vapor_pressure_deficit_hpa: float
    dew_point_c: float
    water_activity_proxy: float
    specific_humidity_kgkg: float


@dataclass(frozen=True)
class FluxEdge:
    source: str
    target: str
    conductance: float


def _finite(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def _validate_observation(obs: WeatherObservation) -> None:
    _finite("temperature_c", obs.temperature_c)
    rh = _finite("relative_humidity_pct", obs.relative_humidity_pct)
    pressure = _finite("pressure_hpa", obs.pressure_hpa)
    if not 0.0 <= rh <= 100.0:
        raise ValueError("relative_humidity_pct must be between 0 and 100")
    if pressure <= 0.0:
        raise ValueError("pressure_hpa must be > 0")


def saturation_vapor_pressure_hpa(temperature_c: float) -> float:
    """Magnus approximation over ordinary near-surface weather ranges."""
    t = _finite("temperature_c", temperature_c)
    return 6.112 * math.exp((17.67 * t) / (t + 243.5))


def dew_point_c(temperature_c: float, relative_humidity_pct: float) -> float:
    t = _finite("temperature_c", temperature_c)
    rh = _finite("relative_humidity_pct", relative_humidity_pct)
    if not 0.0 < rh <= 100.0:
        if rh == 0.0:
            raise ValueError("dew point is undefined for 0% relative humidity")
        raise ValueError("relative_humidity_pct must be between 0 and 100")
    gamma = math.log(rh / 100.0) + (17.67 * t) / (t + 243.5)
    return 243.5 * gamma / (17.67 - gamma)


def translate_weather(obs: WeatherObservation) -> ChemicalSubstrate:
    """Translate weather observables into thermodynamic state variables."""
    _validate_observation(obs)
    es = saturation_vapor_pressure_hpa(obs.temperature_c)
    e = es * obs.relative_humidity_pct / 100.0
    vpd = max(0.0, es - e)
    aw = obs.relative_humidity_pct / 100.0
    q = 0.622 * e / (obs.pressure_hpa - 0.378 * e)
    return ChemicalSubstrate(
        saturation_vapor_pressure_hpa=es,
        vapor_pressure_hpa=e,
        vapor_pressure_deficit_hpa=vpd,
        dew_point_c=dew_point_c(obs.temperature_c, obs.relative_humidity_pct),
        water_activity_proxy=aw,
        specific_humidity_kgkg=q,
    )


def graph_flux(
    potentials: Mapping[str, float],
    edges: Iterable[FluxEdge],
) -> dict[str, float]:
    """Compute signed diffusive flux over an abstract transport graph.

    Positive flux is source -> target. This is a transport equation, not a
    biological claim about fungal or neural tissue.
    """
    flux: dict[str, float] = {node: 0.0 for node in potentials}
    for edge in edges:
        if edge.source not in potentials or edge.target not in potentials:
            raise KeyError(f"unknown node in edge: {edge}")
        conductance = _finite("conductance", edge.conductance)
        if conductance < 0.0:
            raise ValueError("conductance must be >= 0")
        delta = float(potentials[edge.source]) - float(potentials[edge.target])
        edge_flux = conductance * delta
        flux[edge.source] -= edge_flux
        flux[edge.target] += edge_flux
    return flux


def weather_potential(obs: WeatherObservation) -> float:
    """Scalar potential for transport experiments.

    Higher relative humidity and lower VPD increase the potential. The exact
    affine scaling is intentionally explicit so experiments remain reproducible.
    """
    chemistry = translate_weather(obs)
    return chemistry.water_activity_proxy - 0.01 * chemistry.vapor_pressure_deficit_hpa


def canonical_digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def evidence_packet(
    observation: WeatherObservation,
    substrate: ChemicalSubstrate,
    flux: Mapping[str, float],
    *,
    assumptions: list[str],
    uncertainty: list[str],
    dissent: list[str],
) -> dict:
    packet = {
        "schema": "weather-chemistry-mycelial-flux-v0",
        "status": "MODEL_ONLY",
        "observation": asdict(observation),
        "chemical_substrate": asdict(substrate),
        "transport_flux": dict(sorted(flux.items())),
        "assumptions": list(assumptions),
        "uncertainty": list(uncertainty),
        "dissent": list(dissent),
    }
    packet["digest_sha256"] = canonical_digest(packet)
    return packet
