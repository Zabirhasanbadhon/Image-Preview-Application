# 📷 ZaBir | Image Viewer

**ZaBir | Image Viewer** is a modern desktop image viewer built with Python and Tkinter. It features a clean **cream-white interface, elegant glass-effect buttons, and a user-friendly layout** for viewing, transforming, and saving images.

With essential image viewing tools, zoom controls, rotation, flipping, undo/redo functionality, and full-screen mode, SnapView provides a simple and comfortable image-viewing experience.

## ✨ Features

- **📂 Open Images:** Load images directly from your computer.
- **💾 Save As:** Save images to your preferred location and choose the output format.
- **🔍 Zoom Controls:** Zoom in and out using the mouse wheel.
- **🖼️ Fit to Preview:** Double-click the preview to reset the zoom and fit the image.
- **🔄 Image Rotation:** Rotate images 90° left or right.
- **↔️ Image Flipping:** Flip images horizontally or vertically.
- **↩️ Undo & Redo:** Undo or redo recent image transformations.
- **🖥️ Full-Screen Mode:** View images in full-screen mode for a larger preview.
- **🖱️ Drag and Drop:** Open images by dragging and dropping them into the application.
- **📋 Image Information:** Display the filename, dimensions, format, and file size.
- **🧹 Clear Image:** Clear the current image and return to the default preview.
- **🚪 Exit Button:** Close the application using the Exit button.
- **🎨 Modern Glass UI:** Enjoy a cream-white theme with subtle button shadows, elegant borders, and hover effects.
- **⌨️ Keyboard Shortcuts:** Quickly access common actions using keyboard shortcuts.

## 🎨 User Interface

SnapView features a clean, modern design focused on simplicity and usability.

- **Cream-white background** for a warm, comfortable viewing experience.
- **Glass-inspired buttons** with subtle shadows and borders.
- **Smooth hover effects** for improved interaction.
- **Organized toolbar** with Open Image, editing controls, and Save As.
- **Clear image preview area** for viewing images at different zoom levels.
- **Minimal and user-friendly layout** designed for everyday use.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| **Python** | Core programming language |
| **Tkinter** | Desktop graphical user interface |
| **Pillow (PIL)** | Image loading, processing, rotation, flipping, and resizing |
| **tkinterdnd2** | Optional drag-and-drop functionality |

## 📋 Supported Image Formats

SnapView supports common image formats, including:

- PNG
- JPG / JPEG
- GIF
- BMP
- TIFF
- WebP

**Note:** Animated GIFs are displayed as static images rather than played as animations.

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl + O` | Open an image |
| `Ctrl + S` | Save the current image using Save As |
| `Ctrl + Z` | Undo the last change |
| `Ctrl + Y` | Redo the last undone change |
| `Ctrl + Shift + Z` | Redo the last undone change |
| `F11` | Toggle full-screen mode |
| `Esc` | Exit full-screen mode or clear the image, depending on the current state |
| Mouse Wheel | Zoom in or out |
| Double-click | Fit the image to the preview |
| Mouse Drag | Move the zoomed image within the preview |

## 🖼️ How to Use

1. **Launch Image Viewer** by running the Python script.
2. **Open an image** by clicking the Open Image button or pressing `Ctrl + O`.
3. **Zoom in or out** using the mouse wheel.
4. **Fit the image to the preview** by double-clicking the image.
5. **Rotate the image** using the Rotate Left or Rotate Right buttons.
6. **Flip the image** horizontally or vertically using the flip buttons.
7. **Undo or redo changes** using the Undo and Redo buttons or keyboard shortcuts.
8. **Save your image** by clicking Save As or pressing `Ctrl + S`, then choosing the destination and filename.
9. **Enter full-screen mode** by pressing `F11`.
10. **Clear the preview** using the Clear button when you want to open another image.
11. **Exit the application** using the Exit button.

You can also drag and drop an image into the application if `tkinterdnd2` is installed.

## ⚠️ Important Notes

- The original image file is not overwritten when you open or transform an image. Use **Save As** to save the resulting image.
- Undo and Redo let you navigate recent image transformations within the application's available history.
- The available undo history is limited to the number of states maintained by the application.
- Drag-and-drop functionality requires the optional `tkinterdnd2` package.
- Animated GIFs are displayed as static images rather than played as animations.
- Supported output formats depend on Pillow and the selected file format.
- The application's appearance may vary slightly depending on the operating system and display settings.

## 👨‍💻 Developer

**ZaBir HaSan**

Made with ❤️ using Python and Tkinter.
