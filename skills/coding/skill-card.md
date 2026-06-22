## Description: <br>
Coding style memory that adapts to your preferences, conventions, and patterns for consistent coding. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[ivangdavila](https://clawhub.ai/user/ivangdavila) <br>

### License/Terms of Use: <br>


## Use Case: <br>
Developers and coding agents use this skill to remember explicitly confirmed coding preferences and apply them consistently in future coding work. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Persistent local preference records may retain outdated or sensitive coding preferences. <br>
Mitigation: Only save preferences after explicit confirmation, review ~/coding/memory.md periodically, and use the forget or edit flow to remove entries. <br>
Risk: Incorrectly inferred preferences could change future coding guidance without user intent. <br>
Mitigation: Do not infer from project files, silence, or coding patterns; store only preferences the user explicitly confirms. <br>


## Reference(s): <br>
- [ClawHub skill page](https://clawhub.ai/ivangdavila/coding) <br>
- [Skill homepage](https://clawic.com/skills/coding) <br>
- [Preference criteria](artifact/criteria.md) <br>
- [Preference dimensions](artifact/dimensions.md) <br>
- [Memory template](artifact/memory-template.md) <br>


## Skill Output: <br>
**Output Type(s):** [text, markdown, shell commands, guidance] <br>
**Output Format:** [Markdown or plain text guidance with optional shell commands and local markdown memory entries] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Stores only user-confirmed coding preferences in local markdown files under ~/coding/.] <br>

## Skill Version(s): <br>
1.0.3 (source: server release and frontmatter) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
