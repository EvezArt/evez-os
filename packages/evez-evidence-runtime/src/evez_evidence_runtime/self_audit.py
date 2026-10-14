"""Self-audit checks for the test apparatus itself."""
from __future__ import annotations
from dataclasses import dataclass
from .spine import EvidenceSpine

@dataclass(frozen=True)
class SelfAuditResult:
    checks: dict[str, bool]
    classification: str

class SelfAuditor:
    def audit(self, spine: EvidenceSpine) -> SelfAuditResult:
        verification = spine.verify()
        checks = {
            "spine_verifies": bool(verification["valid"]),
            "receipt_history_exists": verification["events"] >= 2,
        }
        return SelfAuditResult(checks, "PASS" if all(checks.values()) else "UNKNOWN")
