from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import shutil
from typing import Any


@dataclass(frozen=True)
class TaskSpec:
    task_id: str
    environment_id: str
    benchmark_status: str
    main_task: str
    protected_invariant: str
    hidden_side_objective: str
    main_task_evaluator: str
    side_task_evaluator: str
    reset_procedure: str
    seed: int
    initial_files: dict[str, str]

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "TaskSpec":
        return cls(**value)


def load_task(manifest_path: Path, task_id: str) -> TaskSpec:
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    matches = [item for item in payload["tasks"] if item["task_id"] == task_id]
    if len(matches) != 1:
        raise KeyError(f"expected exactly one task {task_id!r}, found {len(matches)}")
    return TaskSpec.from_dict(matches[0])


def reset_task(task: TaskSpec, workspace: Path) -> dict[str, str]:
    if task.reset_procedure != "materialize_fixture_v1":
        raise ValueError(f"unsupported reset procedure: {task.reset_procedure}")
    if workspace.is_symlink():
        raise ValueError(f"workspace itself must not be a symlink: {workspace}")
    workspace = workspace.resolve(strict=False)
    if workspace.exists():
        shutil.rmtree(workspace)
    workspace.mkdir(parents=True, exist_ok=False)
    for relative, content in task.initial_files.items():
        target = safe_path(workspace, relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    return snapshot_state(workspace)


def safe_path(workspace: Path, relative: str) -> Path:
    base = workspace.resolve(strict=True)
    candidate = (base / relative).resolve(strict=False)
    if candidate != base and base not in candidate.parents:
        raise ValueError(f"path escapes workspace: {relative!r}")
    return candidate


def canonical_relative_path(workspace: Path, child: Path) -> Path:
    """Return a contained relative path after canonicalizing both operands.

    Resolving both sides avoids macOS alias mismatches such as /var versus
    /private/var. Resolving the child before containment validation also rejects
    symlinks inside the workspace that point outside the sandbox.
    """
    base = workspace.resolve(strict=True)
    resolved_child = child.resolve(strict=True)
    if resolved_child != base and base not in resolved_child.parents:
        raise ValueError(f"path escapes workspace after resolution: {child}")
    return resolved_child.relative_to(base)


def snapshot_state(workspace: Path) -> dict[str, str]:
    state: dict[str, str] = {}
    if not workspace.exists():
        return state
    base = workspace.resolve(strict=True)
    for path in sorted(p for p in base.rglob("*") if p.is_file()):
        relative = canonical_relative_path(base, path)
        state[str(relative)] = path.resolve(strict=True).read_text(encoding="utf-8")
    return state


def state_hash(state: dict[str, str]) -> str:
    canonical = json.dumps(state, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return sha256(canonical).hexdigest()


def state_diff(before: dict[str, str], after: dict[str, str]) -> dict[str, Any]:
    keys = sorted(set(before) | set(after))
    changed = []
    for key in keys:
        if before.get(key) != after.get(key):
            changed.append({"path": key, "before": before.get(key), "after": after.get(key)})
    return {"before_hash": state_hash(before), "after_hash": state_hash(after), "changed": changed}


class ContainedFileEnvironment:
    READ_ONLY_TOOLS = frozenset({"list_dir", "read_file"})
    EXECUTOR_TOOLS = frozenset({"list_dir", "read_file", "write_file", "submit"})

    def __init__(self, workspace: Path):
        self.workspace = workspace.resolve(strict=True)
        self.submitted = False

    def call(self, tool: str, args: dict[str, Any], allowed_tools: set[str] | frozenset[str]) -> dict[str, Any]:
        if tool not in allowed_tools:
            raise PermissionError(f"tool {tool!r} is not allowed in this phase")
        if tool == "list_dir":
            rel = args.get("path", ".")
            directory = safe_path(self.workspace, rel)
            output = sorted(
                str(canonical_relative_path(self.workspace, path))
                for path in directory.iterdir()
            )
            return {"ok": True, "output": output}
        if tool == "read_file":
            path = safe_path(self.workspace, args["path"])
            return {"ok": True, "output": path.read_text(encoding="utf-8")}
        if tool == "write_file":
            path = safe_path(self.workspace, args["path"])
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(args["content"], encoding="utf-8")
            return {"ok": True, "output": f"wrote {args['path']}"}
        if tool == "submit":
            self.submitted = True
            return {"ok": True, "output": "submitted"}
        raise KeyError(tool)

