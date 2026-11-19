"""Luces del cubo de Vector: conecta con el cubo y le pone colores.

Uso:
    python cubo.py                 # demo: arcoíris girando, luego cada esquina de un color
    python cubo.py rojo [segundos] # todo el cubo de un color (nombre o #rrggbb), por defecto 10 s
    python cubo.py off             # apagar las luces

El cubo tiene 4 luces RGB (una por esquina). Necesita pila y estar a 1-2 m del robot.
Las luces vuelven al control del robot cuando el script termina.
"""
import sys
import time

import anki_vector
from anki_vector.color import Color
from anki_vector.lights import Light

NOMBRES = {
    "rojo": "#ff0000", "naranja": "#ff7a00", "amarillo": "#ffd400", "verde": "#00ff40", "turquesa": "#00e5d0",
    "azul": "#0040ff", "morado": "#9a30ff", "rosa": "#ff2a90", "blanco": "#ffffff",
}
ARCOIRIS = ["#ff0000", "#ffd400", "#00ff40", "#0040ff"]


def luz(hex_or_name: str) -> Light:
    h = NOMBRES.get(hex_or_name.lower(), hex_or_name).lstrip("#")
    if len(h) != 6:
        sys.exit(f"Color no válido: {hex_or_name} (usa un nombre: {', '.join(NOMBRES)} o #rrggbb)")
    return Light(on_color=Color(rgb=(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))))


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    secs = float(sys.argv[2]) if len(sys.argv) > 2 else 10.0
    with anki_vector.Robot() as robot:
        print("Conectando con el cubo…")
        robot.world.connect_cube()
        cube = robot.world.connected_light_cube
        if not cube:
            sys.exit("No se ha podido conectar con el cubo: ¿tiene pila y está cerca del robot?")
        print("Cubo conectado.")
        if arg == "off":
            cube.set_lights_off()
            return
        if arg:
            cube.set_lights(luz(arg))
            time.sleep(secs)
            return
        # demo: arcoíris girando por las esquinas
        colores = [luz(c) for c in ARCOIRIS]
        for i in range(16):
            k = i % 4
            cube.set_light_corners(*(colores[k:] + colores[:k]))
            time.sleep(0.35)
        cube.set_light_corners(*colores)
        time.sleep(4)
        cube.set_lights_off()


if __name__ == "__main__":
    main()
