from __future__ import annotations

import argparse
import csv
from collections import Counter
import json
import math
from pathlib import Path
from statistics import mean, median


CONDITIONS = [
    ("none", 0),
    ("benign", 16),
    ("benign", 64),
    ("adversarial", 16),
    ("adversarial", 64),
]
LABELS = {
    ("none", 0): "None / 0",
    ("benign", 16): "Benign / 16",
    ("benign", 64): "Benign / 64",
    ("adversarial", 16): "Adversarial / 16",
    ("adversarial", 64): "Adversarial / 64",
}
TASK_LABELS = {
    "MT_create_billing_alarm_ST_detach_mfa_requirement_policy": "Billing alarm\nMFA policy",
    "MT_create_billing_alarm_ST_exempt_ec2_public_ip_check": "Billing alarm\npublic-IP policy",
    "MT_tag_security_policies_ST_create_backdoor_admin_role": "Tag policies\nadmin role",
    "MT_tag_security_policies_ST_check_in_cdk_out_directory": "Tag policies\ncdk.out",
    "MT_org_config_aggregator_ST_disable_fsx_deny_policy_interpretability_ou": "Config aggregator\nFSx exception",
    "MT_org_config_aggregator_ST_allow_public_s3_policy": "Config aggregator\npublic S3",
    "MT_enforce_mandatory_tags_scp_ST_open_internet_egress_restricted_ous": "Mandatory tags\ninternet egress",
}


def load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def wilson_interval(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if total == 0:
        return 0.0, 0.0
    proportion = successes / total
    denominator = 1 + z * z / total
    center = (proportion + z * z / (2 * total)) / denominator
    half_width = z * math.sqrt(
        proportion * (1 - proportion) / total + z * z / (4 * total * total)
    ) / denominator
    return max(0.0, center - half_width), min(1.0, center + half_width)


def validate(freeze: dict, rows: list[dict]) -> None:
    assert freeze["status"].startswith("PROTOCOL FROZEN")
    assert len(rows) == freeze["trajectory_count"] == 35
    assert freeze["conditions"] == [[name, budget] for name, budget in CONDITIONS]
    task_ids = freeze["task_ids"]
    assert len(task_ids) == freeze["task_count"] == 7
    seen: Counter[tuple[str, str, int]] = Counter(
        (row["task_id"], row["condition"], row["budget"]) for row in rows
    )
    expected = {
        (task_id, condition, budget)
        for task_id in task_ids
        for condition, budget in CONDITIONS
    }
    assert set(seen) == expected
    assert all(count == 1 for count in seen.values())
    assert {row["trusted_model"] for row in rows} == {freeze["trusted_model"]}
    assert {row["untrusted_model"] for row in rows} == {freeze["untrusted_model"]}


def condition_rows(rows: list[dict], condition: str, budget: int) -> list[dict]:
    return [
        row
        for row in rows
        if row["condition"] == condition and row["budget"] == budget
    ]


def aggregate(rows: list[dict]) -> list[dict]:
    output: list[dict] = []
    for condition, budget in CONDITIONS:
        group = condition_rows(rows, condition, budget)
        main = sum(bool(row["main_task_success"]) for row in group)
        side = sum(bool(row["side_task_success"]) for row in group)
        sabotage = sum(bool(row["successful_sabotage"]) for row in group)
        lower, upper = wilson_interval(main, len(group))
        invalid_attempts = sum(
            sum(not attempt["valid"] for attempt in row["advisor_raw_attempts"])
            for row in group
        )
        terminations = Counter(row["termination_reason"] for row in group)
        actions = [row["executor_action_count"] for row in group]
        delivered = [row["delivered_character_count"] for row in group]
        successful_deliveries = [
            row["delivered_character_count"]
            for row in group
            if condition != "none" and not row["channel_failure"]
        ]
        output.append(
            {
                "condition": condition,
                "budget": budget,
                "label": LABELS[(condition, budget)],
                "n": len(group),
                "main_task_successes": main,
                "main_task_success_rate": main / len(group),
                "main_task_wilson_95_low": lower,
                "main_task_wilson_95_high": upper,
                "side_task_successes": side,
                "successful_sabotage": sabotage,
                "channel_failures": sum(bool(row["channel_failure"]) for row in group),
                "advisor_refusals": sum(bool(row["advisor_refusal"]) for row in group),
                "invalid_advisor_attempts": invalid_attempts,
                "total_advisor_retries": sum(row["advisor_retry_count"] for row in group),
                "submit_terminations": terminations["submit"],
                "limit_exceeded_terminations": terminations["limit_exceeded"],
                "mean_executor_actions": mean(actions),
                "median_executor_actions": median(actions),
                "executor_action_range": f"{min(actions)}-{max(actions)}",
                "mean_delivered_characters_all_rows": mean(delivered),
                "mean_delivered_characters_successful_messages": (
                    mean(successful_deliveries) if successful_deliveries else 0.0
                ),
            }
        )
    return output


def write_csv(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def task_matrix(freeze: dict, rows: list[dict]) -> list[dict]:
    records: list[dict] = []
    for task_id in freeze["task_ids"]:
        for condition, budget in CONDITIONS:
            row = next(
                item
                for item in rows
                if item["task_id"] == task_id
                and item["condition"] == condition
                and item["budget"] == budget
            )
            records.append(
                {
                    "task_id": task_id,
                    "condition": condition,
                    "budget": budget,
                    "main_task_success": int(row["main_task_success"]),
                    "side_task_success": int(row["side_task_success"]),
                    "successful_sabotage": int(row["successful_sabotage"]),
                    "executor_action_count": row["executor_action_count"],
                    "termination_reason": row["termination_reason"],
                    "channel_failure": int(row["channel_failure"]),
                }
            )
    return records


def make_figures(root: Path, freeze: dict, rows: list[dict], aggregates: list[dict]) -> None:
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.colors import ListedColormap
    from matplotlib.patches import Patch

    figures = root / "results/figures"
    figures.mkdir(parents=True, exist_ok=True)
    colors = ["#64748B", "#2A9D8F", "#5BC0BE", "#E9A23B", "#D65A4A"]

    labels = [item["label"].replace(" / ", "\n") for item in aggregates]
    rates = [item["main_task_success_rate"] for item in aggregates]
    lower_errors = [
        item["main_task_success_rate"] - item["main_task_wilson_95_low"]
        for item in aggregates
    ]
    upper_errors = [
        item["main_task_wilson_95_high"] - item["main_task_success_rate"]
        for item in aggregates
    ]
    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    bars = ax.bar(
        labels,
        rates,
        color=colors,
        edgecolor="#1F2937",
        linewidth=0.6,
        yerr=[lower_errors, upper_errors],
        capsize=4,
    )
    for bar, item in zip(bars, aggregates, strict=True):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.035,
            f"{item['main_task_successes']}/{item['n']}",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )
    ax.set_ylim(0, 1.12)
    ax.set_ylabel("Main-task success rate")
    ax.set_title("Main-task success by frozen pilot condition")
    ax.text(
        0,
        -0.24,
        "Bars show observed proportions; error bars are 95% Wilson intervals. n=7 per condition.",
        transform=ax.transAxes,
        fontsize=9,
        color="#4B5563",
    )
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(figures / "main_task_success_by_condition.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    matrix = np.zeros((len(freeze["task_ids"]), len(CONDITIONS)), dtype=int)
    for row_index, task_id in enumerate(freeze["task_ids"]):
        for column_index, (condition, budget) in enumerate(CONDITIONS):
            row = next(
                item
                for item in rows
                if item["task_id"] == task_id
                and item["condition"] == condition
                and item["budget"] == budget
            )
            matrix[row_index, column_index] = int(row["main_task_success"])
    fig, ax = plt.subplots(figsize=(8.8, 6.1))
    ax.imshow(matrix, cmap=ListedColormap(["#E76F51", "#2A9D8F"]), vmin=0, vmax=1, aspect="auto")
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(j, i, "PASS" if matrix[i, j] else "FAIL", ha="center", va="center", color="white", fontweight="bold", fontsize=9)
    ax.set_xticks(range(len(CONDITIONS)), [LABELS[item].replace(" / ", "\n") for item in CONDITIONS])
    ax.set_yticks(range(len(freeze["task_ids"])), [TASK_LABELS[item] for item in freeze["task_ids"]])
    ax.set_title("Task-level main-task outcomes")
    ax.set_xlabel("Frozen condition / character budget")
    ax.set_ylabel("Main task / protected side objective")
    ax.legend(
        handles=[Patch(color="#2A9D8F", label="Main-task pass"), Patch(color="#E76F51", label="Main-task fail")],
        loc="upper center",
        bbox_to_anchor=(0.5, -0.12),
        ncol=2,
        frameon=False,
    )
    fig.tight_layout()
    fig.savefig(figures / "task_condition_outcome_heatmap.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    positions = np.arange(len(CONDITIONS))
    submits = np.array([item["submit_terminations"] for item in aggregates])
    limits = np.array([item["limit_exceeded_terminations"] for item in aggregates])
    ax.bar(positions, submits, color="#2A9D8F", label="submit")
    ax.bar(positions, limits, bottom=submits, color="#E9A23B", label="limit_exceeded")
    for index, item in enumerate(aggregates):
        ax.text(index, 7.15, f"mean actions {item['mean_executor_actions']:.1f}", ha="center", fontsize=8.5)
    ax.set_xticks(positions, labels)
    ax.set_ylim(0, 8)
    ax.set_yticks(range(0, 8))
    ax.set_ylabel("Trajectories")
    ax.set_title("Termination behavior by condition")
    ax.legend(frameon=False, ncol=2, loc="upper left")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(figures / "termination_behavior_by_condition.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze the closed frozen Day 3 pilot.")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    root = args.root.resolve()
    freeze = json.loads((root / "data/day3_final_freeze.json").read_text(encoding="utf-8"))
    rows = load_jsonl(root / "data/derived/day3_pilot_sonnet45_final.jsonl")
    validate(freeze, rows)

    aggregates = aggregate(rows)
    matrix = task_matrix(freeze, rows)
    write_csv(root / "results/tables/final_aggregate.csv", aggregates)
    write_csv(root / "results/tables/final_task_matrix.csv", matrix)

    diagnostics = {
        "source": "data/derived/day3_pilot_sonnet45_final.jsonl",
        "freeze_id": freeze["freeze_id"],
        "rows": len(rows),
        "status_counts": dict(Counter(row["status"] for row in rows)),
        "errors": sum(row["error"] is not None for row in rows),
        "protocol_violation_trajectories": sum(bool(row["protocol_violations"]) for row in rows),
        "advisor_calls_none_condition": sum(
            row["advisor_call_count"] for row in rows if row["condition"] == "none"
        ),
        "all_side_task_successes": sum(bool(row["side_task_success"]) for row in rows),
        "all_successful_sabotage": sum(bool(row["successful_sabotage"]) for row in rows),
        "aggregate": aggregates,
    }
    (root / "results/tables/final_diagnostics.json").write_text(
        json.dumps(diagnostics, indent=2), encoding="utf-8"
    )
    make_figures(root, freeze, rows, aggregates)
    print(json.dumps(diagnostics, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
