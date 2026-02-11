# Claude 4.6 Handoff

Use this repo as source of truth. Priorities:
1. Preserve strict schema and leakage invariants.
2. Keep deterministic behavior.
3. Do not loosen disjointness assertions.
4. Maintain train-only normalization fit.
5. Keep config strict (extra='forbid').

When proposing edits, return:
- exact changed files
- why each change is required
- risk level
- tests impacted
