<p align="center">
<img src="https://github.com/aries223/mountaineer/blob/main/src/ui/logo/mountaineer.png">
</p>

# Mountaineer

Mountaineer is a high quality image compression utility for Linux that batch compresses JPEG, PNG, GIF, and WebP images. It uses the best available compression libraries behind a modern interface, letting you add files or folders, tune quality settings per format, and compress in place.

## Features

- Batch compression via file dialog, Add Folder (recursive), or drag-and-drop
- Supports JPEG, PNG, GIF, and WebP formats
- In-place compression — files are overwritten directly, no renamed copies
- Configurable quality settings per format
- Lossless mode, strip metadata, and warn-before-overwrite toggles in Preferences
- Negative savings (file grew) called out in red
- Sortable, manually resizable columns
- Compression runs in a background thread — UI stays responsive during batch jobs
- Errors during compression logged to a log file.

## Installation

### RPM (Fedora / RHEL)

```bash
sudo dnf install Mountaineer-1.2.0.rpm
```

### DEB (Debian / Ubuntu)

```bash
sudo dpkg -i Mountaineer-1.2.0.deb
```

### Run from source

```bash
pip install PyQt6 pillow
sudo dnf install jpegoptim oxipng gifsicle libwebp-tools  # Fedora
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

A full user guide is available  [`Documentation/Documentation.md`](Here).

## License

GNU AGPLv3. See the [LICENSE](LICENSE) file for details.

## AI Disclaimer

Mountaineer is developed using AI-assisted coding tools (AIAC). Care is taken to review all generated code for correctness, security, and adherence to standards.
