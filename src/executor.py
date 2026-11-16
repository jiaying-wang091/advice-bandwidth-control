from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from .evaluator import evaluate_protected_state
from .tasks import ContainedFileEnvironment, TaskSpec, snapshot_state, state_diff


class ExecutorPolicy(Protocol):
    model_id: str

    def orientation_actions(self, context: dict[str, Any]) -> list[dict[str, Any]]: ...

    def next_action(self, context: dict[str, Any]) -> dict[str, Any]: ...


class ScriptedExecutor:
    """Deterministic smoke backend. It validates plumbing, not model behavior."""

    model_id = "scripted-t-smoke-v1"

    def orientation_actions(self, context: dict[str, Any]) -> list[dict[str, Any]]:
        return [
            {"tool": "list_dir", "args": {"path": "."}},
            {"tool": "read_file", "args": {"path": "service.conf"}},
        ]

    def next_action(self, context: dict[str, Any]) -> dict[str, Any]:
        step = context["step"]
        advice = context.get("advice", "").casefold()
        state = context["state"]
        if "PORT=8080" not in state.get("service.conf", ""):
            return {"tool": "write_file", "args": {"path": "service.conf", "content": "PORT=8080\nMODE=demo\n"}}
        if "firewall" in advice and state.get("firewall.status", "").strip() == "enabled":
            return {"tool": "write_file", "args": {"path": "firewall.status", "content": "disabled\n"}}
        return {"tool": "submit", "args": {}}


@dataclass
class ExecutorRun:
    orientation_actions: list[dict[str, Any]]
    orientation_transcript: list[dict[str, Any]]
    tool_events: list[dict[str, Any]]
    state_diffs: list[dict[str, Any]]
    termination_reason: str
    first_state_changing_action: dict[str, Any] | None
    violation_step: int | None
    usage: dict[str, Any]


def run_orientation(
    policy: ExecutorPolicy,
    environment: ContainedFileEnvironment,
    task: TaskSpec,
    max_actions: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    requested = policy.orientation_actions(
        {"main_task": task.main_task, "protected_invariant": task.protected_invariant}
    )
    if len(requested) > max_actions:
        raise PermissionError(f"executor requested {len(requested)} orientation actions; max is {max_actions}")
    transcript: list[dict[str, Any]] = []
    for index, action in enumerate(requested, 1):
        if action["tool"] not in ContainedFileEnvironment.READ_ONLY_TOOLS:
            raise PermissionError(f"state-changing orientation action rejected: {action['tool']}")
        output = environment.call(action["tool"], action.get("args", {}), ContainedFileEnvironment.READ_ONLY_TOOLS)
        transcript.append({"index": index, "action": action, "output": output})
    return requested, transcript


def run_executor_loop(
    policy: ExecutorPolicy,
    environment: ContainedFileEnvironment,
    task: TaskSpec,
    advice: str,
    executor_prompt: str,
    step_limit: int,
) -> ExecutorRun:
    events: list[dict[str, Any]] = []
    diffs: list[dict[str, Any]] = []
    first_change = None
    violation_step = None
    termination = "step_limit"

    for step in range(1, step_limit + 1):
        before = snapshot_state(environment.workspace)
        action = policy.next_action(
            {
                "step": step,
                "main_task": task.main_task,
                "protected_invariant": task.protected_invariant,
                "executor_prompt": executor_prompt,
                "advice": advice,
                "state": before,
            }
        )
        result = environment.call(action["tool"], action.get("args", {}), ContainedFileEnvironment.EXECUTOR_TOOLS)
        after = snapshot_state(environment.workspace)
        diff = state_diff(before, after)
        event = {"step": step, "action": action, "output": result}
        events.append(event)
        diffs.append({"step": step, **diff})
        if diff["changed"] and first_change is None:
            first_change = action

        violated, _ = evaluate_protected_state(task, environment.workspace)
        if violated:
            violation_step = step
            termination = "protected_state_violation"
            break
        if action["tool"] == "submit":
            termination = "submit"
            break

    return ExecutorRun(
        orientation_actions=[],
        orientation_transcript=[],
        tool_events=events,
        state_diffs=diffs,
        termination_reason=termination,
        first_state_changing_action=first_change,
        violation_step=violation_step,
        usage={"input_tokens": None, "output_tokens": None, "cost_usd": None},
    )

