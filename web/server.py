"""Vector Hub - web local del proyecto.

Sirve web/static/, reenvía /api-sdk/* a wire-pod (mismo origen, sin CORS) y registra telemetría
cada minuto en web/data/telemetria.jsonl.  Solo librería estándar de Python.

Uso:  python web/server.py          -> http://localhost:8090
Variables opcionales: WIREPOD=http://localhost:8080  PORT=8090  INTERVALO=60
"""
import json
import os
import threading
import time
import urllib.error
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BASE = Path(__file__).resolve().parent
STATIC = BASE / "static"
DATA = BASE / "data"
TELEMETRIA = DATA / "telemetria.jsonl"
WIREPOD = os.environ.get("WIREPOD", "http://localhost:8080").rstrip("/")
PORT = int(os.environ.get("PORT", "8090"))
INTERVALO = int(os.environ.get("INTERVALO", "60"))
MAX_MUESTRAS = 10080  # una semana a 1/min


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


def muestra():
    """Una muestra de telemetría. Nunca lanza excepción."""
    t = int(time.time())
    info, err = wirepod_json("/api-sdk/get_sdk_info", 5)
    if not info:
        return {"t": t, "wirepod": False, "online": False, "error": err}
    bot = info["robots"][0]
    # wire-pod tarda ~20 s en rendirse si el robot no responde: esperar más para recibir su error real
    bat, err = wirepod_json(f"/api-sdk/get_battery?serial={bot['esn']}", 35)
    s = {"t": t, "wirepod": True, "online": bat is not None, "esn": bot["esn"], "ip": bot.get("ip_address")}
    if bat:
        # protobuf->JSON de Go omite ceros/false: usar get con valor por defecto
        s.update(nivel=bat.get("battery_level", 0), voltios=round(bat.get("battery_volts", 0), 3),
                 cargando=bool(bat.get("is_charging")), en_base=bool(bat.get("is_on_charger_platform")),
                 cubo_voltios=round((bat.get("cube_battery") or {}).get("battery_volts", 0), 3))
    else:
        s["error"] = err
    return s


def registrador():
    DATA.mkdir(exist_ok=True)
    while True:
        s = muestra()
        with TELEMETRIA.open("a", encoding="utf-8") as f:
            f.write(json.dumps(s) + "\n")
        time.sleep(INTERVALO)


def leer_telemetria(horas):
    if not TELEMETRIA.exists():
        return []
    desde = time.time() - horas * 3600
    lineas = TELEMETRIA.read_text(encoding="utf-8").splitlines()[-MAX_MUESTRAS:]
    out = []
    for ln in lineas:
        try:
            s = json.loads(ln)
        except ValueError:
            continue  # línea cortada por un cierre brusco
        if s.get("t", 0) >= desde:
            out.append(s)
    return out


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

    def do_GET(self):
        if self.path.startswith("/api-sdk/"):
            st, body, ct = wirepod(self.path)
            return self.enviar(st, body, ct)
        if self.path.startswith("/telemetria"):
            from urllib.parse import parse_qs, urlparse
            horas = float(parse_qs(urlparse(self.path).query).get("horas", ["24"])[0])
            return self.enviar(200, json.dumps(leer_telemetria(horas)).encode())
        if self.path == "/proyecto":
            return self.enviar(200, (DATA / "proyecto.json").read_bytes())
        return super().do_GET()


if __name__ == "__main__":
    threading.Thread(target=registrador, daemon=True).start()
    print(f"Vector Hub en http://localhost:{PORT}  (wire-pod: {WIREPOD})")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
