# Track: Build a Mini SQLite Clone from Scratch

Build an embedded relational database engine from scratch featuring a custom binary file format, page-based memory buffer, and SQL parsing.

* **Estimated Time**: 4–6 hours
* **Target Languages**: Python, Node.js, Go, or Rust
* **Core Concepts**: B+ Trees, Paged Storage & Page Cache, Byte Serialization, Virtual Database Engine (VDBE), SQL Lexing & Parsing

---

## 🗺️ Learning Milestones

### Milestone 1: REPL & In-Memory Table
* **Goal**: Build an interactive database shell (`.exit`, `.help`) and simple hardcoded table structure.
* **Key Tasks**:
  1. Build a command-line REPL loop.
  2. Implement a fixed-schema Row structure (e.g. `id: int`, `username: string(32)`, `email: string(255)`).
  3. Parse raw commands: `insert <id> <user> <email>` and `select`.
* **Trade-off to Explore**: Fixed-width rows vs variable-width encoded fields.

### Milestone 2: Paged Disk Storage & Binary Serialization
* **Goal**: Serialize rows into fixed-size 4KB memory pages and persist them to a `.db` binary file.
* **Key Tasks**:
  1. Implement a `Pager` component that reads and writes 4096-byte blocks.
  2. Pack Row structs into binary bytes using little-endian byte ordering.
  3. On startup, load existing pages from disk; on close, flush dirty pages.
* **Trade-off to Explore**: Direct filesystem I/O vs memory-mapped files (`mmap`).

### Milestone 3: B-Tree Node Implementation (Leaf Nodes)
* **Goal**: Implement a B-Tree leaf node to keep records ordered by primary key (`id`).
* **Key Tasks**:
  1. Define B-Tree Node Header: `node_type`, `is_root`, `parent_pointer`, `num_cells`.
  2. Implement binary search within a leaf page to locate cell positions.
  3. Support inserting cells in sorted order up to page capacity.
* **Trade-off to Explore**: Append-only storage with periodic compaction vs self-balancing B-Trees.

### Milestone 4: Node Splitting & Internal Nodes
* **Goal**: Handle page overflow by splitting full leaf nodes and creating parent routing nodes.
* **Key Tasks**:
  1. Split leaf node into two halves when maximum capacity is exceeded.
  2. Create an internal root node with divider keys and child pointers.
  3. Support full tree traversal during `SELECT` queries.
* **Trade-off to Explore**: B-Tree vs B+ Tree: storing records in leaves vs internal nodes.
