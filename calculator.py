import numpy as np
from PIL import Image, UnidentifiedImageError


def calculate_percent_black(image_path: str):
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
