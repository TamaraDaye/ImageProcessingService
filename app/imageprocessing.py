import asyncio
from PIL import Image
from pathlib import Path
import time

start = time.perf_counter()
imgpath = Path.cwd().parent / "images/african-family.jpg"


async def load_image(path):
    try:
        img = await asyncio.to_thread(Image.open, path)
        print(img.format, img.size, img.mode)
        rotated_img = img.rotate(45)
        rotated_img.show()
    except Exception as e:
        print(e)
    finally:
        img.close()


async def timer(seconds):
    print("Executing first")
    await asyncio.sleep(seconds)
    print("done executing")


async def main():
    task1 = asyncio.create_task(load_image(imgpath))
    task2 = asyncio.create_task(timer(10))

    await task1
    await task2


if __name__ == "__main__":
    asyncio.run(main())
