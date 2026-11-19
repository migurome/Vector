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

Soporta Python **3.6–3.12** (en este PC hay 3.14: usar un entorno con 3.11/3.12, p. ej. `py -3.12`).
Desinstalar antes otros SDK (`anki_vector`, `ikkez_vector`, `cyb3r_vector_sdk`).

```powershell
py -3.12 -m venv .venv; .\.venv\Scripts\Activate.ps1
python -m pip install -U pip wirepod_vector_sdk
python -m anki_vector.configure      # el robot debe estar ya autenticado en wire-pod; guarda ~/.anki_vector/sdk_config.ini
python examples\python\hola_vector.py
```

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
