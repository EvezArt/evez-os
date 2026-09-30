"""Cross-map invention primitives.

This module generates proposed transformations from registered map surfaces.
Generation is explicitly non-evidentiary: every artifact is PROPOSED until an
external observation/test supplies evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from itertools import combinations
from typing import Iterable

from .maps import MapSpec, UniversalMapRegistry


class InventionState(str, Enum):
    PROPOSED = "PROPOSED"
    TESTABLE = "TESTABLE"
    SUPPORTED = "SUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    ARCHIVED = "ARCHIVED"


@dataclass(frozen=True)
class Transformation:
    transformation_id: str
    name: str
    source_map: str
    operation: str
    constraints: tuple[str, ...] = ()
    provenance: tuple[str, ...] = ()
    state: InventionState = InventionState.PROPOSED


@dataclass(frozen=True)
class Invention:
    invention_id: str
    parent_ids: tuple[str, ...]
    source_maps: tuple[str, ...]
    transformations: tuple[str, ...]
    assumptions: tuple[str, ...]
    predictions: tuple[str, ...]
    falsifiers: tuple[str, ...]
    evidence_requirements: tuple[str, ...]
    state: InventionState = InventionState.PROPOSED


@dataclass(frozen=True)
class CompatibilityResult:
    transformation_id: str
    target_map: str
    compatible: bool
    reasons: tuple[str, ...]


class CrossMapInventionEngine:
    """Generate and route proposals without asserting that they exist in reality."""

    def __init__(self, registry: UniversalMapRegistry) -> None:
        self.registry = registry
        self._transformations: dict[str, Transformation] = {}
        self._inventions: dict[str, Invention] = {}

    def register_transformation(self, transformation: Transformation) -> None:
        if transformation.source_map not in {s.map_id for s in self.registry.all()}:
            raise ValueError("transformation source map is not registered")
        self._transformations[transformation.transformation_id] = transformation

    def transformations(self) -> tuple[Transformation, ...]:
        return tuple(self._transformations[k] for k in sorted(self._transformations))

    def inventions(self) -> tuple[Invention, ...]:
        return tuple(self._inventions[k] for k in sorted(self._inventions))

    def compatibility(
        self,
        transformation_id: str,
        target_map: str,
        *,
        required_kinds: frozenset[str] = frozenset(),
        forbidden_operations: frozenset[str] = frozenset(),
    ) -> CompatibilityResult:
        t = self._transformations[transformation_id]
        target = self.registry.get(target_map)
        reasons: list[str] = []
        compatible = True
        if t.operation in forbidden_operations:
            compatible = False
            reasons.append("operation explicitly forbidden for this routing attempt")
        if required_kinds and target.kind.value not in required_kinds:
            compatible = False
            reasons.append("target map kind does not satisfy the supplied constraint")
        if target.map_id == t.source_map:
            reasons.append("target equals source; cross-map transfer is not demonstrated")
        else:
            reasons.append("routing is structurally admissible; execution and truth remain unverified")
        return CompatibilityResult(t.transformation_id, target.map_id, compatible, tuple(reasons))

    def route(
        self,
        transformation_id: str,
        targets: Iterable[str],
        *,
        required_kinds: frozenset[str] = frozenset(),
        forbidden_operations: frozenset[str] = frozenset(),
    ) -> tuple[CompatibilityResult, ...]:
        return tuple(
            self.compatibility(
                transformation_id,
                target,
                required_kinds=required_kinds,
                forbidden_operations=forbidden_operations,
            )
            for target in sorted(set(targets))
        )

    def synthesize(
        self,
        *,
        invention_id: str,
        transformation_ids: Iterable[str],
        assumptions: Iterable[str] = (),
        predictions: Iterable[str] = (),
        falsifiers: Iterable[str] = (),
        evidence_requirements: Iterable[str] = (),
    ) -> Invention:
        ids = tuple(sorted(set(transformation_ids)))
        if not ids:
            raise ValueError("synthesis requires at least one transformation")
        source_maps = tuple(sorted({self._transformations[i].source_map for i in ids}))
        parent_ids = tuple(sorted(self._inventions))
        invention = Invention(
            invention_id=invention_id,
            parent_ids=parent_ids,
            source_maps=source_maps,
            transformations=ids,
            assumptions=tuple(assumptions),
            predictions=tuple(predictions),
            falsifiers=tuple(falsifiers),
            evidence_requirements=tuple(evidence_requirements),
        )
        self._inventions[invention_id] = invention
        return invention

    def generate_recombinations(
        self,
        *,
        prefix: str,
        max_parents: int = 2,
    ) -> tuple[Invention, ...]:
        items = self.transformations()
        generated: list[Invention] = []
        for width in range(2, max(2, max_parents) + 1):
            for index, combo in enumerate(combinations(items, width)):
                ids = tuple(t.transformation_id for t in combo)
                inv_id = f"{prefix}-{width}-{index:04d}"
                generated.append(
                    self.synthesize(
                        invention_id=inv_id,
                        transformation_ids=ids,
                        assumptions=("generated recombination; assumptions require validation",),
                        predictions=("combined transformation should produce a testable distinction",),
                        falsifiers=("target observation fails the predicted distinction",),
                        evidence_requirements=("execution receipt", "observed output"),
                    )
                )
        return tuple(generated)

    def archive(self, invention_id: str, reason: str) -> Invention:
        old = self._inventions[invention_id]
        archived = Invention(
            invention_id=old.invention_id,
            parent_ids=old.parent_ids,
            source_maps=old.source_maps,
            transformations=old.transformations,
            assumptions=old.assumptions + (reason,),
            predictions=old.predictions,
            falsifiers=old.falsifiers,
            evidence_requirements=old.evidence_requirements,
            state=InventionState.ARCHIVED,
        )
        self._inventions[invention_id] = archived
        return archived
