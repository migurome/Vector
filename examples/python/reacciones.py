"""Comportamientos reactivos: Vector saluda a quien reconoce, comenta tu sonrisa y agradece las caricias.

Uso:  python reacciones.py [minutos]     (por defecto 15; Ctrl+C para salir antes)

Vector sigue con su vida normal: el programa solo toma el control un instante para hablar.
Las frases van sin tildes ni ¿¡ porque su voz (sintetizador inglés) los lee mal.
"""
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

ESPERA_SALUDO = 10 * 60    # s entre saludos a la misma persona
ESPERA_SONRISA = 3 * 60
ESPERA_CARICIA = 20
CARICIA_MIN = 0.6          # s seguidos tocando para contar como caricia
FELIZ = protocol.FacialExpression.Value("EXPRESSION_HAPPINESS")

pendientes = queue.Queue()
ultimo = {}  # clave -> instante de la última reacción


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
    # se ejecuta en el hilo de la conexión: solo encolar, nunca hablar aquí
    if event.face_id <= 0 or not event.name:
        return  # cara no reconocida
    nombre = event.name.capitalize()
    if toca(("saludo", nombre), ESPERA_SALUDO):
        log(f"Veo a {nombre}")
        pendientes.put(random.choice(SALUDOS).format(n=nombre))
    elif event.expression == FELIZ and toca(("sonrisa", nombre), ESPERA_SONRISA):
        log(f"{nombre} sonríe")
        pendientes.put(random.choice(SONRISA))


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


def decir(robot, texto, intentos=3, animacion_si_falla=None):
    # Probado el 2026-11-19: con prioridad OVERRIDE_BEHAVIORS say_text falla SIEMPRE («Failed to say
    # text»); con DEFAULT funciona, salvo justo tras una caricia (su ronroneo ocupa la voz unos segundos).
    # Por eso: prioridad DEFAULT, varios intentos espaciados y, si no hay manera, una animación suya.
    for i in range(intentos):
        try:
            robot.conn.request_control(ControlPriorityLevel.DEFAULT_PRIORITY, timeout=5)
            robot.behavior.say_text(texto)
            return
        except Exception as e:  # p. ej. ocupado con su propia animación, o la web tiene el control
            error = str(e).splitlines()[0]
        finally:
            try:
                robot.conn.release_control(timeout=5)
            except Exception:
                pass
        if i + 1 < intentos:
            time.sleep(2)
    log(f"No he podido hablar: {error}")
    if animacion_si_falla:
        try:
            robot.conn.request_control(ControlPriorityLevel.DEFAULT_PRIORITY, timeout=5)
            # se pasa el trigger ya construido: por nombre, el SDK carga antes la lista entera de
            # animaciones y esa consulta caduca (DEADLINE_EXCEEDED, probado)
            robot.anim.play_animation_trigger(protocol.AnimationTrigger(name=animacion_si_falla))
            log(f"En su lugar, animación {animacion_si_falla}")
        except Exception as e:
            log(f"Tampoco la animación: {str(e).splitlines()[0]}")
        finally:
            try:
                robot.conn.release_control(timeout=5)
            except Exception:
                pass


def main():
    minutos = float(sys.argv[1]) if len(sys.argv) > 1 else 15
    fin = time.time() + minutos * 60
    with anki_vector.Robot(behavior_control_level=None, enable_face_detection=True) as robot:
        robot.events.subscribe(al_ver_cara, Events.robot_observed_face)
        log(f"Reacciones activas durante {minutos:g} min. Ponte delante o acarícialo.")
        tocando_desde = None
        try:
            while time.time() < fin:
                lectura = robot.touch.last_sensor_reading
                if lectura and lectura.is_being_touched:
                    tocando_desde = tocando_desde or time.time()
                    if time.time() - tocando_desde >= CARICIA_MIN and toca("caricia", ESPERA_CARICIA):
                        log("Caricia (hablará al soltarlo)")
                        texto = random.choice(CARICIAS)
                        esperar_sin_tocar(robot)
                        log(f"Dice: {texto}")
                        decir(robot, texto, animacion_si_falla="Feedback_ILoveYou")
                        tocando_desde = None
                else:
                    tocando_desde = None
                try:
                    texto = pendientes.get(timeout=0.15)
                    log(f"Dice: {texto}")
                    decir(robot, texto)
                except queue.Empty:
                    pass
        except KeyboardInterrupt:
            pass
        finally:
            robot.events.unsubscribe(al_ver_cara, Events.robot_observed_face)
            log("Fin de las reacciones.")


if __name__ == "__main__":
    main()
