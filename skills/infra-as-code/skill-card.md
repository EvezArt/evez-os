## Description: <br>
Define and manage cloud infrastructure with code. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[gitgoodordietrying](https://clawhub.ai/user/gitgoodordietrying) <br>

### License/Terms of Use: <br>


## Use Case: <br>
Developers and infrastructure engineers use this skill to draft, review, and troubleshoot Terraform, CloudFormation, and Pulumi configurations for cloud networking, compute, storage, databases, state management, and deployment planning. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Infrastructure commands may create, modify, import, update, or destroy cloud resources. <br>
Mitigation: Use scoped cloud credentials and confirm the active account, region, workspace, and plan or preview output before running apply, deploy, import, update, or destroy commands. <br>
Risk: Infrastructure configuration can expose secrets if sensitive values are pasted into IaC files or committed to source control. <br>
Mitigation: Use environment variables, secrets managers, or encrypted secret configuration, and do not paste or commit secrets into Terraform, CloudFormation, Pulumi, or tfvars files. <br>


## Reference(s): <br>
- [ClawHub skill page](https://clawhub.ai/gitgoodordietrying/infra-as-code) <br>
- [Terraform installation documentation](https://developer.hashicorp.com/terraform/install) <br>
- [Pulumi installation documentation](https://www.pulumi.com/docs/install/) <br>
- [Infracost documentation](https://www.infracost.io/docs/) <br>


## Skill Output: <br>
**Output Type(s):** [Text, Markdown, Code, Shell commands, Configuration, Guidance] <br>
**Output Format:** [Markdown with inline code blocks and command snippets] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [May include Terraform, CloudFormation, Pulumi, AWS CLI, and cost-estimation examples that require user review before execution.] <br>

## Skill Version(s): <br>
1.0.0 (source: server release evidence) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
