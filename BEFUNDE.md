# Maintainer findings — 2026-08-10

## Scope and baseline

- Project: `C:\_LOCAL_DEV\repos\rpx`
- Branch: `master`, HEAD `c412539` (`docs: complete cross-platform source smoke matrix`)
- Initial local status: `master...origin/master [ahead 1]`; this is the existing local
  ref comparison, not a fresh remote readback. No fetch, push, signing, Store upload,
  WACK run, or device/CI acceptance was performed.
- Pre-existing Web Companion changes were preserved unchanged: six tracked files
  (`manifest.webmanifest` plus five PNGs) and nine untracked icon/favicon assets.

## Current clone readback — 2026-08-10

- Fresh readback before this slice: HEAD is `6d7876658770c078657183e69548759c2e907c0e`; the existing local `origin/master` ref is `e13d17210971a6d816695bc72ddb0a6946ffc29f`; the local comparison is `master...origin/master [ahead 2]`. This is not a live-remote parity claim.
- `git ls-remote origin HEAD refs/heads/master` currently returns `3e35863233af76729a4d8004bd5a595fb4b5d419` for both references. No fetch, rebase, or push was run; ancestry and parity against that live head remain unestablished.
- The working tree contains exactly the six previously observed modified tracked Web Companion files (`manifest.webmanifest` plus five PNGs) and nine untracked icon/favicon assets. No staged changes or unmerged entries were present.
- `git diff --check` and `git diff --cached --check` pass. `.git/index.lock`, `.git/HEAD.lock`, `.git/MERGE_HEAD`, `.git/REBASE_HEAD`, and `.git/CHERRY_PICK_HEAD` are absent.

## Verification

- `python -X utf8 -m pytest -q`: **14 passed**.
- `python -X utf8 -m pytest -q tests/test_source_platform_smoke.py`: **5 passed**.
- `python -B -m compileall -q RPX_Pro_1.py manage_translations.py translator.py rpx_pro tests`:
  **pass**.
- Node Web Companion tests: **17 passed, 0 failed**.
- `node --check` for `app.js`, `library.js`, and `sw.js`: **all pass**.
- `python -m ruff check .`: **42 pre-existing findings** (mostly unused imports and
  three import-order findings); no lint cleanup was attempted in this maintenance
  slice.

## Open finding: foreign PWA manifest is not case-sensitive-path safe

The current working-tree manifest references these lowercase paths:

- `icons/icon-192.png`
- `icons/icon-maskable-192.png`
- `icons/icon-512.png`
- `icons/icon-maskable-512.png`

The exact repository paths are the uppercase `Icon-*.png` variants. A case-sensitive
path audit therefore reports **four exact misses**, each with one case-folded match.
The current Windows Node tests do not detect this because the host filesystem resolves
the paths case-insensitively. The service worker still caches the uppercase paths, so
the manifest and offline shell are inconsistent on a case-sensitive host.

The manifest also references root-level `favicon.png` and `apple-touch-icon-180.png`;
those files exist only as current untracked user assets and are not in the tracked tree.
They must not be treated as reproducible repository assets until the owning lane adopts
them deliberately.

Recommended owner action: choose one exact filename convention, make manifest and
service-worker paths agree, and add a case-sensitive manifest-asset existence test.
This run does not edit those foreign files or adopt the untracked binaries.

## Acceptance boundary

The automated local source/PWA checks are green, but the TASKWRITER gates for manual
desktop launch, Android/iOS installation and offline restart, CI run evidence, Windows
Store packaging, WACK, signing, and release metadata remain open. No live, device,
release, or store acceptance claim is made.

## Mutation boundary

Only this report was created. No foreign Web Companion file, source file, generated
asset, or untracked user binary was overwritten, deleted, staged, or committed.
