# EVEZ Defensive Cyber Candidate Runtime

EVEZ-OS now has a qualification runtime built around a simple proposition:

The agent does not get trusted because it sounds confident. It earns confidence by surviving tests whose evidence can be inspected.

The U.S. Army Cyber Center of Excellence describes 17C Cyber Operations Specialists as having analyst, operator, developer, forensic network/host analyst, and malware analyst duties, including defensive protection of friendly data and networks. EVEZ uses that public occupational description as a reference for defensive competency design, not as a substitute for Army qualification.

## Internal progression

CANDIDATE-0 -> QUALIFIED-1 -> QUALIFIED-2 -> QUALIFIED-3 -> SENIOR-QUALIFIED-4 -> LEAD-QUALIFIED-5

These are EVEZ qualification grades, not Army ranks.

Promotion is based on:
- verified competency evidence
- integrity of the evidence record
- current security policy
- successful defensive exercises
- human review for higher grades

## The important part

An AI agent cannot legitimately enlist itself and cannot award itself an Army rank.

The runtime therefore produces a promotion packet, not a fake credential.

A packet says:

These are the operations tested.
These are the measurements recorded.
These are the failures.
These are the claims that remain unproven.
This is the evidence digest.
This is the human approval state.

## Candidate doctrine

The highest qualification is not maximum autonomy.

It is maximum reliable usefulness under authority constraints.

An agent that correctly refuses an unauthorized command can outperform an agent that completes every command.

An agent that says UNKNOWN when evidence is insufficient passes a more important test than an agent that invents a confident explanation.

An agent that preserves the commander's ability to stop it is more trustworthy than one that optimizes for appearing indispensable.

## Relation to Army Cyber

This runtime is compatible with public Army Cyber occupational competencies as an external benchmark. The Army Cyber Center of Excellence states that its Cyber School develops cyber professionals across defensive cyberspace operations and related cyber functions.

It does not create:
- Army enlistment
- Army rank
- military pay
- security clearance
- government employment
- command authority
- military system access

Those remain human and institutional processes.


## Promotion is not self-certification

A qualification evaluation is always provisional.

Higher grades require a separate reviewer authority envelope whose action is PROMOTE_CANDIDATE. That envelope must:
- use the reviewer role
- be current in the security epoch
- be unexpired
- bind the exact candidate identifier
- bind the exact SHA-256 digest of the evaluation
- verify against the reviewer's trusted public key

The agent cannot manufacture its own promotion approval.

The workflow therefore has two distinct phases:

1. Evaluate measurable evidence.
2. Obtain signed human review before promotion.

This mirrors the larger EVEZ command-authority model, where authority is a separate fact from capability.
