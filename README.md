# ZaBir | SnapView Image Viewer

**ZaBir | SnapView Image Viewer** is a modern desktop image viewer built with Python and Tkinter. It provides a clean, dark-themed interface for viewing images with zoom, rotation, flipping, full-screen viewing, and drag-and-drop support.

## ✨ Features

- **Open Images:** Load images from your computer.
- **Zoom Controls:** Zoom in and out using the mouse wheel.
- **Fit to Preview:** Double-click the image to reset the zoom.
- **Image Rotation:** Rotate images 90° left or right.
- **Image Flipping:** Flip images horizontally or vertically.
- **Full-Screen Mode:** View images in full-screen mode.
- **Drag and Drop:** Open images by dragging them into the application.
- **Image Information:** Display the filename, dimensions, format, and file size.
- **Clear Image:** Clear the current preview and return to the default screen.
- **Exit Button:** Close the application directly.
- **Modern UI:** Enjoy a clean interface with a dark theme and purple accents.

## 🛠️ Technologies Used

- **Python** — Core programming language.
- **Tkinter** — Desktop graphical user interface.
- **Pillow (PIL)** — Image loading, processing, rotation, flipping, and resizing.
- **tkinterdnd2** — Optional drag-and-drop functionality.

## 📋 Supported Image Formats

The application supports the following image formats:

- PNG
- JPG / JPEG
- GIF
- BMP
- TIFF
- WebP

## 🚀 Installation

### Install Python

Download and install Python from the official website:

https://www.python.org/downloads/

Make sure Python is added to your system's PATH.

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl + O` | Open an image |
| `F11` | Toggle full-screen mode |
| `Esc` | Exit full-screen mode or clear the image |
| Mouse Wheel | Zoom in or out |
| Double-click | Reset zoom to fit |

## 🖼️ How to Use

1. Launch the application.
2. Click **Open image** to select an image from your computer.
3. Use the mouse wheel to zoom in or out.
4. Double-click the preview to reset the zoom.
5. Use the rotation buttons to rotate the image.
6. Use the flip buttons to flip the image horizontally or vertically.
7. Press `F11` to enter or exit full-screen mode.
8. Click **Clear** to remove the current image.
9. Click **Exit** to close the application.

You can also drag and drop an image into the application if `tkinterdnd2` is installed.

## ⚠️ Important Notes

- Image rotation and flipping affect the preview only.
- The original image file is not modified.
- The application does not currently provide a Save As feature for transformed images.
- Drag-and-drop functionality requires the optional `tkinterdnd2` package.
- Animated GIFs are displayed as static images rather than played as animations.

## 👨‍💻 Author

**ZaBir HaSan**

⭐ **If you find this project useful, consider giving the repository a star on GitHub!**
