## Description: <br>
Automation Workflow Builder designs and executes cross-platform automation workflows with triggers, conditions, and multi-step actions. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[careytian-ai](https://clawhub.ai/user/careytian-ai) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
Developers, operations teams, and business users use this skill to define repeatable workflows for data synchronization, content publishing, report generation, monitoring alerts, and file-based automation. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Generated workflows may run shell commands, move or overwrite files, upload data, post publicly, or send messages with broad permissions. <br>
Mitigation: Review each workflow before execution, keep it scoped to a specific workspace, and require explicit approval for shell commands, file writes, uploads, public posting, and messaging. <br>
Risk: Unauthenticated webhooks or recurring jobs can execute unexpectedly or continue after they are no longer needed. <br>
Mitigation: Use authenticated triggers, document how to disable each recurring job, and avoid unattended schedules unless the owner and rollback path are clear. <br>


## Reference(s): <br>
- [ClawHub skill page](https://clawhub.ai/careytian-ai/automation-workflow-builder) <br>
- [Publisher profile](https://clawhub.ai/user/careytian-ai) <br>
- [Skill source documentation](artifact/SKILL.md) <br>
- [Release changelog](artifact/CHANGELOG.md) <br>


## Skill Output: <br>
**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance] <br>
**Output Format:** [Markdown with structured workflow examples and inline code blocks] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [May propose scheduled jobs, file operations, network requests, notifications, and command execution steps for review before use.] <br>

## Skill Version(s): <br>
1.0.0 (source: release metadata, config.json, metadata.json, and changelog, released 2026-03-29) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
