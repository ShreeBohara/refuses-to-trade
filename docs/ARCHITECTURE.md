# Architecture

A map of the country, not an atlas of its states. This names the layers, the boundaries between them, and the invariants that hold across them. It does not describe modules one by one.

## The shape

Four processes run on one machine during a session. An authentication server that exists only to catch the broker's daily OAuth redirect on loopback. A dashboard backend serving a React single-page app. The runner, which is the trading process. A reporting sidecar that fires after the close.

They do not share memory and there is no message broker. The runner appends to a session log; the dashboard tails that file with incremental byte-offset reads; the dashboard writes operator intent to separate control files with atomic write-and-rename; the runner polls those files between ticks. The filesystem is the bus.

That choice has one consequence worth stating: there is no path from the dashboard into the runner's memory. A defect in the user interface cannot corrupt trading state. It can only fail to write a file the runner will read.

## From a tick to a refusal

A vendor delivers a payload. Three vendors deliver three different shapes, and each has an adapter that produces the same frozen tick type, validating the price is positive and coercing the timestamp into a single naive-IST representation. Anything that fails validation is dropped at the boundary with a named reason, never further in.

The tick reaches a candle builder that buckets on exchange time, anchored to the open, and a running-average accumulator. Both refuse a timestamp older than the last one they saw. This is a hard error rather than a warning, because both structures are order-dependent and a silently accepted backwards tick corrupts the candle an entry decision is computed from.

The strategy engine has two paths. On every tick it evaluates fills, targets and emergency conditions. On a candle close it evaluates entry, reversal and confirmation. It emits intents, never orders.

An intent becomes an order only after the gate chain. Contract resolution first, because an intent that cannot be mapped to a tradeable broker symbol is not an order at all; then the quote guard, the risk gate, and the live-order gate. Pricing happens last, snapping to the exchange tick grid in the direction that improves the chance of a fill.

Every step of that path writes an event. The refusal writes an event too, with the reason, which is the difference between a system you can audit and one you can only watch.

## Invariants, stated as absences

Nothing below the gate chain can construct an order. The broker adapter takes an approved intent and has no code path that builds one.

No projection writes to the log it reads. The dashboard, the ledger generator, the replay engine and the drill validator are all readers.

No component holds broker state as truth. The broker's own order book is the authority, and local tracking is a cache that gets reconciled against it on a fixed interval and at every restart.

No vendor identifier reaches an order. Vendor instrument identities are translated into broker symbols at a single boundary, and the translation refuses to guess.

## The log

One file per session, one JSON object per line, appended and never rewritten. Fifty-five event types, each with required fields validated on write and again on read. Non-finite numbers are rejected because they serialise into JSON that parses back as something else and poisons every downstream reader.

Six things are folds over that file: the dashboard read model, the CSV ledgers, the crash-recovery seed, the offline replay engine, the drill validator, and the exported analysis bundle. Adding a seventh consumer requires no schema change and no migration, which is most of why the design has survived.

The reader contract is the subtle part. A reader consumes only newline-terminated lines and remembers the offset of the last complete one. A partially written final line is not an error to handle; it is a line that does not exist yet.

## Where it is weakest

Two modules carry more than they should, the strategy engine and the largest vendor client, both past 1,500 lines. I wrote an architecture plan proposing a package split, then shipped capability on the flat layout instead, and recorded that I had not followed it. The honest reason is that the split was speculative and the features were not.
