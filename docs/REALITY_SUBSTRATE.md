# EVEZ Reality Substrate

The EVEZ Reality Substrate is a deterministic computational foundation for a persistent world model.

It does not assert that a rendered artifact is reality. The world model is the source state and media are projections of that state.

Core contracts:

- WorldEntity: addressable entity state plus provenance and epistemic status.
- CausalEvent: typed cause/effect transition with evidence and reversibility.
- WorldSnapshot: immutable-style view of entities and causal history.
- AppendOnlyLedger: replayable hash chain for persistent state.
- ProjectionSpec and ArtifactManifest: representation changes without changing source identity.
- CounterfactualBranch: explicit simulated or projected branch from a parent snapshot.
- CulturalUnit: transmissible unit with ancestry and mutation tracking.
- SelfMetric: predicted-versus-observed system behavior.
- DirectorCandidate: bounded resource-aware candidate operation.
- choose_next_operation: deterministic selection that cannot self-authorize or rewrite its own success criterion.

The substrate closes the loop:

intent -> state -> event -> snapshot -> projection -> observation -> event

The same snapshot can drive text, image, video, audio, 3D, UI, simulation, or data projections. The projection is reproducible from the snapshot, observer, representation, and parameters.

The director is deliberately not sovereign. It selects among explicit candidates, preserves a locked success criterion, and returns self_authorization=false.

Uncertainty remains first-class. A simulated projection is never promoted to observed truth merely because it rendered successfully.

Cultural compounding preserves ancestry when a unit is transmitted into a new carrier. Mutation is explicit and indexed.

Self-compounding records prediction error and resource cost so improvement can be measured rather than narrated.

The ledger is suitable as the core content of persistent EVEZ artifacts; exchange payloads can use EVEX envelopes across system boundaries.

This is a reference substrate. Renderer adapters can be attached without changing the world-state contracts.
