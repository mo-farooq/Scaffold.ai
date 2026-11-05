# Scaffold Architectural Reflection & Trade-off Prompts

Use this library of targeted questions when challenging learners at the end-of-milestone Reflection Gate. Choose or adapt the question that best matches the code the student just wrote.

---

## 1. Concurrency, I/O & Networking

* **Event Loop vs Worker Threads**:
  *"We chose a single-threaded event loop to handle concurrent connections. Under what specific workload pattern will this architecture cause high tail latencies, and how would you redesign it to mitigate that?"*
* **TCP Stream Framing**:
  *"TCP is a byte-stream protocol, not a message protocol. Why does reading from a socket not guarantee receiving a full command in a single `data` event, and how does your framing buffer handle fragmented packets?"*
* **Backpressure**:
  *"If a client sends write requests faster than our storage engine can flush them to disk, what prevents our application from exhausting memory? How would you implement backpressure here?"*

---

## 2. Data Modeling & Storage Systems

* **In-Memory Hash Map vs Append-Only Log (AOF)**:
  *"An in-memory hash table gives $O(1)$ reads and writes, but loses everything on a process crash. If we add an append-only log, what is the trade-off between write throughput, disk space amplification, and recovery startup time?"*
* **Mutable State vs Immutability**:
  *"Why did we choose an immutable data structure / frozen record here instead of mutating an object in place? What performance penalty did we trade away to gain safety?"*
* **Indexing & B-Trees**:
  *"Why do relational databases like SQLite use B+ Trees instead of Hash Tables for disk-based storage, even though Hash Tables have $O(1)$ average lookup complexity?"*

---

## 3. Protocol Design & Serialization

* **Binary vs Text Protocols**:
  *"What are the performance and developer-experience trade-offs of using Redis's RESP protocol compared to sending JSON payloads over HTTP?"*
* **Buffer Allocation & Zero-Copy**:
  *"When parsing network payloads, when is it safe to slice an existing buffer vs allocating a new memory block? How does this impact garbage collection overhead in long-running services?"*

---

## 4. API Design, Rate Limiting & Resilience

* **Sliding Window vs Token Bucket**:
  *"We implemented a Token Bucket algorithm for rate limiting. In what scenario would a Sliding Window Counter provide stricter enforcement against burst traffic at window boundaries, and what is the extra memory cost?"*
* **Idempotency**:
  *"If a network timeout occurs while a client is creating a resource, how does your system ensure that retrying the exact same request does not duplicate the record?"*
* **Graceful Degradation & Timeouts**:
  *"What happens if an upstream API hangs indefinitely? What specific timeout and circuit breaker strategy did we implement to protect the main application loop?"*

---

## 5. Domain-Specific Starter Track Prompts

### Redis from Scratch
* *Milestone 1 (TCP Server & RESP)*: *"Why does RESP use explicit length prefixes (`$4\r\nECHO`) instead of relying on null terminators or JSON parsing?"*
* *Milestone 2 (Key-Value Store)*: *"How does our dictionary handle key expiration? What are the trade-offs between active sampling vs passive lazy expiration?"*

### Git from Scratch
* *Milestone 1 (Blob Object Store)*: *"Why does Git hash the header `blob <size>\0` together with the file content, rather than hashing just the raw file bytes?"*
* *Milestone 2 (Tree & Commit Objects)*: *"How does Git's Merkle tree structure make checking whether two repository states are identical an $O(1)$ operation?"*

### HTTP Server from Scratch
* *Milestone 1 (Socket Accept Loop)*: *"Why is `SO_REUSEADDR` crucial for local socket servers, and what security risk does it carry in multi-user operating systems?"*
* *Milestone 2 (HTTP/1.1 Keep-Alive)*: *"How does HTTP/1.1 persistent connections affect server resource consumption compared to opening a new TCP connection per request?"*
