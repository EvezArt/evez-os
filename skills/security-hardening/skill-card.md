## Description: <br>
Security audit and hardening for AI agents covering credential hygiene, secret scanning, prompt injection defense, data leakage prevention, and privacy zones. <br>

This skill is for research and development only. <br>

## Publisher: <br>
[Clawdssen](https://clawhub.ai/user/Clawdssen) <br>

### License/Terms of Use: <br>
CC-BY-NC-4.0 <br>


## Use Case: <br>
Developers, engineers, and agent operators use this skill to inspect an agent workspace for leaked credentials, personal data, weak configuration, prompt injection exposure, and file exposure risks before sharing or operating the workspace. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Audit reports may contain secrets, personal data, or sensitive workspace details discovered during scanning. <br>
Mitigation: Request redacted findings, store reports in a private location, and avoid sharing audit output without review. <br>
Risk: The skill may propose configuration edits or recurring scans that change workspace behavior. <br>
Mitigation: Review proposed config changes before applying them and enable heartbeat or cron audits only when ongoing scans are intended. <br>
Risk: The audit depends on pattern-based checks and security guidance, so it cannot guarantee complete protection. <br>
Mitigation: Use it as one layer of review alongside organization security policies, credential rotation, and manual validation of high-severity findings. <br>


## Reference(s): <br>
- [Security Hardening - Advanced Patterns](references/advanced-patterns.md) <br>
- [ClawHub Skill Page](https://clawhub.ai/Clawdssen/security-hardening) <br>


## Skill Output: <br>
**Output Type(s):** [analysis, markdown, shell commands, configuration, guidance] <br>
**Output Format:** [Markdown reports with findings, remediation steps, checklists, and inline shell commands.] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [May propose configuration changes and periodic audit setup; review findings and proposed edits before applying them.] <br>

## Skill Version(s): <br>
1.0.0 (source: frontmatter and server-resolved release metadata) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
