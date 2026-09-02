"""Composing independent safety gates so that "unknown" means "blocked".

Illustrative re-implementation of a pattern from a private trading system.
Three properties matter more than any single check:

1. Every gate is independent and fail-closed: an exception inside a gate is a
   block, not a pass. The default answer to "may I trade?" is no.
2. The result names the blocker. "Blocked" without a reason trains operators to
   flip switches until it works, which is how safeguards get disabled.
3. The policy is asymmetric. Entries and exits are judged separately, because
   you must always be allowed to leave a position even when you may not open one.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

Gate = Callable[[], str | None]  # returns None to pass, or a reason to block


@dataclass(frozen=True)
class Verdict:
    allowed: bool
    blockers: tuple[str, ...] = field(default_factory=tuple)


def evaluate(gates: dict[str, Gate]) -> Verdict:
    blockers: list[str] = []
    for name, gate in gates.items():
        try:
            reason = gate()
        except Exception as exc:  # a broken gate is a closed gate
            reason = f"gate raised {type(exc).__name__}: {exc}"
        if reason:
            blockers.append(f"{name}: {reason}")
    return Verdict(allowed=not blockers, blockers=tuple(blockers))


# --- demo -------------------------------------------------------------------

def demo() -> None:
    state = {"armed": True, "env_enabled": True, "kill_switch": False,
             "broker_flat": None, "feed_healthy": True, "quote_drift_pct": 2.4}

    def armed():        return None if state["armed"] else "operator has not armed live orders"
    def env():          return None if state["env_enabled"] else "ENABLE_LIVE_ORDERS is not true"
    def kill():         return "kill switch active" if state["kill_switch"] else None
    def flat():
        if state["broker_flat"] is None:
            raise RuntimeError("reconciliation never completed")   # unknown -> blocked
        return None if state["broker_flat"] else "broker holds positions this process cannot account for"
    def feed():         return None if state["feed_healthy"] else "market data stalled"
    def drift():        return f"provider/broker quote drift {state['quote_drift_pct']}% > 2%" if state["quote_drift_pct"] > 2 else None

    entry_gates = {"armed": armed, "env": env, "kill_switch": kill, "reconciled_flat": flat, "feed": feed, "quote_drift": drift}
    exit_gates = {"armed": armed, "env": env}   # exits are never blocked by drift, feed, or flatness

    print("ENTRY:", evaluate(entry_gates))
    print("EXIT :", evaluate(exit_gates))


if __name__ == "__main__":
    demo()
