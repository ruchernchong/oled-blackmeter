from PIL import Image
import numpy as np


def calculate_percent_black(image_path: str) -> int:
    image = Image.open(image_path)
    image_grayscale = image.convert("L")
    image_array = np.array(image_grayscale)

    black_pixels = np.sum(image_array == 0)
    total_pixels = image_array.size
    percent_black = black_pixels / total_pixels * 100

    print(f"Percentage black: {percent_black}%")

    return percent_black


if __name__ == "__main__":
    calculate_percent_black("OLED Black 4K.png")
