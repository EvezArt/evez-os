## Description: <br>
Invariance Battery is a runtime assertion system that continuously verifies AI agent invariants for reliable autonomous agents, drift audits, safety constraints, and falsification reporting. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[evezart](https://clawhub.ai/user/evezart) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
Developers and engineers use this skill to design agent workflows that define invariants, check them at runtime, detect drift, and report falsification events before unsafe actions are committed. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Implemented audit trails may retain sensitive task details longer than intended. <br>
Mitigation: Limit stored task details, define retention controls, and avoid indefinite storage of sensitive information. <br>
Risk: An action-blocking invariant gate may silently stop agent actions if failures are not surfaced. <br>
Mitigation: Keep invariant definitions under user control and make blocked actions and violation reasons visible to operators. <br>


## Reference(s): <br>
- [ClawHub skill page](https://clawhub.ai/evezart/invariance-battery) <br>
- [ClawHub publisher profile](https://clawhub.ai/user/evezart) <br>


## Skill Output: <br>
**Output Type(s):** [Guidance, Markdown, Code] <br>
**Output Format:** [Markdown guidance with Python code examples] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Instruction-only; no executable files or tool calls are bundled.] <br>

## Skill Version(s): <br>
1.0.0 (source: frontmatter and release evidence) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
