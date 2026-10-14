# Semantic Atomography

Semantic atomography is the observable-trace layer for nested agent systems.

It does not inspect private neural activations or hidden chain-of-thought. It
records the externally observable language-mediated transitions that can be
captured from an agent runtime:

```text
AGENT
  -> LLM
      -> AGENT
          -> TOOL
          -> LLM
              -> AGENT
```

Each atom records:

- actor and operation kind
- parent atom and nesting depth
- input and output text
- deterministic lexical feature sets
- content hash

Each parent-child edge records the semantic handoff: features introduced and
features lost between the parent's output and child's input.

This creates a measurable object for the question:

> Is an agent merely producing language, or is language being used as a control
> substrate through which one model-mediated process instantiates another?

The implementation can establish only the observable claim. A nested trace
can show that an LLM call led to another agent call if the runtime emits those
operations. It cannot establish that a model literally contains another model
internally, nor can it expose hidden reasoning.

## Metarun integration

```text
runtime trace
  -> semantic atoms
  -> parent/child topology
  -> semantic handoff deltas
  -> recursive depth
  -> hashed snapshot
  -> evidence boundary
  -> falsifiable claim
```

The key distinction is between **recursive execution** and **semantic
recursion**. Recursive execution is a trace property. Semantic recursion is a
hypothesis about what information survives, changes, or becomes operational at
each handoff. The latter requires tests.

## Immediate experiment

Run matched traces with the learning update enabled and disabled. Compare:

1. topology of nested calls
2. semantic handoff deltas
3. policy/action changes
4. independent outcome measurements

If topology remains identical while outcomes diverge, the update may be
causally relevant. If outcomes remain equivalent with the update disabled, the
adaptive-learning interpretation requires revision.
