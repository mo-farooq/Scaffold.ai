# Track: Build an HTTP/1.1 Server from Scratch

Build a high-performance HTTP/1.1 server from raw TCP sockets—without using built-in HTTP modules (e.g. no `http` in Node, no `http.server` in Python).

* **Estimated Time**: 2–3 hours
* **Target Languages**: Python, Node.js, Go, or Rust
* **Core Concepts**: TCP Sockets, RFC 7230 HTTP/1.1 Framing, Request/Response Lifecycle, Header Parsing, Chunked Transfer Encoding, Connection Keep-Alive

---

## 🗺️ Learning Milestones

### Milestone 1: Raw Socket Listener & Request Line Parser
* **Goal**: Accept incoming TCP connections and parse the HTTP request line (`METHOD /path HTTP/1.1`).
* **Key Tasks**:
  1. Bind raw TCP socket to `0.0.0.0:8080`.
  2. Read incoming request buffer and extract Method, Target Path, and HTTP version.
  3. Send back a valid HTTP/1.1 200 OK text response: `HTTP/1.1 200 OK\r\nContent-Length: 13\r\n\r\nHello, world!`.
* **Trade-off to Explore**: Blocking single-process socket vs thread-per-connection vs non-blocking epoll/kqueue.

### Milestone 2: Headers Parser & Routing Dispatcher
* **Goal**: Parse multi-line HTTP headers into key-value pairs and route to specific path handlers.
* **Key Tasks**:
  1. Parse headers until empty CRLF line (`\r\n\r\n`).
  2. Normalize header keys (case-insensitivity per RFC).
  3. Build basic routing table: `/`, `/echo/<str>`, `/user-agent`.
  4. Return proper `404 Not Found` for unrecognized routes.
* **Trade-off to Explore**: Linear route matching vs trie / radix tree dispatch for URL paths.

### Milestone 3: Request Bodies & Content-Length Handling
* **Goal**: Handle POST and PUT requests with arbitrary payloads (JSON, text, binary).
* **Key Tasks**:
  1. Extract `Content-Length` header.
  2. Accurately read exactly N bytes of body, handling TCP packet fragmentation.
  3. Build an endpoint (e.g. `POST /files/<filename>`) that saves the request body to disk.
* **Trade-off to Explore**: Buffering full body in RAM vs streaming directly to disk sink.

### Milestone 4: Keep-Alive & Persistent TCP Connections
* **Goal**: Support multiple HTTP requests over a single persistent TCP connection.
* **Key Tasks**:
  1. Inspect `Connection: keep-alive` (default in HTTP/1.1).
  2. Keep socket open after dispatching response; listen for subsequent requests.
  3. Close connection on `Connection: close` or client inactivity timeout.
* **Trade-off to Explore**: High socket concurrency vs memory overhead of idle persistent connections.
