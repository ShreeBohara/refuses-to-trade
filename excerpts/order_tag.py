"""A 20-character broker order tag that fully decodes.

Illustrative re-implementation of a pattern from a private trading system.
The broker exposes one free-text field per order, capped at 20 characters.
That field is the only channel through which a process can send a message to
its own future self across a crash: on restart, read the broker's order book,
decode each tag, and rebuild which trade cycle, which action, which side, and
which position tranches every open order belongs to. No local state required.

Layout (20 chars):

    XT 0519 1A TE C 5 A3F2B7C1
    |  |    |  |  | |  '-- 8 hex chars of a content hash (uniqueness)
    |  |    |  |  | '----- tranche bitmask, one hex digit (0b0101 = tranches 1 and 3)
    |  |    |  |  '------- side: C call, P put, N none
    |  |    |  '---------- action code, 2 letters
    |  |    '------------- cycle id, base36, 2 chars (1,295 cycles per day)
    |  '------------------ trading day MMDD
    '--------------------- prefix identifying this system's orders in a shared account
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import date

PREFIX = "XT"
TRANCHES = (1, 2, 3, 4)
ACTIONS = {"SC": "start_cycle", "TE": "target_exit", "EE": "emergency_exit", "KS": "kill_switch_exit"}
_B36 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _b36(n: int, width: int) -> str:
    out = ""
    while n:
        n, r = divmod(n, 36)
        out = _B36[r] + out
    return out.rjust(width, "0")


def _unb36(s: str) -> int:
    n = 0
    for ch in s:
        n = n * 36 + _B36.index(ch)
    return n


@dataclass(frozen=True)
class Tag:
    day: date
    cycle: int
    action: str
    side: str
    tranches: tuple[int, ...]


def encode(day: date, cycle: int, action: str, side: str, tranches: tuple[int, ...], payload: str) -> str:
    if action not in ACTIONS or side not in "CPN" or not 0 <= cycle < 36 * 36:
        raise ValueError("unencodable intent")
    mask = sum(1 << (t - 1) for t in tranches)
    digest = hashlib.sha1(payload.encode()).hexdigest()[:8].upper()
    tag = f"{PREFIX}{day:%m%d}{_b36(cycle, 2)}{action}{side}{mask:X}{digest}"
    assert len(tag) == 20, tag
    return tag


def decode(tag: str, year: int) -> Tag | None:
    """Return None for anything that is not one of ours. Never guess."""
    if len(tag) != 20 or not tag.startswith(PREFIX):
        return None
    try:
        day = date(year, int(tag[2:4]), int(tag[4:6]))
        cycle = _unb36(tag[6:8])
        action, side, mask = tag[8:10], tag[10], int(tag[11], 16)
    except ValueError:
        return None
    if action not in ACTIONS or side not in "CPN":
        return None
    tranches = tuple(t for t in TRANCHES if mask & (1 << (t - 1)))
    return Tag(day, cycle, ACTIONS[action], side, tranches)


if __name__ == "__main__":
    t = encode(date(2026, 5, 19), 46, "TE", "C", (1, 3), "cycle46-target-exit-lots-1-3")
    print(t)                      # XT05191ATEC5 + 8 hex chars = 20
    print(decode(t, 2026))        # Tag(day=2026-05-19, cycle=46, action='target_exit', side='C', tranches=(1, 3))
    print(decode("manual-order", 2026))  # None: a human's order, leave it alone
