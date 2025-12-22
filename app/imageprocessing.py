import asyncio
from PIL import Image
from pathlib import Path


def open_image():
    path = Path.cwd().parent / "images/african-family.jpg"

    print(path)
    with Image.open(path) as img:
        print(img.size)


open_image()
