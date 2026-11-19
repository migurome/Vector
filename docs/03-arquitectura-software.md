# 03 · Arquitectura de software

## Sistema operativo ("vicos")

- Linux embebido construido con **Yocto** (kernel 3.18 de Qualcomm en el original; 4.9 en WireOS), con **systemd**.
- La "personalidad" vive en `/anki` (partición de sistema ext4, solo lectura):
  - `/anki/bin` binarios · `/anki/lib` librerías · `/anki/etc` ficheros de entorno
  - `/anki/data/assets/cozmo_resources` animaciones, sonidos, configuración de comportamientos
- `/data` es la partición escribible (ajustes, caras aprendidas, logs).
- Particiones A/B para OTA, más `recovery`/`recoveryfs` (el modo recuperación del botón 15 s).

## Procesos principales

```
          SDK (gRPC :443)           Nube / wire-pod (voz, jdocs, tokens)
                 │                              │
           vic-gateway ──────────────────── vic-cloud      (Go)
                 │                              │
                 └──────────► vic-engine ◄──────┘          (C++)  IA, visión, SLAM, comportamientos
                                 │    │
                         vic-anim ┘    └ vic-robot          (C++)
          TTS, animación, ojos,          comunicación con el bodyboard
          sonido, wake-word              (spine UART → STM32)
          
   update-engine: OTA (BLE, SSH o timer; URL en /anki/etc/update-engine.env)
   vic-switchboard: configuración por BLE (emparejamiento / recovery)
```

- Los procesos se comunican por **sockets Unix**; `vic-engine` es el núcleo.
- `vic-gateway` expone la **API gRPC** del SDK en el puerto 443 (en WireOS se fusiona con `vic-cloud`).
- `vic-cloud` envía el audio tras la wake-word al servidor de voz (**chipper**, que es lo que reimplementa wire-pod).

## Cómo encaja wire-pod

```
Vector ──(audio tras "Hey Vector")──► wire-pod (chipper) ── STT (Vosk/Whisper/Coqui)
                                          │ texto → intent (o plugin / LLM)
Vector ◄──────── intent + respuesta ──────┘
```

wire-pod también hace de servidor de **autenticación** (emite el token que usan el SDK y la app web)
y de **jdocs** (ajustes del robot).

## Puertos útiles (robot desbloqueado / WireOS)

| Puerto | Servicio |
|---|---|
| 22 | SSH (solo firmware dev/CFW) |
| 443 | gRPC del SDK (vic-gateway) |
| 8080 | `wired` (WireOS): wake-word personalizada, perfiles de CPU, auto-actualización |
| 8887–8890 | Servidores web de depuración (8888: visor de internals en tiempo real, `/demo.html`) |

## Fuentes

- <https://os-vector.github.io/vector-docs/3.-Software-Architecture/architecture.html>
- <https://os-vector.github.io/vector-docs/3.-Software-Architecture/partitions.html>
- <https://os-vector.github.io/vector-docs/4.-Operating-System/os.html>
