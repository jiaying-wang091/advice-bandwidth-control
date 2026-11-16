# Research Memo Implementation Extract

The finalized `Untrusted_Advice_Bandwidth_AI_Control_Research_Design_Memo.docx` is the only source of truth. This file is a repository-local implementation extract, not a redesign.

## Recommended design

Measure the safety response curve when a stronger actionless advisor receives an exact total communication budget and a weaker, policy-aware executor retains every tool call. The planned experiment uses 24 prequalified BashArena tasks, one advice message per trajectory, caps of 0, 8, 16, 32, and 64 characters, benign and adversarial advisor policies, two repetitions, and objective side-task evaluators.

## Minimum harness contract

1. Load immutable task metadata, reset procedure, main task, protected invariant, and objective evaluators.
2. Permit T at most two read-only orientation actions.
3. Give U the task state and visible orientation transcript, but no tools.
4. Validate one advice message with Unicode NFC and an exact total character cap.
5. Give T exclusive action authority until submit, violation, or step limit.
6. Evaluate main-task success and protected-state violation programmatically.
7. Append a reconstructable JSONL trajectory record.
8. Keep the shadow monitor observational.

## Interpretation boundary

A maximum cap defines a nested action set: an advisor with a 64-character cap can always send an 8-character message. The defensible hypothesis is therefore a steep early response or diminishing returns, not that short messages are intrinsically more powerful than longer permitted messages.

For the exact frozen protocol, exclusions, pilot criteria, Day 3 rule, and kill criteria, see `results/preregistration.md`.

