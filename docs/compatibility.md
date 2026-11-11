# Scaffold.ai Compatibility Matrix

Scaffold has one canonical skill package: `skills/scaffold/`. The matrix below separates
the distribution target from behavior that has been manually validated.

| Surface | Installation target | Scripts | Workspace rule | Validation status |
| :--- | :--- | :--- | :--- | :--- |
| skills.sh | GitHub repository via `npx skills add mo-farooq/scaffold` | Included in the skill package | Installed by Scaffold initialization when supported by the host | Package and clean-workspace smoke tests pass; full agent flow pending |
| Codex | Project-scoped `.agents/skills/scaffold/` | Node.js 18+ | `.agents/rules/` when the host loads workspace rules | Repository layout supported; manual first-session validation pending |
| Claude Code | Host skill directory via skills.sh or local installation | Node.js 18+ | `CLAUDE.md` notice plus `.agents/rules/` where applicable | Manual first-session validation pending |
| Cursor | Host skill directory via skills.sh | Node.js 18+ | Host-specific rule loading must be verified | Manual first-session validation pending |
| Google Antigravity | Host skill directory via skills.sh or local installation | Node.js 18+ | `.agents/rules/` | Manual first-session validation pending |
| OpenCode | Host skill directory via skills.sh | Node.js 18+ | Host-specific rule loading must be verified | Manual first-session validation pending |

## Validation Standard

A surface may be labeled **fully supported** only after a maintainer completes this flow in
a clean repository:

1. Install or copy the canonical skill.
2. Start `/scaffold track redis`.
3. Confirm the first-session briefing names the active milestone, ownership boundary, and
   next action.
4. Confirm `PROGRESS.md` and the workspace rule are available.
5. Confirm the host preserves the `TODO(scaffold)` boundary when the learner asks for help.
6. Confirm premature verification leaves progress unchanged.
7. Complete Milestone 1 and confirm the reflection flow records the result.

Until that manual flow is complete, use **validation pending** in public claims rather than
calling the surface native or fully supported.

## Compatibility Boundary

Scaffold's Node.js scripts are deterministic and dependency-free. The conversational
guardrails, hint quality, and ability to honor the learner-owned code boundary depend on the
host agent. Scaffold therefore guarantees the package and script behavior, while agent
behavior remains an integration property to validate per surface.
