# Scaffold.ai — Definition of Done (DoD)

A milestone or feature is objectively **DONE** when it satisfies all of the following verification criteria:

---

## Verification Criteria Checklist

- [ ] **1. Feature Completeness**: All user stories, core functions, and error handling for the milestone are implemented.
- [ ] **2. Type Hints Complete**: All new/modified functions and classes have explicit Python 3.12+ type annotations.
- [ ] **3. Quality Gates Passing**: `scripts/verify.sh` executes cleanly with zero errors across formatting, linting, type checking, and tests.
- [ ] **4. Test Coverage**: 100% of unit tests pass, and new functionality is backed by automated tests in `tests/`.
- [ ] **5. Protocol Validation**: AI agent outputs adhere to the Learning Mode protocol rules with a validator score ≥ 0.85.
- [ ] **6. Documentation Updated**: `README.md`, `architecture.md`, `roadmap.md`, and relevant ADRs reflect the new changes.
- [ ] **7. Clean Code & Zero Debt**: No remaining `TODO`, `FIXME`, or temporary debug statements in production code.
- [ ] **8. Preview CLI Verification**: Interactive preview CLI script executes successfully end-to-end.
- [ ] **9. Walkthrough Updated**: `walkthrough.md` updated with empirical verification results.
- [ ] **10. Git Auto-Sync**: Git working tree is clean, committed with a conventional commit message, and pushed to `origin main`.
