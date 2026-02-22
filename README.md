<p align="center">
<img src="https://github.com/aries223/mountaineer/blob/main/src/ui/logo/mountaineer.png">
</p>

# Mountaineer

Mountaineer is a Linux desktop application for batch compressing JPEG, PNG, GIF, and WebP images. It wraps `jpegoptim`, `oxipng`, `gifsicle`, and `cwebp` behind a Qt interface, letting you add files or folders, tune quality settings per format, and compress in place — all without touching the command line.

## Features

- Batch compression via file dialog, Add Folder (recursive), or drag-and-drop
- Supports JPEG, PNG, GIF, and WebP formats
- In-place compression — files are overwritten directly, no renamed copies
- Configurable quality settings per format: JPEG 0–100, PNG 0–6, GIF 0–200, WebP 0–100
- Lossless mode, strip metadata, and warn-before-overwrite toggles in Preferences
- Results table with six columns: File Name, Format, Dimensions, Size, Compressed, Saved
- Negative savings (file grew) shown in red
- Sortable, manually resizable columns
- Progress bar and status bar, both toggleable
- Compression runs in a background thread — UI stays responsive during batch jobs
- Startup check for required CLI tools with a warning if any are missing
- Application log at `~/.mountaineer/mountaineer.log`

## Installation

### RPM (Fedora / RHEL)

Install the required system tools:

```bash
sudo dnf install jpegoptim oxipng gifsicle libwebp-tools
```

Then install the RPM package:

```bash
sudo dnf install Mountaineer-1.1.0.rpm
```

### Run from source

Install Python dependencies:

```bash
pip install PyQt6 pillow
```

Install the required system tools (Fedora):

```bash
sudo dnf install jpegoptim oxipng gifsicle libwebp-tools
```

Run the application from the repository root:

```bash
python src/main.py
```

## Keyboard Shortcuts

| Shortcut        | Action           |
|-----------------|------------------|
| Ctrl+O          | Add Files        |
| Ctrl+Shift+O    | Add Folder       |
| Ctrl+A          | Select All       |
| Delete          | Remove Selected  |
| Ctrl+,          | Preferences      |
| Ctrl+Q          | Quit             |

## Documentation

A full user guide is available at [`Documentation/Documentation.md`](Documentation/Documentation.md).

## License

GNU AGPLv3. See the [LICENSE](LICENSE) file for details.

## AI Disclaimer

Mountaineer is developed using AI-assisted coding tools, specifically Claude Code by Anthropic. This approach allows a small team to build and maintain a reliable desktop application. Care is taken to review all generated code for correctness, security, and adherence to project standards.
