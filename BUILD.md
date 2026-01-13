# PyInstaller build scripts

The repo includes helper scripts to create a single-file executable of the GUI (`gui.py`) with PyInstaller. Output executables land in `./ejecutable` and temporary build artifacts in `./temp-pyinstaller`. PNG assets from `./lib` are copied to `./ejecutable/lib` so the bundled app can load its images.

Both scripts set the app icon to `lib/ABP.ico`.

## Prerequisites

- Python 3 available in `PATH`.
- PyInstaller installed in the active environment (`pip install pyinstaller`).
- Run the commands from the project root (or let the scripts `cd` there automatically).

## Windows

```powershell
powershell -ExecutionPolicy Bypass -File .\build_windows.ps1
```

The script uses `--onefile` and `--windowed`. It recreates `temp-pyinstaller` on each run and keeps the existing contents of `ejecutable` (overwriting the generated binary name if present).

## Ubuntu/Linux

```bash
chmod +x build_ubuntu.sh
./build_ubuntu.sh
```

The script mirrors the Windows flags and paths. If you prefer a console build, remove `--windowed` inside the script.
