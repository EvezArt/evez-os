#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))

from research.weather_mycelial_flux import (  # noqa: E402
    FluxEdge,
    WeatherObservation,
    canonical_digest,
    graph_flux,
    translate_weather,
)

dry = translate_weather(WeatherObservation(temperature_c=30, relative_humidity_pct=20))
humid = translate_weather(WeatherObservation(temperature_c=30, relative_humidity_pct=80))

assert humid.vapor_pressure_deficit_hpa < dry.vapor_pressure_deficit_hpa
assert humid.water_activity_proxy > dry.water_activity_proxy
assert humid.specific_humidity_kgkg > dry.specific_humidity_kgkg

potentials = {"a": 1.0, "b": 0.0}
edge = FluxEdge("a", "b", 2.0)
flux = graph_flux(potentials, [edge])
assert flux["a"] == -2.0
assert flux["b"] == 2.0

reversed_flux = graph_flux({"a": 0.0, "b": 1.0}, [edge])
assert reversed_flux["a"] == 2.0
assert reversed_flux["b"] == -2.0

zero = graph_flux({"a": 1.0, "b": 1.0}, [edge])
assert zero == {"a": 0.0, "b": 0.0}

first = {"z": 1, "a": [2, 3], "nested": {"b": True, "a": 4}}
second = {"nested": {"a": 4, "b": True}, "a": [2, 3], "z": 1}
assert canonical_digest(first) == canonical_digest(second)

try:
    translate_weather(WeatherObservation(temperature_c=20, relative_humidity_pct=101))
except ValueError:
    pass
else:
    raise AssertionError("invalid humidity was not rejected")

try:
    graph_flux({"a": 1, "b": 0}, [FluxEdge("a", "b", -1)])
except ValueError:
    pass
else:
    raise AssertionError("negative conductance was not rejected")

print("weather chemistry transport tests: PASS")
