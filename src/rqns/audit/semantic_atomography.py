"""Evidence-bound semantic atomography for nested LLM/agent execution.

This module does not expose hidden model internals. It reconstructs only the
observable semantic transitions present in an execution trace: agent/LLM/tool
atoms, parent-child nesting, lexical feature deltas, and causal handoffs.

"Atomography" here means tomography of observable language-mediated state
transitions, not literal inspection of neural activations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import re
from typing import Dict, Iterable, List, Optional, Tuple


TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")


@dataclass(frozen=True)
class SemanticAtom:
    atom_id: str
    parent_id: Optional[str]
    actor_id: str
    kind: str
    input_text: str
    output_text: str
    depth: int = 0
    metadata: Dict[str, str] = field(default_factory=dict)

    def _features(self, text: str) -> Tuple[str, ...]:
        return tuple(sorted(set(TOKEN_RE.findall(text.lower()))))

    @property
    def input_features(self) -> Tuple[str, ...]:
        return self._features(self.input_text)

    @property
    def output_features(self) -> Tuple[str, ...]:
        return self._features(self.output_text)

    @property
    def semantic_delta(self) -> Tuple[Tuple[str, ...], Tuple[str, ...]]:
        before = set(self.input_features)
        after = set(self.output_features)
        return tuple(sorted(after - before)), tuple(sorted(before - after))

    def canonical_bytes(self) -> bytes:
        payload = {
            "atom_id": self.atom_id,
            "parent_id": self.parent_id,
            "actor_id": self.actor_id,
            "kind": self.kind,
            "input_text": self.input_text,
            "output_text": self.output_text,
            "depth": self.depth,
            "metadata": dict(sorted(self.metadata.items())),
        }
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True)
class SemanticTransition:
    parent_atom: str
    child_atom: str
    transition_kind: str
    added_features: Tuple[str, ...]
    removed_features: Tuple[str, ...]

    def canonical_bytes(self) -> bytes:
        payload = {
            "parent_atom": self.parent_atom,
            "child_atom": self.child_atom,
            "transition_kind": self.transition_kind,
            "added_features": self.added_features,
            "removed_features": self.removed_features,
        }
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


class SemanticTomograph:
    """Build an auditable observable trace of nested language-mediated calls."""

    def __init__(self) -> None:
        self.atoms: Dict[str, SemanticAtom] = {}
        self.transitions: List[SemanticTransition] = []

    def add(self, atom: SemanticAtom) -> str:
        if atom.atom_id in self.atoms:
            raise ValueError(f"duplicate semantic atom: {atom.atom_id}")
        if atom.parent_id is not None and atom.parent_id not in self.atoms:
            raise ValueError(f"unknown parent atom: {atom.parent_id}")
        if atom.depth < 0:
            raise ValueError("depth cannot be negative")
        if atom.parent_id is not None:
            parent = self.atoms[atom.parent_id]
            if atom.depth != parent.depth + 1:
                raise ValueError("child depth must equal parent depth + 1")
            added, removed = self._handoff_features(parent, atom)
            transition = SemanticTransition(
                parent_atom=parent.atom_id,
                child_atom=atom.atom_id,
                transition_kind=f"{parent.kind}->{atom.kind}",
                added_features=added,
                removed_features=removed,
            )
            self.transitions.append(transition)
        self.atoms[atom.atom_id] = atom
        return atom.content_hash()

    @staticmethod
    def _handoff_features(parent: SemanticAtom, child: SemanticAtom) -> Tuple[Tuple[str, ...], Tuple[str, ...]]:
        parent_features = set(parent.output_features)
        child_features = set(child.input_features)
        return tuple(sorted(child_features - parent_features)), tuple(sorted(parent_features - child_features))

    def descendants(self, atom_id: str) -> Tuple[SemanticAtom, ...]:
        if atom_id not in self.atoms:
            raise KeyError(atom_id)
        return tuple(atom for atom in self.atoms.values() if atom.parent_id == atom_id)

    def max_depth(self) -> int:
        return max((atom.depth for atom in self.atoms.values()), default=0)

    def recursive_handoffs(self) -> Tuple[SemanticTransition, ...]:
        return tuple(t for t in self.transitions if t.transition_kind.startswith("agent->agent") or t.transition_kind.startswith("llm->agent") or t.transition_kind.startswith("agent->llm"))

    def snapshot_hash(self) -> str:
        payload = {
            "atoms": [self.atoms[key].content_hash() for key in sorted(self.atoms)],
            "transitions": [t.content_hash() for t in self.transitions],
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()

    def summary(self) -> Dict[str, object]:
        return {
            "atom_count": len(self.atoms),
            "transition_count": len(self.transitions),
            "max_depth": self.max_depth(),
            "recursive_handoff_count": len(self.recursive_handoffs()),
            "snapshot_hash": self.snapshot_hash(),
        }


def build_tomograph(atoms: Iterable[SemanticAtom]) -> SemanticTomograph:
    tomograph = SemanticTomograph()
    for atom in atoms:
        tomograph.add(atom)
    return tomograph


__all__ = [
    "SemanticAtom",
    "SemanticTomograph",
    "SemanticTransition",
    "build_tomograph",
]
