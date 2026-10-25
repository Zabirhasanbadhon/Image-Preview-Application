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
        self.root.title("ZaBir | SnapView Image Viewer")
        self.root.geometry("1100x750")
        self.root.minsize(760, 560)
        self.root.configure(bg="#0b1120")

        self.image_original = None
        self.current_image = None
        self.display_image = None
        self.photo_image = None

        self.zoom_factor = 1.0
        self.display_scale = 1.0
        self.image_x = 0
        self.image_y = 0

        self.crop_start_x = None
        self.crop_start_y = None
        self.crop_end_x = None
        self.crop_end_y = None
        self.crop_rectangle = None
        self.crop_active = False

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
        # Header
        header = tk.Frame(self.root, bg="#111c31", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="📷 ZaBir HaSan",
            font=("Segoe UI", 18, "bold"),
            bg="#111c31",
            fg="#e5e7eb"
        ).pack(side="left", padx=20)

        self.fullscreen_btn = tk.Button(
            header,
            text="⛶ Full Screen",
            command=self.toggle_fullscreen,
            bg="#263650",
            fg="white",
            activebackground="#354a69",
            activeforeground="white",
            relief="flat",
            padx=12,
            pady=7,
            cursor="hand2"
        )
        self.fullscreen_btn.pack(side="right", padx=15)

        # Top toolbar
        toolbar = tk.Frame(self.root, bg="#0f172a")
        toolbar.pack(fill="x", padx=10, pady=(8, 5))

        self.create_button(
            toolbar, "Open Image", self.open_image, "#2563eb"
        )
        self.create_button(
            toolbar, "Save As", self.save_image, "#0f766e"
        )
        self.create_button(
            toolbar, "Start Crop", self.start_crop, "#7c3aed"
        )
        self.create_button(
            toolbar, "Apply Crop", self.apply_crop, "#6d28d9"
        )
        self.create_button(
            toolbar, "Cancel Crop", self.cancel_crop, "#a16207"
        )
        self.undo_button = self.create_button(
            toolbar, "Undo", self.undo, "#475569"
        )
        self.redo_button = self.create_button(
            toolbar, "Redo", self.redo, "#475569"
        )
        self.create_button(
            toolbar, "Rotate Left", lambda: self.rotate_image(90), "#334155"
        )
        self.create_button(
            toolbar, "Rotate Right", lambda: self.rotate_image(-90), "#334155"
        )
        self.create_button(
            toolbar, "Flip Horizontal", self.flip_horizontal, "#334155"
        )
        self.create_button(
            toolbar, "Flip Vertical", self.flip_vertical, "#334155"
        )

        # Main image preview
        image_container = tk.Frame(self.root, bg="#0b1120")
        image_container.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(5, 5)
        )

        self.canvas = tk.Canvas(
            image_container,
            bg="#080e1a",
            highlightthickness=1,
            highlightbackground="#263650"
        )
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<Configure>", self.on_canvas_resize)
        self.canvas.bind("<MouseWheel>", self.zoom_image)
        self.canvas.bind("<Button-4>", self.zoom_image)
        self.canvas.bind("<Button-5>", self.zoom_image)

        self.canvas.bind("<ButtonPress-1>", self.crop_mouse_down)
        self.canvas.bind("<B1-Motion>", self.crop_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.crop_mouse_up)

        if DND_AVAILABLE:
            self.canvas.drop_target_register(DND_FILES)
            self.canvas.dnd_bind("<<Drop>>", self.drop_image)

        # Bottom area: image information and Clear/Exit
        bottom_area = tk.Frame(self.root, bg="#111c31")
        bottom_area.pack(
            fill="x",
            side="bottom",
            padx=10,
            pady=(0, 10)
        )

        # Compact image information bar
        info_bar = tk.Frame(bottom_area, bg="#17243a")
        info_bar.pack(fill="x", padx=5, pady=(5, 5))

        self.filename_label = tk.Label(
            info_bar,
            text="File: No image loaded",
            font=("Segoe UI", 9),
            bg="#17243a",
            fg="#cbd5e1",
            anchor="w"
        )
        self.filename_label.grid(
            row=0, column=0, sticky="ew", padx=10, pady=5
        )

        self.dimensions_label = tk.Label(
            info_bar,
            text="Dimensions: —",
            font=("Segoe UI", 9),
            bg="#17243a",
            fg="#cbd5e1",
            anchor="w"
        )
        self.dimensions_label.grid(
            row=0, column=1, sticky="ew", padx=10, pady=5
        )

        self.format_label = tk.Label(
            info_bar,
            text="Format: —",
            font=("Segoe UI", 9),
            bg="#17243a",
            fg="#cbd5e1",
            anchor="w"
        )
        self.format_label.grid(
            row=1, column=0, sticky="ew", padx=10, pady=5
        )

        self.filesize_label = tk.Label(
            info_bar,
            text="File Size: —",
            font=("Segoe UI", 9),
            bg="#17243a",
            fg="#cbd5e1",
            anchor="w"
        )
        self.filesize_label.grid(
            row=1, column=1, sticky="ew", padx=10, pady=5
        )

        info_bar.grid_columnconfigure(0, weight=1)
        info_bar.grid_columnconfigure(1, weight=1)

        # Bottom controls
        controls_bar = tk.Frame(bottom_area, bg="#111c31")
        controls_bar.pack(fill="x", padx=5, pady=(0, 3))

        self.zoom_label = tk.Label(
            controls_bar,
            text="Zoom: 100%",
            font=("Segoe UI", 9),
            bg="#111c31",
            fg="#94a3b8"
        )
        self.zoom_label.pack(side="left", padx=10, pady=5)

        self.status_label = tk.Label(
            controls_bar,
            text="Ready",
            font=("Segoe UI", 9),
            bg="#111c31",
            fg="#94a3b8"
        )
        self.status_label.pack(side="left", padx=10, pady=5)

        right_controls = tk.Frame(controls_bar, bg="#111c31")
        right_controls.pack(side="right")

        self.create_button(
            right_controls, "Clear", self.clear_image, "#b45309"
        )
        self.create_button(
            right_controls, "Exit", self.exit_app, "#dc2626"
        )

    def create_button(self, parent, text, command, color):
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg="white",
            activebackground="#475569",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=7,
            cursor="hand2"
        )
        button.pack(side="left", padx=3, pady=3)
        return button

    # ================= KEYBOARD SHORTCUTS =================
    def bind_shortcuts(self):
        self.root.bind("<F11>", lambda event: self.toggle_fullscreen())
        self.root.bind("<Escape>", self.handle_escape)
        self.root.bind("<Control-o>", lambda event: self.open_image())
        self.root.bind("<Control-s>", lambda event: self.save_image())
        self.root.bind("<Control-z>", lambda event: self.undo())
        self.root.bind("<Control-y>", lambda event: self.redo())
        self.root.bind("<Control-Shift-Z>", lambda event: self.redo())

    def handle_escape(self, event=None):
        if self.crop_active:
            self.cancel_crop()
        elif self.is_fullscreen:
            self.toggle_fullscreen()

    # ================= UNDO / REDO =================
    def save_history(self):
        """Save the current image before applying an edit."""
        if self.current_image is None:
            return

        self.undo_stack.append(self.current_image.copy())

        # Limit memory use by keeping only the latest history entries.
        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)

        # A new edit invalidates the previous redo history.
        self.redo_stack.clear()
        self.update_history_buttons()

    def undo(self):
        if self.current_image is None or not self.undo_stack:
            self.status_label.config(text="Nothing to undo")
            return

        self.redo_stack.append(self.current_image.copy())
        self.current_image = self.undo_stack.pop()

        self.cancel_crop_state()
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

        self.cancel_crop_state()
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
        file_path = filedialog.askopenfilename(
            title="Open Image",
            filetypes=[
                (
                    "Image Files",
                    "*.png *.jpg *.jpeg *.gif *.bmp *.tif *.tiff *.webp"
                ),
                ("All Files", "*.*")
            ]
        )

        if file_path:
            self.load_image(file_path)

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
            self.cancel_crop_state()
            self.reset_history()

            self.update_image_info()
            self.render_image()

            self.status_label.config(text="Image loaded successfully")

        except Exception as error:
            messagebox.showerror(
                "Open Image Error",
                f"Unable to open this image.\n\n{error}"
            )

    # ================= IMAGE DISPLAY =================
    def render_image(self):
        self.canvas.delete("all")
        self.crop_rectangle = None

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

        display_width = max(1, int(image_width * self.display_scale))
        display_height = max(1, int(image_height * self.display_scale))

        resized_image = self.current_image.resize(
            (display_width, display_height),
            Image.Resampling.LANCZOS
        )

        self.photo_image = ImageTk.PhotoImage(resized_image)

        self.image_x = (canvas_width - display_width) // 2
        self.image_y = (canvas_height - display_height) // 2

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

        # Redraw an active crop selection after a canvas redraw.
        if (
            self.crop_active
            and self.crop_start_x is not None
            and self.crop_start_y is not None
            and self.crop_end_x is not None
            and self.crop_end_y is not None
        ):
            self.crop_rectangle = self.canvas.create_rectangle(
                self.crop_start_x,
                self.crop_start_y,
                self.crop_end_x,
                self.crop_end_y,
                outline="#38bdf8",
                width=2,
                dash=(5, 3)
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

        self.zoom_factor = max(0.1, min(self.zoom_factor, 8.0))
        self.render_image()

    # ================= ROTATE AND FLIP =================
    def rotate_image(self, angle):
        if self.current_image is None:
            messagebox.showinfo("No Image", "Please open an image first.")
            return

        self.save_history()
        self.current_image = self.current_image.rotate(angle, expand=True)

        self.cancel_crop_state()
        self.render_image()
        self.update_image_info()

        self.status_label.config(text="Image rotated")

    def flip_horizontal(self):
        if self.current_image is None:
            messagebox.showinfo("No Image", "Please open an image first.")
            return

        self.save_history()
        self.current_image = ImageOps.mirror(self.current_image)

        self.cancel_crop_state()
        self.render_image()
        self.update_image_info()

        self.status_label.config(text="Image flipped horizontally")

    def flip_vertical(self):
        if self.current_image is None:
            messagebox.showinfo("No Image", "Please open an image first.")
            return

        self.save_history()
        self.current_image = ImageOps.flip(self.current_image)

        self.cancel_crop_state()
        self.render_image()
        self.update_image_info()

        self.status_label.config(text="Image flipped vertically")

    # ================= CROP =================
    def start_crop(self):
        if self.current_image is None:
            messagebox.showinfo("No Image", "Please open an image first.")
            return

        self.cancel_crop_state()
        self.crop_active = True

        self.status_label.config(
            text="Crop mode: drag to select an area"
        )

    def crop_mouse_down(self, event):
        if not self.crop_active or self.current_image is None:
            return

        # Ignore clicks outside the displayed image.
        display_width = self.current_image.width * self.display_scale
        display_height = self.current_image.height * self.display_scale

        if not (
            self.image_x <= event.x <= self.image_x + display_width
            and self.image_y <= event.y <= self.image_y + display_height
        ):
            return

        if self.crop_rectangle:
            self.canvas.delete(self.crop_rectangle)

        self.crop_start_x = event.x
        self.crop_start_y = event.y
        self.crop_end_x = event.x
        self.crop_end_y = event.y

        self.crop_rectangle = self.canvas.create_rectangle(
            event.x,
            event.y,
            event.x,
            event.y,
            outline="#38bdf8",
            width=2,
            dash=(5, 3)
        )

    def crop_mouse_move(self, event):
        if not self.crop_active or self.crop_start_x is None:
            return

        self.crop_end_x = event.x
        self.crop_end_y = event.y

        if self.crop_rectangle:
            self.canvas.coords(
                self.crop_rectangle,
                self.crop_start_x,
                self.crop_start_y,
                self.crop_end_x,
                self.crop_end_y
            )

    def crop_mouse_up(self, event):
        if not self.crop_active or self.crop_start_x is None:
            return

        self.crop_end_x = event.x
        self.crop_end_y = event.y

        if self.crop_rectangle:
            self.canvas.coords(
                self.crop_rectangle,
                self.crop_start_x,
                self.crop_start_y,
                self.crop_end_x,
                self.crop_end_y
            )

    def apply_crop(self):
        if not self.crop_active or self.current_image is None:
            messagebox.showinfo(
                "Crop",
                "Click Start Crop and select an area first."
            )
            return

        if (
            self.crop_start_x is None
            or self.crop_start_y is None
            or self.crop_end_x is None
            or self.crop_end_y is None
        ):
            messagebox.showinfo(
                "Crop",
                "Drag over the image to select a crop area first."
            )
            return

        x1 = min(self.crop_start_x, self.crop_end_x)
        y1 = min(self.crop_start_y, self.crop_end_y)
        x2 = max(self.crop_start_x, self.crop_end_x)
        y2 = max(self.crop_start_y, self.crop_end_y)

        left = int((x1 - self.image_x) / self.display_scale)
        top = int((y1 - self.image_y) / self.display_scale)
        right = int((x2 - self.image_x) / self.display_scale)
        bottom = int((y2 - self.image_y) / self.display_scale)

        left = max(0, min(left, self.current_image.width))
        top = max(0, min(top, self.current_image.height))
        right = max(0, min(right, self.current_image.width))
        bottom = max(0, min(bottom, self.current_image.height))

        if right <= left or bottom <= top:
            messagebox.showwarning(
                "Invalid Crop",
                "Please select a valid area inside the image."
            )
            return

        # Save the pre-crop image so the crop can be undone.
        self.save_history()

        self.current_image = self.current_image.crop(
            (left, top, right, bottom)
        )

        self.zoom_factor = 1.0
        self.cancel_crop_state()

        self.render_image()
        self.update_image_info()
        self.update_history_buttons()

        self.status_label.config(text="Crop applied successfully")

    def cancel_crop_state(self):
        self.crop_active = False
        self.crop_start_x = None
        self.crop_start_y = None
        self.crop_end_x = None
        self.crop_end_y = None
        self.crop_rectangle = None

    def cancel_crop(self):
        if not self.crop_active:
            self.status_label.config(text="No active crop selection")
            return

        self.cancel_crop_state()
        self.render_image()

        self.status_label.config(text="Crop selection cancelled")

    # ================= SAVE IMAGE =================
    def save_image(self):
        if self.current_image is None:
            messagebox.showinfo("No Image", "Please open an image first.")
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

            self.status_label.config(text="Image saved successfully")

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

        if self.current_file_path and os.path.exists(self.current_file_path):
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

        self.cancel_crop_state()
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
