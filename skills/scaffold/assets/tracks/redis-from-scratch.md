# Track: Build a Redis Clone from Scratch

Redis is Scaffold's recommended first systems track. It is small enough to produce a
working result quickly, but rich enough to teach networking, protocols, state, expiration,
and durability.

* **Estimated Time**: 2–4 hours
* **Target Languages**: Python, Node.js, Go, or Rust
* **Core Concepts**: Raw TCP sockets, RESP protocol parsing, $O(1) hash stores, TTL and key expiration, append-only log persistence (AOF)

## First Observable Win

By the end of Milestone 1, the learner should be able to connect with `redis-cli`, send
`PING` or `ECHO`, and explain how a TCP byte stream becomes a RESP command.

## 🗺️ Learning Milestones

### Milestone 1: TCP Server & PING / ECHO

* **Goal**: Establish a raw TCP server that accepts client connections and handles the
  basic PING / ECHO command loop.
* **Observable outcome**: `redis-cli ping` receives `PONG`, and `ECHO` returns the expected
  bulk string.
* **Learner-owned concept**: Message boundaries in a TCP byte stream and the first RESP
  framing rules.
* **Expected artifact**: A runnable server plus focused tests or a repeatable `redis-cli`
  verification.
* **Primary failure mode**: Assuming one socket `data` event contains one complete command.
* **Key tasks**:
  1. Bind a TCP server to `127.0.0.1:6379`.
  2. Implement the initial RESP stream reader.
  3. Respond to `PING` with `+PONG\r\n` and `ECHO <msg>` with a bulk string.
  4. Verify the result with `redis-cli` or an equivalent client.
* **Trade-off to explore**: Text protocol parsing versus length-prefixed binary buffers.
* **Reflection question**: Why does RESP use explicit length prefixes instead of relying on
  null terminators or JSON parsing?

### Milestone 2: Full RESP Parser & Multi-Bulk Arrays

* **Goal**: Support standard client commands encoded as RESP arrays
  (`*<count>\r\n$<len>\r\n...`).
* **Observable outcome**: The server accepts multi-argument commands even when input is
  fragmented across multiple TCP chunks.
* **Learner-owned concept**: Incremental parsing as a state machine with incomplete input.
* **Expected artifact**: Parser tests covering complete, fragmented, nested, and malformed
  RESP values.
* **Primary failure mode**: Dropping bytes or reading beyond a declared bulk-string length.
* **Key tasks**:
  1. Parse nested arrays of bulk strings without dropping bytes.
  2. Handle fragmented TCP chunks across multiple network packets.
  3. Normalize command names to uppercase before dispatch.
* **Trade-off to explore**: Streaming parser state machine versus buffering complete requests.
* **Reflection question**: What state must survive when a chunk ends halfway through a bulk
  string?

### Milestone 3: In-Memory Key-Value Storage (GET / SET / DEL)

* **Goal**: Store and retrieve string values with constant-time average lookup.
* **Observable outcome**: `SET`, `GET`, `DEL`, `EXISTS`, and `KEYS *` behave predictably from
  a Redis client.
* **Learner-owned concept**: State ownership, mutation boundaries, and event-loop safety.
* **Expected artifact**: Storage and command-dispatch tests, including missing keys.
* **Primary failure mode**: Returning stale values or exposing mutable state across commands.
* **Key tasks**:
  1. Implement an event-loop-safe storage table.
  2. Implement `SET key value` and `GET key`, returning `$-1\r\n` for nil.
  3. Implement `DEL key`, `EXISTS key`, and `KEYS *`.
* **Trade-off to explore**: A single-threaded event loop versus concurrent mutex-locked maps.
* **Reflection question**: Which operations remain safe if command handling later becomes
  concurrent?

### Milestone 4: TTL & Key Expiration Engine

* **Goal**: Support automatic data eviction using time-to-live.
* **Observable outcome**: Expired keys disappear on access and are reported correctly by
  `TTL`.
* **Learner-owned concept**: Time-based state validity and bounded cleanup work.
* **Expected artifact**: Tests using a controllable clock or short deterministic expirations.
* **Primary failure mode**: Expired data remaining in memory indefinitely under low traffic.
* **Key tasks**:
  1. Implement `SET key value EX seconds` and `EXPIRE key seconds`.
  2. Implement lazy expiration when a key is accessed.
  3. Implement active sampling to clean expired keys periodically.
* **Trade-off to explore**: Lazy expiration versus periodic active cleanup.
* **Reflection question**: Which workload makes lazy expiration retain too much memory, and
  what CPU cost does active sampling introduce?

### Milestone 5: Crash Durability with Append-Only Log (AOF)

* **Goal**: Persist state so data survives a server restart.
* **Observable outcome**: Successful writes replay from an AOF file after process restart.
* **Learner-owned concept**: Recovery ordering, durability guarantees, and failure windows.
* **Expected artifact**: Restart tests covering valid logs, partial final records, and replay.
* **Primary failure mode**: Replaying a partial or corrupted write and producing invalid state.
* **Key tasks**:
  1. Append successful write commands to `appendonly.aof`.
  2. Read and replay the AOF at server boot.
  3. Handle `fsync` flush intervals and explain the possible data-loss window.
* **Trade-off to explore**: `fsync=always`, `fsync=everysec`, and `fsync=no`.
* **Reflection question**: What can be lost or corrupted under each flush policy if the
  process or machine fails at the worst possible moment?
