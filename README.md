<p align="center">
<img src="https://github.com/aries223/mountaineer/blob/main/src/ui/logo/mountaineer.png">
</p>



# Mountaineer

Mountaineer is a powerful desktop application designed to simplify image compression for photographers, designers, and anyone working with large collections of JPEG and PNG images. It provides an intuitive interface for batch compressing images while offering compression customization options through its preferences system.

## Core Features

### 1. **Image Compression**
- **JPEG Support**: Uses `jpegoptim` for efficient JPEG compression with adjustable quality levels
- **PNG Support**: Uses `oxipng` for optimal PNG compression with lossy and lossless options
- **Metadata Stripping**: Option to remove metadata from compressed files for reduced file size

### 2. **User Interface**
- **Intuitive Main Window**: Clean, organized layout showing all image information in a table format
- **Drag-and-Drop Support**: Easy file addition via drag-and-drop or traditional file dialogs
- **Context Menu**: Individual file removal through right-click context menu

### 3. **Preferences System**
- **Compression Levels**: Customizable JPEG and PNG compression quality levels
- **Lossless Mode**: Toggle for lossless compression when needed
- **Metadata Options**: Control whether metadata should be stripped from compressed files
- **Window Position/Size Memory**: Remembers last window position and size for both main application and preferences dialog

### 4. **Progress Tracking**
- **Real-time Status Updates**: Detailed status bar showing current operation progress
- **Progress Bar**: Visual indicator of compression progress during batch operations
- **Performance Metrics**: Displays compression time and average speed after completion

### 5. **File Management**
- **Comprehensive File List**: Displays file name, format, dimensions, size, compressed size, and savings percentage
- **Error Handling**: Clear feedback for incompatible files or processing errors
- **Contextual Information**: All relevant details displayed in an organized table with proper column alignment

### 6. **User Experience**
- **Threaded Processing**: Background compression operations keep UI responsive
- **Window Management**: Customizable and rememberable window sizes/positions
- **Error Reporting**: Clear status bar messages for all operations including errors and warnings

Mountaineer combines powerful image compression capabilities with an intuitive user interface, making it the perfect tool for anyone needing to efficiently manage and compress large collections of images.

___

## Installation

This app has been tested to run on Fedora 42 KDE and Gnome. 

#### Prerequisites
- Python 3.8 or higher (preferably the latest Python 3.13 release)
- Pip (Python package installer)

1. Install Prerequisites (if you dont have them already)
```bash
pip install PyQt6 pillow
```
2. Install the app
```bash
sudo dnf install <Mountaineer-XXXXX.rpm>
```
(<insert current .rpm filename>)
