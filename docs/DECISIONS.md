# Decisions

Context, the alternatives, what I chose, and what it cost. Two entries record reversals.

## The log is the database

**Context.** Every consumer needs session state: a dashboard, ledgers, crash recovery, replay, a validator.

**Alternatives.** Postgres or SQLite with the log as a side effect.

**Decision.** An append-only JSONL file is the record. Everything else is a fold over it.

**Consequences.** Audit trail, replay and crash recovery came free, and adding a consumer needs no migration. The cost is real: there are no queries. Analysis means writing a reader, and a schema mistake is permanent in old files, which is why two field aliases from March still exist.

## Ambiguity is a state, not an error

**Context.** A place-order call times out. The order may or may not exist at the broker.

**Alternatives.** Treat a timeout as failure and retry, which can place two orders. Treat it as success, which strands a position.

**Decision.** A third status. The report is recorded as unknown, requiring reconciliation; the order book is re-read immediately and matched by tag; new entries are blocked while any unknown is outstanding; and the restart path refuses to start rather than guess.

**Consequences.** Every consumer handles a third case. It took three separate changes to get right, and it is the piece of this system I would defend first.

## Trade identity lives in the broker's tag field

**Context.** After a crash the process has no trustworthy local state, but the broker knows what orders exist.

**Alternatives.** A local order journal, which can be stale or corrupt exactly when it is needed.

**Decision.** Encode the trading day, cycle, action, side and a tranche bitmask into the twenty characters the broker allows, with a hash for uniqueness, and decode it on restart.

**Consequences.** Recovery works from the broker's own data. The constraint forced the bitmask, which is the detail that makes it complete rather than merely suggestive.

## Limit orders everywhere, including exits

**Context.** An emergency exit wants certainty of execution.

**Alternatives.** Market orders on emergency paths.

**Decision.** Limit orders with a small buffer, repriced a fixed number of times, then an alert.

**Consequences.** An exit can fail to fill, which is the sharpest risk in the system. The control is a present operator with the broker's app open. I accepted a worse automated path in exchange for never sending an unbounded order into an illiquid strike.

## The human draws the level

**Context.** The one input that requires judgment is where the day's reference level sits.

**Alternatives.** Infer it from the prior session.

**Decision.** A person sets it from the dashboard before the session does anything.

**Consequences.** Unattended operation is impossible by construction, which is the point. The system cannot start without a human, and that is a feature I would not trade away for convenience.

## Reversed: the package refactor I planned and did not build

**Context.** A long design document proposed splitting the codebase into provider, broker, contract and runtime packages.

**Decision at the time.** Ship capability on the existing flat layout instead.

**Reversal.** I wrote in the status document that most of the plan's structural deliverables were not built, and why.

**Consequences.** Two modules are oversized and documented as such. I would do the scoped extraction before adding a second execution broker, and not before.

## Reversed: promoting a vendor after two clean runs

**Context.** The third vendor passed two consecutive clean live drills.

**Decision at the time.** Promote it from diagnostic to decision-driving.

**Reversal.** Kept it diagnostic. A warning about out-of-order timestamps was still firing at a low rate and I could not explain the cause.

**Consequences.** A working integration sits unused. I think this is the right trade: a tolerated warning you cannot explain is a bug you have agreed to ship.
