# Track: Build Git from Scratch

Build a content-addressable version control system from scratch that can initialize repos, hash objects, create commits, and inspect history using real Git object formats.

* **Estimated Time**: 3–5 hours
* **Target Languages**: Python, Node.js, Go, or Rust
* **Core Concepts**: SHA-1 / SHA-256 Content-Addressing, zlib Deflate Compression, Merkle Trees, DAGs (Directed Acyclic Graphs), Git Index & Reflog

---

## 🗺️ Learning Milestones

### Milestone 1: Initialize Repo & Write Blob Objects (`init` & `hash-object`)
* **Goal**: Create `.git/` internal directory structure and write compressed blob objects.
* **Key Tasks**:
  1. Implement `mygit init`: create `.git/objects`, `.git/refs/heads`, and `HEAD` pointing to `ref: refs/heads/main`.
  2. Implement `mygit hash-object -w <file>`: prepend header `blob <size>\0`, compute SHA-1, compress with zlib deflate, and write to `.git/objects/<xx>/<xxxx...>`.
  3. Verify with official `git cat-file -p <hash>`.
* **Trade-off to Explore**: Why does Git store raw content hashes rather than delta diffs for objects?

### Milestone 2: Read & Inspect Objects (`cat-file`)
* **Goal**: Decompress and inspect any object type (`blob`, `tree`, `commit`) from `.git/objects`.
* **Key Tasks**:
  1. Read object header, parse type string and byte size.
  2. Implement `mygit cat-file -t <hash>` (print type) and `mygit cat-file -p <hash>` (pretty-print content).
  3. Handle partial/abbreviated hashes (e.g. 7-character prefix matching).
* **Trade-off to Explore**: Decompressing on every read vs caching unpacked objects.

### Milestone 3: Hierarchical Trees (`write-tree` & `ls-tree`)
* **Goal**: Construct Git's directory tree objects representing file snapshots and permissions.
* **Key Tasks**:
  1. Format tree entries: `<mode> <filename>\0<20-byte-binary-sha>`.
  2. Recursively generate tree objects for directory structures.
  3. Implement `mygit ls-tree <tree-hash>` to view directory contents.
* **Trade-off to Explore**: Flat file tables vs recursive Merkle trees for change detection.

### Milestone 4: Commits & History Graph (`commit-tree` & `log`)
* **Goal**: Link trees into an immutable DAG of commits with metadata, authors, and parents.
* **Key Tasks**:
  1. Construct commit object payload: `tree <hash>`, `parent <hash>`, `author ...`, `committer ...`, and commit message.
  2. Implement `mygit commit-tree <tree-hash> -m "First commit"`.
  3. Implement `mygit log`: traverse the commit graph backwards following `parent` pointers.
* **Trade-off to Explore**: Content-addressable DAGs vs monotonic revision numbers (like Subversion).
