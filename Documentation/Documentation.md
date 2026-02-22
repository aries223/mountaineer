# Mountaineer — User Guide

**Revision:** 1.0
**Date:** 2026-02-21

---

## Table of Contents

1. [Overview](#1-overview)
2. [Main Window](#2-main-window)
3. [Adding Files](#3-adding-files)
4. [Compression Settings](#4-compression-settings)
5. [Running Compression](#5-running-compression)
6. [Keyboard Shortcuts](#6-keyboard-shortcuts)
7. [Preferences Storage](#7-preferences-storage)

---

## 1. Overview

Mountaineer is a desktop image compression tool for JPEG, PNG, GIF, and WebP files. Compression runs in-place using four external CLI tools: `jpegoptim`, `oxipng`, `gifsicle`, and `cwebp`. The application checks for these tools at startup and disables the Compress button if any are missing.

---

## 2. Main Window

The main window contains the following areas:

- **Menu bar** — File, Edit, View, and Help menus
- **Button bar** — Add Files, Clear File List, and Preferences buttons
- **File table** — six columns: File Name, Format, Dimensions, Size, Compressed, Saved
- **Status bar** — progress bar and status text, toggleable via View > Toggle Status Bar
- **Bottom row** — Compress Images and Quit buttons

---

## 3. Adding Files

Three methods are supported:

1. **File dialog** — Ctrl+O or File > Add Files; select one or more image files
2. **Add Folder** — Ctrl+Shift+O or File > Add Folder; recurses all subdirectories
3. **Drag and drop** — drag files or folders directly onto the file table

**Removing files:**

- Select one or more rows and press Delete, or right-click and choose Remove
- Edit > Clear (or the Clear File List button) removes all entries

---

## 4. Compression Settings

Open Preferences with Ctrl+, or the Preferences button.

### Format Sliders

| Format | Range | Default | Notes |
|--------|-------|---------|-------|
| JPEG   | 0–100 | 95      | Higher value = better quality |
| PNG    | 0–6   | 1       | Lower value = higher quality |
| GIF    | 0–200 | 40      | 0 = lossless |
| WebP   | 0–100 | 80      | Higher value = better quality |

### Checkboxes

- **Lossless Compression** — JPEG: repacks without quality loss. PNG: maximum-effort lossless (slowest). GIF and WebP: uses lossless mode.
- **Strip Metadata** — removes EXIF, IPTC, and XMP data from output files
- **Warn Before Overwriting Files** — shows a confirmation prompt before compression begins; the prompt includes a "Don't show again" option that permanently disables the warning by saving the setting to the preferences file

---

## 5. Running Compression

1. Add files using any method described in [Adding Files](#3-adding-files)
2. Adjust settings in Preferences if needed
3. Click **Compress Images**
4. Confirm the overwrite prompt if "Warn Before Overwriting Files" is enabled
5. Monitor progress in the status bar
6. Review results in the **Saved** column

If a file grows after compression, the savings percentage is shown in red. File list controls (Add Files, Clear, Remove) are disabled during compression. Files are modified in-place — there is no undo.

---

## 6. Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Add Files | Ctrl+O |
| Add Folder | Ctrl+Shift+O |
| Select All | Ctrl+A |
| Remove Selected | Delete |
| Preferences | Ctrl+, |
| Exit | Ctrl+Q |

---

## 7. Preferences Storage

- **Preferences file:** `~/.mountaineer/mountaineer-prefs` (JSON format)
- **Log file:** `~/.mountaineer/mountaineer.log`

The preferences file stores compression levels for all four formats, checkbox states, and window positions and sizes for the main window and the Preferences dialog.
