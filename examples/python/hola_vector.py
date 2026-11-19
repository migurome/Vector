"""Prueba mínima del SDK: Vector habla, mueve cabeza y brazo, y guarda una foto.

Requisitos: robot autenticado en wire-pod, `pip install wirepod_vector_sdk` y
`python -m anki_vector.configure` ejecutado una vez. Uso: python hola_vector.py [serial]
"""
import sys

import anki_vector
from anki_vector.util import degrees


def main():
    serial = sys.argv[1] if len(sys.argv) > 1 else None  # None = robot por defecto de sdk_config.ini
    with anki_vector.Robot(serial) as robot:
        print("Batería:", robot.get_battery_state().battery_level)
        robot.behavior.say_text("Hola, soy Vector y sigo vivo")
        robot.behavior.set_head_angle(degrees(30))
        robot.behavior.set_lift_height(1.0)
        robot.behavior.set_lift_height(0.0)
        robot.camera.capture_single_image().raw_image.save("vector_foto.jpg")
        print("Foto guardada en vector_foto.jpg")


if __name__ == "__main__":
    main()
