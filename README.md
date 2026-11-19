# Vector Hub — Repositorio de conocimiento y desarrollo para Anki Vector

Punto de partida para **entender** cómo está construido el robot Vector (Anki → Digital Dream Labs)
y **desarrollar** para él ahora que no dependemos del fabricante.

> Investigación realizada en noviembre de 2026. El ecosistema es comunitario y cambia rápido:
> verifica versiones y URLs antes de flashear nada.

## Resumen en 30 segundos

| Necesito… | Usa | Doc |
|---|---|---|
| Que Vector vuelva a responder a la voz sin la nube de DDL | **wire-pod** (servidor local: Windows, macOS, Linux, Raspberry Pi, Android) | [04-wire-pod](docs/04-wire-pod.md) |
| Programar comportamientos desde un PC (moverlo, hablar, cámara…) | **SDK Python** (`wirepod-vector-sdk`) o **SDK Go** (`vector-go-sdk`) sobre gRPC | [05-sdk-y-apis](docs/05-sdk-y-apis.md) |
| Añadir comandos de voz propios | Plugins Go de wire-pod / intents personalizados | [04-wire-pod](docs/04-wire-pod.md) |
| Cambiar el firmware (root, SSH, nuevas funciones) | Desbloqueo + **WireOS** (CFW) | [06-firmware](docs/06-firmware-y-desbloqueo.md) |
| Entender el hardware | Hoja técnica + TRM de Randall Maas | [02-hardware](docs/02-hardware.md) |

## Web del proyecto (Vector Hub)

Doble clic en **`iniciar_web.bat`** (abre wire-pod si está cerrado, arranca la web y el navegador), o:

```powershell
python web\server.py      # → http://localhost:8090
```

Panel local con:

- **Estado y telemetría**: en línea / sin conexión, batería (voltaje o nivel), carga, disponibilidad,
  gráfico histórico con vista en tabla.
- **Hablar**: Vector dice lo que escribas, con frases rápidas e historial.
- **Cámara en directo** (MJPEG ~4 fps, 640×360) con **control remoto**: tomar control / modo libre,
  ruedas, cabeza y brazo (ratón, táctil o teclado), velocidad y capturas.
- Estadísticas de vida, caras conocidas, fotos del robot y volumen.
- Fases con su % de avance, memoria del proyecto y protocolo de cambio de Wi-Fi. Lee los datos de wire-pod (tiene que estar abierto) y guarda una muestra por
minuto en `web/data/telemetria.jsonl`. Las fases y la memoria se editan en `web/data/proyecto.json`.

**Cambio de red Wi-Fi:** [docs/08-cambio-de-wifi.md](docs/08-cambio-de-wifi.md) — en resumen:
doble pulsación en el robot y `node tools\vector-ble-cli\index.js --wifi "RED" "CONTRASEÑA"`.

## Estructura

```
docs/                 Documentación propia en castellano (empieza por aquí)
  01-historia-y-estado.md
  02-hardware.md
  03-arquitectura-software.md
  04-wire-pod.md
  05-sdk-y-apis.md
  06-firmware-y-desbloqueo.md
  07-catalogo-de-recursos.md
examples/python/      Ejemplos mínimos con el SDK Python
tools/vector-ble-cli/ Configuración por Bluetooth desde terminal (emparejar, Wi-Fi, OTA, auth)
web/                  Vector Hub: server.py + static/index.html + data/proyecto.json
iniciar_web.bat       Arranca wire-pod (si hace falta) y la web
scripts/              Clonado de repos y diagnóstico Bluetooth
repos.txt             Lista de repos de referencia (código fuente, SDKs, docs)
scripts/clone_repos.ps1  Clona/actualiza todos los repos de repos.txt en third_party/
third_party/          (ignorado por git) copias locales de los repos externos
```

## Primeros pasos recomendados

1. **Instalar wire-pod** en un PC de la red (en Windows: instalador `WirePodInstaller-vX.Y.Z.exe`
   de <https://github.com/kercre123/WirePod/releases/latest>) y emparejar el robot. Ver [04-wire-pod](docs/04-wire-pod.md).
2. **Probar el SDK** (Python 3.11/3.12, no 3.14): `pip install wirepod_vector_sdk`, `python -m anki_vector.configure` y ejecutar [`examples/python/hola_vector.py`](examples/python/hola_vector.py).
3. **Descargar el código de referencia**: `powershell -File scripts\clone_repos.ps1`.
4. Si queremos tocar el sistema operativo: leer **entero** [06-firmware](docs/06-firmware-y-desbloqueo.md) antes de desbloquear.

## Ruta de desarrollo propuesta

1. **Nivel 1 – Sin tocar el robot**: wire-pod + SDK (Python/Go). Riesgo cero, cubre el 80 % de los casos
   (comportamientos, integración con LLM, domótica, visión con la cámara).
2. **Nivel 2 – Servidor**: plugins e intents en wire-pod, STT/TTS/LLM propios.
3. **Nivel 3 – Firmware**: robot desbloqueado + WireOS; compilar `wire-os-victor` y desplegar por SSH.
   Requiere Linux x86_64 con 16 GB RAM y ~200 GB de disco.
