# The safety chain

Eleven checks stand between a strategy decision and a broker call. This describes what each one refuses, how it behaves when it cannot decide, and what proves it.

## The rule the whole design rests on

A gate answers no, or it answers yes. If it raises while deciding, that is a no. The default state of the system is refusal, and a yes requires eleven affirmative answers in the same instant.

Two habits from other fields shaped this. Railway signalling puts the arm in the danger position when the cable breaks, so the failure of the mechanism produces the safe state rather than the unsafe one. A launch poll requires every station to say go, and silence from a station is not a go. Both ideas are cheap to implement and hard to argue with after something has gone wrong.

## The gates

**Execution mode.** The branch configuration must name live. Observe and paper modes route to a synthetic adapter that fabricates fills locally and cannot reach the network.

**Environment flag.** The process environment must enable live orders. This is deliberately not in the dashboard, so arming requires touching the machine.

**Operator arm.** A dashboard control must be set, from loopback, with a token. It resets to off.

**Kill switch.** Set from the dashboard, honoured within half a second by a dedicated thread, and persisted to the branch configuration so a session started after a kill begins with entries blocked until a human clears it.

**Startup reconciliation.** Before arming, the broker's orders and positions are read. Anything unexplained blocks the session. A position that today's order tags can fully account for may be adopted into a rebuilt cycle, and that adoption is protective only: the system will manage an exit and will not open anything new.

**Capital floor.** Available margin is compared against a configured minimum. If the margin payload cannot be parsed, that is a refusal, not a default.

**Provider and broker pairing.** Only approved combinations of data source and execution broker may arm. Unknown combinations and every combination involving the unbuilt execution adapter fail closed.

**Risk gate.** Latches on a daily loss limit, a margin rejection from the broker, a partial fill that does not map to whole tranches, or an order lifecycle that could not be resolved. A loss latch also exits the open position. The others block new entries and leave the position alone, because the correct response to bookkeeping ambiguity is to stop, not to act.

**Broker quote guard.** The vendor price and the broker's own price are compared immediately before an order is priced. Beyond tolerance, an entry is refused. A missing broker quote refuses an entry and permits an exit.

**Market-data health.** A stalled stream, a gap, a processing backlog or a queue overflow arms a timed block on new entries. Exits stay available throughout. Terminal conditions end the session into a safe mode that cancels working orders and attempts an exit.

**Contract compatibility.** The instrument selected on vendor data must map to exactly one tradeable broker contract with a matching lot size. Ambiguous, missing or mismatched mappings raise. The failure direction is deliberate: a mapping defect stops trading and cannot trade the wrong instrument.

## What the gates do not cover

A fill the broker reports late. An exit order that does not fill because the strike is illiquid. A vendor that reports success and delivers nothing, which has happened, and which health checks now catch only after a delay measured in seconds.

The control for all three is a person watching the screen, which is why there is no unattended mode and why the emergency exit is a button a human presses.

## How each gate is proven

Every gate has a test that feeds it a missing or malformed input and asserts a refusal. That is the shape of the assertion: not that the gate passes good input, which is easy, but that it refuses bad input, which is the property that matters.

Beyond unit tests, sessions ran against live market data with a validator that checks recorded evidence against declared budgets and emits a verdict rather than an impression. A session where a stream stalls and the system stops cleanly is a pass. A session that completes while quietly comparing against stale data is a failure, and one of those is why a working vendor integration is still not trusted.
