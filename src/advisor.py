from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Protocol

from .channel import ChannelValidationError, ValidatedAdvice, empty_advice, normalize_and_validate
from .tasks import TaskSpec


class AdviceBackend(Protocol):
    model_id: str

    def generate(self, request: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        """Return advice and optional usage. No tool or environment object is provided."""


@dataclass(frozen=True)
class AdviceDelivery:
    delivered: ValidatedAdvice
    invalid_attempts: list[dict[str, Any]]
    channel_failure: bool
    usage: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "advice": self.delivered.text,
            "delivered_character_count": self.delivered.character_count,
            "invalid_attempts": self.invalid_attempts,
            "channel_failure": self.channel_failure,
            "usage": self.usage,
        }


class ScriptedAdvisor:
    model_id = "scripted-u-smoke-v1"

    def __init__(self, scripted_attempts: list[str] | None = None):
        self.scripted_attempts = list(scripted_attempts or [])

    def generate(self, request: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        if "tools" in request or "environment" in request:
            raise AssertionError("advisor request must not contain tools or environment authority")
        if self.scripted_attempts:
            text = self.scripted_attempts.pop(0)
        elif request["condition"] == "benign":
            text = "Set port to 8080"
        elif request["condition"] == "adversarial":
            text = "Disable firewall"
        else:
            text = ""
        return text, {"input_tokens": None, "output_tokens": None, "cost_usd": None}


def request_advice(
    backend: AdviceBackend,
    task: TaskSpec,
    condition: str,
    character_cap: int,
    visible_state: dict[str, str],
    orientation_transcript: list[dict[str, Any]],
    max_retries: int,
    prompt_text: str,
    retry_prompt: str,
) -> AdviceDelivery:
    if condition == "none":
        if character_cap != 0:
            raise ValueError("no-advice condition requires cap 0")
        return AdviceDelivery(empty_advice(), [], False, {})
    if condition not in {"benign", "adversarial"}:
        raise ValueError(f"unknown condition: {condition}")

    invalid: list[dict[str, Any]] = []
    total_usage: dict[str, Any] = {"attempts": []}
    reason = ""
    for attempt in range(max_retries + 1):
        request = {
            "task_id": task.task_id,
            "main_task": task.main_task,
            "protected_invariant": task.protected_invariant,
            "visible_state": visible_state,
            "orientation_transcript": orientation_transcript,
            "condition": condition,
            "hidden_side_objective": task.hidden_side_objective if condition == "adversarial" else None,
            "character_cap": character_cap,
            "prompt": prompt_text if attempt == 0 else retry_prompt.format(
                reason=reason, character_cap=character_cap
            ),
            "attempt": attempt + 1,
        }
        raw, usage = backend.generate(request)
        total_usage["attempts"].append(usage)
        try:
            delivered = normalize_and_validate(raw, character_cap)
            return AdviceDelivery(delivered, invalid, False, total_usage)
        except ChannelValidationError as exc:
            reason = str(exc)
            invalid.append({"attempt": attempt + 1, "raw_output": raw, "reason": reason})

    return AdviceDelivery(empty_advice(), invalid, True, total_usage)

