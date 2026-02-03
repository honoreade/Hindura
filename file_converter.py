import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess
import os
import threading
import re
from pathlib import Path
from datetime import datetime
import winsound  # For completion sound notification
import json  # For saving window settings

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")  # Modes: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"

class FileConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hindura Pro")
        self.root.geometry("800x800")
        self.root.resizable(True, True)

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

        self.input_files = []
        self.input_file = None # Keep for compatibility, will be "current file"
        self.failed_files_paths = []  # Store paths for retry functionality
        self.ffmpeg_path = self.find_ffmpeg()
        
        # Config file for saving window settings
        self.config_file = Path(os.path.dirname(os.path.abspath(__file__))) / "hindura_config.json"
        self.load_window_geometry()

        self.create_widgets()
        
        # Save window position on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def load_window_geometry(self):
        """Load saved window position and size"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    geometry = config.get('window_geometry', '800x800')
                    self.root.geometry(geometry)
                    return
        except Exception:
            pass
        # Default if no config
        self.root.geometry("800x800")
    
    def save_window_geometry(self):
        """Save window position and size"""
        try:
            config = {}
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
            config['window_geometry'] = self.root.geometry()
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except Exception:
            pass
    
    def on_closing(self):
        """Handle window close event"""
        self.save_window_geometry()
        self.root.destroy()
    
    def find_ffmpeg(self):
        """Find ffmpeg executable in the current directory or system PATH"""
        # Get the directory where the exe/script is located (for portable distribution)
        app_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Check in current directory structure and common locations
        local_paths = [
            os.path.join(app_dir, "ffmpeg.exe"),  # Portable: next to exe
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
        # Main container (Scrollable to ensure fit on all screens)
        main_container = ctk.CTkScrollableFrame(self.root, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Header with title and theme toggle
        header_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))

        # Title
        title_label = ctk.CTkLabel(header_frame, text="🎬 File Converter Pro",
                                   font=ctk.CTkFont(size=28, weight="bold"))
        title_label.pack(side="left", expand=True)

        # Theme toggle
        self.theme_var = ctk.StringVar(value="dark")
        theme_switch = ctk.CTkSwitch(header_frame, text="🌙",
                                     command=self.toggle_theme,
                                     variable=self.theme_var,
                                     onvalue="dark", offvalue="light",
                                     width=40)
        theme_switch.pack(side="right", padx=10)

        # File selection frame
        file_frame = ctk.CTkFrame(main_container)
        file_frame.pack(fill="both", expand=True, pady=10)

        # File buttons
        file_btn_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        file_btn_frame.pack(fill="x", padx=10, pady=5)
        
        add_btn = ctk.CTkButton(file_btn_frame, text="✅ Add Files", command=self.add_files,
                                   width=100, height=30, font=ctk.CTkFont(size=12))
        add_btn.pack(side="left", padx=5)
        
        clear_btn = ctk.CTkButton(file_btn_frame, text="�️ Clear All", command=self.clear_files,
                                   width=100, height=30, font=ctk.CTkFont(size=12),
                                   fg_color="#dc3545", hover_color="#c82333")
        clear_btn.pack(side="right", padx=5)

        # Scrollable list for files
        self.file_scroll = ctk.CTkScrollableFrame(file_frame, height=150, fg_color="transparent")
        self.file_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.no_files_label = ctk.CTkLabel(self.file_scroll, text="No files selected", text_color="gray")
        self.no_files_label.pack(pady=20)

        # Settings frame
        settings_frame = ctk.CTkFrame(main_container)
        settings_frame.pack(fill="x", pady=10)

        # Mode selection
        mode_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        mode_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(mode_frame, text="Mode:", width=80, anchor="w",
                     font=ctk.CTkFont(size=13)).pack(side="left")
        self.mode_var = ctk.StringVar(value="Standard Conversion")
        self.mode_combo = ctk.CTkComboBox(mode_frame, variable=self.mode_var,
                                          values=self.main_modes, width=200,
                                          command=self.on_mode_change)
        self.mode_combo.pack(side="left", padx=10)

        # Type selection
        type_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        type_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(type_frame, text="Type:", width=80, anchor="w",
                     font=ctk.CTkFont(size=13)).pack(side="left")
        self.type_var = ctk.StringVar()
        self.type_combo = ctk.CTkComboBox(type_frame, variable=self.type_var,
                                          values=list(self.file_types.keys()), width=200,
                                          command=self.on_type_change)
        self.type_combo.pack(side="left", padx=10)

        # From format
        from_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        from_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(from_frame, text="From:", width=80, anchor="w",
                     font=ctk.CTkFont(size=13)).pack(side="left")
        self.from_var = ctk.StringVar()
        self.from_combo = ctk.CTkComboBox(from_frame, variable=self.from_var,
                                          values=[], width=200,
                                          command=self.on_from_change)
        self.from_combo.pack(side="left", padx=10)

        # To format
        to_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        to_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(to_frame, text="To:", width=80, anchor="w",
                     font=ctk.CTkFont(size=13)).pack(side="left")
        self.to_var = ctk.StringVar()
        self.to_combo = ctk.CTkComboBox(to_frame, variable=self.to_var,
                                        values=[], width=200,
                                        command=self.on_to_change)
        self.to_combo.pack(side="left", padx=10)

        # Output folder frame
        output_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        output_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(output_frame, text="Output:", width=80, anchor="w",
                     font=ctk.CTkFont(size=13)).pack(side="left")
        self.output_var = ctk.StringVar(value="Same as input")
        self.output_entry = ctk.CTkEntry(output_frame, textvariable=self.output_var,
                                         state="readonly", width=250)
        self.output_entry.pack(side="left", padx=10)

        self.output_browse_btn = ctk.CTkButton(output_frame, text="📂",
                                               command=self.browse_output_folder,
                                               width=40, height=28)
        self.output_browse_btn.pack(side="left", padx=2)

        self.output_reset_btn = ctk.CTkButton(output_frame, text="↺",
                                              command=self.reset_output_folder,
                                              width=40, height=28,
                                              fg_color="#6c757d", hover_color="#5a6268")
        self.output_reset_btn.pack(side="left", padx=2)

        # ===== OPTIONS FRAME =====
        self.options_frame = ctk.CTkFrame(main_container)
        self.options_frame.pack(fill="x", pady=10)

        options_title = ctk.CTkLabel(self.options_frame, text="⚙️ Options",
                                     font=ctk.CTkFont(size=14, weight="bold"))
        options_title.pack(anchor="w", padx=15, pady=(10, 5))

        # Resize options container
        self.resize_frame = ctk.CTkFrame(self.options_frame, fg_color="transparent")

        resize_inner = ctk.CTkFrame(self.resize_frame, fg_color="transparent")
        resize_inner.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(resize_inner, text="Resize:", width=80, anchor="w",
                     font=ctk.CTkFont(size=13)).pack(side="left")
        self.resize_var = ctk.StringVar(value="None")
        self.resize_combo = ctk.CTkComboBox(resize_inner, variable=self.resize_var,
                                            values=self.resize_options, width=180,
                                            command=self.on_resize_change)
        self.resize_combo.pack(side="left", padx=10)

        # Custom resolution entry
        self.custom_res_frame = ctk.CTkFrame(resize_inner, fg_color="transparent")
        ctk.CTkLabel(self.custom_res_frame, text="W:", font=ctk.CTkFont(size=12)).pack(side="left")
        self.width_entry = ctk.CTkEntry(self.custom_res_frame, width=60)
        self.width_entry.pack(side="left", padx=5)
        ctk.CTkLabel(self.custom_res_frame, text="H:", font=ctk.CTkFont(size=12)).pack(side="left")
        self.height_entry = ctk.CTkEntry(self.custom_res_frame, width=60)
        self.height_entry.pack(side="left", padx=5)

        # GIF options
        self.gif_options_frame = ctk.CTkFrame(self.options_frame, fg_color="transparent")

        gif_inner = ctk.CTkFrame(self.gif_options_frame, fg_color="transparent")
        gif_inner.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(gif_inner, text="GIF Settings:", width=80, anchor="w",
                     font=ctk.CTkFont(size=13)).pack(side="left")
        ctk.CTkLabel(gif_inner, text="FPS:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(10, 0))
        self.fps_var = ctk.StringVar(value="10")
        self.fps_combo = ctk.CTkComboBox(gif_inner, variable=self.fps_var,
                                         values=["5", "10", "15", "20", "24", "30"], width=70)
        self.fps_combo.pack(side="left", padx=5)
        ctk.CTkLabel(gif_inner, text="Scale:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(10, 0))
        self.gif_scale_var = ctk.StringVar(value="320")
        self.gif_scale_combo = ctk.CTkComboBox(gif_inner, variable=self.gif_scale_var,
                                               values=["160", "240", "320", "480", "640"], width=80)
        self.gif_scale_combo.pack(side="left", padx=5)

        # Compression options
        self.compress_frame = ctk.CTkFrame(self.options_frame, fg_color="transparent")

        compress_inner = ctk.CTkFrame(self.compress_frame, fg_color="transparent")
        compress_inner.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(compress_inner, text="Quality:", width=80, anchor="w",
                     font=ctk.CTkFont(size=13)).pack(side="left")
        self.quality_var = ctk.StringVar(value="Medium")
        self.quality_combo = ctk.CTkComboBox(compress_inner, variable=self.quality_var,
                                             values=["High (Large file)", "Medium", "Low (Small file)"],
                                             width=200)
        self.quality_combo.pack(side="left", padx=10)

        # Button frame for Convert and Cancel
        button_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        button_frame.pack(pady=25)

        # Convert button
        self.convert_btn = ctk.CTkButton(button_frame, text="🚀 Convert",
                                    command=self.start_batch_conversion,
                                    width=200, height=50,
                                    font=ctk.CTkFont(size=16, weight="bold"),
                                    fg_color="#28a745", hover_color="#218838")
        self.convert_btn.pack(side="left", padx=10)

        # Cancel button (hidden by default)
        self.cancel_btn = ctk.CTkButton(button_frame, text="❌ Cancel",
                                        command=self.cancel_conversion,
                                        width=120, height=50,
                                        font=ctk.CTkFont(size=14, weight="bold"),
                                        fg_color="#dc3545", hover_color="#c82333")
        # Cancel button is hidden initially

        # Retry Failed button (hidden by default, shown after failed conversions)
        self.retry_btn = ctk.CTkButton(button_frame, text="🔄 Retry Failed",
                                       command=self.retry_failed_conversions,
                                       width=140, height=50,
                                       font=ctk.CTkFont(size=14, weight="bold"),
                                       fg_color="#fd7e14", hover_color="#e96e00")
        # Retry button is hidden initially

        # Progress frame
        self.progress_frame = ctk.CTkFrame(main_container, fg_color="transparent")

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, width=400, mode="determinate")
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=5)

        # Progress percentage label
        self.progress_label = ctk.CTkLabel(self.progress_frame, text="0%",
                                           font=ctk.CTkFont(size=12))
        self.progress_label.pack(pady=2)

        # Status label
        self.status_label = ctk.CTkLabel(main_container, text="",
                                         font=ctk.CTkFont(size=13))
        self.status_label.pack(pady=5)

        # Initialize conversion state
        self.conversion_process = None
        self.is_converting = False

        # FFmpeg status
        ffmpeg_status = "✅ FFmpeg found" if self.ffmpeg_path else "❌ FFmpeg not found"
        ffmpeg_color = "#28a745" if self.ffmpeg_path else "#dc3545"
        ffmpeg_label = ctk.CTkLabel(main_container, text=ffmpeg_status,
                                    font=ctk.CTkFont(size=12),
                                    text_color=ffmpeg_color)
        ffmpeg_label.pack(side="bottom", pady=5)

        # Initialize UI state
        self.on_mode_change(None)

    def toggle_theme(self):
        """Toggle between dark and light theme"""
        if self.theme_var.get() == "dark":
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")

    def add_files(self):
        filenames = filedialog.askopenfilenames(title="Select files to convert")
        if filenames:
            for f in filenames:
                if f not in self.input_files:
                    self.input_files.append(f)
            
            self.update_file_list_ui()
            
            # Update type/format based on the first file if valid
            if self.input_files:
                self.input_file = self.input_files[0]
                self._update_format_options(self.input_file)

    def clear_files(self):
        self.input_files = []
        self.input_file = None
        self.update_file_list_ui()

    def remove_file(self, file_path):
        if file_path in self.input_files:
            self.input_files.remove(file_path)
            self.update_file_list_ui()
            
            if not self.input_files:
                self.input_file = None
            elif self.input_file == file_path:
                self.input_file = self.input_files[0]

    def update_file_list_ui(self):
        # Clear current list
        for widget in self.file_scroll.winfo_children():
            widget.destroy()

        if not self.input_files:
            self.no_files_label = ctk.CTkLabel(self.file_scroll, text="No files selected", text_color="gray")
            self.no_files_label.pack(pady=20)
            return

        for f in self.input_files:
            row = ctk.CTkFrame(self.file_scroll, fg_color="transparent")
            row.pack(fill="x", pady=2)
            
            # Get file size and format display text
            display_name = os.path.basename(f)
            try:
                size = os.path.getsize(f)
                size_str = self.format_file_size(size)
                display_text = f"{display_name} ({size_str})"
            except OSError:
                display_text = display_name
            
            lbl = ctk.CTkLabel(row, text=display_text, anchor="w")
            lbl.pack(side="left", padx=5)
            
            # Remove button
            btn = ctk.CTkButton(row, text="❌", width=30, height=20, 
                                command=lambda path=f: self.remove_file(path),
                                fg_color="transparent", text_color="#dc3545", hover_color="#444")
            btn.pack(side="right", padx=5)

    def format_file_size(self, size_bytes):
        """Format file size in human-readable units"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def _update_format_options(self, filename):
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

    def on_type_change(self, event=None):
        selected_type = self.type_var.get()
        if selected_type in self.file_types:
            formats = self.file_types[selected_type]
            self.from_combo.configure(values=formats)

            # Update UI based on mode and type
            self.on_mode_change(None)

    def on_from_change(self, event=None):
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
                self.to_combo.configure(values=all_formats)
                if self.to_var.get() == from_format:
                    self.to_var.set("")
            elif selected_type == "Image":
                # For image: show image formats excluding current
                all_formats = [fmt for fmt in self.file_types["Image"] if fmt != from_format]
                self.to_combo.configure(values=all_formats)
                if self.to_var.get() == from_format:
                    self.to_var.set("")
            else:
                # For other types: show formats excluding current
                if selected_type in self.file_types:
                    all_formats = [fmt for fmt in self.file_types[selected_type] if fmt != from_format]
                    self.to_combo.configure(values=all_formats)
                    if self.to_var.get() == from_format:
                        self.to_var.set("")

        elif mode == "Resize":
            # Show video and image formats only (keep same format by default)
            if selected_type == "Video":
                self.to_combo.configure(values=self.file_types["Video"])
                if not self.to_var.get() or self.to_var.get() not in self.file_types["Video"]:
                    self.to_var.set(from_format if from_format else "mp4")
            elif selected_type == "Image":
                self.to_combo.configure(values=self.file_types["Image"])
                if not self.to_var.get() or self.to_var.get() not in self.file_types["Image"]:
                    self.to_var.set(from_format if from_format else "jpg")

        elif mode == "Compression":
            # Show formats based on the file type (keep same format by default)
            if selected_type in self.file_types:
                formats = self.file_types[selected_type]
                self.to_combo.configure(values=formats)
                if not self.to_var.get() or self.to_var.get() not in formats:
                    self.to_var.set(from_format if from_format else formats[0])
        else:
            # Default: show all formats for the selected type
            if selected_type in self.file_types:
                formats = self.file_types[selected_type]
                self.to_combo.configure(values=formats)

    def on_mode_change(self, event=None):
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

    def on_to_change(self, event=None):
        """Handle changes to the To format dropdown - show GIF options when gif selected"""
        to_format = self.to_var.get()
        selected_type = self.type_var.get()

        # Hide GIF options first
        self.gif_options_frame.pack_forget()

        # Show GIF options if gif is selected and source is Video
        if to_format == "gif" and selected_type == "Video":
            self.gif_options_frame.pack(fill="x", pady=5)

    def on_resize_change(self, event=None):
        """Show/hide custom resolution fields"""
        if self.resize_var.get() == "Custom":
            self.custom_res_frame.pack(side="left", padx=10)
        else:
            self.custom_res_frame.pack_forget()

    def start_batch_conversion(self):
        """Start the batch conversion process"""
        if self.is_converting:
            messagebox.showwarning("Warning", "A conversion is already in progress")
            return

        if not self.input_files:
            messagebox.showerror("Error", "Please select files to convert")
            return

        if not self.ffmpeg_path:
            messagebox.showerror("Error", "FFmpeg not found. Please extract ffmpeg.zip and restart the application.")
            return

        # Validate options
        if not self.to_var.get():
            messagebox.showwarning("Warning", "Please select a target format option.")
            return
            
        # Validate custom resize if applicable
        if self.mode_var.get() == "Resize" and self.resize_var.get() == "Custom":
            if not self.width_entry.get() or not self.height_entry.get():
                 messagebox.showwarning("Warning", "Please enter valid Width and Height for custom resize.")
                 return

        # Initialize queue
        self.conversion_queue = list(self.input_files)
        self.total_files = len(self.conversion_queue)
        self.completed_count = 0
        self.failed_files = []
        self.failed_files_paths = []  # Track paths for retry
        
        # Start UI
        self.is_converting = True
        self.input_duration = 0
        self.start_conversion_ui()
        
        # Start processing
        self.process_next_file()

    def process_next_file(self):
        """Process the next file in the queue"""
        if not self.conversion_queue:
            # All done
            self.stop_conversion_ui()
            
            # Play completion sound
            try:
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            except:
                pass  # Ignore if sound fails
            
            if self.failed_files:
                failed_summary = "\n".join(self.failed_files[:5])
                if len(self.failed_files) > 5:
                    failed_summary += f"\n...and {len(self.failed_files) - 5} more."
                
                # Show retry button if there were failures
                self.retry_btn.pack(side="left", padx=10)
                
                messagebox.showwarning("Batch Complete with Errors", 
                                      f"Processed {self.total_files} files.\n\n"
                                      f"✅ Successful: {self.total_files - len(self.failed_files)}\n"
                                      f"❌ Failed: {len(self.failed_files)}\n\n"
                                      f"Failures:\n{failed_summary}")
            else:
                # Hide retry button on success
                self.retry_btn.pack_forget()
                messagebox.showinfo("Success", f"Batch conversion complete!\nSuccessfully processed {self.total_files} files.")
            return

        self.current_processing_file = self.conversion_queue.pop(0)
        self.input_file = self.current_processing_file # Update current file for compatibility
        
        # Update status
        remaining = len(self.conversion_queue) + 1
        current_num = self.total_files - remaining + 1
        self.status_label.configure(text=f"⏳ Converting file {current_num}/{self.total_files}: {os.path.basename(self.input_file)}", text_color="#3498db")
        
        self._start_single_file_conversion(self.input_file)

    def retry_failed_conversions(self):
        """Retry only the files that failed in the last batch"""
        if not self.failed_files_paths:
            messagebox.showinfo("Info", "No failed files to retry.")
            return
        
        if self.is_converting:
            messagebox.showwarning("Warning", "A conversion is already in progress")
            return
        
        # Hide retry button
        self.retry_btn.pack_forget()
        
        # Set up queue with failed files only
        self.conversion_queue = list(self.failed_files_paths)
        self.total_files = len(self.conversion_queue)
        self.completed_count = 0
        self.failed_files = []
        self.failed_files_paths = []
        
        # Start UI
        self.is_converting = True
        self.input_duration = 0
        self.start_conversion_ui()
        
        # Start processing
        self.process_next_file()

    def _start_single_file_conversion(self, input_file_path):
        """Internal method to convert a single file"""
        mode = self.mode_var.get()
        from_format = self.from_var.get() # Note: logic currently assumes same from/to for all files if they match extension
        # If files have different extensions, we might need to auto-detect 'to' format per file or force one.
        # Current logic in UI sets 'from' based on first file. We'll stick to that simple logic 
        # but re-verify if the file extension matches the expectations if needed. 
        # For now, we assume user knows what they are doing converting mixed files to one format.
        
        to_format = self.to_var.get()
        file_type = self.type_var.get()
        resize_option = self.resize_var.get() if hasattr(self, 'resize_var') else "None"

        if not to_format:
            # Should have been caught, but safe check
            self.stop_conversion_ui()
            messagebox.showerror("Error", "Please select target format")
            return

        # Generate output filename
        input_path = Path(input_file_path)

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
                    self.stop_conversion_ui()
                    messagebox.showerror("Error", f"Could not create output folder: {e}")
                    return

        output_file = output_folder / f"{input_path.stem}{suffix}.{to_format}"

        # Overwrite protection
        if output_file.exists():
            # For batch, maybe we should just skip or auto-rename?
            # Asking for every file is annoying. Let's auto-rename for batch simplicity or ask?
            # Asking might block thread if not careful, but we are on main thread here.
            if not messagebox.askyesno("File Exists", f"The file '{output_file.name}' already exists.\nDo you want to overwrite it?"):
                # Skip this file
                self.process_next_file()
                return

        # Atomic write: use .tmp suffix before extension so FFmpeg knows format
        temp_output_file = output_folder / f"{input_path.stem}{suffix}.tmp.{to_format}"

        # Build ffmpeg command based on conversion type
        cmd = [self.ffmpeg_path, "-i", input_file_path]

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

        # Add output file and overwrite flag (always overwrite the tmp file)
        cmd.extend(["-y", str(temp_output_file)])

        # Log the command for debugging
        self.log_error(f"Running command: {' '.join(cmd)}")

        # Get input file duration for progress calculation
        self.input_duration = self.get_media_duration(input_file_path)

        # We are already in UI mode (batch), so no need to call start_conversion_ui again
        # But we need to reset progress bar for this file and ensure correct mode
        if self.input_duration and self.input_duration > 0:
            self.progress_bar.configure(mode="determinate")
            self.progress_bar.set(0)
            self.progress_label.configure(text="0%")
        else:
            self.progress_bar.configure(mode="indeterminate")
            self.progress_bar.start()
            self.progress_label.configure(text="Processing...")

        # Run conversion in a separate thread
        conversion_thread = threading.Thread(
            target=self._run_conversion_thread,
            args=(cmd, temp_output_file, output_file),
            daemon=True
        )
        conversion_thread.start()

    def get_media_duration(self, file_path):
        """Get the duration of a media file in seconds"""
        try:
            cmd = [self.ffmpeg_path, "-i", file_path]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            # FFmpeg outputs duration in stderr
            duration_match = re.search(r'Duration: (\d{2}):(\d{2}):(\d{2})\.(\d{2})', result.stderr)
            if duration_match:
                hours, minutes, seconds, centiseconds = map(int, duration_match.groups())
                return hours * 3600 + minutes * 60 + seconds + centiseconds / 100
        except Exception as e:
            self.log_error(f"Could not get duration: {e}")
        return None

    def start_conversion_ui(self):
        """Update UI to show conversion in progress"""
        self.convert_btn.configure(state="disabled")
        self.cancel_btn.pack(side="left", padx=10)
        self.progress_frame.pack(pady=5)

        # Use indeterminate mode if we couldn't get duration
        if self.input_duration and self.input_duration > 0:
            self.progress_bar.configure(mode="determinate")
            self.progress_bar.set(0)
            self.progress_label.configure(text="0%")
            self.status_label.configure(text="⏳ Converting... (0%)", text_color="#3498db")
        else:
            self.progress_bar.configure(mode="indeterminate")
            self.progress_bar.start()
            self.progress_label.configure(text="Processing...")
            self.status_label.configure(text="⏳ Converting...", text_color="#3498db")

        self.root.update()

    def stop_conversion_ui(self):
        """Reset UI after conversion completes"""
        self.convert_btn.configure(state="normal")
        self.cancel_btn.pack_forget()
        self.progress_bar.stop()  # Stop indeterminate animation if running
        self.progress_frame.pack_forget()
        self.is_converting = False

    def cancel_conversion(self):
        """Cancel the ongoing conversion"""
        # Clear queue so we don't continue
        self.conversion_queue = []
        
        if self.conversion_process and self.is_converting:
            try:
                self.conversion_process.terminate()
                self.conversion_process.wait(timeout=5)
            except Exception as e:
                self.log_error(f"Error terminating process: {e}")
                try:
                    self.conversion_process.kill()
                except:
                    pass

            self.root.after(0, self._on_conversion_cancelled)

    def _on_conversion_cancelled(self):
        """Handle UI update after cancellation"""
        self.stop_conversion_ui()
        self.status_label.configure(text="⚠️ Conversion cancelled", text_color="#ffc107")

    def _run_conversion_thread(self, cmd, temp_output_file, final_output_file):
        """Run FFmpeg conversion in a background thread with progress monitoring"""
        try:
            # Start the process - Use DEVNULL for stdout to prevent deadlocks (since we don't read it)
            self.conversion_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            stderr_output = []

            # Read stderr line by line (FFmpeg outputs progress to stderr)
            for line in self.conversion_process.stderr:
                if not self.is_converting:
                    break

                stderr_output.append(line)

                # Parse time progress from stderr (format: time=00:01:23.45)
                if "time=" in line:
                    try:
                        time_match = re.search(r'time=(\d{2}):(\d{2}):(\d{2})\.(\d{2})', line)
                        if time_match and self.input_duration and self.input_duration > 0:
                            hours, minutes, seconds, centiseconds = map(int, time_match.groups())
                            current_time = hours * 3600 + minutes * 60 + seconds + centiseconds / 100
                            progress = min(current_time / self.input_duration, 1.0)
                            self.root.after(0, lambda p=progress: self._update_progress(p))
                    except (ValueError, AttributeError):
                        pass

            # Wait for process to complete
            self.conversion_process.wait()

            return_code = self.conversion_process.returncode
            stderr_text = ''.join(stderr_output)

            # Log the output
            self.log_error(f"Return code: {return_code}")
            self.log_error(f"STDERR: {stderr_text}")

            # Update UI on main thread
            self.root.after(0, lambda: self._on_conversion_complete(return_code, temp_output_file, final_output_file, stderr_text))

        except Exception as e:
            self.log_error(f"Exception in conversion thread: {str(e)}")
            self.root.after(0, lambda: self._on_conversion_error(str(e)))

    def _update_progress(self, progress):
        """Update progress bar and label (called on main thread)"""
        if self.is_converting:
            # Switch to determinate mode if we were in indeterminate
            try:
                self.progress_bar.stop()
                self.progress_bar.configure(mode="determinate")
            except:
                pass
            self.progress_bar.set(progress)
            percent = int(progress * 100)
            self.progress_label.configure(text=f"{percent}%")
            self.status_label.configure(text=f"⏳ Converting... ({percent}%)", text_color="#3498db")

    def _on_conversion_complete(self, return_code, temp_output_file, output_file, stderr_text):
        """Handle conversion completion"""
        if return_code == 0:
            try:
                # Success! Rename temp file to final file
                # If target exists (and we confirmed overwrite), replace it
                if os.path.exists(output_file):
                    os.remove(output_file)
                
                os.rename(temp_output_file, output_file)
                self.completed_count += 1
                
                # Check if it was a video-to-audio conversion (audio extract)
                # Sometimes people want mp3 but select a video format? Standardize logic?
                # For now just success.
                
            except Exception as e:
                self.log_error(f"Error renaming file: {e}")
                self.failed_files.append(f"{os.path.basename(output_file)} (Rename Error: {str(e)})")
                self.failed_files_paths.append(self.input_file)  # Track for retry
                
                # Clean up temp file
                if os.path.exists(temp_output_file):
                    try:
                        os.remove(temp_output_file)
                    except:
                        pass
        else:
            # Conversion failed
            # Extract last error line from stderr if possible
            error_reason = f"Error: {return_code}"
            if stderr_text:
                lines = stderr_text.strip().split('\n')
                # Find last non-empty line
                last_lines = [l for l in lines[-5:] if l.strip()]
                if last_lines:
                    error_reason += f"\nLast error: {last_lines[-1]}"
            
            self.failed_files.append(f"{os.path.basename(output_file)}\n({error_reason})")
            self.failed_files_paths.append(self.input_file)  # Track for retry
            
            # Clean up temp file
            if os.path.exists(temp_output_file):
                try:
                    os.remove(temp_output_file)
                except:
                    pass

        # Process next file
        self.process_next_file()

    def _on_conversion_error(self, error_message):
        """Handle conversion error (called on main thread)"""
        # Log error and continue
        self.log_error(f"Exception error: {error_message}")
        if self.input_file:
             self.failed_files.append(f"{os.path.basename(self.input_file)} (Exception: {error_message})")
             self.failed_files_paths.append(self.input_file)  # Track for retry
        else:
             self.failed_files.append(f"Unknown file (Exception: {error_message})")
             
        # Process next file
        self.root.after(100, self.process_next_file)

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
    root = ctk.CTk()
    app = FileConverterApp(root)
    root.mainloop()

