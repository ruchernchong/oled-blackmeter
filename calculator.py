import os.path
import tkinter as tk
from tkinter import filedialog, messagebox

import numpy as np
from PIL import Image, UnidentifiedImageError


def calculate_percent_black(image_path: str) -> int:
    try:
        image = Image.open(image_path)
        image_grayscale = image.convert("L")
        image_array = np.array(image_grayscale)

        black_pixels = np.sum(image_array == 0)
        total_pixels = image_array.size

        return black_pixels / total_pixels * 100

    except UnidentifiedImageError:
        print("The selected file is not a valid image.")
    except Exception as e:
        print(f"An error has occurred: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(
        title="Select files",
        filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff *.tif"),
                   ("PNG files", "*.png"),
                   ("JPEG files", "*.jpg *.jpeg"),
                   ("GIF files", "*.gif"),
                   ("BMP files", "*.bmp"),
                   ("TIFF files", "*.tiff *.tif")]
    )

    if file_path:
        percent_black = calculate_percent_black(file_path)
        image_name = os.path.basename(file_path)
        messagebox.showinfo("Result", f"Image: {image_name}\nTrue Black: {percent_black:.2f}%")
    else:
        print("No file selected")

    root.destroy()
