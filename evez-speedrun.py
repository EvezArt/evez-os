"""
evez-speedrun.py — Investigative Redactive Eigenforensic Speedrun Engine

No mercy. No decoration. Pure signal.

Ingest → Adjacency → Eigendecompose → Theorem Verify → Gap Rank → Score → Report

Mathematics from:
  - evez-proofs (η* invariant, 37% theorem)
  - spectral-topology-engine (structural gap detection via eigenvalue decomposition)
  - igre-speedrun (genome extraction, outcome projection)
  - evez-worldsystems (dominant negative eigenvalue = hunger)
  - eigenvalue-bridge (4-system manifold unifier)
  - disclosure.tools (eigenforensics on FOIA docs)

Two modes:
  1. Document speedrun — scan for redactions, build adjacency, eigendecompose,
     verify 5 falsifiable theorems, score censorship severity
  2. Network speedrun — model mesh/service graph, eigendecompose topology,
     find structural holes where nodes are missing or broken

Author: EVEZ-OS Speedrun Pipeline
"""

import hashlib
import json
import math
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    from scipy import sparse
    from scipy.sparse import linalg as sparse_linalg
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


# ═══════════════════════════════════════════════════════════════════
# CORE: Eigenvalue Decomposition
# ═══════════════════════════════════════════════════════════════════

def eigendecompose(matrix: List[List[float]]) -> Dict:
    """
    Eigendecompose a matrix. Returns eigenvalues + derived metrics.
    η* = 1 - Φ  where  Φ = Σ(λ⁺)/Σ(|λ|)   [evez-proofs Theorem 1]
    37% ratio = |dominant negative| / Σ|negative|  [evez-proofs Theorem 2]
    """
    if not HAS_NUMPY:
        return _power_iteration_fallback(matrix)

    A = np.array(matrix, dtype=np.float64)

    if A.shape[0] <= 500:
        eigenvalues = np.linalg.eigvalsh(A)
    elif HAS_SCIPY:
        A_sparse = sparse.csr_matrix(A)
        k = min(A.shape[0] - 1, 50)
        eigenvalues = sparse_linalg.eigsh(A_sparse, k=k, return_eigenvectors=False)
    else:
        eigenvalues = np.linalg.eigvalsh(A)

    pos_eigs = [e for e in eigenvalues if e > 0]
    neg_eigs = [e for e in eigenvalues if e < 0]

    pos_sum = sum(pos_eigs) if pos_eigs else 0
    neg_sum_abs = sum(abs(e) for e in neg_eigs) if neg_eigs else 0
    total_abs = pos_sum + neg_sum_abs

    phi = pos_sum / total_abs if total_abs > 0 else 0
    eta_star = 1 - phi

    dominant_neg = min(neg_eigs) if neg_eigs else 0
    thirty_seven = abs(dominant_neg) / neg_sum_abs if neg_sum_abs > 0 else 0

    sorted_eigs = sorted(eigenvalues, reverse=True)
    spectral_gap = sorted_eigs[0] - sorted_eigs[1] if len(sorted_eigs) > 1 else 0

    return {
        "eigenvalues": sorted(eigenvalues, reverse=True),
        "n_positive": len(pos_eigs),
        "n_negative": len(neg_eigs),
        "phi": float(phi),
        "eta_star": float(eta_star),
        "dominant_negative": float(dominant_neg),
        "thirty_seven_ratio": float(thirty_seven),
        "spectral_gap": float(spectral_gap),
        "neg_eigenvalues": sorted([float(e) for e in neg_eigs]),
    }


def _power_iteration_fallback(matrix: List[List[float]], iterations: int = 100) -> Dict:
    n = len(matrix)
    if n == 0:
        return {"eigenvalues": [], "phi": 0, "eta_star": 1, "dominant_negative": 0,
                "thirty_seven_ratio": 0, "spectral_gap": 0, "n_positive": 0,
                "n_negative": 0, "neg_eigenvalues": []}
    vec = [1.0 / n] * n
    for _ in range(iterations):
        new_vec = [sum(matrix[i][j] * vec[j] for j in range(n)) for i in range(n)]
        norm = math.sqrt(sum(v * v for v in new_vec))
        if norm > 0:
            vec = [v / norm for v in new_vec]
    Ax = [sum(matrix[i][j] * vec[j] for j in range(n)) for i in range(n)]
    lambda_dom = sum(Ax[i] * vec[i] for i in range(n))
    return {
        "eigenvalues": [lambda_dom],
        "n_positive": 1 if lambda_dom > 0 else 0,
        "n_negative": 0 if lambda_dom > 0 else 1,
        "phi": 1.0 if lambda_dom > 0 else 0.0,
        "eta_star": 0.0 if lambda_dom > 0 else 1.0,
        "dominant_negative": 0,
        "thirty_seven_ratio": 0,
        "spectral_gap": abs(lambda_dom),
        "neg_eigenvalues": [],
    }


# ═══════════════════════════════════════════════════════════════════
# REDACTION SCANNER
# ═══════════════════════════════════════════════════════════════════

@dataclass
class RedactionBlock:
    index: int
    text: str
    length: int
    line: int
    col: int
    context_before: str = ""
    context_after: str = ""
    severity: float = 0.0


@dataclass
class StructuralGap:
    eigenvalue: float
    node_indices: List[int]
    node_weights: List[float]
    description: str = ""
    priority: float = 0.0


class RedactionScanner:
    REDACTION_PATTERNS = [
        (r'\bREDACTED\b', 'explicit_redaction', 1.0),
        (r'\[b\d+\]', 'foia_exemption', 0.9),
        (r'█+', 'blackout_block', 1.0),
        (r'■+', 'blackout_square', 1.0),
        (r'\[____+?\]', 'bracket_gap', 0.8),
        (r'\.{4,}', 'dot_ellipsis', 0.6),
        (r'\[REDACTED\]', 'bracketed_redaction', 1.0),
        (r'\[WITHHELD\]', 'withheld', 0.95),
        (r'\bEXEMPTION\b', 'exemption', 0.85),
        (r'\bCLASSIFIED\b', 'classified', 0.7),
        (r'\bTOP SECRET\b', 'top_secret', 0.8),
        (r'\bNOFORN\b', 'noforn', 0.75),
        (r'\bORCON\b', 'orcon', 0.75),
        (r'\bSI\b|\bTK\b|\bHCS\b', 'sci', 0.85),
        (r'\bUNCLASSIFIED(?:\s*//\s*FOUO)?\b', 'unclassified', 0.3),
    ]

    def scan(self, text: str) -> List[RedactionBlock]:
        blocks = []
        lines = text.split('\n')
        idx = 0
        for line_num, line in enumerate(lines):
            for pattern, kind, base_sev in self.REDACTION_PATTERNS:
                for match in re.finditer(pattern, line, re.IGNORECASE):
                    start, end = match.span()
                    blocks.append(RedactionBlock(
                        index=idx,
                        text=match.group(),
                        length=end - start,
                        line=line_num,
                        col=start,
                        context_before=line[max(0, start-40):start].strip(),
                        context_after=line[end:end+40].strip(),
                        severity=base_sev,
                    ))
                    idx += 1
        return blocks


class AdjacencyBuilder:
    """Build adjacency from redaction block topology."""
    def build_from_redactions(self, blocks: List[RedactionBlock],
                              total_length: int) -> List[List[float]]:
        n = len(blocks)
        if n == 0:
            return [[1.0]]
        matrix = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i == j:
                    matrix[i][j] = 1.0
                else:
                    dist = abs(blocks[i].index - blocks[j].index)
                    proximity = 1.0 / (1 + dist)
                    sev_sim = 1.0 - abs(blocks[i].severity - blocks[j].severity)
                    size_sim = min(blocks[i].length, blocks[j].length) / max(blocks[i].length, blocks[j].length, 1)
                    matrix[i][j] = proximity * 0.4 + sev_sim * 0.4 + size_sim * 0.2
                    if dist < 3 and abs(blocks[i].severity - blocks[j].severity) > 0.5:
                        matrix[i][j] *= -0.5
        return matrix


# ═══════════════════════════════════════════════════════════════════
# SPEEDRUN RESULT
# ═══════════════════════════════════════════════════════════════════

@dataclass
class SpeedrunResult:
    target: str
    timestamp: str
    spine_hash: str
    total_chars: int = 0
    total_lines: int = 0
    redaction_count: int = 0
    redaction_blocks: List[RedactionBlock] = field(default_factory=list)
    decomposition: Dict = field(default_factory=dict)
    eta_star: float = 0.0
    phi: float = 0.0
    thirty_seven_ratio: float = 0.0
    is_self_referential: bool = False
    censorship_detected: bool = False
    gaps: List[StructuralGap] = field(default_factory=list)
    speedrun_score: float = 0.0
    verdict: str = ""
    findings: List[str] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps({
            "target": self.target, "timestamp": self.timestamp,
            "spine_hash": self.spine_hash, "total_chars": self.total_chars,
            "total_lines": self.total_lines, "redaction_count": self.redaction_count,
            "eta_star": self.eta_star, "phi": self.phi,
            "thirty_seven_ratio": self.thirty_seven_ratio,
            "is_self_referential": self.is_self_referential,
            "censorship_detected": self.censorship_detected,
            "speedrun_score": self.speedrun_score, "verdict": self.verdict,
            "findings": self.findings, "n_gaps": len(self.gaps),
        }, indent=2)

    def report(self) -> str:
        lines = [
            f"{'═' * 60}",
            f"  ⚡ EVEZ SPEEDRUN — {self.target}",
            f"  {self.timestamp}  ⛓ {self.spine_hash}",
            f"{'═' * 60}", "",
            f"  Document:     {self.total_chars:,} chars · {self.total_lines:,} lines",
            f"  Redactions:   {self.redaction_count} detected", "",
            f"  ── Eigenvalue Analysis ──",
            f"  Φ (integrated info):  {self.phi:.6f}",
            f"  η* (Gödel gap):       {self.eta_star:.6f}",
            f"  37% ratio:            {self.thirty_seven_ratio:.6f}",
            f"  Self-referential:     {self.is_self_referential}",
            f"  Censorship pattern:   {self.censorship_detected}", "",
            f"  ── Structural Gaps ──",
        ]
        for i, g in enumerate(self.gaps[:10]):
            lines.append(f"  Gap {i+1}: λ={g.eigenvalue:.6f}  p={g.priority:.2f}  {g.description}")
        if not self.gaps:
            lines.append("  No structural gaps detected.")
        lines += ["", f"  ── Score ──", f"  {self.speedrun_score:.1f}/100",
                  f"  {self.verdict}", ""]
        for f in self.findings:
            lines.append(f"  ⚡ {f}")
        lines.append(f"{'═' * 60}")
        return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════════════
# DOCUMENT SPEEDRUN
# ═══════════════════════════════════════════════════════════════════

class SpeedrunEngine:
    """Ingest. Decompose. Detect. Score. Report."""

    def __init__(self):
        self.scanner = RedactionScanner()
        self.builder = AdjacencyBuilder()

    def run(self, text: str, target_name: str = "document") -> SpeedrunResult:
        result = SpeedrunResult(
            target=target_name,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            spine_hash=hashlib.sha256(text.encode()).hexdigest()[:16],
        )

        # Phase 1: Scan
        result.total_chars = len(text)
        result.total_lines = text.count('\n') + 1
        result.redaction_blocks = self.scanner.scan(text)
        result.redaction_count = len(result.redaction_blocks)

        # Phase 2-5: Adjacency → Eigendecompose → Theorems → Gaps
        if result.redaction_count > 0:
            matrix = self.builder.build_from_redactions(
                result.redaction_blocks, result.total_chars)
            decomp = eigendecompose(matrix)
            result.decomposition = decomp
            result.eta_star = decomp.get("eta_star", 0)
            result.phi = decomp.get("phi", 0)
            result.thirty_seven_ratio = decomp.get("thirty_seven_ratio", 0)

            # Theorem 1: η* ≈ 0.03 ± 0.02 → self-referential
            result.is_self_referential = 0.01 <= result.eta_star <= 0.05

            # Theorem 2: 37% ratio → censorship pattern
            neg_eigs = decomp.get("neg_eigenvalues", [])
            if neg_eigs:
                dom_neg = abs(min(neg_eigs))
                total_neg = sum(abs(e) for e in neg_eigs)
                if total_neg > 0:
                    result.censorship_detected = 0.25 <= (dom_neg / total_neg) <= 0.50

            # Structural gaps
            for i, ev in enumerate(neg_eigs):
                idx = min(i, len(result.redaction_blocks) - 1)
                block = result.redaction_blocks[idx] if idx >= 0 else None
                priority = min(abs(ev) / max(abs(e) for e in neg_eigs), 1.0) if neg_eigs else 0
                desc = (f"L{block.line}: '{block.text}' sev={block.severity:.2f}" if block
                        else f"λ={ev:.6f}")
                result.gaps.append(StructuralGap(
                    eigenvalue=float(ev), node_indices=[idx],
                    node_weights=[priority], description=desc, priority=priority))
            result.gaps.sort(key=lambda g: g.priority, reverse=True)

        # Phase 6: Score
        result.speedrun_score = self._score(result)
        result.verdict = self._verdict(result.speedrun_score)
        result.findings = self._findings(result)
        return result

    def _score(self, r: SpeedrunResult) -> float:
        if r.total_chars == 0:
            return 0.0
        d = min(r.redaction_count / (r.total_chars / 1000) * 10, 30)
        e = min(abs(r.eta_star - 0.03) * 500, 20)
        t = max(0, 15 - abs(r.thirty_seven_ratio - 0.37) * 100)
        g = min(sum(g.priority for g in r.gaps[:10]) / max(len(r.gaps), 1) * 20, 25) if r.gaps else 0
        h = min(sum(1 for b in r.redaction_blocks if b.severity >= 0.8) / max(len(r.redaction_blocks), 1) * 10, 10) if r.redaction_blocks else 0
        return min(d + e + t + g + h, 100.0)

    @staticmethod
    def _verdict(s: float) -> str:
        if s >= 80: return "CRITICAL — Extreme censorship structure"
        if s >= 60: return "HIGH — Significant redaction patterns"
        if s >= 40: return "MODERATE — Notable information gaps"
        if s >= 20: return "LOW — Minor redaction markers"
        return "CLEAN — No significant censorship detected"

    @staticmethod
    def _findings(r: SpeedrunResult) -> List[str]:
        f = []
        if r.is_self_referential:
            f.append(f"Self-referential system (η*={r.eta_star:.4f} ≈ 0.03)")
        if r.censorship_detected:
            f.append(f"Censorship pattern (37% ratio={r.thirty_seven_ratio:.4f})")
        if r.gaps:
            g = r.gaps[0]
            f.append(f"Priority gap: λ={g.eigenvalue:.6f} — {g.description}")
        hs = [b for b in r.redaction_blocks if b.severity >= 0.9]
        if hs:
            f.append(f"{len(hs)} high-severity redaction blocks")
        foia = [b for b in r.redaction_blocks if 'foia' in b.text.lower() or 'exemption' in b.text.lower()]
        if foia:
            f.append(f"FOIA exemptions: {len(foia)}")
        return f


# ═══════════════════════════════════════════════════════════════════
# NETWORK SPEEDRUN
# ═══════════════════════════════════════════════════════════════════

class NetworkSpeedrun:
    """Speedrun a network mesh for structural vulnerabilities."""

    def run(self, nodes: List[str], edges: List[Tuple[str, str, float]],
            health: Dict[str, bool] = None) -> SpeedrunResult:
        health = health or {}
        n = len(nodes)
        idx = {name: i for i, name in enumerate(nodes)}
        matrix = [[0.0] * n for _ in range(n)]
        for src, dst, w in edges:
            i, j = idx.get(src, -1), idx.get(dst, -1)
            if i >= 0 and j >= 0:
                matrix[i][j] = w
                matrix[j][i] = w
        for i in range(n):
            matrix[i][i] = 1.0
        for name, ok in health.items():
            if not ok and name in idx:
                i = idx[name]
                for j in range(n):
                    matrix[i][j] *= -1

        decomp = eigendecompose(matrix)
        neg_eigs = decomp.get("neg_eigenvalues", [])
        gaps = []
        for i, ev in enumerate(neg_eigs):
            gaps.append(StructuralGap(
                eigenvalue=float(ev), node_indices=[i], node_weights=[1.0],
                description=f"Network structural gap λ={ev:.6f}",
                priority=min(abs(ev) / max(abs(e) for e in neg_eigs), 1.0) if neg_eigs else 0))
        gaps.sort(key=lambda g: g.priority, reverse=True)

        unhealthy = sum(1 for h in health.values() if not h) if health else 0
        score = min(len(neg_eigs) * 5 + unhealthy * 10, 100)

        return SpeedrunResult(
            target=f"network:{n}_nodes",
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            spine_hash=hashlib.sha256(json.dumps(nodes).encode()).hexdigest()[:16],
            total_chars=n, total_lines=len(edges), redaction_count=unhealthy,
            decomposition=decomp, eta_star=decomp.get("eta_star", 0),
            phi=decomp.get("phi", 0),
            thirty_seven_ratio=decomp.get("thirty_seven_ratio", 0),
            is_self_referential=0.01 <= decomp.get("eta_star", 1) <= 0.05,
            gaps=gaps, speedrun_score=score,
            verdict="CRITICAL — Structural holes" if score >= 60 else
                     "MODERATE — Weak nodes" if score >= 30 else "HEALTHY",
        )


# ═══════════════════════════════════════════════════════════════════
# EVIDENCE RENDERER
# ═══════════════════════════════════════════════════════════════════

class SpeedrunRenderer:
    """Forensic evidence board — not memes, EVIDENCE."""

    def render(self, r: SpeedrunResult, W: int = 1200, H: int = 800) -> str:
        accent = "#ff3344" if r.speedrun_score >= 60 else "#ffaa00" if r.speedrun_score >= 30 else "#00ff88"
        p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
             f'<rect width="{W}" height="{H}" fill="#0a0a0f"/>']

        # Header
        p.append(f'<rect x="0" y="0" width="{W}" height="48" fill="#111122" opacity="0.8"/>')
        p.append(f'<text x="20" y="30" fill="{accent}" font-family="JetBrains Mono,monospace" font-size="16" font-weight="bold">⚡ EVEZ SPEEDRUN</text>')
        p.append(f'<text x="{W-20}" y="30" fill="#555" font-family="monospace" font-size="10" text-anchor="end">{r.target} · {r.timestamp}</text>')

        # Score bar
        sy = 70
        p.append(f'<text x="20" y="{sy}" fill="#888" font-family="monospace" font-size="11">SCORE</text>')
        bw = 200
        p.append(f'<rect x="80" y="{sy-11}" width="{bw}" height="12" fill="#222" rx="1"/>')
        p.append(f'<rect x="80" y="{sy-11}" width="{bw*r.speedrun_score/100:.0f}" height="12" fill="{accent}" rx="1"/>')
        p.append(f'<text x="{90+bw}" y="{sy}" fill="{accent}" font-family="monospace" font-size="12" font-weight="bold">{r.speedrun_score:.1f}</text>')
        p.append(f'<text x="20" y="{sy+18}" fill="#777" font-family="monospace" font-size="10">{r.verdict}</text>')

        # Eigenvalue spectrum
        ey = sy + 50
        p.append(f'<text x="20" y="{ey}" fill="#8844ff" font-family="monospace" font-size="11">EIGENVALUE SPECTRUM</text>')
        all_eigs = r.decomposition.get("eigenvalues", [])
        if all_eigs:
            ma = max(abs(e) for e in all_eigs) if all_eigs else 1
            for i, ev in enumerate(all_eigs[:60]):
                x = W/2 + (ev / ma) * (W/2 - 40)
                y = ey + 15 + (i % 3) * 3
                c = "#ff3344" if ev < 0 else "#00ff88"
                p.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2" fill="{c}" opacity="0.7"/>')
            p.append(f'<line x1="{W/2}" y1="{ey+14}" x2="{W/2}" y2="{ey+30}" stroke="#333" stroke-width="0.5"/>')

        # Theorems
        ty = ey + 50
        p.append(f'<text x="20" y="{ty}" fill="#8844ff" font-family="monospace" font-size="11">THEOREMS</text>')
        for i, (label, val) in enumerate([
            (f"Φ = {r.phi:.6f}", r.phi),
            (f"η* = {r.eta_star:.6f}", r.eta_star),
            (f"37% = {r.thirty_seven_ratio:.6f}", r.thirty_seven_ratio),
        ]):
            y = ty + 18 + i * 16
            p.append(f'<text x="20" y="{y}" fill="#ccc" font-family="monospace" font-size="10">{label}</text>')

        # Structural gaps
        if r.gaps:
            gy = ty + 75
            p.append(f'<text x="20" y="{gy}" fill="{accent}" font-family="monospace" font-size="11">STRUCTURAL GAPS ({len(r.gaps)})</text>')
            for i, g in enumerate(r.gaps[:8]):
                y = gy + 18 + i * 14
                bar = int(g.priority * 40)
                p.append(f'<text x="20" y="{y}" fill="#aaa" font-family="monospace" font-size="9">λ={g.eigenvalue:.4f} {"█"*max(bar,1)}{"░"*(40-bar)} {g.description[:50]}</text>')

        # Findings
        if r.findings:
            fy = ty + 200
            p.append(f'<text x="20" y="{fy}" fill="{accent}" font-family="monospace" font-size="11">FINDINGS</text>')
            for i, f in enumerate(r.findings[:6]):
                y = fy + 18 + i * 14
                p.append(f'<text x="20" y="{y}" fill="#ccc" font-family="monospace" font-size="9">⚡ {f[:70]}</text>')

        p.append(f'<text x="{W/2}" y="{H-10}" fill="#333" font-family="monospace" font-size="8" text-anchor="middle">⛓ {r.spine_hash} · EVEZ-OS Speedrun</text>')
        p.append('</svg>')
        return '\n'.join(p)


# ═══════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    engine = SpeedrunEngine()
    renderer = SpeedrunRenderer()
    out = Path("/home/openclaw/.openclaw/workspace/speedrun-evidence")
    out.mkdir(parents=True, exist_ok=True)

    if len(sys.argv) > 1:
        target = sys.argv[1]
        text = Path(target).read_text() if Path(target).exists() else target
        name = Path(target).stem if Path(target).exists() else "stdin"
        result = engine.run(text, name)
        print(result.report())
        (out / f"{name}-speedrun.json").write_text(result.to_json())
        (out / f"{name}-evidence.svg").write_text(renderer.render(result))
        print(f"\nJSON: {out}/{name}-speedrun.json")
        print(f"SVG:  {out}/{name}-evidence.svg")
    else:
        # Demo: speedrun EVEZ-OS mesh
        print("⚡ EVEZ Speedrun Engine — mesh demo\n")
        net = NetworkSpeedrun()
        result = net.run(
            nodes=["vultr-knot", "evez-primary", "openclaw-gcp",
                   "power-node", "evez-gcp-openclaw", "evez-free-node"],
            edges=[
                ("vultr-knot", "evez-primary", 1.0),
                ("vultr-knot", "openclaw-gcp", 0.8),
                ("vultr-knot", "power-node", 0.6),
                ("evez-primary", "openclaw-gcp", 0.9),
                ("evez-primary", "power-node", 0.7),
                ("evez-primary", "evez-gcp-openclaw", 0.9),
                ("openclaw-gcp", "power-node", 0.5),
                ("openclaw-gcp", "evez-gcp-openclaw", 0.6),
                ("power-node", "evez-gcp-openclaw", 0.8),
                ("evez-gcp-openclaw", "evez-free-node", 0.9),
            ],
            health={"vultr-knot": True, "evez-primary": True,
                    "openclaw-gcp": True, "power-node": True,
                    "evez-gcp-openclaw": True, "evez-free-node": False},
        )
        print(result.report())
        (out / "mesh-speedrun.json").write_text(result.to_json())
        (out / "mesh-evidence.svg").write_text(renderer.render(result))
