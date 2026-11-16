from __future__ import annotations

import unittest

from src.advisor import ScriptedAdvisor, request_advice
from src.channel import ChannelValidationError, normalize_and_validate
from src.tasks import TaskSpec


TASK = TaskSpec(
    task_id="test",
    environment_id="test",
    benchmark_status="fixture",
    main_task="main",
    protected_invariant="protect",
    hidden_side_objective="side",
    main_task_evaluator="service_port_8080",
    side_task_evaluator="firewall_disabled",
    reset_procedure="materialize_fixture_v1",
    seed=1,
    initial_files={},
)


class ChannelTests(unittest.TestCase):
    def test_at_cap_is_accepted(self) -> None:
        result = normalize_and_validate("12345678", 8)
        self.assertEqual(result.character_count, 8)

    def test_over_cap_is_rejected(self) -> None:
        with self.assertRaises(ChannelValidationError):
            normalize_and_validate("123456789", 8)

    def test_unicode_nfc_count(self) -> None:
        result = normalize_and_validate("e\u0301", 1)
        self.assertEqual(result.text, "é")
        self.assertEqual(result.character_count, 1)

    def test_newline_is_rejected(self) -> None:
        with self.assertRaises(ChannelValidationError):
            normalize_and_validate("one\ntwo", 20)

    def test_two_private_retries_then_success(self) -> None:
        backend = ScriptedAdvisor(["too long for cap", "still too long", "ok"])
        result = request_advice(
            backend, TASK, "benign", 2, {}, [], 2, "prompt", "retry {reason} {character_cap}"
        )
        self.assertEqual(result.delivered.text, "ok")
        self.assertEqual(len(result.invalid_attempts), 2)
        self.assertFalse(result.channel_failure)

    def test_channel_failure_never_truncates(self) -> None:
        backend = ScriptedAdvisor(["long", "long", "long"])
        result = request_advice(
            backend, TASK, "benign", 2, {}, [], 2, "prompt", "retry {reason} {character_cap}"
        )
        self.assertEqual(result.delivered.text, "")
        self.assertEqual(result.delivered.character_count, 0)
        self.assertEqual(len(result.invalid_attempts), 3)
        self.assertTrue(result.channel_failure)

    def test_zero_advice_does_not_call_backend(self) -> None:
        class ExplodingBackend:
            model_id = "never-called"
            def generate(self, request):
                raise AssertionError("backend should not be called")

        result = request_advice(
            ExplodingBackend(), TASK, "none", 0, {}, [], 2, "prompt", "retry"
        )
        self.assertEqual(result.delivered.text, "")

    def test_advisor_receives_no_tool_interface(self) -> None:
        class ProbeBackend:
            model_id = "probe"
            def generate(self, request):
                self.request = request
                return "ok", {}

        backend = ProbeBackend()
        request_advice(backend, TASK, "benign", 2, {}, [], 0, "prompt", "retry")
        self.assertNotIn("tools", backend.request)
        self.assertNotIn("environment", backend.request)


if __name__ == "__main__":
    unittest.main()

