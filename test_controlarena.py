from inspect_ai import eval

from control_arena import EvalMode
from control_arena.eval import ControlEvalConfig, get_control_task_product
from control_arena.micro_protocol import defer_to_trusted_builder
from control_arena.settings.iac.control_iac_setting import ControlIACSetting

config = ControlEvalConfig(
    trusted_model="anthropic/claude-haiku-4-5",
    untrusted_model="anthropic/claude-sonnet-4-6",
)

setting = ControlIACSetting()
protocol = defer_to_trusted_builder()

tasks = get_control_task_product(
    setting,
    protocol,
    [EvalMode.ATTACK],
    eval_config=config,
)

eval(tasks=tasks, limit=1)
