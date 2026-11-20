"""Comportamientos programados: Vector reacciona a caras, sonrisas y caricias según el modo elegido.

Uso:  python reacciones.py [minutos] [modo]     (por defecto 15 min y modo «reacciones»; Ctrl+C para salir)

Modos:
  reacciones  saluda a quien reconoce, comenta tu sonrisa y agradece las caricias (hablando)
  tranquila   lo mismo, pero sin hablar: responde solo con animaciones
  vigilante   si ve una cara que no conoce, le hace una foto (web/static/vigilante/)

Vector sigue con su vida normal: el programa solo toma el control un instante para actuar.
Las frases van sin tildes ni ¿¡ porque su voz (sintetizador inglés) los lee mal.
"""
import contextlib
import pathlib
import queue
import random
import sys
import time

import anki_vector
from anki_vector.connection import ControlPriorityLevel
from anki_vector.events import Events
from anki_vector.messaging import protocol

SALUDOS = ["Hola {n}!", "Hola {n}, que alegria verte", "Anda, {n}! Hola!"]
SONRISA = ["Que sonrisa mas bonita", "Me encanta verte contento", "Esa sonrisa me gusta"]
CARICIAS = ["Que gustito", "Me encanta", "Otra vez, otra vez!", "Mmm, que bien"]
# animaciones del modo tranquila (nombres de AnimationTrigger documentados o ya probados)
ANIM_SALUDO, ANIM_CARIÑO = "GreetAfterLongTime", "Feedback_ILoveYou"

ESPERA_SALUDO = 10 * 60    # s entre saludos a la misma persona
ESPERA_SONRISA = 3 * 60
ESPERA_CARICIA = 20
ESPERA_FOTO = 60           # s entre fotos del vigilante
CARICIA_MIN = 0.6          # s seguidos tocando para contar como caricia
FELIZ = protocol.FacialExpression.Value("EXPRESSION_HAPPINESS")
MODOS = ("reacciones", "tranquila", "vigilante")
FOTOS = pathlib.Path(__file__).resolve().parents[2] / "web" / "static" / "vigilante"

pendientes = queue.Queue()  # (acción, valor) a ejecutar en el hilo principal
ultimo = {}  # clave -> instante de la última reacción
modo = "reacciones"


def toca(clave, espera):
    """True si ha pasado el tiempo de espera para esta reacción (y la marca)."""
    ahora = time.time()
    if ahora - ultimo.get(clave, 0) < espera:
        return False
    ultimo[clave] = ahora
    return True


def log(msg):
    print(time.strftime("%H:%M:%S"), msg, flush=True)


def al_ver_cara(robot, event_type, event, *args):
    # se ejecuta en el hilo de la conexión: solo encolar, nunca actuar aquí
    if modo == "vigilante":
        if not event.name and toca("foto", ESPERA_FOTO):
            log("Cara desconocida")
            pendientes.put(("foto", None))
        return
    if event.face_id <= 0 or not event.name:
        return  # cara no reconocida
    nombre = event.name.capitalize()
    if toca(("saludo", nombre), ESPERA_SALUDO):
        log(f"Veo a {nombre}")
        pendientes.put(("anim", ANIM_SALUDO) if modo == "tranquila" else ("decir", random.choice(SALUDOS).format(n=nombre)))
    elif event.expression == FELIZ and toca(("sonrisa", nombre), ESPERA_SONRISA):
        log(f"{nombre} sonríe")
        pendientes.put(("anim", ANIM_CARIÑO) if modo == "tranquila" else ("decir", random.choice(SONRISA)))


def esperar_sin_tocar(robot, quieto=0.5, maximo=8):
    """Espera a que le quiten la mano de encima (con un margen), como mucho `maximo` segundos."""
    fin, libre_desde = time.time() + maximo, None
    while time.time() < fin:
        lectura = robot.touch.last_sensor_reading
        if lectura and lectura.is_being_touched:
            libre_desde = None
        else:
            libre_desde = libre_desde or time.time()
            if time.time() - libre_desde >= quieto:
                return
        time.sleep(0.1)


@contextlib.contextmanager
def con_control(robot):
    robot.conn.request_control(ControlPriorityLevel.DEFAULT_PRIORITY, timeout=5)
    try:
        yield
    finally:
        try:
            robot.conn.release_control(timeout=5)
        except Exception:
            pass


def animar(robot, nombre):
    try:
        with con_control(robot):
            # se pasa el trigger ya construido: por nombre, el SDK carga antes la lista entera de
            # animaciones y esa consulta caduca (DEADLINE_EXCEEDED, probado)
            robot.anim.play_animation_trigger(protocol.AnimationTrigger(name=nombre))
        log(f"Animación {nombre}")
    except Exception as e:
        log(f"No he podido animarme: {str(e).splitlines()[0]}")


def foto(robot):
    try:
        with con_control(robot):
            imagen = robot.camera.capture_single_image().raw_image
        FOTOS.mkdir(parents=True, exist_ok=True)
        nombre = time.strftime("%Y%m%d-%H%M%S.jpg")
        imagen.save(FOTOS / nombre, quality=90)
        log(f"Foto vigilante/{nombre}")
    except Exception as e:
        log(f"No he podido hacer la foto: {str(e).splitlines()[0]}")


def decir(robot, texto, intentos=3, animacion_si_falla=None):
    # Probado el 2026-11-19: con prioridad OVERRIDE_BEHAVIORS say_text falla SIEMPRE («Failed to say
    # text»); con DEFAULT funciona, salvo justo tras una caricia (su ronroneo ocupa la voz unos segundos).
    # Por eso: prioridad DEFAULT, varios intentos espaciados y, si no hay manera, una animación suya.
    log(f"Dice: {texto}")
    for i in range(intentos):
        try:
            with con_control(robot):
                robot.behavior.say_text(texto)
            return
        except Exception as e:  # p. ej. ocupado con su propia animación, o la web tiene el control
            error = str(e).splitlines()[0]
        if i + 1 < intentos:
            time.sleep(2)
    log(f"No he podido hablar: {error}")
    if animacion_si_falla:
        animar(robot, animacion_si_falla)


def main():
    global modo
    minutos = float(sys.argv[1]) if len(sys.argv) > 1 else 15
    modo = sys.argv[2] if len(sys.argv) > 2 else "reacciones"
    if modo not in MODOS:
        sys.exit(f"Modo desconocido «{modo}». Usa uno de: {', '.join(MODOS)}")
    fin = time.time() + minutos * 60
    with anki_vector.Robot(behavior_control_level=None, enable_face_detection=True) as robot:
        robot.events.subscribe(al_ver_cara, Events.robot_observed_face)
        log(f"Modo {modo} activo durante {minutos:g} min.")
        tocando_desde = None
        try:
            while time.time() < fin:
                lectura = robot.touch.last_sensor_reading
                if modo != "vigilante" and lectura and lectura.is_being_touched:
                    tocando_desde = tocando_desde or time.time()
                    if time.time() - tocando_desde >= CARICIA_MIN and toca("caricia", ESPERA_CARICIA):
                        log("Caricia (reaccionará al soltarlo)")
                        esperar_sin_tocar(robot)
                        if modo == "tranquila":
                            animar(robot, ANIM_CARIÑO)
                        else:
                            decir(robot, random.choice(CARICIAS), animacion_si_falla=ANIM_CARIÑO)
                        tocando_desde = None
                else:
                    tocando_desde = None
                try:
                    accion, valor = pendientes.get(timeout=0.15)
                except queue.Empty:
                    continue
                if accion == "decir":
                    decir(robot, valor)
                elif accion == "anim":
                    animar(robot, valor)
                else:
                    foto(robot)
        except KeyboardInterrupt:
            pass
        finally:
            robot.events.unsubscribe(al_ver_cara, Events.robot_observed_face)
            log(f"Fin del modo {modo}.")


if __name__ == "__main__":
    main()
