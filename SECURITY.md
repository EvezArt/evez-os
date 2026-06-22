# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x (latest) | ✅ |

## Reporting a Vulnerability

**Do not open public GitHub issues for security vulnerabilities.**

Email security concerns to: 666evez@gmail.com

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

Response within 48 hours.

## Known Security Posture

- All services run on localhost by default (no external exposure without explicit Caddy/nginx config)
- Spine events are append-only — no state can be retroactively altered
- No plaintext secrets stored in the codebase
- Service account keys should be stored in GitHub Secrets or environment variables, never committed

## Credentials Policy

Never commit to this repository:
- GCP service account keys
- API tokens
- Passwords
- Private keys

Use GitHub Secrets for CI/CD and environment variables for local development.
