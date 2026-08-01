# macOS/Linux Source Smoke Test

This smoke test defines the minimum source-level acceptance path for running
RPX Pro outside the Windows build. It does not replace a real tabletop session
test; it proves that the source tree still exposes the cross-platform contracts
needed for a manual macOS or Linux launch.

## Automated source smoke

Run from a local clone, not from a OneDrive-synced worktree:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pytest
python -m pytest tests/test_source_platform_smoke.py
```

The automated smoke covers:

- application entry-point imports without starting the Qt event loop;
- Linux/macOS audio selection cannot fall back to Windows-only `winsound`;
- the player-screen controller still exposes monitor selection, fullscreen
  routing, and second-screen geometry handoff;
- image file selection still uses native Qt file dialogs;
- the packaged source still compiles.

## Manual launch smoke

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

Record the OS, Python version, display count, selected audio backend, and the
result of the automated command when closing the smoke.
