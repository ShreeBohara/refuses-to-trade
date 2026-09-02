# Excerpts

Three small, self-contained modules that re-implement patterns from the private
system, written fresh for this write-up. They are illustrations, not production
code: no vendor SDKs, synthetic data only, each runnable with plain Python 3.11+.

| File | Pattern | Run |
|---|---|---|
| `order_tag.py` | A 20-character broker order tag that fully decodes, so crash recovery works from the broker's own data | `python order_tag.py` |
| `fail_closed_gates.py` | Composing independent gates so that an unknown state is a blocked state, with named blockers and an entry/exit asymmetry | `python fail_closed_gates.py` |
| `event_log_projection.py` | An append-only JSONL log as the system of record, read by byte offset so a torn line is never parsed | `python event_log_projection.py` |
