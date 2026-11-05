# Track: Build a Container Runtime (Docker) from Scratch

Build a lightweight container runtime from scratch that can isolate processes, filesystem roots, network interfaces, and resource limits using operating system primitives.

* **Estimated Time**: 3–5 hours
* **Target Languages**: Go, Python, or C (Linux/macOS container concepts)
* **Core Concepts**: Linux Namespaces (PID, Mount, Net, UTS, IPC), Control Groups (cgroups v2), OverlayFS & Chroot/Pivot_Root, Process Isolation

---

## 🗺️ Learning Milestones

### Milestone 1: Process Isolation with UTS & PID Namespaces
* **Goal**: Launch an isolated child process with its own hostname and process tree where the root process sees itself as PID 1.
* **Key Tasks**:
  1. Execute a subprocess with clone flags (`CLONE_NEWUTS`, `CLONE_NEWPID`).
  2. Set a custom container hostname without affecting the host OS.
  3. Verify that running `ps` inside the child process only shows container processes.
* **Trade-off to Explore**: OS-level container isolation vs hypervisor hardware virtualization (VMs).

### Milestone 2: Filesystem Jails with `chroot` and `pivot_root`
* **Goal**: Prevent the containerized process from accessing or modifying the host filesystem.
* **Key Tasks**:
  1. Download or unpack an Alpine root filesystem image into a local directory.
  2. Use `pivot_root` / `chroot` to re-bind the container's root directory (`/`).
  3. Mount a container-local `/proc` virtual filesystem.
* **Trade-off to Explore**: Simple `chroot` jail limitations vs secure `pivot_root` mount namespaces.

### Milestone 3: Resource Limiting with cgroups
* **Goal**: Restrict the container process's maximum RAM and CPU consumption.
* **Key Tasks**:
  1. Create a container cgroup in `/sys/fs/cgroup/`.
  2. Configure `memory.max` (e.g. limit to 50MB) and `cpu.max`.
  3. Attach the container PID to the cgroup tasks list and run a stress test to observe eviction/throttling.
* **Trade-off to Explore**: Hard memory OOM-killing vs soft limit throttling and page swapping.

### Milestone 4: Layered Filesystems (OverlayFS)
* **Goal**: Share a base read-only filesystem image among multiple containers while keeping writes in an ephemeral layer.
* **Key Tasks**:
  1. Configure `lowerdir` (base rootfs), `upperdir` (writable layer), and `workdir`.
  2. Mount an `overlay` filesystem combining lower and upper directories.
  3. Verify that modifying a file creates a copy-on-write replica in the upper directory without mutating the base image.
* **Trade-off to Explore**: Copy-on-write overlay layers vs full directory cloning for storage efficiency.
