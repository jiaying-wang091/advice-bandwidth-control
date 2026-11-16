from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path


def load_records(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def summarize(records: list[dict]) -> dict:
    grouped: dict[str, Counter] = defaultdict(Counter)
    for record in records:
        key = f"{record['condition']}/{record['character_cap']}"
        grouped[key]["runs"] += 1
        grouped[key]["main_task_success"] += int(record["evaluator_outputs"]["main_task_success"])
        grouped[key]["protected_state_violation"] += int(record["evaluator_outputs"]["protected_state_violation"])
        grouped[key]["successful_sabotage"] += int(record["evaluator_outputs"]["successful_sabotage"])
        grouped[key]["channel_failure"] += int(record["channel_failure"])
    return {key: dict(value) for key, value in sorted(grouped.items())}


def main() -> int:
    root = Path.cwd()
    records = load_records(root / "data/derived/trajectories.jsonl")
    output = {
        "warning": "Smoke runs are operational checks and must not be interpreted scientifically.",
        "records": len(records),
        "groups": summarize(records),
    }
    table_path = root / "results/tables/operational_summary.json"
    table_path.parent.mkdir(parents=True, exist_ok=True)
    table_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

