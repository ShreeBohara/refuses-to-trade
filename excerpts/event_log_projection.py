"""An append-only JSONL log as the system of record, and a reader that never
parses a half-written line.

Illustrative re-implementation of a pattern from a private trading system.
One process appends events; several others (a dashboard, report generators,
a crash-recovery seed, a replay engine) tail the same file. Two rules make
that safe without a database:

- The writer appends whole lines only.
- The reader consumes only newline-terminated lines and remembers the byte
  offset of the last complete one. A torn final line is picked up whole on the
  next poll instead of raising a JSON error every few seconds.

Every consumer is then a left fold: state = reduce(apply, events, initial).
"""
from __future__ import annotations

import json
from pathlib import Path


def read_complete_lines(path: Path, offset: int) -> tuple[list[dict], int]:
    """Return (events, new_offset). Only whole lines are returned."""
    with path.open("rb") as fh:
        fh.seek(offset)
        chunk = fh.read()
    last_nl = chunk.rfind(b"\n")
    if last_nl == -1:
        return [], offset
    complete, new_offset = chunk[: last_nl + 1], offset + last_nl + 1
    events = [json.loads(line) for line in complete.splitlines() if line.strip()]
    return events, new_offset


def apply(state: dict, event: dict) -> dict:
    """One branch per event type. Unknown events are recorded, not fatal."""
    kind = event.get("event")
    if kind == "session_started":
        state.update(session=event["session_id"], ticks=0, orders=[])
    elif kind == "tick":
        state["ticks"] += 1
        state["last_price"] = event["last_price"]
    elif kind == "execution_report":
        state["orders"].append((event["order_id"], event["status"]))
    else:
        state.setdefault("unknown_events", []).append(kind)
    return state


if __name__ == "__main__":
    import tempfile
    log = Path(tempfile.mkdtemp()) / "session.jsonl"
    log.write_text('{"event":"session_started","session_id":"demo"}\n'
                   '{"event":"tick","last_price":24000.5}\n'
                   '{"event":"tick","last_price":24001.0}\n'
                   '{"event":"execution_report","order_id":"1","status":"FILLED"}\n'
                   '{"event":"tick","last_price":2400')   # torn: writer mid-line
    events, off = read_complete_lines(log, 0)
    state = {}
    for e in events:
        state = apply(state, e)
    print(state, "| next offset", off)   # the torn tick is NOT here yet
    with log.open("a") as fh:
        fh.write('2.5}\n')                 # writer finishes the line
    events, off = read_complete_lines(log, off)
    print([e["last_price"] for e in events], "| resumed cleanly at byte", off)
