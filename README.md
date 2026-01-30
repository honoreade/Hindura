# Hindura Pro

A powerful, modern file converter for Windows with batch processing support.

<img width="1453" height="1079" alt="image" src="https://github.com/user-attachments/assets/48e54a9d-3491-4db5-a71a-07e222743b80" />

## ✨ Features

### Core Conversion
- **Standard Conversion** - Convert between video, audio, image, and document formats
- **Video to Audio** - Extract audio tracks from video files
- **Video to GIF** - Create animated GIFs with customizable FPS and scale
- **Resize** - Resize videos/images with preset or custom dimensions
- **Compression** - Reduce file sizes with quality control (High/Medium/Low)

### Batch & Workflow
- **Batch Processing** - Convert multiple files at once
- **Retry Failed** - One-click retry for failed conversions
- **Custom Output Folder** - Choose where to save converted files
- **Progress Tracking** - Real-time progress with percentage display

### User Experience
- **File Size Display** - See file sizes before converting
- **Sound Notification** - Audio alert when conversion completes
- **Remember Window Position** - Automatically saves and restores window size/position
- **Dark/Light Theme** - Toggle between themes

## 📋 Supported Formats

| Type | Formats |
|------|---------|
| Video | MP4, AVI, MKV, MOV, WMV, FLV, WebM, M4V, MPG, MPEG, GIF |
| Audio | MP3, WAV, AAC, FLAC, OGG, M4A, WMA, OPUS, AIFF |
| Image | JPG, PNG, GIF, BMP, WebP, TIFF, ICO, SVG |
| Document | PDF, TXT, DOCX, HTML |

## 🔧 Requirements

- Windows 10/11
- FFmpeg (for media conversions)

## 📥 Installation

### Option 1: Run the Executable
1. Download `HinduraPro.exe` from the releases
2. Download FFmpeg from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/)
3. Extract FFmpeg to `C:\ffmpeg\bin\ffmpeg.exe`
4. Run `HinduraPro.exe`

### Option 2: Run from Source
```bash
pip install customtkinter
python file_converter.py
```

## 🚀 Usage

1. Click **Add Files** to select files (or multiple at once)
2. Choose the **Mode** (Standard Conversion, Resize, or Compression)
3. Select the output **Format**
4. (Optional) Set resize dimensions or compression quality
5. Click **Convert**
6. If any fail, use **🔄 Retry Failed** to reprocess them

## 🛠️ Building from Source

```bash
pip install pyinstaller customtkinter
pyinstaller --onefile --windowed --name "HinduraPro" file_converter.py
```

## 📄 License

MIT License - Feel free to use and modify.
