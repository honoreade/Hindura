# File Converter Pro

A simple and powerful file converter application for Windows built with Python and FFmpeg.

## Features

- **Standard Conversion** - Convert between video, audio, image, and document formats
- **Video to Audio** - Extract audio tracks from video files
- **Video to GIF** - Create animated GIFs with customizable FPS and scale
- **Resize** - Resize videos and images with preset or custom dimensions
- **Compression** - Reduce file sizes with quality control (High/Medium/Low)
- **Custom Output Folder** - Choose where to save converted files

## Supported Formats

| Type | Formats |
|------|---------|
| Video | MP4, AVI, MKV, MOV, WMV, FLV, WebM, M4V, MPG, MPEG, GIF |
| Audio | MP3, WAV, AAC, FLAC, OGG, M4A, WMA, OPUS, AIFF |
| Image | JPG, PNG, GIF, BMP, WebP, TIFF, ICO, SVG |
| Document | PDF, TXT, DOCX, HTML |

## Requirements

- Windows 10/11
- FFmpeg (for media conversions)

## Installation

### Option 1: Run the Executable (Recommended)

1. Download `FileConverterPro.exe` from the `dist` folder
2. Download FFmpeg Essentials from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/)
3. Extract FFmpeg and place it so the path is: `C:\ffmpeg\bin\ffmpeg.exe`
4. Run `FileConverterPro.exe`

### Option 2: Run from Source

1. Ensure Python 3.8+ is installed
2. Install FFmpeg and add to PATH
3. Run: `python file_converter.py`

## Usage

1. Click **Browse** to select a file
2. Choose the **Mode** (Standard Conversion, Resize, or Compression)
3. Select the output **Format** from the "To" dropdown
4. (Optional) Set resize dimensions or compression quality
5. (Optional) Choose a custom output folder
6. Click **Convert**

## Building from Source

To create your own executable:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "FileConverterPro" file_converter.py
```

The executable will be created in the `dist` folder.

## License

MIT License - Feel free to use and modify.