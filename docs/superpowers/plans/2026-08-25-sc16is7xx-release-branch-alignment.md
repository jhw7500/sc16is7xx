# sc16is7xx Release Branch Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `master` carry the driver source used by the official GitLab `pim-package` release while preserving the latest corrected driver on `fix/sc16is7xx-critical-regressions` for the private GitHub workflow.

**Architecture:** Preserve the existing commit graph and avoid force-push. First commit the provenance and branch policy while `master` still contains the latest driver, fast-forward the fix branch to that commit, then restore only `sc16is7xx.c` on `master` from canonical source commit `9f71cb97ff1c0fe2401a0d1b8b6ababbecac2e19` and commit the release alignment.

**Tech Stack:** Git, Linux kernel out-of-tree module build, Markdown, Git LFS package metadata

**Spec:** `docs/sc16is7xx-ext-ko-provenance.md`

## Global Constraints

- `pim-package` is the official GitLab release and its tracked module is the release authority.
- `pim-package-jhw` is a private GitHub workflow repository.
- `sc16is7xx_ext.ko` is excluded from GitHub-to-GitLab synchronization.
- Do not force-push `master` or the fix branch.
- Preserve unrelated working-tree changes in both package repositories.
- The official source baseline is `9f71cb97ff1c0fe2401a0d1b8b6ababbecac2e19` with `sc16is7xx.c` blob `62675b6ee0811dbf6e7bcad0ef95fc534a08a6ae`.
- The private workflow source baseline is merge commit `1788388e038760c899e78009e6a4b1b0e3bdfc8c` with `sc16is7xx.c` blob `070bb868090420f23bebce8bfc1cd17173d20276`.
- The canonical `9f71cb9` source contains 18 pre-existing trailing-whitespace findings. Preserve the exact blob instead of normalizing those lines during this alignment.

---

### Task 1: Record Repository Roles and Branch Policy

**Files:**
- Modify: `docs/sc16is7xx-ext-ko-provenance.md`
- Modify: `/home/jhw/ai/opencode/projects/pim-package/docs/sc16is7xx/build-deploy.md`
- Modify: `/home/jhw/ai/opencode/projects/pim-package-jhw/docs/sc16is7xx/build-deploy.md`

**Interfaces:**
- Consumes: verified package commits `e1ade54` and `158fff4`
- Produces: an explicit source-selection gate for all future builders

- [ ] **Step 1: Document package roles**

State that GitLab `pim-package` is the official release, `pim-package-jhw` is a private workflow repository, and the driver binary is excluded from synchronization.

- [ ] **Step 2: Document branch roles**

State that `master` carries the official `9f71cb9` source content and `fix/sc16is7xx-critical-regressions` carries the latest corrected source content.

- [ ] **Step 3: Verify documentation consistency**

Run:

```bash
git diff --check
rg -n 'official|정식|private|개인|sync|동기화|9f71cb9|1788388|fix/sc16is7xx-critical-regressions' docs/sc16is7xx-ext-ko-provenance.md
```

Expected: no whitespace errors and all policy terms present.

### Task 2: Preserve Latest Source on the Fix Branch

**Files:**
- Commit: `docs/sc16is7xx-ext-ko-provenance.md`
- Commit: `docs/superpowers/plans/2026-08-25-sc16is7xx-release-branch-alignment.md`

**Interfaces:**
- Consumes: current latest source blob `070bb868090420f23bebce8bfc1cd17173d20276`
- Produces: a commit reachable from `fix/sc16is7xx-critical-regressions`

- [ ] **Step 1: Verify the latest source before committing**

Run:

```bash
git rev-parse HEAD:sc16is7xx.c
git diff --check
```

Expected source blob: `070bb868090420f23bebce8bfc1cd17173d20276`.

- [ ] **Step 2: Commit the provenance policy**

Run:

```bash
git add docs/sc16is7xx-ext-ko-provenance.md docs/superpowers/plans/2026-08-25-sc16is7xx-release-branch-alignment.md
git commit -m "docs: define package provenance and branch roles"
```

- [ ] **Step 3: Fast-forward the fix branch and push it**

Run:

```bash
git branch -f fix/sc16is7xx-critical-regressions HEAD
git push origin fix/sc16is7xx-critical-regressions
```

Expected: a fast-forward from `85a3de4` with no force-push.

### Task 3: Align Master Driver Source with the Official Release

**Files:**
- Modify: `sc16is7xx.c`

**Interfaces:**
- Consumes: canonical source tree entry `9f71cb9:sc16is7xx.c`
- Produces: `master:sc16is7xx.c` blob `62675b6ee0811dbf6e7bcad0ef95fc534a08a6ae`

- [ ] **Step 1: Confirm only the driver source differs in build inputs**

Run:

```bash
git diff --name-status 9f71cb9 -- sc16is7xx.c sc16is7xx.h Makefile make-for-imx8
```

Expected: only `sc16is7xx.c` differs.

- [ ] **Step 2: Restore the official source content**

Run:

```bash
git restore --source=9f71cb9 -- sc16is7xx.c
git hash-object sc16is7xx.c
```

Expected blob: `62675b6ee0811dbf6e7bcad0ef95fc534a08a6ae`.

`git diff --check -- sc16is7xx.c` is expected to report the 18 inherited
trailing-whitespace findings from `9f71cb9`. The exact blob check is the release
gate; no new whitespace cleanup is part of this task.

- [ ] **Step 3: Build and inspect the official source**

Run:

```bash
./make-for-imx8
modinfo -p sc16is7xx_ext.ko
modinfo -F vermagic sc16is7xx_ext.ko
```

Expected: no `diag`, `diag_period_ms`, or `rx_trigger` parameters; vermagic is `5.10.35-lts-5.10.y+g2fce14defc04 SMP preempt mod_unload modversions aarch64`.

- [ ] **Step 4: Commit the master release alignment**

Run:

```bash
git add sc16is7xx.c
git commit -m "release: align master driver with official pim-package"
```

### Task 4: Publish and Verify the Final Topology

**Files:**
- No additional file changes

**Interfaces:**
- Consumes: the two commits created by Tasks 2 and 3
- Produces: remote branch pointers and reproducible source blobs

- [ ] **Step 1: Push master without rewriting history**

Run:

```bash
git push origin master
```

Expected: a normal fast-forward from the pre-change `origin/master` head
`fb086e00d8d755c2d1cc331f2b16fb49cf845825`; no history rewrite.

- [ ] **Step 2: Verify remote branch source blobs**

Run:

```bash
git fetch origin
git rev-parse origin/master:sc16is7xx.c
git rev-parse origin/fix/sc16is7xx-critical-regressions:sc16is7xx.c
git merge-base --is-ancestor origin/fix/sc16is7xx-critical-regressions~0 origin/master
```

Expected:

- `origin/master:sc16is7xx.c` is `62675b6ee0811dbf6e7bcad0ef95fc534a08a6ae`.
- `origin/fix/sc16is7xx-critical-regressions:sc16is7xx.c` is `070bb868090420f23bebce8bfc1cd17173d20276`.
- The ancestry check succeeds because master descends from the preserved documentation commit and then restores only the driver source.

- [ ] **Step 3: Verify package documents without committing unrelated work**

Run in each package repository:

```bash
git diff --check
git status --short
```

Expected: only the requested documentation plus pre-existing unrelated changes are present.
