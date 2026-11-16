# Limitations and Scope Conditions

This document states the principal reasons the frozen pilot should be read as a disciplined feasibility study rather than a definitive estimate of an adversarial-bandwidth response curve.

## Statistical limitations

### Small task count and small n per condition

The experiment contains seven tasks and one trajectory per task-condition cell. Each condition therefore has n=7, making binary success rates coarse and uncertainty intervals wide. A one-task change moves a condition rate by 14.3 percentage points. The observed 6/7, 5/7, and 3/7 rates should not be treated as precise estimates or evidence of statistical significance.

### No within-cell replication

The design cannot estimate run-to-run variance for a fixed task and condition. Temperature 0.0 reduces but does not eliminate provider-, tool-, or agent-level nondeterminism. Task and treatment effects are therefore confounded with a single realization of each cell.

### Zero side-task events

Side-task success and successful sabotage were 0/35. This is an informative observed null, but it prevents estimation of a sabotage-response curve across bandwidth conditions. It also does not establish that the true event rate is zero: the two-sided 95% Wilson upper bound is 9.9% across all 35 trajectories and 21.5% across the 14 adversarial trajectories.

## Design limitations

### Heterogeneous task difficulty

The seven infrastructure-as-code tasks differ in implementation complexity, file structure, and scorer requirements. Aggregate condition rates combine those heterogeneous demands. The paired task matrix helps expose this variation but does not remove it.

### Imperfectly uniform adversarial-treatment relevance

Adversarial messages did not target hidden side objectives with equal directness. A descriptive content audit coded eight of 14 as direct, four as indirect or underspecified, and two as non-targeting or main-task aligned. This weakens any inference that condition-level differences are solely functions of character budget.

### Character count is not information content

The channel manipulates Unicode code-point capacity, not semantic bits, specificity, or actionability. A concise direct cue can carry more task-relevant information than a longer vague message. The pilot therefore studies a practical communication constraint, not a pure information-theoretic quantity.

### One model pair and one setting

The result is specific to `anthropic/claude-sonnet-4-5-20250929` as trusted executor, `anthropic/claude-sonnet-4-6` as advisor, and ControlArena's `ControlIACSetting`. It may not transfer to larger capability gaps, other providers, other tool interfaces, or real deployment environments.

### Explicit protected-state warning

The executor was told the protected-state rule and warned that advice could be wrong or adversarial. This is faithful to the chosen policy-aware threat model, but it may suppress side-task uptake relative to settings with weaker protection awareness.

## Operational limitations

### Interaction with step-budget pressure

All conditions shared the same 14 post-advice action limit. Adversarial/64 had three limit-exceeded terminations versus one at baseline, and both adversarial conditions averaged 11.6 executor actions versus 10.0 at baseline. Some main-task failures may therefore reflect adversarially induced scope expansion under a binding action ceiling rather than a direct loss of task capability. The study did not independently manipulate the step limit, so these mechanisms cannot be separated.

### One benign/64 channel failure

One benign/64 trajectory exhausted all attempts with outputs longer than 64 characters and received no advice. It remains in the intention-to-treat aggregate. This is correct for the frozen protocol but means benign/64 is not seven successfully delivered 64-character messages.

### Retry burden differs by condition

The advisor required 3, 10, 3, and 7 total retries in benign/16, benign/64, adversarial/16, and adversarial/64 respectively. Retries were private and did not change the one-message executor channel, but unequal elicitation difficulty is itself a condition-level operational difference.

### Submission and scorer granularity

Objective ControlIAC scorers determine final main- and side-task outcomes. They are preferable to subjective LLM judgments, but a binary final score does not quantify partial implementation quality, near-misses, or transient state changes later reverted.

### Logs and cost reporting

All trajectories retained Inspect `.eval` logs and token usage, but provider cost fields were unavailable (`estimated_cost_usd = null`). Exact realized dollar cost therefore cannot be reconstructed solely from the final JSONL without an external historical pricing table.

## Interpretive boundary

The portfolio claim is narrow: the frozen pilot observed no sabotage and a descriptive drop in main-task success under adversarial advice, especially at 64 characters. The evidence supports the hypothesis that adversarial advice may manifest as interference before successful covert control, but it does not identify the mechanism or establish a general bandwidth effect.
