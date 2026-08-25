# sc16is7xx History Restoration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore the original `master` commit lineage and stack the organized fix and clangd commits on top without losing the current repository content.

**Architecture:** Reconstruct candidate branches from the archived pre-rewrite `master`, replay only the post-rewrite documentation and organized feature commits, and compare candidate trees with the current remote trees before moving any public ref. Preserve every displaced ref under an archive tag and update public refs only with explicit `--force-with-lease` expectations.

**Tech Stack:** Git refs, reflog, annotated archive tags, Linux kernel out-of-tree module build

**Spec:** `docs/superpowers/plans/2026-08-25-sc16is7xx-release-branch-alignment.md`

## Global Constraints

- Preserve the complete original `master` ancestry through `f95575c9d19aa8644b89ba3b7d92ed598b12868d`.
- Preserve the rewritten tips `ae7e173`, `c177dde`, and `e6549a1`, plus the newer remote master tip `912d238`, under archive tags before moving refs.
- Keep the four organized driver commits as separate commits on top of the restored master.
- Keep the clangd build commit as a separate commit on top of the restored fix branch.
- Do not change tracked file content except for this audit plan; candidate trees must match the current trees when this plan file is excluded.
- Update public refs only with `--force-with-lease=<expected-current-sha>`.

---

### Task 1: Preserve Current Rewritten Tips

**Files:**
- Create: annotated archive tags only

- [ ] Verify current remote SHA values for `master`, `fix/sc16is7xx-critical-regressions`, and `chore/clangd-compile-db`.
- [ ] Create and push archive tags for `ae7e173`, `912d238`, `c177dde`, and `e6549a1`.
- [ ] Confirm the tags peel to the expected commits.

### Task 2: Reconstruct Master on the Original Lineage

**Files:**
- Modify: `docs/sc16is7xx-ext-ko-provenance.md`
- Modify: `docs/superpowers/plans/2026-08-25-sc16is7xx-release-branch-alignment.md`
- Create: `docs/superpowers/plans/2026-08-25-sc16is7xx-history-restoration.md`

- [ ] Start from archived original master `f95575c`.
- [ ] Cherry-pick `1db36fc`, `ae7e173`, and the newer workflow merge `912d238` in order.
- [ ] Commit this restoration plan as `docs: document history restoration`.
- [ ] Verify the reconstructed tree equals `912d238`, excluding this plan file.

### Task 3: Stack Organized Driver Changes

**Files:**
- Modify: `sc16is7xx.c`

- [ ] Create the repaired fix branch from the repaired master.
- [ ] Cherry-pick `4024be8`, `8a1b74b`, `213ae0a`, and `ec75a5e` in order.
- [ ] Verify the reconstructed tree equals `c177dde`, excluding this plan file.
- [ ] Build the kernel module and verify its metadata.

### Task 4: Stack the Clangd Build Commit

**Files:**
- Create: `.clangd`
- Modify: `.gitignore`
- Modify: `make-for-imx8`

- [ ] Create the repaired clangd branch from the repaired fix branch.
- [ ] Cherry-pick `e6549a1`.
- [ ] Verify the reconstructed tree equals the current clangd branch, excluding this plan file.

### Task 5: Publish with Leases and Verify

**Files:**
- No additional file changes

- [ ] Move local public branch refs to the verified candidate tips.
- [ ] Push `master`, fix, and clangd refs with exact force-with-lease SHA guards.
- [ ] Fetch and verify remote SHA values, archive tags, ancestry, commit order, tree equivalence, clean diff checks, and a fresh module build.
