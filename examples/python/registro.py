"""Registro técnico de Vector, al estilo dmesg: qué decide, qué detecta y qué hacen sus motores.

Uso:  python registro.py [minutos]     (por defecto 60; Ctrl+C para salir)

Escribe una línea JSON por suceso: {"t": epoch, "lvl": nivel syslog, "fac": categoría, "msg": texto}.
Solo cambios, no cada lectura (robot_state llega ~30 veces por segundo). No toma el control: solo escucha.
Niveles: 3 err (sin suelo, cayendo), 4 warn (levantado, empujado), 5 notice (comportamiento), 6 info, 7 debug.
"""
import json
import sys
import time

import anki_vector
from anki_vector.messaging import protocol

FLAGS = {v.number: v.name.replace("ROBOT_STATUS_", "") for v in protocol.RobotStatus.DESCRIPTOR.values if v.number}
NIVEL_FLAG = {"CLIFF_DETECTED": 3, "IS_FALLING": 3, "IS_PICKED_UP": 4, "IS_BEING_HELD": 4,
              "IS_PATHING": 6, "IS_ON_CHARGER": 6, "IS_CHARGING": 6, "IS_BUTTON_PRESSED": 6, "CALM_POWER_MODE": 6}
CERCA_MM = 100  # el sensor de distancia ve hasta ~30 cm, pero por debajo de 10 cm es «obstáculo delante»

ant = {"flags": set(), "ruedas": None, "cerca": None, "estim": None}


def log(lvl, fac, msg):
    print(json.dumps({"t": round(time.time(), 6), "lvl": lvl, "fac": fac, "msg": msg}), flush=True)


def campos(msg):
    """Mensaje protobuf en una línea: clave=valor."""
    return " ".join(f"{f.name}={v}" for f, v in msg.ListFields()) or "-"


def sentido(l, r):
    if abs(l) < 5 and abs(r) < 5:
        return "parado"
    if l > 5 and r > 5:
        return "adelante"
    if l < -5 and r < -5:
        return "atrás"
    return "giro izq." if r > l else "giro der."


def al_estado(robot, name, m):
    flags = {n for b, n in FLAGS.items() if m.status & b}
    if flags != ant["flags"]:
        for f in sorted(flags - ant["flags"]):
            log(NIVEL_FLAG.get(f, 7), "status", f"+{f}" + (f" prox={m.prox_data.distance_mm}mm" if f == "CLIFF_DETECTED" else ""))
        for f in sorted(ant["flags"] - flags):
            log(min(NIVEL_FLAG.get(f, 7) + 1, 7), "status", f"-{f}")
        ant["flags"] = flags
    l, r = round(m.left_wheel_speed_mmps), round(m.right_wheel_speed_mmps)
    s = sentido(l, r)
    if s != ant["ruedas"]:
        log(6, "motor", f"ruedas {s} l={l} r={r} mm/s")
        ant["ruedas"] = s
    p = m.prox_data
    cerca = p.distance_mm < CERCA_MM and p.signal_quality > 0.01
    if cerca != ant["cerca"]:
        if ant["cerca"] is not None:
            log(6, "prox", f"obstáculo {'detectado' if cerca else 'despejado'} dist={p.distance_mm}mm "
                f"calidad={p.signal_quality:.3f} brazo_en_vista={p.is_lift_in_fov}")
        ant["cerca"] = cerca


def al_comportamiento(robot, name, m):
    st = m.status
    log(5, "behavior", campos(st.feature_status) if st.HasField("feature_status") else campos(st))


def al_estimulo(robot, name, m):
    if m.emotion_events:  # los periódicos sin suceso solo bajan el estímulo poco a poco: ruido
        log(6, "stim", f"eventos={','.join(m.emotion_events)} estímulo={m.value:.3f} "
            f"(antes {m.value_before_event:.3f}, {m.value - m.value_before_event:+.3f})")


def otro(nivel, fac):
    return lambda robot, name, m: log(nivel, fac, f"{name} {campos(m)}")


def main():
    fin = time.time() + float(sys.argv[1] if len(sys.argv) > 1 else 60) * 60
    with anki_vector.Robot(behavior_control_level=None) as robot:
        log(6, "registro", "conectado — escuchando")
        ev = robot.events
        ev.subscribe_by_name(al_estado, event_name="robot_state")
        ev.subscribe_by_name(al_comportamiento, event_name="time_stamped_status")
        ev.subscribe_by_name(al_estimulo, event_name="stimulation_info")
        ev.subscribe_by_name(otro(4, "motion"), event_name="unexpected_movement")
        ev.subscribe_by_name(otro(5, "voice"), event_name="wake_word")
        ev.subscribe_by_name(otro(5, "voice"), event_name="user_intent")
        while time.time() < fin:
            time.sleep(1)
        log(6, "registro", "tiempo máximo alcanzado — fin")


if __name__ == "__main__":
    main()
