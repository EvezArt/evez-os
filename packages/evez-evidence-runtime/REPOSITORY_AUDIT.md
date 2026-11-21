# Repository Self-Audit

This document records findings discovered by applying the EVEZ evidence philosophy to the repository itself.

## EA-001 — Invariant expression execution boundary

Status: PATCHED on this branch.

The historical Invariance Battery accepted expressions through its HTTP assertion interface and evaluated them with Python eval(). The restricted globals dictionary did not change the fact that the assertion language was an execution boundary.

Remediation: replace dynamic evaluation with an explicit AST interpreter and add regression tests against eval() and exec().

Evidence class:
- OBSERVED: eval() exists in the historical implementation.
- PATCHED: active branch uses an explicit interpreter.
- UNKNOWN: whether the service was externally reachable at the time.
- UNKNOWN: whether the condition was ever exploited.

## EA-002 — Unauthenticated healing control

Status: PATCHED on this branch.

The Mesh Health service exposes POST /heal and can restart sibling services. The service is bound to all interfaces in the historical implementation. The healing operation was not authenticated.

Remediation: the healing endpoint is local-only on the active branch.

Evidence class:
- OBSERVED: /heal triggers heal_sibling()/heal_all().
- OBSERVED: sibling services can be restarted through systemd or a direct Python fallback.
- PATCHED: non-loopback clients receive HTTP 403.
- UNKNOWN: historical network exposure.

This is an availability/control-plane issue, not proof of successful compromise.

## EA-003 — Shell execution in healing fallback

Status: PATCHED on this branch.

The historical fallback used subprocess.run(..., shell=True) for a fuser command. The port came from a registry lookup, which reduces practical injection surface, but shell interpretation was unnecessary.

Remediation: pass the executable and arguments as an argv list.

## EA-004 — Repository-contained runtime credential

Status: REMEDIATED in this branch.

The historical docker-compose configuration contained a non-placeholder default OpenClaw gateway token in source control.

Remediation: the default secret is removed and the compose configuration requires the value from the environment. Telegram bot token and chat ID values are also moved to environment interpolation.

Important limitation: removing a secret from the current branch does not revoke a credential that may have been exposed in Git history. Credential rotation must occur at the provider or service boundary.

The actual secret is intentionally not reproduced in this document.

## EA-005 — Precision claims without executable evidence

Status: DOCUMENTATION PATCHED on this branch.

The repository README previously presented exact emergence values and historical event counts as current status. The repository evidence layer did not establish those figures as reproducible measurements.

Remediation: README now labels historical precision claims as evidence-gated and states:

DECLARED != EFFECTIVE

CLAIMED != MEASURED != REPLICATED != EXPLAINED

PROVENANCE != TRUTH

## What remains unknown

This repository audit does not establish:
- that any historical credential was used by an unauthorized party;
- that the healing endpoint was reachable from the public internet;
- that any reported emergence value was fabricated rather than merely undocumented;
- that every deployment documented in the repository still exists.

Unknown is retained as a result rather than converted into a narrative.
