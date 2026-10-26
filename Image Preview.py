import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageOps

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False


class ImageViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ZaBir | Image Viewer")
        self.root.geometry("1100x750")
        self.root.minsize(760, 560)

        # ================= CREAM WHITE THEME =================
        self.colors = {
            "background": "#FFFDF5",
            "header": "#F5EEDC",
            "toolbar": "#FAF6EA",
            "canvas": "#F3EFE5",
            "panel": "#EDE4D2",
            "panel_inner": "#F8F3E8",
            "border": "#DCD1BD",
            "text": "#343434",
            "secondary_text": "#746D61",

            "primary": "#527DA8",
            "primary_hover": "#416A92",

            "save": "#66866A",
            "save_hover": "#527457",

            "neutral": "#81796E",
            "neutral_hover": "#696258",

            "transform": "#667C91",
            "transform_hover": "#50677D",

            "clear": "#C47B4B",
            "clear_hover": "#AB6539",

            "exit": "#C65D5D",
            "exit_hover": "#AE4848",

            "button_shadow": "#D4C9B5",
            "button_border": "#E8DFCF",
            "button_highlight": "#FFFFFF",
        }

        c = self.colors
        self.root.configure(bg=c["background"])

        self.image_original = None
        self.current_image = None
        self.display_image = None
        self.photo_image = None

        self.zoom_factor = 1.0
        self.display_scale = 1.0
        self.image_x = 0
        self.image_y = 0

        # Movable image functionality
        self.pan_x = 0
        self.pan_y = 0
        self.dragging_image = False
        self.drag_last_x = 0
        self.drag_last_y = 0

        self.current_file_path = None
        self.current_image_format = None
        self.is_fullscreen = False

        # Undo and Redo history
        self.undo_stack = []
        self.redo_stack = []
        self.max_history = 30

        self.undo_button = None
        self.redo_button = None

        self.build_ui()
        self.bind_shortcuts()
        self.update_history_buttons()

    # ================= USER INTERFACE =================
    def build_ui(self):
        c = self.colors

        # ================= HEADER =================
        header = tk.Frame(
            self.root,
            bg=c["header"],
            height=60,
            highlightbackground=c["border"],
            highlightthickness=1
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="📷 ZaBir HaSan",
            font=("Segoe UI", 25, "bold"),
            bg=c["header"],
            fg=c["text"]
        ).pack(side="left", padx=20)

        self.fullscreen_btn = self.create_button(
            header,
            "⛶ Full Screen",
            self.toggle_fullscreen,
            c["transform"],
            c["transform_hover"],
            side="right",
            padx=10,
            pady=6
        )

        # ================= TOP TOOLBAR =================
        toolbar = tk.Frame(
            self.root,
            bg=c["toolbar"],
            highlightbackground=c["border"],
            highlightthickness=1,
            height=58
        )
        toolbar.pack(fill="x", padx=10, pady=(8, 5))
        toolbar.pack_propagate(False)

        toolbar.grid_columnconfigure(0, weight=1)
        toolbar.grid_columnconfigure(1, weight=0)
        toolbar.grid_columnconfigure(2, weight=1)

        left_toolbar = tk.Frame(
            toolbar,
            bg=c["toolbar"]
        )
        left_toolbar.grid(
            row=0, column=0, sticky="w", padx=(10, 15), pady=3
        )

        center_toolbar = tk.Frame(
            toolbar,
            bg=c["toolbar"]
        )
        center_toolbar.grid(
            row=0, column=1, sticky="n", pady=3
        )

        right_toolbar = tk.Frame(
            toolbar,
            bg=c["toolbar"]
        )
        right_toolbar.grid(
            row=0, column=2, sticky="e", padx=(15, 10), pady=3
        )

        # ---------- OPEN IMAGE ----------
        self.create_button(
            left_toolbar,
            "Open Image",
            self.open_image,
            c["primary"],
            c["primary_hover"],
            padx=12,
            pady=7
        )

        # ---------- UNDO / REDO ----------
        self.undo_button = self.create_button(
            center_toolbar,
            "Undo",
            self.undo,
            c["neutral"],
            c["neutral_hover"],
            padx=10,
            pady=7
        )

        self.redo_button = self.create_button(
            center_toolbar,
            "Redo",
            self.redo,
            c["neutral"],
            c["neutral_hover"],
            padx=10,
            pady=7
        )

        # ---------- ROTATE ----------
        self.create_button(
            center_toolbar,
            "Rotate Left",
            lambda: self.rotate_image(90),
            c["transform"],
            c["transform_hover"],
            padx=10,
            pady=7
        )

        self.create_button(
            center_toolbar,
            "Rotate Right",
            lambda: self.rotate_image(-90),
            c["transform"],
            c["transform_hover"],
            padx=10,
            pady=7
        )

        # ---------- FLIP ----------
        self.create_button(
            center_toolbar,
            "Flip Horizontal",
            self.flip_horizontal,
            c["transform"],
            c["transform_hover"],
            padx=10,
            pady=7
        )

        self.create_button(
            center_toolbar,
            "Flip Vertical",
            self.flip_vertical,
            c["transform"],
            c["transform_hover"],
            padx=10,
            pady=7
        )

        # ---------- SAVE AS ----------
        self.create_button(
            right_toolbar,
            "Save As",
            self.save_image,
            c["save"],
            c["save_hover"],
            padx=12,
            pady=7
        )

        # ================= MAIN IMAGE PREVIEW =================
        image_container = tk.Frame(
            self.root,
            bg=c["background"]
        )
        image_container.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(5, 5)
        )

        self.canvas = tk.Canvas(
            image_container,
            bg=c["canvas"],
            highlightthickness=1,
            highlightbackground=c["border"]
        )
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<Configure>", self.on_canvas_resize)
        self.canvas.bind("<MouseWheel>", self.zoom_image)
        self.canvas.bind("<Button-4>", self.zoom_image)
        self.canvas.bind("<Button-5>", self.zoom_image)

        # Move image by dragging
        self.canvas.bind("<ButtonPress-1>", self.crop_mouse_down)
        self.canvas.bind("<B1-Motion>", self.crop_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.crop_mouse_up)

        # Drag-and-drop support
        if DND_AVAILABLE:
            self.canvas.drop_target_register(DND_FILES)
            self.canvas.dnd_bind("<<Drop>>", self.drop_image)

        # ================= BOTTOM AREA =================
        bottom_area = tk.Frame(
            self.root,
            bg=c["panel"],
            highlightbackground=c["border"],
            highlightthickness=1
        )
        bottom_area.pack(
            fill="x",
            side="bottom",
            padx=10,
            pady=(0, 10)
        )

        # Image information
        info_bar = tk.Frame(
            bottom_area,
            bg=c["panel_inner"]
        )
        info_bar.pack(fill="x", padx=5, pady=(5, 5))

        self.filename_label = tk.Label(
            info_bar,
            text="File: No image loaded",
            font=("Segoe UI", 9),
            bg=c["panel_inner"],
            fg=c["text"],
            anchor="w"
        )
        self.filename_label.grid(
            row=0, column=0, sticky="ew", padx=10, pady=5
        )

        self.dimensions_label = tk.Label(
            info_bar,
            text="Dimensions: —",
            font=("Segoe UI", 9),
            bg=c["panel_inner"],
            fg=c["text"],
            anchor="w"
        )
        self.dimensions_label.grid(
            row=0, column=1, sticky="ew", padx=10, pady=5
        )

        self.format_label = tk.Label(
            info_bar,
            text="Format: —",
            font=("Segoe UI", 9),
            bg=c["panel_inner"],
            fg=c["text"],
            anchor="w"
        )
        self.format_label.grid(
            row=1, column=0, sticky="ew", padx=10, pady=5
        )

        self.filesize_label = tk.Label(
            info_bar,
            text="File Size: —",
            font=("Segoe UI", 9),
            bg=c["panel_inner"],
            fg=c["text"],
            anchor="w"
        )
        self.filesize_label.grid(
            row=1, column=1, sticky="ew", padx=10, pady=5
        )

        info_bar.grid_columnconfigure(0, weight=1)
        info_bar.grid_columnconfigure(1, weight=1)

        # ================= BOTTOM CONTROLS =================
        controls_bar = tk.Frame(
            bottom_area,
            bg=c["panel"]
        )
        controls_bar.pack(fill="x", padx=5, pady=(0, 3))

        self.zoom_label = tk.Label(
            controls_bar,
            text="Zoom: 100%",
            font=("Segoe UI", 9),
            bg=c["panel"],
            fg=c["secondary_text"]
        )
        self.zoom_label.pack(side="left", padx=10, pady=5)

        self.status_label = tk.Label(
            controls_bar,
            text="Ready",
            font=("Segoe UI", 9),
            bg=c["panel"],
            fg=c["secondary_text"]
        )
        self.status_label.pack(side="left", padx=10, pady=5)

        right_controls = tk.Frame(
            controls_bar,
            bg=c["panel"]
        )
        right_controls.pack(side="right")

        self.create_button(
            right_controls,
            "Clear",
            self.clear_image,
            c["clear"],
            c["clear_hover"]
        )

        self.create_button(
            right_controls,
            "Exit",
            self.exit_app,
            c["exit"],
            c["exit_hover"]
        )

    # ================= GLASS-STYLE BUTTONS =================
    def create_button(
        self,
        parent,
        text,
        command,
        color,
        hover_color=None,
        side="left",
        padx=10,
        pady=7
    ):
        if hover_color is None:
            hover_color = color

        shadow_frame = tk.Frame(
            parent,
            bg=self.colors["button_shadow"],
            bd=0,
            highlightthickness=0
        )
        shadow_frame.pack(
            side=side,
            padx=4,
            pady=4
        )

        button_border = tk.Frame(
            shadow_frame,
            bg=self.colors["button_border"],
            bd=0,
            padx=1,
            pady=1
        )
        button_border.pack(
            padx=(0, 2),
            pady=(0, 2)
        )

        button = tk.Button(
            button_border,
            text=text,
            command=command,
            bg=color,
            fg="white",
            activebackground=hover_color,
            activeforeground="white",
            disabledforeground="#D6D0C6",
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            font=("Segoe UI", 9, "bold"),
            padx=padx,
            pady=pady,
            cursor="hand2",
            takefocus=True
        )
        button.pack()

        button.shadow_frame = shadow_frame
        button.button_border = button_border
        button.normal_color = color
        button.hover_color = hover_color

        def on_enter(event):
            if str(button["state"]) != "disabled":
                button.config(
                    bg=hover_color,
                    activebackground=hover_color
                )
                button_border.config(
                    bg=self.colors["button_highlight"]
                )

        def on_leave(event):
            if str(button["state"]) != "disabled":
                button.config(
                    bg=color,
                    activebackground=hover_color
                )
                button_border.config(
                    bg=self.colors["button_border"]
                )

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

        return button

    # ================= KEYBOARD SHORTCUTS =================
    def bind_shortcuts(self):
        self.root.bind(
            "<F11>",
            lambda event: self.toggle_fullscreen()
        )
        self.root.bind(
            "<Escape>",
            self.handle_escape
        )
        self.root.bind(
            "<Control-o>",
            lambda event: self.open_image()
        )
        self.root.bind(
            "<Control-s>",
            lambda event: self.save_image()
        )
        self.root.bind(
            "<Control-z>",
            lambda event: self.undo()
        )
        self.root.bind(
            "<Control-y>",
            lambda event: self.redo()
        )
        self.root.bind(
            "<Control-Shift-Z>",
            lambda event: self.redo()
        )

    def handle_escape(self, event=None):
        if self.is_fullscreen:
            self.toggle_fullscreen()

    # ================= UNDO / REDO =================
    def save_history(self):
        if self.current_image is None:
            return

        self.undo_stack.append(self.current_image.copy())

        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)

        self.redo_stack.clear()
        self.update_history_buttons()

    def undo(self):
        if self.current_image is None or not self.undo_stack:
            self.status_label.config(text="Nothing to undo")
            return

        self.redo_stack.append(self.current_image.copy())
        self.current_image = self.undo_stack.pop()

        self.render_image()
        self.update_image_info()
        self.update_history_buttons()

        self.status_label.config(text="Undo successful")

    def redo(self):
        if self.current_image is None or not self.redo_stack:
            self.status_label.config(text="Nothing to redo")
            return

        self.undo_stack.append(self.current_image.copy())

        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)

        self.current_image = self.redo_stack.pop()

        self.render_image()
        self.update_image_info()
        self.update_history_buttons()

        self.status_label.config(text="Redo successful")

    def update_history_buttons(self):
        if self.undo_button is not None:
            self.undo_button.config(
                state="normal" if self.undo_stack else "disabled"
            )

        if self.redo_button is not None:
            self.redo_button.config(
                state="normal" if self.redo_stack else "disabled"
            )

    def reset_history(self):
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.update_history_buttons()

    # ================= OPEN IMAGE =================
    def open_image(self):
        path = filedialog.askopenfilename(
            title="Open Image",
            filetypes=[
                (
                    "All Supported Images",
                    "*.png *.jpg *.jpeg *.jpe *.jfif *.bmp *.dib "
                    "*.gif *.tif *.tiff *.webp *.ico *.icns "
                    "*.ppm *.pgm *.pbm *.pnm *.pcx *.tga "
                    "*.jp2 *.j2k *.jpf *.jpx *.j2c "
                    "*.apng *.avif *.heic *.heif *.psd",
                ),
                ("PNG Images", "*.png"),
                ("JPEG Images", "*.jpg *.jpeg *.jpe *.jfif"),
                ("BMP Images", "*.bmp *.dib"),
                ("GIF Images", "*.gif"),
                ("TIFF Images", "*.tif *.tiff"),
                ("WebP Images", "*.webp"),
                ("Icon Files", "*.ico *.icns"),
                ("Portable Images", "*.ppm *.pgm *.pbm *.pnm"),
                (
                    "Other Image Formats",
                    "*.pcx *.tga *.jp2 *.j2k *.jpf *.jpx *.j2c",
                ),
                ("All Files", "*.*"),
            ],
        )

        # Load the selected image.
        if path:
            self.load_image(path)

    # ================= LOAD IMAGE =================
    def load_image(self, file_path):
        try:
            with Image.open(file_path) as img:
                original_format = img.format
                image = ImageOps.exif_transpose(img)
                image.load()
                loaded_image = image.copy()

            self.current_image = loaded_image
            self.image_original = loaded_image.copy()
            self.current_image_format = original_format
            self.current_file_path = file_path

            self.zoom_factor = 1.0

            # Reset image position.
            self.pan_x = 0
            self.pan_y = 0
            self.dragging_image = False

            self.reset_history()

            self.update_image_info()
            self.render_image()

            self.status_label.config(
                text="Image loaded successfully"
            )

        except Exception as error:
            messagebox.showerror(
                "Open Image Error",
                f"Unable to open this image.\n\n{error}"
            )

    # ================= IMAGE DISPLAY =================
    def render_image(self):
        self.canvas.delete("all")

        if self.current_image is None:
            self.photo_image = None
            return

        canvas_width = max(self.canvas.winfo_width(), 1)
        canvas_height = max(self.canvas.winfo_height(), 1)

        image_width, image_height = self.current_image.size

        if image_width <= 0 or image_height <= 0:
            return

        fit_scale = min(
            canvas_width / image_width,
            canvas_height / image_height
        )

        self.display_scale = fit_scale * self.zoom_factor

        display_width = max(
            1, int(image_width * self.display_scale)
        )
        display_height = max(
            1, int(image_height * self.display_scale)
        )

        resized_image = self.current_image.resize(
            (display_width, display_height),
            Image.Resampling.LANCZOS
        )

        self.photo_image = ImageTk.PhotoImage(resized_image)

        self.image_x = (
            (canvas_width - display_width) // 2 + self.pan_x
        )
        self.image_y = (
            (canvas_height - display_height) // 2 + self.pan_y
        )

        self.canvas.create_image(
            self.image_x,
            self.image_y,
            anchor="nw",
            image=self.photo_image,
            tags="image"
        )

        self.zoom_label.config(
            text=f"Zoom: {int(self.zoom_factor * 100)}%"
        )

    def on_canvas_resize(self, event=None):
        self.render_image()

    # ================= ZOOM =================
    def zoom_image(self, event):
        if self.current_image is None:
            return

        if getattr(event, "delta", 0):
            direction = 1 if event.delta > 0 else -1
        elif getattr(event, "num", None) == 4:
            direction = 1
        elif getattr(event, "num", None) == 5:
            direction = -1
        else:
            return

        if direction > 0:
            self.zoom_factor *= 1.1
        else:
            self.zoom_factor /= 1.1

        self.zoom_factor = max(
            0.1,
            min(self.zoom_factor, 8.0)
        )

        self.render_image()

    # ================= ROTATE AND FLIP =================
    def rotate_image(self, angle):
        if self.current_image is None:
            messagebox.showinfo(
                "No Image",
                "Please open an image first."
            )
            return

        self.save_history()

        self.current_image = self.current_image.rotate(
            angle,
            expand=True
        )

        self.render_image()
        self.update_image_info()

        self.status_label.config(text="Image rotated")

    def flip_horizontal(self):
        if self.current_image is None:
            messagebox.showinfo(
                "No Image",
                "Please open an image first."
            )
            return

        self.save_history()

        self.current_image = ImageOps.mirror(self.current_image)

        self.render_image()
        self.update_image_info()

        self.status_label.config(
            text="Image flipped horizontally"
        )

    def flip_vertical(self):
        if self.current_image is None:
            messagebox.showinfo(
                "No Image",
                "Please open an image first."
            )
            return

        self.save_history()

        self.current_image = ImageOps.flip(self.current_image)

        self.render_image()
        self.update_image_info()

        self.status_label.config(
            text="Image flipped vertically"
        )

    # ================= IMAGE MOVEMENT =================
    def crop_mouse_down(self, event):
        if self.current_image is None:
            return

        display_width = (
            self.current_image.width * self.display_scale
        )
        display_height = (
            self.current_image.height * self.display_scale
        )

        inside_image = (
            self.image_x <= event.x <= self.image_x + display_width
            and self.image_y <= event.y <= self.image_y + display_height
        )

        if not inside_image:
            return

        self.dragging_image = True
        self.drag_last_x = event.x
        self.drag_last_y = event.y

    def crop_mouse_move(self, event):
        if (
            self.current_image is None
            or not self.dragging_image
        ):
            return

        delta_x = event.x - self.drag_last_x
        delta_y = event.y - self.drag_last_y

        self.pan_x += delta_x
        self.pan_y += delta_y

        self.drag_last_x = event.x
        self.drag_last_y = event.y

        self.render_image()

    def crop_mouse_up(self, event):
        if self.dragging_image:
            self.dragging_image = False
            self.status_label.config(
                text="Image position updated"
            )

    # ================= SAVE IMAGE =================
    def save_image(self):
        if self.current_image is None:
            messagebox.showinfo(
                "No Image",
                "Please open an image first."
            )
            return

        default_name = "edited_image.png"

        if self.current_file_path:
            base_name = os.path.splitext(
                os.path.basename(self.current_file_path)
            )[0]

            default_name = f"{base_name}_edited.png"

        file_path = filedialog.asksaveasfilename(
            title="Save Image As",
            defaultextension=".png",
            initialfile=default_name,
            filetypes=[
                ("PNG Image", "*.png"),
                ("JPEG Image", "*.jpg *.jpeg"),
                ("WebP Image", "*.webp"),
                ("TIFF Image", "*.tiff *.tif"),
                ("BMP Image", "*.bmp")
            ]
        )

        if not file_path:
            return

        try:
            extension = os.path.splitext(file_path)[1].lower()
            image_to_save = self.current_image.copy()

            if extension in (".jpg", ".jpeg", ".bmp"):
                if image_to_save.mode in ("RGBA", "LA") or (
                    image_to_save.mode == "P"
                    and "transparency" in image_to_save.info
                ):
                    image_to_save = image_to_save.convert("RGBA")

                    background = Image.new(
                        "RGB",
                        image_to_save.size,
                        (255, 255, 255)
                    )

                    background.paste(
                        image_to_save,
                        mask=image_to_save.getchannel("A")
                    )

                    image_to_save = background
                else:
                    image_to_save = image_to_save.convert("RGB")

            image_to_save.save(file_path)

            self.status_label.config(
                text="Image saved successfully"
            )

            messagebox.showinfo(
                "Saved Successfully",
                f"Image saved successfully:\n{file_path}"
            )

        except Exception as error:
            messagebox.showerror(
                "Save Error",
                f"Unable to save the image.\n\n{error}"
            )

    # ================= IMAGE INFORMATION =================
    def update_image_info(self):
        if self.current_image is None:
            return

        filename = (
            os.path.basename(self.current_file_path)
            if self.current_file_path
            else "Untitled"
        )

        width, height = self.current_image.size

        self.filename_label.config(text=f"File: {filename}")

        self.dimensions_label.config(
            text=f"Dimensions: {width} × {height} pixels"
        )

        image_format = (
            self.current_image_format
            or self.current_image.format
            or "Edited Image"
        )

        self.format_label.config(text=f"Format: {image_format}")

        if (
            self.current_file_path
            and os.path.exists(self.current_file_path)
        ):
            size_bytes = os.path.getsize(self.current_file_path)
            size_kb = size_bytes / 1024

            self.filesize_label.config(
                text=f"File Size: {size_kb:.2f} KB"
            )
        else:
            self.filesize_label.config(text="File Size: Unsaved")

    # ================= CLEAR IMAGE =================
    def clear_image(self):
        self.current_image = None
        self.image_original = None
        self.display_image = None
        self.photo_image = None

        self.current_file_path = None
        self.current_image_format = None

        self.zoom_factor = 1.0
        self.display_scale = 1.0

        self.pan_x = 0
        self.pan_y = 0
        self.dragging_image = False

        self.reset_history()
        self.canvas.delete("all")

        self.filename_label.config(text="File: No image loaded")
        self.dimensions_label.config(text="Dimensions: —")
        self.format_label.config(text="Format: —")
        self.filesize_label.config(text="File Size: —")
        self.zoom_label.config(text="Zoom: 100%")
        self.status_label.config(text="Ready")

    # ================= FULL SCREEN =================
    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen

        self.root.attributes("-fullscreen", self.is_fullscreen)

        if self.is_fullscreen:
            self.fullscreen_btn.config(text="⛶ Exit Full Screen")
        else:
            self.fullscreen_btn.config(text="⛶ Full Screen")
            self.root.geometry("1100x750")

        self.root.after(100, self.render_image)

    # ================= DRAG AND DROP =================
    def drop_image(self, event):
        file_path = event.data.strip()

        if file_path.startswith("{") and file_path.endswith("}"):
            file_path = file_path[1:-1]

        if os.path.isfile(file_path):
            self.load_image(file_path)

    # ================= EXIT APPLICATION =================
    def exit_app(self):
        if messagebox.askyesno(
            "Exit SnapView",
            "Are you sure you want to exit SnapView Image Viewer?"
        ):
            self.root.destroy()


if __name__ == "__main__":
    if DND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()

    app = ImageViewerApp(root)
    root.mainloop()