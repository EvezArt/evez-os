"""Epistemic dependency graph, debt, and blast radius."""
from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class DependencyGraph:
    edges: dict[str, set[str]] = field(default_factory=dict)

    def depends_on(self, node: str, dependency: str) -> None:
        self.edges.setdefault(node, set()).add(dependency)

    def dependencies_of(self, node: str) -> set[str]:
        seen: set[str] = set()
        stack = list(self.edges.get(node, ()))
        while stack:
            dep = stack.pop()
            if dep in seen:
                continue
            seen.add(dep)
            stack.extend(self.edges.get(dep, ()))
        return seen

    def epistemic_debt(self, uncertain: set[str]) -> dict[str, int]:
        return {node: len(self.dependencies_of(node) & uncertain) for node in self.edges}

    def blast_radius(self, uncertain_node: str) -> set[str]:
        affected: set[str] = set()
        changed = True
        while changed:
            changed = False
            for node, deps in self.edges.items():
                if uncertain_node in deps or deps & affected:
                    if node not in affected:
                        affected.add(node)
                        changed = True
        return affected
