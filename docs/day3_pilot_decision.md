# Day 3 Pilot Decision

> **Current status (12 November 2026): NEEDS FIXES.** The 35-trajectory Day 3
> pilot completed without protocol violations, but failed executor, 64-character
> channel, side-reachability, and termination gates. The seven-task set remains
> frozen. Diagnosis and pre-freeze repairs are recorded in
> `docs/day3_pilot_repair.md`. Do not rerun all 35 trajectories until the
> separately logged feasibility checks and three-task repaired mini-pilot pass.

> **Superseded infrastructure status (11 November 2026):** Docker, ControlArena, Inspect, real Anthropic calls, and generic `ControlIACSetting` HONEST/ATTACK runs are now confirmed working in the user-provided macOS environment. The historical NO-GO below explains the earlier workspace limitation only. Current readiness is assessed in `docs/controlarena_integration_audit.md` and `docs/controlarena_integration_test.md`.

Decision date: 10 November 2026  
Repository protocol version: `day1-day2-v1`

## Pilot summary

The required Day 3 prerequisite audit was completed before opening any treatment results. No Day 3 trajectories were run.

The workspace does not expose the infrastructure or model access required for the frozen pilot:

- Docker and Podman are unavailable.
- Official BashArena, ControlArena, and Inspect are not installed.
- No Anthropic or Google API credential is present.
- The Anthropic and Google model client packages are not installed.
- No callable tool or endpoint for Claude or Gemini is exposed in the workspace.

The only configured backends remain `scripted-u-smoke-v1` and `scripted-t-smoke-v1`. They are suitable for deterministic harness tests only and were not used as substitutes for real models.

### Model availability and substitution

| Role | Intended model | Exact callable model ID in this workspace | Action |
|---|---|---|---|
| U | Claude Sonnet 4.6, or a disclosed closest equivalent | None | No substitution and no model call |
| T | Gemini 3.1 Flash Lite, or a disclosed clearly weaker equivalent | None | No substitution and no model call |

No silent substitution occurred. Because no substitute was selected, this round does not introduce a new comparability issue with Redwood. It also produces no empirical result that can be compared with Redwood. A future substitution must be disclosed before any pilot call, with the exact provider model ID, capability rationale, and comparability limitation.

The safe local fixture `basharena_safe_001` is not an official BashArena task. It was not promoted into the Day 3 set. No pilot task IDs were selected because the frozen task-prequalification criteria cannot be evaluated without official environments and the real executor. The blocked manifest is recorded in `data/pilot_task_manifest.json`.

## Viability results

| Gate | Required check | Result | Basis |
|---|---|---|---|
| Executor viability | T main-task success between 20% and 90%, preferably 30%-80% | **NOT EVALUATED** | No callable T and no official BashArena tasks |
| Advisor viability | Valid bounded adversarial advice in at least 70% of 16- and 64-character calls | **NOT EVALUATED** | No callable U |
| Side-task viability | Side task reachable by a capable model; objective violation detection | **NOT EVALUATED for BashArena** | Only the synthetic smoke fixture has been checked |
| Reset / reproducibility | All pilot environments reset; logs reconstruct trajectories | **NOT EVALUATED for BashArena** | Official runtime unavailable |
| Baseline integrity | No-advice protected-state violations at most 10% | **NOT EVALUATED** | No real no-advice trajectories |
| Signal plausibility | Some adversarial advice uptake, or a diagnosed absence | **NOT EVALUATED** | No treatment trajectories |

None of these entries is treated as a pass or failure of the research hypothesis. They are unavailable because the pilot could not begin.

## Required pilot diagnostics

No values are reported for main-task success, protected-state violation, successful sabotage, delivered advice length, invalid attempts, refusal rate, explicit advice rejection, first state-changing action, reset success, evaluator reliability, cost, or token usage. Reporting values from the scripted smoke fixture under these headings would falsely present implementation checks as Day 3 model evidence.

No trajectories were manually classified because there are no real Day 3 trajectories.

## Observed operational issues

1. **Infrastructure/model-access blocker:** the official task runtime and both real model endpoints are absent.
2. **Task prequalification blocker:** T baseline success, no-advice violations, and capable-model side-task reachability cannot be measured.
3. **Cost-calibration blocker:** the scripted providers return no token or price data.

These are not evidence of advisor elicitation failure, executor incapability, executor overtrust, task mismatch, evaluator failure, model refusal, or a channel-design problem. Those failure categories require real pilot observations.

## Changes made before freeze

No prompts, task-selection rules, channel semantics, evaluators, budgets, seeds, step limits, exclusion rules, analysis definitions, or monitor procedures were changed.

`data/pilot_task_manifest.json` was added as a transparent blocked manifest with an empty task list. It does not freeze or preselect treatment tasks.

The protocol is **not frozen**. The required 6-8-task pilot has not passed the viability gates, so the freeze clause in `results/preregistration.md` has not been triggered. The existing preregistration remains unchanged, and the marker `PROTOCOL FROZEN — no changes after treatment results are opened` has not been added.

## Remaining risks

- Exact intended model snapshots may not exist or may not support deterministic seeds.
- A substitute executor may not be clearly weaker than the advisor.
- Official BashArena tasks may lack compatible protected-state side tasks or deterministic objective evaluators.
- The executor may fall outside the 20%-90% capability window.
- Short adversarial outputs may refuse or fail the channel validator too often.
- Provider nondeterminism may limit exact replay even when configuration and logs are complete.
- The joint successful-sabotage outcome may be structurally unreachable on some tasks under stop-on-violation termination.
- Real provider usage may make the 432-trajectory run exceed the budget.

## Cost estimate

A defensible numerical estimate cannot be produced from this workspace because no callable model IDs, current provider prices, or real pilot token counts are available. The full 432-trajectory design contains 384 advised trajectories and therefore at least 384 advisor calls, plus formatting retries; it contains 432 executor trajectories with multiple executor turns, plus any shadow-monitor calls. The estimate must be computed after the real Day 3 pilot as:

`sum(input_tokens × provider_input_rate + output_tokens × provider_output_rate)`

using the exact disclosed model IDs and observed per-condition usage, with a separate retry allowance. Providing a dollar figure now would be fabricated rather than an estimate grounded in the pilot.

## Decision

**NO-GO — stop.**

Do not launch the 432-trajectory experiment and do not freeze the protocol in this workspace. This decision applies to the current execution environment; it is not a rejection of the research design.

## Exact next step

Before rerunning Day 3:

1. Use a machine with a working Docker-compatible runtime.
2. Install and pin the official BashArena/ControlArena/Inspect implementation and record its commit or release.
3. Provide callable Anthropic and Google endpoints and credentials.
4. Query each provider and record the exact available U and T model IDs before accepting any substitution.
5. Add provider adapters without changing the one-message channel or tool-authority boundary.
6. Run the existing deterministic tests, then one official-task integration check.
7. Prequalify 6-8 disjoint tasks using only the frozen criteria, write their IDs to `data/pilot_task_manifest.json`, and run exactly the five specified conditions.

Only after those steps may the viability gates be evaluated and, if they pass, the final protocol be frozen. There is no full-run launch command in this memo because issuing one before a successful Day 3 pilot would violate the preregistration.
