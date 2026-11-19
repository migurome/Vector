# 05 · SDKs y APIs

Toda la programación "externa" usa la **API gRPC** que expone `vic-gateway` en el puerto 443 del robot,
autenticada con un token (GUID) que emite el servidor (wire-pod). Las definiciones `.proto` son la
fuente de verdad: están en `anki_vector/messaging/*.proto` (SDK Python) y en `pkg/vectorpb` (SDK Go).

## SDK Python (recomendado para empezar)

| Paquete | Estado |
|---|---|
| `anki/vector-python-sdk` | Original de Anki (2019). Archivado; Python 3.6–3.8. Útil como **documentación**. |
| `cyb3rdog/vector-python-sdk` | Fork mantenido por la comunidad (compatibilidad Escape Pod). |
| **`kercre123/wirepod-vector-python-sdk`** → PyPI **`wirepod-vector-sdk`** | Fork para wire-pod y Python moderno. **Usar este.** |

Soporta Python **3.6–3.12** (en este PC: Python 3.12 instalado con
`winget install Python.Python.3.12 --scope user`, conviviendo con el 3.14 por defecto).

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -U pip wirepod_vector_sdk
.\.venv\Scripts\python.exe scripts\configurar_sdk.py     # robot encendido + wire-pod abierto
.\.venv\Scripts\python.exe examples\python\hola_vector.py
```

**Por qué `configurar_sdk.py` y no `python -m anki_vector.configure`:** el asistente oficial pide el
certificado del robot a wire-pod (`/session-certs/<serie>`), que solo lo tiene si lo descargó de los
servidores de DDL. En nuestro robot (autenticado con `vector-ble-cli`) no existía: `cert does not exist`.
El script lee el certificado **directamente del robot** (TLS del puerto 443), saca el nombre del propio
certificado, y reutiliza las funciones del asistente oficial para autenticar y escribir
`~/.anki_vector/sdk_config.ini`. **Hay que relanzarlo si cambia la IP del robot** (p. ej. al cambiar de Wi-Fi).

### Ejemplos del repositorio

| Ejemplo | Qué hace |
|---|---|
| `examples/python/hola_vector.py` | Batería, habla, mueve cabeza y brazo, guarda una foto |
| `examples/python/pantalla.py` | Muestra una imagen o GIF animado en su cara (adapta a 184×96 sin deformar) |
| `examples/python/cubo.py` | Luces del cubo: demo arcoíris, un color (`rojo`, `#ff00aa`…) u `off` |
| `examples/python/reacciones.py` | Saluda por su nombre a quien reconoce, comenta tu sonrisa y agradece caricias |

Log detallado: `$env:VECTOR_LOG_LEVEL = "DEBUG"`. Documentación del fork: <https://keriganc.com/sdkdocs>

El paquete se importa como `anki_vector`, así que toda la documentación del SDK original sirve.

Capacidades: movimiento (ruedas, cabeza, brazo), animaciones y *triggers*, TTS (`say_text`), pantalla
(mostrar imágenes 184×96), cámara (stream de fotogramas), sensores (táctil, precipicio, ToF, IMU),
caras/objetos/cubo, eventos (wake-word, caras vistas…), control de comportamientos
(`behavior_control_level`), audio (reproducir WAV, stream de micro en algunas versiones).

Documentación API original: el sitio de Anki ya no es fiable; usar <https://keriganc.com/sdkdocs>,
el código y los ejemplos en `third_party/anki__vector-python-sdk/` tras ejecutar el script de clonado.

## SDK Go

| Repo | Notas |
|---|---|
| `digital-dream-labs/vector-go-sdk` | Oficial DDL, alpha. |
| **`fforchino/vector-go-sdk`** | Fork usado por wire-pod; soporta `NewWpExternal` (conexión vía wire-pod sin `sdk_config.ini`). |

Ideal para plugins de wire-pod y para binarios que se ejecuten **en el propio robot** (ARMv7).

## SDK .NET

- `randym32/Anki.Vector.SDK` — SDK en C#/.NET (Randall Maas), con documentación propia.

## Otras interfaces

- **BLE (vic-switchboard)**: protocolo de configuración (Wi-Fi, OTA, cuentas). Implementado en
  `digital-dream-labs/vector-web-setup` (Web Bluetooth) — base de los sitios de setup comunitarios.
- **HTTP de depuración** (solo dev/CFW): puertos 8887–8890.
- **SSH** (solo dev/CFW): acceso root completo al Linux del robot.

## Patrones de desarrollo recomendados

1. **Script en PC + SDK Python** para prototipar comportamientos y visión (OpenCV sobre los fotogramas).
2. **Plugin Go de wire-pod** cuando el comportamiento debe dispararse por voz.
3. **Servicio en el robot** (Go cross-compilado o C++ dentro de `wire-os-victor`) solo con robot desbloqueado.
