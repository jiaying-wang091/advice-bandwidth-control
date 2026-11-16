# Documentation map

The files in this directory preserve the project's implementation and repair history. Documents describing integration failures, prompt repairs, executor substitution, feasibility checks, and pilot decisions are **historical audit records**. They explain how the final frozen protocol was reached; they are not competing versions of the final result and should not be pooled as treatment data.

## Authoritative final materials

- [`../README.md`](../README.md): public project overview and reproduction instructions
- [`../FINAL_ANALYSIS.md`](../FINAL_ANALYSIS.md): authoritative descriptive analysis of the frozen 35-trajectory pilot
- [`../LIMITATIONS.md`](../LIMITATIONS.md): authoritative limitations and scope conditions
- [`../data/day3_final_freeze.json`](../data/day3_final_freeze.json): frozen protocol record and source hashes
- [`../data/derived/day3_pilot_sonnet45_final.jsonl`](../data/derived/day3_pilot_sonnet45_final.jsonl): authoritative final dataset

The final analysis uses only the frozen dataset above. Earlier JSONL files, feasibility runs, mini-pilots, elicitation checks, and repair documents remain in the repository solely for reproducibility and auditability.

## Historical audit records

The remaining Markdown files in `docs/` record pre-freeze development decisions. Their model choices, readiness labels, and operational diagnoses may have been superseded by later repairs. Read them chronologically when auditing the project, but use the authoritative materials above for the final design and results.
