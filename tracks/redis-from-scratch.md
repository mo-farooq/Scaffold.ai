# Track: Build a Redis Clone from Scratch

Build an in-memory key-value database that speaks the real Redis Serialization Protocol (RESP) and connects with the official `redis-cli`.

* **Estimated Time**: 2–4 hours
* **Target Languages**: Python, Node.js, Go, or Rust
* **Core Concepts**: Raw TCP Sockets, RESP Protocol Parsing, $O(1)$ Hash Stores, TTL & Key Expiration, Append-Only Log Persistence (AOF)

---

## 🗺️ Learning Milestones

### Milestone 1: TCP Server & PING / ECHO
* **Goal**: Establish a raw TCP server that accepts client connections and handles the basic PING / ECHO command loop.
* **Key Tasks**:
  1. Bind a TCP server to `127.0.0.1:6379`.
  2. Implement initial RESP stream reader.
  3. Respond to `PING` with `+PONG\r\n` and `ECHO <msg>` with a bulk string.
  4. Verify by running `redis-cli ping` from your terminal!
* **Trade-off to Explore**: Text protocol parsing vs length-prefixed binary buffers.

### Milestone 2: Full RESP Parser & Multi-Bulk Arrays
* **Goal**: Support standard client commands encoded as RESP arrays (`*<count>\r\n$<len>\r\n...`).
* **Key Tasks**:
  1. Parse nested arrays of bulk strings without dropping bytes.
  2. Handle fragmented TCP chunks across multiple network packets.
  3. Standardize command dispatch (normalize command names to uppercase).
* **Trade-off to Explore**: Streaming parser with state machine vs reading entire buffers in memory.

### Milestone 3: In-Memory Key-Value Storage (GET / SET / DEL)
* **Goal**: Store and retrieve string values in memory with constant-time lookup.
* **Key Tasks**:
  1. Implement a thread-safe / event-loop-safe storage table.
  2. Implement `SET key value` and `GET key` (returning `$-1\r\n` on nil).
  3. Implement `DEL key`, `EXISTS key`, and `KEYS *`.
* **Trade-off to Explore**: Single-threaded event loop (real Redis model) vs concurrent mutex-locked maps.

### Milestone 4: TTL & Key Expiration Engine
* **Goal**: Support automatic data eviction using time-to-live (`EXPIRE` and `TTL`).
* **Key Tasks**:
  1. Implement `SET key value EX seconds` and `EXPIRE key seconds`.
  2. Implement lazy expiration (evicting expired keys on access).
  3. Implement active sampling background loop (cleaning random expired keys periodically).
* **Trade-off to Explore**: Lazy expiration vs periodic active cleanup: memory pressure vs CPU cycles.

### Milestone 5: Crash Durability with Append-Only Log (AOF)
* **Goal**: Persist state to disk so data survives server restarts.
* **Key Tasks**:
  1. Append successful write commands to an `appendonly.aof` file.
  2. On server boot, read and replay the AOF file to reconstruct in-memory state.
  3. Handle `fsync` flush intervals.
* **Trade-off to Explore**: `fsync=always` (safe, slow) vs `fsync=everysec` (industry standard) vs `fsync=no` (risk of data loss).
