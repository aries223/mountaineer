# Mountaineer - Claude Project Context

## Project Overview

Mountaineer is a Linux desktop application for batch JPEG and PNG image compression. It provides a PyQt6 GUI that wraps two external CLI tools (`jpegoptim`, `oxipng`) with Pillow handling image metadata extraction.

**Version:** 1.1.0
**Target Platform:** Linux (tested on Fedora 42 with KDE and GNOME)
**Language:** Python 3.8+
**GUI Framework:** PyQt6

---

## Directory Structure

```
Mountaineer/
├── CLAUDE.md                      # This file
├── README.md
├── requirements.txt               # PyQt6, Pillow
├── SECURITY.md
├── Mountaineer-1.1.0.spec         # RPM build spec
├── dist/                          # Build output
└── src/
    ├── main.py                    # Entry point
    ├── compression/
    │   ├── base_compressor.py     # Abstract base (subprocess runner)
    │   ├── jpeg_compressor.py     # Wraps jpegoptim
    │   └── png_compressor.py      # Wraps oxipng
    ├── ui/
    │   ├── main_window.py         # Primary window (~725 lines)
    │   ├── about.py               # About dialog
    │   ├── preferences_dialog.py  # Settings dialog
    │   └── logo/
    │       ├── mountaineer.png    # App icon
    │       └── mountaineer.desktop
    └── utils/
        ├── file_utils.py          # Metadata extraction (dimensions, size, format)
        ├── preferences.py         # JSON preferences manager
        ├── signals.py             # PyQt6 signals for thread-safe UI updates
        └── temp_files.py          # Temp file tracker (defined but currently unused)
```

---

## Running the Application

```bash
cd /home/chris/coding-projects/Mountaineer
source venv/bin/activate
python src/main.py
```

**System dependencies required:**
- `jpegoptim` — JPEG compression
- `oxipng` — PNG compression

---

## Architecture & Key Mechanics

### Threading Model
Compression runs in a worker thread. All UI updates are communicated back to the main thread via PyQt6 signals defined in `src/utils/signals.py`. Never update UI directly from the worker thread.

| Signal | Type | Purpose |
|--------|------|---------|
| `progress_updated` | `int` | Progress bar percentage (0–100) |
| `status_updated` | `str` | Status label text |
| `compression_complete` | `str` | Final completion message |
| `compression_result_updated` | `int, str, float` | Per-file result (row index, compressed size, savings %) |

### Compression Commands

**JPEG** (`src/compression/jpeg_compressor.py`):
```
jpegoptim -f -m{quality} [--strip-all] [--dest {dest}] {input}
```
- Quality: 0–100 (default 95)
- Lossless mode: currently stubbed (returns True, no compression performed)

**PNG** (`src/compression/png_compressor.py`):
```
oxipng -o{quality} -f 0-9 [--strip=all] [-a] [--out {dest}] {input}
```
- Quality/level: 0–6 (default 1, lower = more compression)
- Lossless mode: `oxipng -omax -Z --fast`

### Preferences
Stored as JSON at `~/.mountaineer/mountaineer-prefs`.

| Key | Default | Description |
|-----|---------|-------------|
| `jpeg_compression_level` | 95 | jpegoptim -m value |
| `png_compression_level` | 1 | oxipng -o value |
| `lossless_compression` | False | Lossless mode toggle |
| `strip_metadata` | False | Strip EXIF/metadata |
| `main_window_x/y/width/height` | varies | Window geometry |
| `prefs_dialog_x/y/width/height` | varies | Dialog geometry |

### File Table Columns
`File Name | Format | Dimensions | Size | Compressed | Saved`
"Compressed" and "Saved" columns are populated after compression completes.

---

## Known Issues & Stubs

- **Lossless JPEG** is a no-op — `jpeg_compressor.py` returns `True` without running any command when lossless is enabled.
- **`temp_files.py`** is implemented but never called anywhere in the compression workflow.
- **Error handling** is mostly silent — exceptions in compression fall back to "N/A" or are swallowed with no user-facing error dialog.
- **No test suite** exists.
- Scattered `pass # Removed debug print statement` comments throughout the codebase.

---

## Code Conventions

- PyQt6 patterns: signals/slots for threading, `QMainWindow` subclass for the main window
- Compression classes follow a simple strategy pattern: `BaseCompressor` → `JpegCompressor` / `PngCompressor`
- File utilities use Pillow (`PIL.Image.open()`) for format detection and `os.path.getsize()` for sizes
- Human-readable sizes use 1024 boundaries (B → KB → MB → GB)
- Preferences manager handles missing/corrupted files gracefully with defaults
- Window position is only saved if `x > 0 and y > 0` to avoid persisting minimized states

---

## Build & Distribution

The app is packaged as an RPM for Fedora/RHEL via `Mountaineer-1.1.0.spec`.

- Binary installs to: `/usr/local/bin/mountaineer`
- Icon installs to: `/usr/share/pixmaps/mountaineer.png`
- Desktop entry installs to: `/usr/share/applications/mountaineer.desktop`
- Post-install hook runs `update-desktop-database`
