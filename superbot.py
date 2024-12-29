import requests
import time
from PIL import Image
import threading

class PlaceBot:
    def __init__(self, grid_size=64):
        self.grid_size = grid_size
        self.target_image = [[[255, 255, 255] for _ in range(grid_size)] for _ in range(grid_size)]
        self.lock = threading.Lock()

    def load_image(self, file_path):
        try:
            with Image.open(file_path) as img:
                img = img.convert("RGB")
                pixels = list(img.getdata())
                self.target_image = [pixels[i * self.grid_size:(i + 1) * self.grid_size] for i in range(self.grid_size)]
                if len(self.target_image) != self.grid_size or any(len(row) != self.grid_size for row in self.target_image):
                    raise ValueError("Image dimensions must be 64x64.")
        except Exception as e:
            raise ValueError(f"Failed to load image: {e}")

    def check_and_update_pixel(self, x, y, color):
        url = "https://place.danieldb.uk/set_pixel_color"
        payload = {"x": x, "y": y, "r": color[0], "g": color[1], "b": color[2]}
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
        except requests.RequestException:
            pass

    def update_pixel_with_delay(self, x, y):
        color = self.target_image[y][x]
        self.check_and_update_pixel(x, y, color)
        print(f"Changing the pixel at ({x}, {y}) to {color}")

    def run(self):
        threads = []

        for y in range(self.grid_size):
            for x in range(self.grid_size):
                thread = threading.Thread(target=self.update_pixel_with_delay, args=(x, y))
                threads.append(thread)
                thread.start()

        for thread in threads:
            thread.join()

if __name__ == "__main__":
    bot = PlaceBot()
    bot.load_image("file.png")
    while True:
        bot.run()
