# Weather -> Chemistry -> Mycelial/Synaptic Flux Contract

This module is a bounded computational experiment for translating weather data
into a chemistry-shaped state representation and then transporting that state
over an abstract network.

It is deliberately MODEL_ONLY. It does not establish a biological,
neurological, fungal, climatic, or consciousness mechanism.

## Translation

For a weather observation (T, RH, P):

- saturation vapor pressure is estimated with a Magnus approximation
- vapor pressure is saturation vapor pressure multiplied by RH
- vapor-pressure deficit is max(0, saturation vapor pressure - vapor pressure)
- RH/100 is used only as a water-activity proxy
- specific humidity is derived from vapor pressure and pressure
- dew point is derived from the same state

These quantities are reproducible from the same input values.

## Transport

The mycelial/synaptic language denotes an abstract graph:

    J_ij = k_ij * (x_i - x_j)

where x is an explicitly supplied scalar potential and k is an explicitly
supplied conductance.

Useful falsifiers and invariants:

- zero gradient -> zero flux
- reversing a gradient -> reversing the sign of flux
- zero conductance -> zero transport
- invalid humidity -> rejection
- canonicalization must make object-key order irrelevant

The graph is an engineering abstraction inspired by transport networks. It is
not a claim that fungal hyphae and neurons obey this exact model.

## Evidence discipline

Every evidence packet carries:

- status = MODEL_ONLY
- assumptions
- uncertainty
- dissent
- deterministic SHA-256 digest

A result becomes MEASURED only when backed by actual sensor data. It becomes
REPLICATED only when an independent run reproduces the measurement.

## Verification boundary

Promotion is:

    MODEL_ONLY -> MEASURED -> REPLICATED

No autonomous deploy, merge, privilege grant, or secret exposure belongs in
this experiment.
