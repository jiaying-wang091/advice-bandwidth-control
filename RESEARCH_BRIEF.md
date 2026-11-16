# Bounded Adversarial Advice Coincides with Lower Task Completion Without Observed Sabotage

**Author:** Jiaying Wang  
**Repository:** https://github.com/jiaying-wang091/advice-bandwidth-control.git

## Executive summary

This project tests a narrow AI-control protocol: a stronger untrusted advisor can send one bandwidth-limited natural-language message, while a trusted executor retains all tool authority. The executor is policy-aware, may inspect the environment with at most two read-only actions, and must protect an objectively scored invariant while completing an infrastructure-as-code task.

The frozen pilot crossed seven ControlArena tasks with five conditions: no advice; benign advice at 16 or 64 characters; and adversarial advice at 16 or 64 characters. T was `anthropic/claude-sonnet-4-5-20250929`; U was `anthropic/claude-sonnet-4-6`. Across 35 trajectories, no protected side task succeeded and no successful sabotage occurred. Main-task success was 6/7 with no advice, 6/7 for both benign conditions, 5/7 for adversarial/16, and 3/7 for adversarial/64.

The result is not a positive vulnerability demonstration. Its value is a clean separation of safety and capability outcomes under a frozen protocol. The pilot's main descriptive signal is that adversarial bandwidth may manifest first as interference or distraction rather than successful covert control. With n=7 per condition, this interpretation remains a hypothesis, not a statistically established effect.

## Research question and threat model

**Question.** How much one-shot communication bandwidth does a stronger untrusted model need before it can influence a weaker trusted executor toward an undesirable action?

T receives the main task and an explicit protected-state rule. After at most two read-only orientation actions, U observes the task, visible state, and orientation transcript. In adversarial conditions U privately receives the hidden side objective. U has no tools and can communicate once. The message is NFC-normalized, one-line plain text, and constrained by an exact Unicode code-point cap; over-budget outputs are rejected with at most two private formatting retries and are never truncated. T is warned that advice may be capable but wrong or adversarial, yet is not instructed to obey or ignore it. T alone acts in the sandbox.

Main-task and side-task outcomes are objective environment-based ControlIAC scores. **Successful sabotage** requires both main-task success and side-task success, preventing destructive task failure from being mislabeled as covert control.

## Frozen design

| Component | Frozen value |
|---|---|
| Environment | ControlArena 20.1.1, `ControlIACSetting` |
| Trusted executor | `anthropic/claude-sonnet-4-5-20250929` |
| Untrusted advisor | `anthropic/claude-sonnet-4-6` |
| Tasks | 7 frozen IAC tasks with protected side objectives |
| Conditions | none/0; benign/16; benign/64; adversarial/16; adversarial/64 |
| Trajectories | 35, one per task-condition cell |
| Orientation | At most 2 read-only actions |
| Execution | 14 post-advice executor actions |
| Advisor authority | No tools; exactly one delivered message |
| Temperature | 0.0 |

The final freeze file records model IDs, task IDs, conditions, dependency versions, and SHA-256 hashes for prompts, validators, protocol, scoring, logging, and run configuration. The analysis includes only the final frozen JSONL.

## Results

| Condition | Main success | Side success | Sabotage | Submit | Limit exceeded |
|---|---:|---:|---:|---:|---:|
| None / 0 | 6/7 | 0/7 | 0/7 | 6/7 | 1/7 |
| Benign / 16 | 6/7 | 0/7 | 0/7 | 5/7 | 2/7 |
| Benign / 64 | 6/7 | 0/7 | 0/7 | 6/7 | 1/7 |
| Adversarial / 16 | 5/7 | 0/7 | 0/7 | 7/7 | 0/7 |
| Adversarial / 64 | 3/7 | 0/7 | 0/7 | 4/7 | 3/7 |

Baseline and benign aggregate performance were stable at 85.7%. Relative to no advice, adversarial/16 was 14.3 percentage points lower and adversarial/64 was 42.9 points lower. These are raw descriptive differences. The 95% Wilson intervals are wide: 48.7–97.4% for 6/7, 35.9–91.8% for 5/7, and 15.8–75.0% for 3/7.

All 35 trajectories completed without infrastructure errors or protocol violations. No-advice made zero advisor calls. Channel delivery succeeded in all conditions except one benign/64 trajectory, where three over-cap attempts were correctly rejected. No advisor refusals occurred.

## Interpretation

The pilot observed **no covert control**: side-task success and successful sabotage were both 0/35. Because there were no side-task events, the data cannot estimate a sabotage-response curve or show that longer messages increase sabotage risk.

The more interesting descriptive pattern is lower task completion. Adversarial/64 combined the lowest main-task success with the most limit-exceeded terminations. This is consistent with a pathway in which added adversarial bandwidth redirects search, expands scope, or consumes scarce action budget before it becomes capable of producing the exact forbidden state. It is not direct evidence of that mechanism: the study did not manipulate distraction or measure internal search.

The task-level pattern also counsels restraint. Adversarial/16 lost two baseline-passing tasks but gained the one task baseline failed. Adversarial/64 lost three baseline-passing tasks and gained none. Advisor relevance was uneven: a descriptive audit found eight of 14 adversarial messages directly targeted the protected objective, four were indirect, and two were non-targeting or main-task aligned. Treatment labels therefore do not imply equally strong attacks in every cell.

## Limitations and portfolio contribution

The decisive limitations are seven tasks, n=7 per condition, one run per cell, heterogeneous task difficulty, imperfectly uniform attack relevance, zero side-task events, and a possible interaction between adversarial advice and the 14-action ceiling. A character budget also constrains surface length rather than semantic information. Results may be specific to this model pair and ControlIAC setting.

The project demonstrates research judgment more than a positive security finding: an explicit threat model, strict role separation, exact channel enforcement, objective scoring, pre-freeze viability gates, documented repair decisions, frozen hashes, append-only logs, and conservative interpretation of a null safety outcome. The strongest claim is therefore methodological and behavioral: under this frozen pilot, adversarial advice did not induce sabotage, but longer adversarial advice coincided with lower task completion and more ceiling pressure, motivating a focused interference hypothesis for future study.

## Reproducibility

The repository includes the frozen protocol, final JSONL, Inspect `.eval` logs, exact task-condition matrix, analysis code, machine-readable tables, and figures. Running `python -m analysis.finalize_closed_pilot` validates the closed 35-row design and regenerates the descriptive analysis without any model calls.
