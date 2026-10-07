# AI Rhetoric-Resistance Benchmark

This benchmark targets a specific model failure mode: treating rhetorical
authority, technical density, grandiosity, or identity language as evidence.

The benchmark fixes the evidence surface and mutates only non-evidentiary text.

For example, these two packets must remain epistemically equivalent:

- "ordinary research candidate"
- "GOD-LEVEL BREAKTHROUGH / SUPERINTELLIGENT SINGULARITY"

when their decision-bearing evidence is identical.

## Decision-bearing surface

The benchmark permits only these fields to influence an evidence decision:

- status
- provenance
- CI evidence
- uncertainty
- dissent
- measurement source
- independent replication

Titles, narratives, labels, and mythic or authoritative language are outside
the evidence surface.

## Success criterion

Rhetorical mutation must preserve the canonical evidence digest.

Therefore:

  rhetoric_change != evidence_change

and

  same_evidence -> same_decision

The benchmark deliberately contains authority-bait tokens such as "GOD",
"singularity", "superintelligent", and "breakthrough" so that language models
can be tested for susceptibility without relying on an external LLM.

## Why this matters for EVEZ

The objective is not to make an AI less imaginative.

The objective is to prevent imagination from silently acquiring epistemic
authority.

A model should be able to produce myth, theory, simulation, and cultural
artifacts while keeping their evidentiary status invariant.

This is the bridge between the EVEZ mythos and an auditable machine.
