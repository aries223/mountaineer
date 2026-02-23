# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]

### Added

- Copyright header added to all Python source files (`© 2026 Aries223`)
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

### Security

- Argument injection: POSIX `--` end-of-options separator added before all user-supplied file paths in `jpegoptim`, `oxipng`, and `gifsicle` subprocess calls
- Argument injection (cwebp): filenames whose basename begins with `-` are now rejected in `_try_add_file_to_list` and `WebpCompressor`, since cwebp's non-POSIX argument order makes `--` placement incompatible with its trailing `-o` flag
- Symlink traversal: `_try_add_file_to_list` now rejects symlinks before any further processing, preventing out-of-scope files from being overwritten via symlinked paths
- Preferences race condition: Preferences button and menu action are disabled during compression; compression thread now snapshots `current_preferences` into a local dict before processing begins
- File permissions: log file (`~/.mountaineer/mountaineer.log`) and preferences file (`~/.mountaineer/mountaineer-prefs`) are now created with mode `0600`; preferences directory created with mode `0700`
- Log injection: `_sanitise_for_log()` helper replaces control characters in user-supplied paths before they are written to the log; applied across all logger call sites in `main_window.py`, `file_utils.py`, and `base_compressor.py`
- Quality clamping: `JpegCompressor` and `PngCompressor` now clamp quality values to their valid ranges before interpolating into CLI arguments
- `JpegCompressor` `--dest` corrected to pass the parent directory of `output_path`, as required by `jpegoptim`

### Fixed

- Compression failure details were not written to the log file; failures now emit `logger.error()` with the error detail, and skipped files (no longer exists, unsupported format) now emit `logger.warning()`
- Log file (`~/.mountaineer/mountaineer.log`) was not being created due to a broken `os.fdopen`+`StreamHandler`+`basicConfig` logging setup; replaced with `FileHandler` on a pre-created `0600` file, with the root logger configured directly via `addHandler`
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

## [1.1.0] - 2025-01-01

### Added

- Initial public release with JPEG and PNG compression support
