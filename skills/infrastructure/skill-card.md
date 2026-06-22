## Description: <br>
Design, provision, and connect cloud resources across servers, networks, and services. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[ivangdavila](https://clawhub.ai/user/ivangdavila) <br>

### License/Terms of Use: <br>


## Use Case: <br>
Developers and engineers use this skill to plan infrastructure stages, compare cloud provider options, draft provisioning commands, and design backup and recovery workflows. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Generated cloud and backup commands can create, modify, restore, or delete infrastructure and data if run without review. <br>
Mitigation: Review commands before execution, use least-privilege cloud credentials, and test backup and restore flows in staging before touching production. <br>
Risk: Restore or retention commands can affect live databases, volumes, or backup history. <br>
Mitigation: Confirm retention rules and recovery targets before deleting old backups or running restore commands against live systems. <br>


## Reference(s): <br>
- [Architecture Patterns by Stage](patterns.md) <br>
- [Cloud Provider Reference](providers.md) <br>
- [Backup Strategies](backups.md) <br>


## Skill Output: <br>
**Output Type(s):** [guidance, markdown, shell commands, configuration] <br>
**Output Format:** [Markdown with inline shell and configuration snippets] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Produces user-reviewed infrastructure guidance and commands; it does not execute provisioning or store credentials.] <br>

## Skill Version(s): <br>
1.0.1 (source: frontmatter and server release metadata) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
