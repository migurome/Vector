"""Posición de Vector en directo: una línea JSON cada 0,2 s con su pose y la de la base (si la ha visto).

Uso:  python posicion.py [minutos]     (por defecto 30; Ctrl+C para salir)

Coordenadas en mm respecto al origen de su odometría (donde empezó a contar); x hacia delante del origen,
y hacia su izquierda, ángulo en grados (antihorario). Si lo levantan, el origen cambia («origen» distinto).
No toma el control: solo escucha, así que puede ir a la vez que el mando o las reacciones.
"""
import json
import sys
import time

import anki_vector


def pose(p):
    return {"x": round(p.position.x), "y": round(p.position.y), "ang": round(p.rotation.angle_z.degrees, 1),
            "origen": p.origin_id}


def main():
    fin = time.time() + float(sys.argv[1] if len(sys.argv) > 1 else 30) * 60
    with anki_vector.Robot(behavior_control_level=None) as robot:
        while time.time() < fin:
            r = pose(robot.pose)
            base = robot.world.charger  # None hasta que ve la marca de la base
            if base is not None and base.pose is not None:
                b = pose(base.pose)
                if b["origen"] == r["origen"]:  # con otro origen sus coordenadas no son comparables
                    r["base"] = b
            r["en_base"] = bool(robot.status.is_on_charger)
            print(json.dumps(r), flush=True)
            time.sleep(0.2)


if __name__ == "__main__":
    main()
