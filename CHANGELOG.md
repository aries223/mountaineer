# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

## [1.1.0] - 2026-02-21

### Added

- GIF and WebP compression support via `gifsicle` and `cwebp`
- Keyboard shortcuts: Ctrl+O (Add Files), Ctrl+Shift+O (Add Folder), Ctrl+Q (Quit), Ctrl+A (Select All), Ctrl+, (Preferences), Delete (Remove Selected)
- Startup check for required CLI tools with a warning dialog if any are missing
- One-time overwrite confirmation dialog with a "Don't show again" option
- Compression completion summary showing success and failure counts (e.g. "12/15 files compressed. 3 failed.")
- Tooltips on all four format sliders in Preferences
- Documentation item in the Help menu
- User guide at `Documentation/Documentation.md`
- Application log written to `~/.mountaineer/mountaineer.log`
- Recursive subdirectory traversal in Add Folder and drag-and-drop
- Per-file existence check before compression with an informative skip message
- Negative savings percentage shown in red when a file grows after compression
- Sortable file list columns; sorting is automatically disabled while compression is running

### Changed

- Project re-licensed from proprietary EULA to GNU AGPLv3
- SPDX license identifier (`AGPL-3.0-or-later`) added to all Python source files
- SECURITY.md updated to reflect open source status and GitHub-based vulnerability reporting
- Preferences dialog sliders now show tick-mark scale labels instead of verbose parenthetical range hints
- Preferences dialog has improved padding, alignment, and layout polish
- File list table columns are now manually resizable; the Saved column no longer stretches to fill remaining space
- About dialog logo falls back to the source-relative path when the application is not installed system-wide
- About dialog link colour now adapts to the system theme
- Lossless JPEG compression now fully implemented (`jpegoptim --optimize --all-progressive`) instead of a no-op stub
- Window position is validated against screen bounds before being restored from preferences
- Drag-and-drop table mode changed to DropOnly to avoid conflict with the window-level drop handler
- Overwrite warning dialog confirmation button relabelled from "Ok" to "Compress"
- Hiding the status bar now reclaims the vertical space in the layout instead of leaving a gap
- Main window now enforces a minimum size of 500 × 400 pixels

### Fixed

- Preferences data loss on save: settings are now merged into the existing file instead of overwriting it
- Sort desync data corruption: file paths are now read from `UserRole` data rather than positional indices, which broke after any column sort
- Thread-safety race condition: table data is snapshotted before the compression thread is spawned
- Slider signals in Preferences firing before preferences are loaded, causing incorrect initial values
- `warn_before_overwrite` preference lost from in-memory state after saving
- Re-entrant event dispatch caused by `QApplication.processEvents()` calls inside signal handler slots
- `os.makedirs` in `Preferences.__init__` missing `exist_ok=True`
- Startup tool-availability warning dialog appearing before the main window was visible
- Python 3.14 stdlib conflict: local `src/compression/` package shadowed by the new stdlib `compression` module; fixed by adding `__init__.py` files to all `src/` packages
- Artificial per-file delay (`time.sleep(0.01)`) removed from the compression loop, improving throughput on large batches

## [1.0.0] - 2025-01-01

### Added

- Initial public release with JPEG and PNG compression support
