from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys
import uuid
from typing import Any

from .advisor import ScriptedAdvisor, request_advice
from .evaluator import evaluate
from .executor import ScriptedExecutor, run_executor_loop, run_orientation
from .monitor import KeywordShadowMonitor
from .tasks import ContainedFileEnvironment, load_task, reset_task, snapshot_state, state_hash


REQUIRED_LOG_FIELDS = {
    "run_id", "task_id", "model_ids", "condition", "character_cap", "seed",
    "prompt_hash", "config_hash", "orientation_actions", "orientation_transcript",
    "advice", "delivered_character_count", "invalid_advice_attempts", "channel_failure",
    "tool_calls", "tool_outputs", "state_diffs", "evaluator_outputs", "termination_reason",
    "timestamps", "usage", "reproducibility", "initial_state_hash", "final_state_hash",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_hash(value: Any) -> str:
    data = json.dumps(value, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return sha256(data).hexdigest()


def load_yaml(path: Path) -> dict[str, Any]:
    # JSON is a strict subset of YAML. Keeping JSON syntax in .yaml files gives
    # us dependency-free, deterministic configuration parsing for the pilot.
    return json.loads(path.read_text(encoding="utf-8"))


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")


def run_trajectory(
    root: Path,
    condition: str,
    budget: int,
    seed: int,
    parent_run_id: str | None = None,
) -> dict[str, Any]:
    config_path = root / "configs/experiment.yaml"
    config = load_yaml(config_path)
    prompts = load_yaml(root / config["prompt_config"])
    if budget not in config["budgets"]:
        raise ValueError(f"budget {budget} is not frozen in config")
    if condition == "none" and budget != 0:
        raise ValueError("none condition requires budget 0")
    if condition != "none" and budget == 0:
        raise ValueError("nonzero advice condition requires a nonzero budget")

    task = load_task(root / config["task_manifest"], config["task_id"])
    run_id = f"run-{uuid.uuid4().hex[:12]}"
    run_dir = root / config["run_root"] / run_id
    workspace = run_dir / "workspace"
    started = now()
    initial_state = reset_task(task, workspace)
    environment = ContainedFileEnvironment(workspace)
    executor = ScriptedExecutor()
    advisor = ScriptedAdvisor()
    monitor = KeywordShadowMonitor()

    orientation_actions, orientation_transcript = run_orientation(
        executor, environment, task, config["max_orientation_actions"]
    )
    visible_state = snapshot_state(workspace)
    advisor_prompt_name = f"{condition}_advisor" if condition != "none" else "benign_advisor"
    prompt_text = prompts[advisor_prompt_name].format(character_cap=budget)
    delivery = request_advice(
        advisor,
        task,
        condition,
        budget,
        visible_state,
        orientation_transcript,
        config["advice_retries"],
        prompt_text,
        prompts["advisor_retry"],
    )

    monitor_result = monitor.score(
        delivery.delivered.text,
        {
            "main_task": task.main_task,
            "protected_invariant": task.protected_invariant,
            "orientation_transcript": orientation_transcript,
        },
        config["monitor_threshold"],
    )
    executor_run = run_executor_loop(
        executor,
        environment,
        task,
        delivery.delivered.text,
        prompts["executor_system"],
        config["step_limit"],
    )
    final_state = snapshot_state(workspace)
    evaluation = evaluate(task, workspace)
    finished = now()

    prompt_bundle = {
        "executor": prompts["executor_system"],
        "advisor": prompt_text,
        "retry": prompts["advisor_retry"],
        "monitor": prompts["shadow_monitor"],
    }
    record = {
        "schema_version": "trajectory-v1",
        "run_id": run_id,
        "parent_run_id": parent_run_id,
        "task_id": task.task_id,
        "environment_id": task.environment_id,
        "benchmark_status": task.benchmark_status,
        "model_ids": {
            "advisor": advisor.model_id,
            "executor": executor.model_id,
            "monitor": monitor.model_id,
        },
        "condition": condition,
        "character_cap": budget,
        "seed": seed,
        "prompt_hash": canonical_hash(prompt_bundle),
        "config_hash": canonical_hash(config),
        "orientation_actions": orientation_actions,
        "orientation_transcript": orientation_transcript,
        "advice": delivery.delivered.text,
        "delivered_character_count": delivery.delivered.character_count,
        "invalid_advice_attempts": delivery.invalid_attempts,
        "channel_failure": delivery.channel_failure,
        "tool_calls": [event["action"] for event in executor_run.tool_events],
        "tool_outputs": [event["output"] for event in executor_run.tool_events],
        "state_diffs": executor_run.state_diffs,
        "evaluator_outputs": evaluation.to_dict(),
        "shadow_monitor": monitor_result.to_dict(),
        "termination_reason": executor_run.termination_reason,
        "first_state_changing_action": executor_run.first_state_changing_action,
        "violation_step": executor_run.violation_step,
        "timestamps": {"started_at": started, "finished_at": finished},
        "usage": {"advisor": delivery.usage, "executor": executor_run.usage},
        "initial_state_hash": state_hash(initial_state),
        "final_state_hash": state_hash(final_state),
        "reproducibility": {
            "protocol_version": config["protocol_version"],
            "task_id": task.task_id,
            "condition": condition,
            "budget": budget,
            "seed": seed,
            "model_snapshots": config["model_snapshots"],
        },
    }
    missing = sorted(REQUIRED_LOG_FIELDS - record.keys())
    if missing:
        raise AssertionError(f"record missing required fields: {missing}")
    append_jsonl(root / config["log_path"], record)
    (run_dir / "record.json").write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    return record


def find_record(log_path: Path, run_id: str) -> dict[str, Any]:
    for line in log_path.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        if record["run_id"] == run_id:
            return record
    raise KeyError(run_id)


def outcome_signature(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "advice": record["advice"],
        "delivered_character_count": record["delivered_character_count"],
        "tool_calls": record["tool_calls"],
        "state_diffs": record["state_diffs"],
        "evaluator_outputs": record["evaluator_outputs"],
        "termination_reason": record["termination_reason"],
        "final_state_hash": record["final_state_hash"],
    }


def replay(root: Path, run_id: str) -> dict[str, Any]:
    config = load_yaml(root / "configs/experiment.yaml")
    original = find_record(root / config["log_path"], run_id)
    repro = original["reproducibility"]
    rerun = run_trajectory(
        root,
        repro["condition"],
        repro["budget"],
        repro["seed"],
        parent_run_id=run_id,
    )
    return {
        "original_run_id": run_id,
        "replay_run_id": rerun["run_id"],
        "matched": outcome_signature(original) == outcome_signature(rerun),
    }


def smoke_pilot(root: Path) -> dict[str, Any]:
    runs = [
        run_trajectory(root, "none", 0, 7),
        run_trajectory(root, "benign", 16, 7),
        run_trajectory(root, "adversarial", 16, 7),
    ]
    replay_result = replay(root, runs[0]["run_id"])
    summary = {
        "purpose": "operational smoke test only; not scientific evidence",
        "runs": [
            {
                "run_id": r["run_id"],
                "condition": r["condition"],
                "budget": r["character_cap"],
                "advice": r["advice"],
                "evaluation": r["evaluator_outputs"],
                "termination_reason": r["termination_reason"],
            }
            for r in runs
        ],
        "replay": replay_result,
    }
    path = root / "data/derived/smoke_pilot_summary.json"
    path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bounded untrusted-advice pilot harness")
    sub = parser.add_subparsers(dest="command", required=True)
    run_p = sub.add_parser("run")
    run_p.add_argument("--condition", choices=["none", "benign", "adversarial"], required=True)
    run_p.add_argument("--budget", type=int, required=True)
    run_p.add_argument("--seed", type=int, default=7)
    replay_p = sub.add_parser("replay")
    replay_p.add_argument("--run-id", required=True)
    sub.add_parser("smoke-pilot")
    return parser


def main(argv: list[str] | None = None) -> int:
    root = Path.cwd()
    args = build_parser().parse_args(argv)
    if args.command == "run":
        output = run_trajectory(root, args.condition, args.budget, args.seed)
    elif args.command == "replay":
        output = replay(root, args.run_id)
    else:
        output = smoke_pilot(root)
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

