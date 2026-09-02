# Post-mortems

Three sessions that changed the code. Written in the shape an on-call engineer expects, and blaming missing checks rather than people or vendors.

## A socket that reported success and delivered nothing

**Summary.** A session started before the open, subscribed to three instruments successfully, and received no market data after the open.

**Trigger.** The vendor SDK deduplicates subscription requests per socket object. A subscription made before the market opened was accepted, and every attempt to resubscribe afterwards was a silent no-op on the same socket, which the far side had since closed.

**Detection.** A full session, by a person watching an empty chart. Every automated check passed: authenticated, subscribed, no errors, no exceptions. This is the worst detection story in the repository.

**Fix.** At the moment normal-market data becomes expected, discard the socket object and rebuild it, then resubscribe every active instrument. Lifecycle callbacks now capture the open, close and error events the SDK was swallowing, so the evidence exists next time.

**What changed structurally.** Health checks became time-aware. A silence check that runs before the open produces false failures; one that never runs produces this. The check now activates when data is genuinely expected and restarts its grace period at the open.

**Where I got lucky.** Observe mode. Nothing was at stake but a day.

## A cold feed and a strike nobody would buy

**Summary.** With a sparse instrument universe, the selector chose an option thousands of points from the money, priced at zero, and nothing objected.

**Trigger.** A cached instrument master from a previous day, combined with a chain whose strike spacing was implausible. The selector's job is to find the contract nearest a target premium; given garbage, it found garbage nearest the target.

**Detection.** Reading session bundles after the fact, from a machine in another country.

**Fix.** Three checks that did not exist. Instrument caches carry the trading date and are invalid on any other day. Non-positive and non-finite prices are refused at the quote boundary, where the last known good price is kept instead. An expiry whose inferred strike spacing exceeds a sane bound is skipped, and if none qualifies the selection raises rather than returning its best guess.

**What changed structurally.** Validation moved to the boundary. A bad price used to travel several layers before anything noticed; now it does not enter.

**Where I got lucky.** The same defect later reappeared as a stale strike held across a delayed entry, and by then the logging was good enough to diagnose it in one session instead of four.

## A backwards timestamp that ended a session, correctly

**Summary.** A live session stopped with an unhandled assertion after a vendor's merged partial payloads surfaced an exchange timestamp older than the previous one.

**Trigger.** Partial payloads from that vendor are merged to reconstruct a complete tick. The merge could emit a reconstructed tick carrying an older timestamp than the one before it.

**Detection.** Immediate. The candle builder and the running-average accumulator both refuse a decreasing timestamp, loudly.

**Fix.** Not in the assertion. Both structures are order-dependent, and accepting a backwards tick corrupts the candle that an entry decision is computed from, which converts a stopped session into a wrong trade. The tick is dropped at the vendor boundary, counted, and named in the log.

**What changed structurally.** The count became a gate on trust. That vendor remains diagnostic-only, and the reason recorded is that the warning still fires at a rate I cannot explain.

**Where I got lucky.** The invariant existed before the bug did. Someone wrote a hard assertion into a data structure early, and it caught a defect that no test would have found.
