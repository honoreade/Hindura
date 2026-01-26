import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
from pathlib import Path
from datetime import datetime

class FileConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Converter Pro")
        self.root.geometry("700x700")
        self.root.resizable(False, False)

        # File types and their supported formats
        self.file_types = {
            "Video": ["mp4", "avi", "mkv", "mov", "wmv", "flv", "webm", "m4v", "mpg", "mpeg", "gif"],
            "Audio": ["mp3", "wav", "aac", "flac", "ogg", "m4a", "wma", "opus", "aiff"],
            "Image": ["jpg", "png", "gif", "bmp", "webp", "tiff", "ico", "svg"],
            "Document": ["pdf", "txt", "docx", "html"]
        }

        # Main modes (simplified)
        self.main_modes = [
            "Standard Conversion",
            "Resize",
            "Compression"
        ]

        # Conversion sub-options for visual media
        self.conversion_options = ["None", "Video to Audio", "Video to GIF"]

        # Resize sub-options
        self.resize_options = ["None", "1920x1080 (1080p)", "1280x720 (720p)",
                               "854x480 (480p)", "640x360 (360p)", "Custom"]

        self.input_file = None
        self.ffmpeg_path = self.find_ffmpeg()

        self.create_widgets()
    
    def find_ffmpeg(self):
        """Find ffmpeg executable in the current directory or system PATH"""
        # Check in current directory structure and common locations
        local_paths = [
            r"C:\ffmpeg-2026-01-12-git-21a3e44fbe-full_build\bin\ffmpeg.exe",
            "ffmpeg.exe",
            "ffmpeg/bin/ffmpeg.exe",
            "ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe"
        ]

        # Also check for any ffmpeg folder in current directory
        try:
            for item in os.listdir('.'):
                if os.path.isdir(item) and 'ffmpeg' in item.lower():
                    ffmpeg_exe = os.path.join(item, 'bin', 'ffmpeg.exe')
                    if os.path.exists(ffmpeg_exe):
                        local_paths.append(ffmpeg_exe)
        except:
            pass

        # Also check C:\ for any ffmpeg folders
        try:
            for item in os.listdir('C:\\'):
                if os.path.isdir(os.path.join('C:\\', item)) and 'ffmpeg' in item.lower():
                    ffmpeg_exe = os.path.join('C:\\', item, 'bin', 'ffmpeg.exe')
                    if os.path.exists(ffmpeg_exe):
                        local_paths.append(ffmpeg_exe)
        except:
            pass

        for path in local_paths:
            if os.path.exists(path):
                # Test if ffmpeg actually works
                try:
                    test_result = subprocess.run([path, "-version"],
                                                capture_output=True,
                                                text=True,
                                                timeout=5,
                                                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                    if test_result.returncode == 0:
                        return os.path.abspath(path)
                except:
                    continue

        # Check system PATH
        try:
            result = subprocess.run(["where", "ffmpeg"], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except:
            pass

        return None

    def log_error(self, message):
        """Log errors to a file for debugging"""
        try:
            with open("converter_log.txt", "a", encoding="utf-8") as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"\n[{timestamp}]\n{message}\n")
        except:
            pass
    
    def create_widgets(self):
        # Title
        title_label = tk.Label(self.root, text="File Converter Pro", font=("Arial", 20, "bold"))
        title_label.pack(pady=15)

        # File selection frame
        file_frame = tk.Frame(self.root)
        file_frame.pack(pady=10, padx=20, fill="x")

        self.file_label = tk.Label(file_frame, text="No file selected", bg="lightgray", relief="sunken", anchor="w")
        self.file_label.pack(side="left", fill="x", expand=True, padx=(0, 10))

        browse_btn = tk.Button(file_frame, text="Browse", command=self.browse_file, width=10)
        browse_btn.pack(side="right")

        # Main Mode frame (Standard Conversion, Resize, Compression)
        mode_frame = tk.Frame(self.root)
        mode_frame.pack(pady=10, padx=20, fill="x")

        tk.Label(mode_frame, text="Mode:", width=10, anchor="w").pack(side="left")
        self.mode_var = tk.StringVar(value="Standard Conversion")
        self.mode_combo = ttk.Combobox(mode_frame, textvariable=self.mode_var,
                                       values=self.main_modes, state="readonly", width=20)
        self.mode_combo.pack(side="left", padx=10)
        self.mode_combo.bind("<<ComboboxSelected>>", self.on_mode_change)

        # Type selection frame
        type_frame = tk.Frame(self.root)
        type_frame.pack(pady=10, padx=20, fill="x")

        tk.Label(type_frame, text="Type:", width=10, anchor="w").pack(side="left")
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(type_frame, textvariable=self.type_var,
                                       values=list(self.file_types.keys()), state="readonly", width=20)
        self.type_combo.pack(side="left", padx=10)
        self.type_combo.bind("<<ComboboxSelected>>", self.on_type_change)

        # From format frame
        from_frame = tk.Frame(self.root)
        from_frame.pack(pady=10, padx=20, fill="x")

        tk.Label(from_frame, text="From:", width=10, anchor="w").pack(side="left")
        self.from_var = tk.StringVar()
        self.from_combo = ttk.Combobox(from_frame, textvariable=self.from_var, state="readonly", width=20)
        self.from_combo.pack(side="left", padx=10)
        self.from_combo.bind("<<ComboboxSelected>>", self.on_from_change)

        # To format frame
        self.to_frame = tk.Frame(self.root)
        self.to_frame.pack(pady=10, padx=20, fill="x")

        tk.Label(self.to_frame, text="To:", width=10, anchor="w").pack(side="left")
        self.to_var = tk.StringVar()
        self.to_combo = ttk.Combobox(self.to_frame, textvariable=self.to_var, state="readonly", width=20)
        self.to_combo.pack(side="left", padx=10)
        self.to_combo.bind("<<ComboboxSelected>>", self.on_to_change)

        # Output folder frame
        output_frame = tk.Frame(self.root)
        output_frame.pack(pady=10, padx=20, fill="x")

        tk.Label(output_frame, text="Output:", width=10, anchor="w").pack(side="left")
        self.output_var = tk.StringVar(value="Same as input")
        self.output_entry = tk.Entry(output_frame, textvariable=self.output_var, state="readonly", width=35)
        self.output_entry.pack(side="left", padx=(10, 5), fill="x", expand=True)

        self.output_browse_btn = tk.Button(output_frame, text="Browse", command=self.browse_output_folder, width=8)
        self.output_browse_btn.pack(side="left", padx=2)

        self.output_reset_btn = tk.Button(output_frame, text="Reset", command=self.reset_output_folder, width=6)
        self.output_reset_btn.pack(side="left", padx=2)

        # ===== OPTIONS FRAME =====
        self.options_frame = tk.LabelFrame(self.root, text="Options", padx=10, pady=10)
        self.options_frame.pack(pady=10, padx=20, fill="x")

        # Resize options for visual media (Standard Conversion)
        self.resize_frame = tk.Frame(self.options_frame)
        tk.Label(self.resize_frame, text="Resize:", width=10, anchor="w").pack(side="left")
        self.resize_var = tk.StringVar(value="None")
        self.resize_combo = ttk.Combobox(self.resize_frame, textvariable=self.resize_var,
                                         values=self.resize_options, state="readonly", width=18)
        self.resize_combo.pack(side="left", padx=5)
        self.resize_combo.bind("<<ComboboxSelected>>", self.on_resize_change)

        # Custom resolution entry
        self.custom_res_frame = tk.Frame(self.resize_frame)
        tk.Label(self.custom_res_frame, text="W:").pack(side="left")
        self.width_entry = tk.Entry(self.custom_res_frame, width=5)
        self.width_entry.pack(side="left", padx=2)
        tk.Label(self.custom_res_frame, text="H:").pack(side="left")
        self.height_entry = tk.Entry(self.custom_res_frame, width=5)
        self.height_entry.pack(side="left", padx=2)

        # GIF options (shown when gif is selected in "To:")
        self.gif_options_frame = tk.Frame(self.options_frame)
        tk.Label(self.gif_options_frame, text="GIF Settings:", width=10, anchor="w").pack(side="left")
        tk.Label(self.gif_options_frame, text="FPS:").pack(side="left")
        self.fps_var = tk.StringVar(value="10")
        self.fps_combo = ttk.Combobox(self.gif_options_frame, textvariable=self.fps_var,
                                      values=["5", "10", "15", "20", "24", "30"],
                                      state="readonly", width=5)
        self.fps_combo.pack(side="left", padx=5)
        tk.Label(self.gif_options_frame, text="Scale:").pack(side="left")
        self.gif_scale_var = tk.StringVar(value="320")
        self.gif_scale_combo = ttk.Combobox(self.gif_options_frame, textvariable=self.gif_scale_var,
                                            values=["160", "240", "320", "480", "640"],
                                            state="readonly", width=5)
        self.gif_scale_combo.pack(side="left", padx=5)

        # ===== COMPRESSION OPTIONS =====
        self.compress_frame = tk.Frame(self.options_frame)
        tk.Label(self.compress_frame, text="Quality:", width=10, anchor="w").pack(side="left")
        self.quality_var = tk.StringVar(value="Medium")
        self.quality_combo = ttk.Combobox(self.compress_frame, textvariable=self.quality_var,
                                          values=["High (Large file)", "Medium", "Low (Small file)"],
                                          state="readonly", width=20)
        self.quality_combo.pack(side="left", padx=5)

        # Convert button
        convert_btn = tk.Button(self.root, text="Convert", command=self.convert_file,
                               bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
                               width=20, height=2)
        convert_btn.pack(pady=20)

        # Status label
        self.status_label = tk.Label(self.root, text="", fg="blue")
        self.status_label.pack(pady=5)

        # FFmpeg status
        ffmpeg_status = "FFmpeg found ✓" if self.ffmpeg_path else "FFmpeg not found ✗"
        ffmpeg_color = "green" if self.ffmpeg_path else "red"
        tk.Label(self.root, text=ffmpeg_status, fg=ffmpeg_color).pack(side="bottom", pady=5)

        # Initialize UI state
        self.on_mode_change(None)
    
    def browse_file(self):
        filename = filedialog.askopenfilename(title="Select a file to convert")
        if filename:
            self.input_file = filename
            self.file_label.config(text=os.path.basename(filename))

            # Auto-detect file type and format
            ext = Path(filename).suffix[1:].lower()
            for file_type, formats in self.file_types.items():
                if ext in formats:
                    self.type_combo.set(file_type)
                    self.from_combo.set(ext)
                    self.on_type_change(None)
                    break

    def browse_output_folder(self):
        """Browse for output folder"""
        folder = filedialog.askdirectory(title="Select output folder")
        if folder:
            self.output_var.set(folder)

    def reset_output_folder(self):
        """Reset output folder to same as input"""
        self.output_var.set("Same as input")

    def on_type_change(self, event):
        selected_type = self.type_var.get()
        if selected_type in self.file_types:
            formats = self.file_types[selected_type]
            self.from_combo.config(values=formats)

            # Update UI based on mode and type
            self.on_mode_change(None)

    def on_from_change(self, event):
        """Handle changes to the From format dropdown"""
        self.update_to_formats()

    def update_to_formats(self):
        """Update the 'To' format dropdown based on mode and current format"""
        mode = self.mode_var.get()
        selected_type = self.type_var.get()
        from_format = self.from_var.get()

        if mode == "Standard Conversion":
            if selected_type == "Video":
                # For video: show video formats (excluding current) + audio formats + gif
                video_formats = [fmt for fmt in self.file_types["Video"] if fmt != from_format]
                audio_formats = self.file_types["Audio"]
                all_formats = video_formats + audio_formats
                self.to_combo.config(values=all_formats)
                if self.to_var.get() == from_format:
                    self.to_var.set("")
            elif selected_type == "Image":
                # For image: show image formats excluding current
                all_formats = [fmt for fmt in self.file_types["Image"] if fmt != from_format]
                self.to_combo.config(values=all_formats)
                if self.to_var.get() == from_format:
                    self.to_var.set("")
            else:
                # For other types: show formats excluding current
                if selected_type in self.file_types:
                    all_formats = [fmt for fmt in self.file_types[selected_type] if fmt != from_format]
                    self.to_combo.config(values=all_formats)
                    if self.to_var.get() == from_format:
                        self.to_var.set("")

        elif mode == "Resize":
            # Show video and image formats only (keep same format by default)
            if selected_type == "Video":
                self.to_combo.config(values=self.file_types["Video"])
                if not self.to_var.get() or self.to_var.get() not in self.file_types["Video"]:
                    self.to_var.set(from_format if from_format else "mp4")
            elif selected_type == "Image":
                self.to_combo.config(values=self.file_types["Image"])
                if not self.to_var.get() or self.to_var.get() not in self.file_types["Image"]:
                    self.to_var.set(from_format if from_format else "jpg")

        elif mode == "Compression":
            # Show formats based on the file type (keep same format by default)
            if selected_type in self.file_types:
                formats = self.file_types[selected_type]
                self.to_combo.config(values=formats)
                if not self.to_var.get() or self.to_var.get() not in formats:
                    self.to_var.set(from_format if from_format else formats[0])
        else:
            # Default: show all formats for the selected type
            if selected_type in self.file_types:
                formats = self.file_types[selected_type]
                self.to_combo.config(values=formats)

    def on_mode_change(self, event):
        """Handle main mode changes (Standard Conversion, Resize, Compression)"""
        mode = self.mode_var.get()
        selected_type = self.type_var.get()

        # Hide all option frames first
        self.resize_frame.pack_forget()
        self.compress_frame.pack_forget()
        self.gif_options_frame.pack_forget()
        self.custom_res_frame.pack_forget()

        if mode == "Standard Conversion":
            # Show resize option for visual media (Video/Image)
            if selected_type in ["Video", "Image"]:
                self.resize_frame.pack(fill="x", pady=5)
                self.resize_var.set("None")
            self.update_to_formats()

        elif mode == "Resize":
            # Show resize options (for Video and Image only)
            if selected_type in ["Video", "Image"]:
                self.resize_frame.pack(fill="x", pady=5)
                # Set default resolution
                if self.resize_var.get() == "None":
                    self.resize_var.set("1280x720 (720p)")
            else:
                messagebox.showinfo("Info", "Resize is only available for Video and Image files")
                self.mode_var.set("Standard Conversion")
                self.on_mode_change(None)
                return
            self.update_to_formats()

        elif mode == "Compression":
            # Show compression options (for all types)
            self.compress_frame.pack(fill="x", pady=5)
            self.update_to_formats()

    def on_to_change(self, event):
        """Handle changes to the To format dropdown - show GIF options when gif selected"""
        to_format = self.to_var.get()
        selected_type = self.type_var.get()

        # Hide GIF options first
        self.gif_options_frame.pack_forget()

        # Show GIF options if gif is selected and source is Video
        if to_format == "gif" and selected_type == "Video":
            self.gif_options_frame.pack(fill="x", pady=5)

    def on_resize_change(self, event):
        """Show/hide custom resolution fields"""
        if self.resize_var.get() == "Custom":
            self.custom_res_frame.pack(side="left", padx=10)
        else:
            self.custom_res_frame.pack_forget()

    def convert_file(self):
        if not self.input_file:
            messagebox.showerror("Error", "Please select a file to convert")
            return

        if not self.ffmpeg_path:
            messagebox.showerror("Error", "FFmpeg not found. Please extract ffmpeg.zip and restart the application.")
            return

        mode = self.mode_var.get()
        from_format = self.from_var.get()
        to_format = self.to_var.get()
        file_type = self.type_var.get()
        resize_option = self.resize_var.get() if hasattr(self, 'resize_var') else "None"

        if not from_format:
            messagebox.showerror("Error", "Please select source format")
            return

        if not to_format:
            messagebox.showerror("Error", "Please select target format")
            return

        # Generate output filename
        input_path = Path(self.input_file)

        # Determine conversion type based on mode and "to" format
        suffix = "_converted"
        conversion_type = "standard"

        # Check if it's video to audio (video source + audio destination)
        is_video_to_audio = (file_type == "Video" and to_format in self.file_types["Audio"])
        is_video_to_gif = (file_type == "Video" and to_format == "gif")
        has_resize = (resize_option != "None")

        if mode == "Standard Conversion":
            if is_video_to_audio:
                suffix = "_audio"
                conversion_type = "audio_extract"
            elif is_video_to_gif:
                suffix = "_gif"
                conversion_type = "gif"
            elif has_resize:
                suffix = "_resized"
                conversion_type = "resize_standard"
            else:
                suffix = "_converted"
                conversion_type = "standard"

        elif mode == "Resize":
            suffix = "_resized"
            conversion_type = "resize"

        elif mode == "Compression":
            suffix = "_compressed"
            conversion_type = "compress"

        # Determine output folder
        output_folder_setting = self.output_var.get()
        if output_folder_setting == "Same as input":
            output_folder = input_path.parent
        else:
            output_folder = Path(output_folder_setting)
            # Create folder if it doesn't exist
            if not output_folder.exists():
                try:
                    output_folder.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    messagebox.showerror("Error", f"Could not create output folder: {e}")
                    return

        output_file = output_folder / f"{input_path.stem}{suffix}.{to_format}"

        self.status_label.config(text="Converting...", fg="blue")
        self.root.update()

        try:
            # Build ffmpeg command based on conversion type
            cmd = [self.ffmpeg_path, "-i", self.input_file]

            if conversion_type == "audio_extract":
                cmd.extend(self.get_audio_extraction_params(to_format))

            elif conversion_type == "gif":
                cmd.extend(self.get_gif_conversion_params())

            elif conversion_type == "resize" or conversion_type == "resize_standard":
                cmd.extend(self.get_resize_params(to_format))

            elif conversion_type == "compress":
                cmd.extend(self.get_compression_params(to_format))

            else:
                # Standard conversion
                cmd.extend(self.get_standard_conversion_params(file_type, to_format))

            # Add output file and overwrite flag
            cmd.extend(["-y", str(output_file)])

            # Run ffmpeg conversion
            # Log the command for debugging
            self.log_error(f"Running command: {' '.join(cmd)}")

            result = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)

            # Log the output
            self.log_error(f"Return code: {result.returncode}")
            self.log_error(f"STDOUT: {result.stdout}")
            self.log_error(f"STDERR: {result.stderr}")

            if result.returncode == 0 and os.path.exists(output_file):
                self.status_label.config(text=f"Conversion successful! Saved to: {output_file.name}", fg="green")
                messagebox.showinfo("Success", f"File converted successfully!\n\nSaved as:\n{output_file}")
            else:
                self.status_label.config(text="Conversion failed", fg="red")
                error_msg = result.stderr if result.stderr else "Unknown error occurred"
                # Show only the last few lines of error for readability
                error_lines = error_msg.split('\n')
                relevant_error = '\n'.join([line for line in error_lines if 'error' in line.lower() or 'failed' in line.lower()][-5:])
                if not relevant_error:
                    relevant_error = '\n'.join(error_lines[-10:])
                messagebox.showerror("Error", f"Conversion failed:\n\n{relevant_error}\n\nCheck converter_log.txt for details")
        except Exception as e:
            self.status_label.config(text="Conversion failed", fg="red")
            self.log_error(f"Exception: {str(e)}")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}\n\nCheck converter_log.txt for details")

    def get_audio_extraction_params(self, to_format):
        """Get ffmpeg parameters for extracting audio from video"""
        params = []

        if to_format == "mp3":
            params.extend(["-vn", "-c:a", "libmp3lame", "-b:a", "192k"])
        elif to_format == "aac":
            params.extend(["-vn", "-c:a", "aac", "-b:a", "192k"])
        elif to_format == "flac":
            params.extend(["-vn", "-c:a", "flac"])
        elif to_format == "wav":
            params.extend(["-vn", "-c:a", "pcm_s16le"])
        elif to_format == "ogg":
            params.extend(["-vn", "-c:a", "libvorbis", "-q:a", "5"])
        elif to_format == "m4a":
            params.extend(["-vn", "-c:a", "aac", "-b:a", "192k"])
        else:
            params.extend(["-vn", "-c:a", "copy"])

        return params

    def get_gif_conversion_params(self):
        """Get ffmpeg parameters for converting video to GIF"""
        fps = self.fps_var.get()
        scale = self.gif_scale_var.get()

        params = [
            "-vf", f"fps={fps},scale={scale}:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
            "-loop", "0"
        ]

        return params

    def get_resize_params(self, to_format):
        """Get ffmpeg parameters for resizing (used in both Standard Conversion and Resize mode)"""
        params = []
        resolution = self.resize_var.get()
        file_type = self.type_var.get()

        # Determine resolution
        if resolution == "None":
            # No resize, just do standard conversion
            return self.get_standard_conversion_params(file_type, to_format)
        elif resolution == "Custom":
            width = self.width_entry.get()
            height = self.height_entry.get()
            if width and height:
                scale_filter = f"scale={width}:{height}"
            else:
                messagebox.showerror("Error", "Please enter custom width and height")
                return []
        else:
            # Extract resolution from string like "1920x1080 (1080p)"
            res = resolution.split()[0]
            scale_filter = f"scale={res}"

        params.extend(["-vf", scale_filter])

        # Add codec params
        params.extend(self.get_standard_conversion_params(file_type, to_format))

        return params

    def get_compression_params(self, to_format):
        """Get ffmpeg parameters for compressing media"""
        params = []
        quality = self.quality_var.get()
        file_type = self.type_var.get()

        if file_type == "Video":
            # Video compression
            if quality == "High (Large file)":
                crf = "18"
                bitrate = "5000k"
            elif quality == "Medium":
                crf = "23"
                bitrate = "2500k"
            else:  # Low (Small file)
                crf = "28"
                bitrate = "1000k"

            if to_format == "mp4":
                params.extend(["-c:v", "libx264", "-crf", crf, "-c:a", "aac", "-b:a", "128k"])
            elif to_format == "webm":
                params.extend(["-c:v", "libvpx-vp9", "-b:v", bitrate, "-c:a", "libopus", "-b:a", "96k"])
            else:
                params.extend(["-c:v", "libx264", "-crf", crf, "-c:a", "aac", "-b:a", "128k"])

        elif file_type == "Audio":
            # Audio compression
            if quality == "High (Large file)":
                bitrate = "256k"
            elif quality == "Medium":
                bitrate = "192k"
            else:  # Low (Small file)
                bitrate = "128k"

            if to_format == "mp3":
                params.extend(["-c:a", "libmp3lame", "-b:a", bitrate])
            elif to_format == "aac":
                params.extend(["-c:a", "aac", "-b:a", bitrate])
            elif to_format == "ogg":
                params.extend(["-c:a", "libvorbis", "-b:a", bitrate])
            else:
                params.extend(["-c:a", "aac", "-b:a", bitrate])

        elif file_type == "Image":
            # Image compression
            if to_format == "jpg" or to_format == "jpeg":
                if quality == "High (Large file)":
                    params.extend(["-q:v", "2"])
                elif quality == "Medium":
                    params.extend(["-q:v", "5"])
                else:
                    params.extend(["-q:v", "10"])
            elif to_format == "png":
                params.extend(["-compression_level", "9"])

        return params

    def get_standard_conversion_params(self, file_type, to_format):
        """Get ffmpeg parameters for standard conversion"""
        params = []

        if file_type == "Video":
            # Video conversion with codec settings
            if to_format == "mp4":
                params.extend(["-c:v", "libx264", "-c:a", "aac", "-strict", "experimental"])
            elif to_format == "avi":
                params.extend(["-c:v", "mpeg4", "-c:a", "mp3"])
            elif to_format == "mkv":
                params.extend(["-c:v", "libx264", "-c:a", "aac"])
            elif to_format == "webm":
                params.extend(["-c:v", "libvpx-vp9", "-c:a", "libopus"])
            elif to_format == "mov":
                params.extend(["-c:v", "libx264", "-c:a", "aac"])
            elif to_format in ["mpg", "mpeg"]:
                # MPEG requires mpeg2video and mp2 audio
                params.extend(["-c:v", "mpeg2video", "-c:a", "mp2", "-b:v", "4000k", "-b:a", "192k"])
            elif to_format == "wmv":
                params.extend(["-c:v", "wmv2", "-c:a", "wmav2"])
            elif to_format == "flv":
                params.extend(["-c:v", "flv1", "-c:a", "mp3"])
            elif to_format == "m4v":
                params.extend(["-c:v", "libx264", "-c:a", "aac"])
            else:
                # Default: use H.264 and AAC for best compatibility
                params.extend(["-c:v", "libx264", "-c:a", "aac"])

        elif file_type == "Audio":
            # Audio conversion with quality settings
            if to_format == "mp3":
                params.extend(["-c:a", "libmp3lame", "-b:a", "192k"])
            elif to_format == "aac":
                params.extend(["-c:a", "aac", "-b:a", "192k"])
            elif to_format == "flac":
                params.extend(["-c:a", "flac"])
            elif to_format == "wav":
                params.extend(["-c:a", "pcm_s16le"])
            elif to_format == "ogg":
                params.extend(["-c:a", "libvorbis", "-q:a", "5"])
            elif to_format == "m4a":
                params.extend(["-c:a", "aac", "-b:a", "192k"])
            elif to_format == "opus":
                params.extend(["-c:a", "libopus", "-b:a", "128k"])
            elif to_format == "wma":
                params.extend(["-c:a", "wmav2", "-b:a", "192k"])
            elif to_format == "aiff":
                params.extend(["-c:a", "pcm_s16be"])
            else:
                # Default: use AAC
                params.extend(["-c:a", "aac", "-b:a", "192k"])

        elif file_type == "Image":
            # Image conversion
            if to_format == "jpg" or to_format == "jpeg":
                params.extend(["-q:v", "2"])
            elif to_format == "png":
                params.extend(["-compression_level", "6"])
            elif to_format == "webp":
                params.extend(["-quality", "90"])
            elif to_format == "bmp":
                pass  # No special params needed
            elif to_format == "tiff":
                pass  # No special params needed

        return params

if __name__ == "__main__":
    root = tk.Tk()
    app = FileConverterApp(root)
    root.mainloop()

