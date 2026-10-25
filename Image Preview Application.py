import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageOps

# Optional drag-and-drop support
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_FILES = None
    TkinterDnD = None
    DND_AVAILABLE = False


SUPPORTED_EXTENSIONS = (
    ".png", ".jpg", ".jpeg", ".gif",
    ".bmp", ".tif", ".tiff", ".webp"
)


class ImageViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ZaBir | SnapView Image Viewer")
        self.root.geometry("1000x700")
        self.root.minsize(760, 560)
        self.root.configure(bg="#0b1120")

        self.image_original = None
        self.image_tk = None
        self.current_path = None

        # Zoom settings
        self.zoom = 1.0
        self.min_zoom = 0.10
        self.max_zoom = 8.0
        self.fit_scale = 1.0
        self.display_scale = 1.0

        # Full-screen state
        self.fullscreen = False

        # Image transformations
        self.rotation = 0
        self.flip_horizontal = False
        self.flip_vertical = False

        # Theme colors
        self.bg = "#0b1120"
        self.panel = "#111a2e"
        self.panel_2 = "#17233b"
        self.text = "#edf2ff"
        self.muted = "#91a0bc"
        self.accent = "#7c5cff"
        self.accent_hover = "#9278ff"
        self.border = "#263450"

        self._build_ui()

        self.root.bind(
            "<Control-o>",
            lambda event: self.open_image()
        )
        self.root.bind(
            "<Escape>",
            self._handle_escape
        )
        self.root.bind(
            "<F11>",
            self.toggle_fullscreen
        )
        self.root.bind(
            "<Configure>",
            self._on_resize
        )

        # Mouse wheel zoom support
        self.preview.bind(
            "<MouseWheel>",
            self._on_mousewheel
        )
        self.preview.bind(
            "<Button-4>",
            self._on_mousewheel
        )
        self.preview.bind(
            "<Button-5>",
            self._on_mousewheel
        )
        self.preview.bind(
            "<Double-Button-1>",
            self._reset_zoom
        )

        # Optional drag-and-drop support
        if DND_AVAILABLE:
            self._enable_drag_drop()

    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg=self.bg)
        header.pack(fill="x", padx=28, pady=(22, 16))

        brand = tk.Frame(header, bg=self.bg)
        brand.pack(side="left", fill="x", expand=True)

        tk.Label(
            brand,
            text="▧",
            font=("Segoe UI Symbol", 25, "bold"),
            fg="#b7a7ff",
            bg=self.bg
        ).pack(side="left", padx=(0, 12))

        title_area = tk.Frame(brand, bg=self.bg)
        title_area.pack(side="left")

        tk.Label(
            title_area,
            text="ZaBir HaSan",
            font=("Segoe UI", 22, "bold"),
            fg=self.text,
            bg=self.bg
        ).pack(anchor="w")

        tk.Label(
            title_area,
            text="A clean space for your images",
            font=("Segoe UI", 10),
            fg=self.muted,
            bg=self.bg
        ).pack(anchor="w", pady=(2, 0))

        self.open_btn = tk.Button(
            header,
            text="＋  Open image",
            command=self.open_image,
            font=("Segoe UI", 10, "bold"),
            fg="white",
            bg=self.accent,
            activeforeground="white",
            activebackground=self.accent_hover,
            relief="flat",
            bd=0,
            padx=18,
            pady=11,
            cursor="hand2"
        )
        self.open_btn.pack(side="right")

        self.open_btn.bind(
            "<Enter>",
            lambda event: self.open_btn.configure(
                bg=self.accent_hover
            )
        )
        self.open_btn.bind(
            "<Leave>",
            lambda event: self.open_btn.configure(
                bg=self.accent
            )
        )

        # Main preview card
        outer = tk.Frame(
            self.root,
            bg=self.panel,
            highlightbackground=self.border,
            highlightthickness=1
        )
        outer.pack(
            fill="both",
            expand=True,
            padx=28,
            pady=(0, 12)
        )

        # Preview header
        preview_header = tk.Frame(
            outer,
            bg=self.panel
        )
        preview_header.pack(
            fill="x",
            padx=18,
            pady=(14, 10)
        )

        tk.Label(
            preview_header,
            text="PREVIEW",
            font=("Segoe UI", 9, "bold"),
            fg=self.muted,
            bg=self.panel
        ).pack(side="left")

        self.zoom_label = tk.Label(
            preview_header,
            text="FIT",
            font=("Segoe UI", 9, "bold"),
            fg=self.text,
            bg=self.panel,
            padx=8
        )
        self.zoom_label.pack(side="right")

        self.status_label = tk.Label(
            preview_header,
            text="READY",
            font=("Segoe UI", 8, "bold"),
            fg="#9de6c0",
            bg="#16352f",
            padx=10,
            pady=4
        )
        self.status_label.pack(
            side="right",
            padx=(0, 10)
        )

        self.preview = tk.Canvas(
            outer,
            bg="#0e1729",
            highlightthickness=0,
            bd=0,
            relief="flat"
        )
        self.preview.pack(
            fill="both",
            expand=True,
            padx=16,
            pady=(0, 12)
        )

        self.preview.bind(
            "<Configure>",
            lambda event: self._render_image()
        )

        self._draw_placeholder()

        # Image controls
        controls = tk.Frame(
            self.root,
            bg=self.bg
        )
        controls.pack(
            fill="x",
            padx=28,
            pady=(0, 10)
        )

        self._make_control_button(
            controls,
            "↶ Rotate Left",
            lambda: self.rotate_image(-90)
        ).pack(side="left", padx=(0, 6))

        self._make_control_button(
            controls,
            "↷ Rotate Right",
            lambda: self.rotate_image(90)
        ).pack(side="left", padx=(0, 6))

        self._make_control_button(
            controls,
            "↔ Flip H",
            self.flip_h
        ).pack(side="left", padx=(0, 6))

        self._make_control_button(
            controls,
            "↕ Flip V",
            self.flip_v
        ).pack(side="left", padx=(0, 6))

        self._make_control_button(
            controls,
            "⛶ Full Screen",
            self.toggle_fullscreen
        ).pack(side="right")

        # Footer
        footer = tk.Frame(
            self.root,
            bg=self.bg
        )
        footer.pack(
            fill="x",
            padx=28,
            pady=(0, 10)
        )

        info = tk.Frame(
            footer,
            bg=self.bg
        )
        info.pack(
            side="left",
            fill="x",
            expand=True
        )

        self.file_label = tk.Label(
            info,
            text="No image selected",
            font=("Segoe UI", 10, "bold"),
            fg=self.text,
            bg=self.bg,
            anchor="w"
        )
        self.file_label.pack(anchor="w")

        self.details_label = tk.Label(
            info,
            text="Choose JPG, PNG, GIF, BMP, or TIFF",
            font=("Segoe UI", 9),
            fg=self.muted,
            bg=self.bg,
            anchor="w"
        )
        self.details_label.pack(
            anchor="w",
            pady=(4, 0)
        )

        actions = tk.Frame(
            footer,
            bg=self.bg
        )
        actions.pack(side="right")

        self.clear_btn = tk.Button(
            actions,
            text="Clear",
            command=self.clear_image,
            font=("Segoe UI", 10),
            fg=self.text,
            bg=self.panel_2,
            activebackground="#263653",
            activeforeground=self.text,
            relief="flat",
            bd=0,
            padx=18,
            pady=10,
            cursor="hand2"
        )
        self.clear_btn.pack(
            side="left",
            padx=(0, 9)
        )

        self.exit_btn = tk.Button(
            actions,
            text="Exit",
            command=self.root.destroy,
            font=("Segoe UI", 10),
            fg="#ffd7dc",
            bg="#3a202e",
            activebackground="#512a3c",
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            padx=18,
            pady=10,
            cursor="hand2"
        )
        self.exit_btn.pack(side="left")

        tip = (
            "TIP  •  Scroll to zoom  |  Double-click to fit  |  "
            "Ctrl + O to open  |  F11 for full screen  |  "
            "Esc to clear/exit full screen"
        )

        tk.Label(
            self.root,
            text=tip,
            font=("Segoe UI", 8),
            fg="#65738e",
            bg=self.bg
        ).pack(pady=(0, 9))

    def _make_control_button(self, parent, text, command):
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=("Segoe UI", 9, "bold"),
            fg=self.text,
            bg=self.panel_2,
            activebackground=self.accent,
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=9,
            pady=8,
            cursor="hand2"
        )

    def _enable_drag_drop(self):
        try:
            self.preview.drop_target_register(DND_FILES)
            self.preview.dnd_bind(
                "<<Drop>>",
                self._on_drop
            )

            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind(
                "<<Drop>>",
                self._on_drop
            )
        except (AttributeError, tk.TclError):
            pass

    def _on_drop(self, event):
        try:
            paths = self.root.tk.splitlist(event.data)

            if not paths:
                return

            path = paths[0].strip()

            if os.path.isfile(path):
                if path.lower().endswith(SUPPORTED_EXTENSIONS):
                    self.load_image(path)
                else:
                    messagebox.showwarning(
                        "Unsupported file",
                        "Please drop a supported image file.",
                        parent=self.root
                    )

        except (OSError, tk.TclError) as exc:
            messagebox.showerror(
                "Drag-and-drop error",
                str(exc),
                parent=self.root
            )

    def _draw_placeholder(self):
        self.preview.delete("all")

        width = max(
            self.preview.winfo_width(), 400
        )
        height = max(
            self.preview.winfo_height(), 300
        )

        cx, cy = width // 2, height // 2

        self.preview.create_rectangle(
            cx - 49, cy - 47,
            cx + 49, cy + 25,
            outline="#7182a4",
            width=2
        )

        self.preview.create_line(
            cx - 38, cy + 13,
            cx - 10, cy - 14,
            cx + 7, cy + 3,
            cx + 20, cy - 8,
            cx + 38, cy + 13,
            fill="#8b79ff",
            width=3,
            smooth=True
        )

        self.preview.create_oval(
            cx + 15, cy - 34,
            cx + 26, cy - 23,
            outline="#8b79ff",
            width=2
        )

        self.preview.create_text(
            cx, cy + 64,
            text="Your image will appear here",
            fill="#d9e2f4",
            font=("Segoe UI", 14, "bold")
        )

        hint = (
            "Drag and drop an image here"
            if DND_AVAILABLE
            else "Click 'Open image' to get started"
        )

        self.preview.create_text(
            cx, cy + 91,
            text=hint,
            fill="#8493af",
            font=("Segoe UI", 10)
        )

    def open_image(self):
        path = filedialog.askopenfilename(
            parent=self.root,
            title="Choose an image",
            initialdir=os.path.expanduser("~"),
            filetypes=[
                (
                    "Image files",
                    "*.png *.jpg *.jpeg *.gif *.bmp "
                    "*.tif *.tiff *.webp"
                ),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )

        if path:
            self.load_image(path)

    def load_image(self, path):
        try:
            with Image.open(path) as source:
                image_format = source.format or "Image"
                original = ImageOps.exif_transpose(
                    source
                ).convert("RGBA")

            self.current_path = path
            self.image_original = original
            self.zoom = 1.0

            self.rotation = 0
            self.flip_horizontal = False
            self.flip_vertical = False

            self.file_label.configure(
                text=os.path.basename(path)
            )

            width, height = original.size
            size_text = self._format_size(
                os.path.getsize(path)
            )

            self.details_label.configure(
                text=(
                    f"{width:,} × {height:,} px   •   "
                    f"{image_format}   •   {size_text}"
                )
            )

            self.status_label.configure(
                text="IMAGE LOADED",
                fg="#9de6c0",
                bg="#16352f"
            )

            self._render_image()

        except (OSError, ValueError) as exc:
            messagebox.showerror(
                "Unable to open image",
                f"This file could not be opened as an image.\n\n{exc}",
                parent=self.root
            )

    @staticmethod
    def _format_size(size):
        if size < 1024:
            return f"{size} B"
        elif size < 1024 ** 2:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 ** 2):.2f} MB"

    def _get_transformed_image(self):
        image = self.image_original

        # Pillow rotates counterclockwise for positive angles.
        if self.rotation:
            image = image.rotate(
                self.rotation,
                expand=True
            )

        if self.flip_horizontal:
            image = ImageOps.mirror(image)

        if self.flip_vertical:
            image = ImageOps.flip(image)

        return image

    def rotate_image(self, angle):
        if self.image_original is None:
            return

        self.rotation = (
            self.rotation + angle
        ) % 360

        self._render_image()

    def flip_h(self):
        if self.image_original is None:
            return

        self.flip_horizontal = not self.flip_horizontal
        self._render_image()

    def flip_v(self):
        if self.image_original is None:
            return

        self.flip_vertical = not self.flip_vertical
        self._render_image()

    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen

        self.root.attributes(
            "-fullscreen",
            self.fullscreen
        )

        return "break"

    def _handle_escape(self, event=None):
        if self.fullscreen:
            self.fullscreen = False
            self.root.attributes("-fullscreen", False)
        else:
            self.clear_image()

        return "break"

    def _on_mousewheel(self, event):
        if self.image_original is None:
            return "break"

        if getattr(event, "num", None) == 4:
            direction = 1
        elif getattr(event, "num", None) == 5:
            direction = -1
        elif getattr(event, "delta", 0) > 0:
            direction = 1
        elif getattr(event, "delta", 0) < 0:
            direction = -1
        else:
            return "break"

        if direction > 0:
            self.zoom = min(
                self.zoom * 1.15,
                self.max_zoom
            )
        else:
            self.zoom = max(
                self.zoom / 1.15,
                self.min_zoom
            )

        self._render_image()
        return "break"

    def _reset_zoom(self, event=None):
        if self.image_original is not None:
            self.zoom = 1.0
            self._render_image()

        return "break"

    def _render_image(self):
        if self.image_original is None:
            return

        area_w = self.preview.winfo_width() - 36
        area_h = self.preview.winfo_height() - 36

        if area_w < 20 or area_h < 20:
            return

        image = self._get_transformed_image()
        original_w, original_h = image.size

        self.fit_scale = min(
            area_w / original_w,
            area_h / original_h,
            1.0
        )

        self.display_scale = (
            self.fit_scale * self.zoom
        )

        new_w = max(
            1, int(original_w * self.display_scale)
        )
        new_h = max(
            1, int(original_h * self.display_scale)
        )

        resized = image.resize(
            (new_w, new_h),
            Image.Resampling.LANCZOS
        )

        self.image_tk = ImageTk.PhotoImage(resized)

        self.preview.delete("all")

        self.preview.create_image(
            self.preview.winfo_width() // 2,
            self.preview.winfo_height() // 2,
            image=self.image_tk,
            anchor="center"
        )

        self.zoom_label.configure(
            text=f"{int(self.zoom * 100)}%  •  Scroll to zoom"
        )

    def clear_image(self):
        self.image_original = None
        self.image_tk = None
        self.current_path = None

        self.zoom = 1.0
        self.rotation = 0
        self.flip_horizontal = False
        self.flip_vertical = False

        self.file_label.configure(
            text="No image selected"
        )

        self.details_label.configure(
            text="Choose JPG, PNG, GIF, BMP, or TIFF"
        )

        self.status_label.configure(
            text="READY",
            fg="#9de6c0",
            bg="#16352f"
        )

        self.zoom_label.configure(text="FIT")
        self._draw_placeholder()

    def _on_resize(self, event):
        if (
            event.widget == self.root
            and self.image_original is not None
        ):
            self.root.after_idle(
                self._render_image
            )


def main():
    if DND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()

    ImageViewerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
