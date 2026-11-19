"""Muestra una imagen o un GIF animado en la cara de Vector (184x96).

Uso:
    python pantalla.py                    # demo: dibuja un saludo
    python pantalla.py foto.jpg [segundos] # imagen fija (por defecto 5 s)
    python pantalla.py animacion.gif [vueltas]   # GIF animado (por defecto 2 vueltas)

La imagen se adapta sin deformar (bandas negras si la proporción no coincide).
"""
import sys
import time

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageSequence

import anki_vector
from anki_vector.screen import SCREEN_HEIGHT, SCREEN_WIDTH, convert_image_to_screen_data

SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)


def to_screen(img: Image.Image) -> bytes:
    """Adapta cualquier imagen PIL al formato de la pantalla."""
    fitted = ImageOps.pad(img.convert("RGB"), SIZE, color=(0, 0, 0))
    return convert_image_to_screen_data(fitted)


def demo() -> Image.Image:
    img = Image.new("RGB", SIZE, (0, 30, 60))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 34)
    except OSError:
        font = ImageFont.load_default()
    d.text((SIZE[0] // 2, SIZE[1] // 2), "¡Hola!", fill=(0, 220, 255), font=font, anchor="mm")
    return img


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else None
    extra = float(sys.argv[2]) if len(sys.argv) > 2 else None
    with anki_vector.Robot() as robot:
        if path is None or not path.lower().endswith(".gif"):
            secs = extra or 5.0
            img = demo() if path is None else Image.open(path)
            robot.screen.set_screen_with_image_data(to_screen(img), secs)
            time.sleep(secs)
            return
        gif = Image.open(path)
        frames = [(to_screen(f), f.info.get("duration", 100) / 1000) for f in ImageSequence.Iterator(gif)]
        for _ in range(int(extra or 2)):
            for data, dur in frames:
                # duración algo mayor que el fotograma para que no parpadee entre envíos
                robot.screen.set_screen_with_image_data(data, dur + 0.5)
                time.sleep(dur)


if __name__ == "__main__":
    main()
