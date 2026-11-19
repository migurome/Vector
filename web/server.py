"""Vector Hub - web local del proyecto.

Sirve web/static/, reenvía /api-sdk/* a wire-pod (mismo origen, sin CORS) y registra telemetría
cada minuto en web/data/telemetria.jsonl.  Solo librería estándar de Python.

Uso:  python web/server.py          -> http://localhost:8090
Variables opcionales: WIREPOD=http://localhost:8080  PORT=8090  INTERVALO=60
"""
import json
import os
import re
import socket
import subprocess
import tempfile
import threading
import time
import urllib.error
import urllib.request
from collections import deque
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

BASE = Path(__file__).resolve().parent
STATIC = BASE / "static"
DATA = BASE / "data"
TELEMETRIA = DATA / "telemetria.jsonl"
VOZ = DATA / "voz.jsonl"
EJEMPLOS = BASE.parent / "examples" / "python"
VENV_PY = BASE.parent / ".venv" / "Scripts" / "python.exe"
ENV_SDK = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUNBUFFERED": "1"}
WIREPOD = os.environ.get("WIREPOD", "http://localhost:8080").rstrip("/")
PORT = int(os.environ.get("PORT", "8090"))
INTERVALO = int(os.environ.get("INTERVALO", "60"))
MAX_MUESTRAS = 10080  # una semana a 1/min


def leer_jsonl(path, ultimas=None):
    """Objetos de un fichero JSON-lines; ignora líneas cortadas por un cierre brusco."""
    if not path.exists():
        return []
    out = []
    for ln in path.read_text(encoding="utf-8").splitlines()[-ultimas if ultimas else None:]:
        try:
            out.append(json.loads(ln))
        except ValueError:
            continue
    return out


# ---------- wire-pod ----------

def wirepod(path, timeout=25):
    """GET a wire-pod; devuelve (status, bytes, content_type)."""
    try:
        with urllib.request.urlopen(WIREPOD + path, timeout=timeout) as r:
            return r.status, r.read(), r.headers.get("Content-Type", "text/plain")
    except urllib.error.HTTPError as e:
        return e.code, e.read(), "text/plain"
    except Exception as e:  # wire-pod apagado, timeout...
        return 502, f"error: wire-pod no responde ({e})".encode(), "text/plain"


def wirepod_json(path, timeout=25):
    st, body, _ = wirepod(path, timeout)
    text = body.decode("utf-8", "replace")
    if st != 200 or text.startswith("error"):
        return None, text
    try:
        return json.loads(text), None
    except ValueError:
        return None, text


def robot_registrado():
    """(robot de wire-pod, error)."""
    info, err = wirepod_json("/api-sdk/get_sdk_info", 5)
    return (info["robots"][0], None) if info else (None, err)


def bateria(esn):
    # wire-pod tarda ~20 s en rendirse si el robot no responde: esperar más para recibir su error real
    return wirepod_json(f"/api-sdk/get_battery?serial={esn}", 35)


def robot_en_red(ip, timeout=3):
    """¿Acepta el robot conexiones en su puerto 443?"""
    try:
        with socket.create_connection((ip, 443), timeout=timeout):
            return True
    except OSError:
        return False


def renovar_conexion(esn):
    """wire-pod guarda la conexión gRPC con el robot; tras un reinicio del robot queda inservible
    (401 / timeouts) hasta que se descarta. /api-sdk/disconnect la descarta y la siguiente llamada la recrea."""
    wirepod(f"/api-sdk/disconnect?serial={esn}", 10)


# ---------- telemetría (en memoria la última semana; en disco, todo) ----------

TELE = deque(leer_jsonl(TELEMETRIA, MAX_MUESTRAS), maxlen=MAX_MUESTRAS)
_escritura = threading.Lock()  # registrador y /reconectar escriben a la vez


def muestra():
    """Una muestra de telemetría. Nunca lanza excepción."""
    t = int(time.time())
    bot, err = robot_registrado()
    if not bot:
        return {"t": t, "wirepod": False, "online": False, "error": err}
    bat, err = bateria(bot["esn"])
    if not bat and robot_en_red(bot["ip_address"]):
        # robot en la red pero wire-pod no habla con él: conexión caducada (p. ej. tras reiniciarse)
        renovar_conexion(bot["esn"])
        bat, err = bateria(bot["esn"])
    s = {"t": t, "wirepod": True, "online": bat is not None, "esn": bot["esn"], "ip": bot.get("ip_address")}
    if bat:
        # protobuf->JSON de Go omite ceros/false: usar get con valor por defecto
        s.update(nivel=bat.get("battery_level", 0), voltios=round(bat.get("battery_volts", 0), 3),
                 cargando=bool(bat.get("is_charging")), en_base=bool(bat.get("is_on_charger_platform")),
                 cubo_voltios=round((bat.get("cube_battery") or {}).get("battery_volts", 0), 3))
    else:
        s["error"] = err
    return s


def guardar(s):
    with _escritura:
        TELE.append(s)
        with TELEMETRIA.open("a", encoding="utf-8") as f:
            f.write(json.dumps(s) + "\n")


def registrador():
    DATA.mkdir(exist_ok=True)
    while True:
        guardar(muestra())
        time.sleep(INTERVALO)


def leer_telemetria(horas):
    desde = time.time() - horas * 3600
    with _escritura:
        return [s for s in TELE if s.get("t", 0) >= desde]


# ---------- reconexión ----------

def reconectar():
    """Diagnóstico paso a paso + renovación de la conexión. Devuelve los pasos para mostrarlos en la web."""
    bot, _ = robot_registrado()
    if not bot:
        return {"ok": False, "pasos": [["wire-pod", False, "No responde. Ábrelo desde el menú Inicio (WirePod) o con iniciar_web.bat."]]}
    pasos = [["wire-pod", True, "En marcha"]]
    if not robot_en_red(bot["ip_address"], 5):
        pasos.append(["Robot en la red", False, "No responde en su IP. ¿Está encendido, arrancando o fuera de la Wi-Fi? "
                      "Si acaba de reiniciarse, espera 1–2 minutos y vuelve a probar. Si cambió de red, sigue el protocolo de cambio de Wi-Fi."])
        return {"ok": False, "pasos": pasos}
    pasos.append(["Robot en la red", True, "Responde en su IP"])
    renovar_conexion(bot["esn"])
    pasos.append(["Conexión renovada", True, "wire-pod ha descartado la conexión anterior"])
    bat, err = bateria(bot["esn"])
    if bat:
        pasos.append(["Comunicación con el robot", True, "Responde correctamente"])
        guardar(muestra())  # que la web no siga mostrando la última muestra «sin conexión»
        return {"ok": True, "pasos": pasos}
    pasos.append(["Comunicación con el robot", False, f"Sigue fallando: {(err or '')[:160]}. Si acaba de arrancar, "
                  "espera un minuto y repite. Si persiste, cierra y vuelve a abrir wire-pod."])
    return {"ok": False, "pasos": pasos}


# ---------- reacciones (examples/python/reacciones.py en segundo plano) ----------

REACCIONES = {"proc": None, "inicio": None, "lineas": []}
_reac_lock = threading.Lock()


def _leer_salida(proc):
    for ln in proc.stdout:
        ln = ln.rstrip()
        if ln and " INFO " not in ln and "WARNING" not in ln:  # solo lo que escribe el programa, no el log del SDK
            with _reac_lock:
                REACCIONES["lineas"] = (REACCIONES["lineas"] + [ln])[-200:]


def reacciones(accion, minutos=10):
    with _reac_lock:
        p = REACCIONES["proc"]
        activo = p is not None and p.poll() is None
        if accion == "start" and not activo:
            if not VENV_PY.exists():
                return {"error": "falta el entorno .venv con el SDK (ver guía del SDK)"}
            p = subprocess.Popen([str(VENV_PY), "-I", str(EJEMPLOS / "reacciones.py"), f"{minutos:g}"],
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                                 errors="replace", env=ENV_SDK)
            REACCIONES.update(proc=p, inicio=time.time(), lineas=[])
            threading.Thread(target=_leer_salida, args=(p,), daemon=True).start()
            activo = True
        elif accion == "stop" and activo:
            p.terminate()
            REACCIONES["lineas"].append(time.strftime("%H:%M:%S") + " Parado desde la web.")
            activo = False
        return {"activo": activo, "inicio": REACCIONES["inicio"], "lineas": REACCIONES["lineas"][-60:]}


# ---------- registro de voz ----------
# wire-pod solo guarda en memoria las 50 últimas líneas de su log de interfaz: las copiamos a disco
RE_INTENT = re.compile(r"^(\d{4}\.\d\d\.\d\d \d\d:\d\d:\d\d): Intent matched: (\S+), transcribed text: '(.*)', device: (\S+)$")
RE_LLM = re.compile(r"^(\d{4}\.\d\d\.\d\d \d\d:\d\d:\d\d): LLM response for (\S+): (.*)$")


def parse_voz(linea):
    """Convierte una línea del log de wire-pod en un evento, o None si no es de voz."""
    if m := RE_INTENT.match(linea):
        fecha, intent, texto, _ = m.groups()
        ev = {"tipo": "orden", "intent": intent, "texto": texto}
    elif m := RE_LLM.match(linea):
        fecha, _, texto = m.groups()
        ev = {"tipo": "ia", "texto": texto}
    else:
        return None
    ev["t"] = int(time.mktime(time.strptime(fecha, "%Y.%m.%d %H:%M:%S")))
    ev["raw"] = linea  # clave de deduplicado (el buffer de wire-pod se repite en cada lectura)
    return ev


def registrador_voz():
    vistos = {ev["raw"] for ev in leer_jsonl(VOZ) if "raw" in ev}
    while True:
        st, body, _ = wirepod("/api/get_logs", 5)
        if st == 200:
            nuevos = [ev for ln in body.decode("utf-8", "replace").splitlines()
                      if (ev := parse_voz(ln.strip())) and ev["raw"] not in vistos]
            if nuevos:
                with VOZ.open("a", encoding="utf-8") as f:
                    for ev in nuevos:
                        vistos.add(ev["raw"])
                        f.write(json.dumps(ev, ensure_ascii=False) + "\n")
        time.sleep(10)


def leer_voz(n):
    return [{k: v for k, v in ev.items() if k != "raw"} for ev in leer_jsonl(VOZ, n)]


# ---------- HTTP ----------

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(STATIC), **kw)

    def log_message(self, fmt, *args):
        pass  # silencioso; la telemetría ya deja rastro

    def enviar(self, status, body, ctype="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def enviar_json(self, status, obj):
        self.enviar(status, json.dumps(obj, ensure_ascii=False).encode())

    def stream_camara(self):
        """Reenvía el MJPEG de wire-pod trozo a trozo hasta que el navegador cierre."""
        try:
            up = urllib.request.urlopen(WIREPOD + self.path, timeout=30)
        except Exception as e:
            return self.enviar(502, f"error: {e}".encode(), "text/plain")
        with up:
            self.send_response(200)
            self.send_header("Content-Type", up.headers.get("Content-Type", "multipart/x-mixed-replace; boundary=--boundary"))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            try:
                while chunk := up.read1(65536):
                    self.wfile.write(chunk)
                    self.wfile.flush()
            except (ConnectionError, TimeoutError, OSError):
                pass  # el navegador ha cerrado o el robot ha dejado de enviar

    def do_POST(self):
        url = urlparse(self.path)
        if url.path != "/pantalla":
            return self.enviar_json(404, {"error": "no encontrado"})
        q = parse_qs(url.query)
        ext = q.get("ext", ["png"])[0].lower()
        if ext not in ("png", "jpg", "jpeg", "gif", "webp", "bmp"):
            return self.enviar_json(400, {"error": "formato no admitido"})
        try:
            valor = float(q.get("valor", ["5"])[0])  # segundos (imagen) o vueltas (GIF)
        except ValueError:
            return self.enviar_json(400, {"error": "valor no numérico"})
        valor = max(1, min(valor, 60 if ext != "gif" else 10))
        n = int(self.headers.get("Content-Length", 0))
        if not 0 < n <= 8 * 1024 * 1024:
            return self.enviar_json(400, {"error": "imagen vacía o mayor de 8 MB"})
        datos = self.rfile.read(n)
        if not VENV_PY.exists():
            return self.enviar_json(501, {"error": "falta el entorno .venv con el SDK (ver guía del SDK)"})
        with tempfile.TemporaryDirectory() as tmp:  # carpeta propia: el fichero subido no se ejecuta, solo se abre como imagen
            f = Path(tmp) / f"imagen.{ext}"
            f.write_bytes(datos)
            try:
                r = subprocess.run([str(VENV_PY), "-I", str(EJEMPLOS / "pantalla.py"), str(f), f"{valor:g}"],
                                   capture_output=True, text=True, encoding="utf-8", errors="replace",
                                   timeout=150, env=ENV_SDK)
            except subprocess.TimeoutExpired:
                return self.enviar_json(504, {"error": "el robot tardó demasiado"})
        if r.returncode != 0:
            ult = [ln for ln in r.stderr.splitlines() if ln.strip()][-1:] or ["error desconocido"]
            return self.enviar_json(502, {"error": ult[0][:300]})
        return self.enviar_json(200, {"ok": True})

    def do_GET(self):
        url = urlparse(self.path)
        q = parse_qs(url.query)
        arg = lambda k, d: q.get(k, [d])[0]
        if url.path == "/cam-stream":
            return self.stream_camara()
        if url.path.startswith("/api-sdk/"):
            st, body, ct = wirepod(self.path)
            return self.enviar(st, body, ct)
        if url.path == "/telemetria":
            return self.enviar_json(200, leer_telemetria(float(arg("horas", "24"))))
        if url.path == "/reacciones":
            try:
                minutos = max(1, min(float(arg("min", "10")), 120))
            except ValueError:
                minutos = 10
            return self.enviar_json(200, reacciones(arg("accion", "estado"), minutos))
        if url.path == "/reconectar":
            return self.enviar_json(200, reconectar())
        if url.path == "/voz":
            return self.enviar_json(200, leer_voz(int(arg("n", "500"))))
        if url.path == "/proyecto":
            return self.enviar(200, (DATA / "proyecto.json").read_bytes())
        return super().do_GET()


if __name__ == "__main__":
    threading.Thread(target=registrador, daemon=True).start()
    threading.Thread(target=registrador_voz, daemon=True).start()
    print(f"Vector Hub en http://localhost:{PORT}  (wire-pod: {WIREPOD})")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
