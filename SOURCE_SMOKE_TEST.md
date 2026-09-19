# macOS/Linux Source Smoke Test

This smoke test defines the minimum source-level acceptance path for running
RPX Pro outside the Windows build. It does not replace a real tabletop session
test; it proves that the source tree still exposes the cross-platform contracts
needed for a manual macOS or Linux launch.

## Scope and test matrix

| Layer | Linux | macOS | Evidence type |
|---|---|---|---|
| Source/CI | `ubuntu-latest`, Python 3.12 | `macos-latest`, Python 3.12 | Automated import, backend, file-dialog, monitor-routing, and compile smoke |
| Desktop launch | A supported desktop session (X11 or Wayland) | A visible macOS window session | Manual launch and interaction record |
| Display | One monitor; repeat with a second monitor when available | One monitor; repeat with a second monitor when available | Manual geometry/fullscreen record |
| Audio | Qt Multimedia or `pygame`; unavailable audio is an allowed warning path | Qt Multimedia or `pygame`; unavailable audio is an allowed warning path | Backend/log record, never a crash-only claim |

The CI job is a source contract check. It cannot prove physical audio output,
window-manager behavior, a real file picker, or second-monitor geometry.
Those claims require the manual target-desktop row of the matrix.

## Prerequisites

- A local Git clone (do not run this from an OneDrive-synchronised worktree).
- Python 3.10 or newer, a visible desktop session for the manual row, and a
  readable PNG or JPG fixture for the file-picker row.
- Install the source dependencies and the test runner:

  ```bash
  python -m pip install -r requirements.txt pytest
  ```

- `PySide6` is required for the desktop and Qt import paths. `pygame` is an
  optional audio fallback; a machine without a working audio device must still
  produce a clear warning and keep the application usable.
- A second physical/virtual display is optional for the single-monitor row but
  required to claim the second-monitor row.

## Automated source smoke

Run from a local clone, not from a OneDrive-synced worktree:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pytest
python -m pytest -q tests/test_source_platform_smoke.py
```

The automated smoke covers:

- application entry-point imports without starting the Qt event loop;
- Linux/macOS audio selection cannot fall back to Windows-only `winsound`;
- the player-screen controller still exposes monitor selection, fullscreen
  routing, and second-screen geometry handoff;
- image file selection still uses native Qt file dialogs;
- the packaged source still compiles.

Expected result: the command exits with code 0 and every source-smoke test
passes. The GitHub Actions `source-smoke` matrix runs the same command on
`ubuntu-latest` and `macos-latest` with Python 3.12. A green CI job is useful
source evidence, but is not hardware evidence.

## Manual launch smoke (target desktop)

Run this on the target machine with a visible desktop session:

```bash
python -m rpx_pro.app
```

Pass criteria:

- the main window opens without import, Qt platform, or resource errors;
- audio initialization logs either `QtMultimedia` or `pygame`, or a clear
  "audio unavailable" warning without crashing the app;
- `Spieler-Bildschirm > Spieler-Bildschirm öffnen` opens the player display;
- with a second monitor connected, the player display is moved to the selected
  screen and enters fullscreen;
- with only one monitor connected, the player display opens as a normal window;
- `Bild laden...` accepts a local PNG/JPG via the native file picker and renders
  it on the player display.

Run the manual rows once on Linux and once on macOS when both targets are in
scope. Record a failed optional row as `not available` with its reason; do not
convert an unavailable audio device or display into a passing claim.

## Boundaries and non-goals

- Windows remains the primary desktop and release line. This smoke does not
  change `START.bat`, the PyInstaller spec, MSIX, Store, WACK, signing, or the
  Windows test matrix.
- This is not evidence for a macOS app bundle, DMG, Homebrew package,
  Flatpak/deb/rpm package, notarisation, or distribution-channel acceptance.
- Backend behavior can vary with Qt plugins, `pygame`/SDL, audio devices,
  display servers, window managers, and macOS permissions. The source smoke
  proves the fallback contract, not every driver or compositor combination.
- Headless CI or `xvfb` can supplement import/compile checks but cannot replace
  the visible manual rows for audio, file dialogs, fullscreen, or monitors.

## Evidence location

Store one Markdown run note per target under
`docs/evidence/source-smoke/<YYYY-MM-DD>-<os>-<python>.md`. Include the commit
SHA, OS/version, Python version, dependency versions, display count, selected
audio backend (or the exact unavailable warning), fixture used, automated
command and result, each manual row's result, and the CI run URL/SHA when one
exists. The directory is an evidence register; it is not a release artifact.
