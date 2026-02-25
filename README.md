<p align="center">
<img src="https://github.com/aries223/mountaineer/blob/main/src/ui/logo/mountaineer.png">
</p>

# Mountaineer

Mountaineer is a high quality image compression utility for Linux that batch compresses JPEG, PNG, GIF, and WebP images. It uses the best available compression libraries behind a modern interface, letting you add files or folders, tune quality settings per format, and compress in place.

## Features

- Supports JPEG, PNG, GIF, and WebP formats
- Batch compression via file dialog, Add Folder (recursive), or drag-and-drop
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
sudo dnf install Mountaineer-1.2.1.rpm
```

### DEB (Debian / Ubuntu)
The oxipng library is not available in the Debian/Ubuntu repos for some reason. You will need to install it first.
https://github.com/oxipng/oxipng/releases
<br/>
<br/>
After that install Mountaineer:
```bash
sudo apt install Mountaineer-1.2.1.deb
```
#### Testing
Mountaineer is developed, tested and used exclusively on Fedora KDE. I've created a .deb for Debian/Ubuntu systems, but dont test it there past making sure it installs and runs.

## Documentation

A full user guide is available  [`Documentation/Documentation.md`](Here).

## License

GNU AGPLv3. See the [LICENSE](LICENSE) file for details.

## AI Disclaimer

Mountaineer is developed using AI assistance yada yada yada...
