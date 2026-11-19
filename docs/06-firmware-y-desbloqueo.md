# 06 · Firmware, desbloqueo y CFW

> ⚠️ Flashear firmware puede **dejar el robot inservible**. Haz primero todo lo que puedas con
> wire-pod + SDK. Antes de desbloquear, apunta número de serie, versión de firmware y ten el robot
> cargado.

## Tipos de robot / firmware

| Tipo | Qué acepta |
|---|---|
| **Producción (bloqueado)** | Solo OTA firmadas por Anki/DDL (prod, y la variante `ep` para Escape Pod / wire-pod). |
| **OSKR** | Desbloqueado por el programa oficial de DDL. Acepta OTA dev; SSH. |
| **Producción desbloqueado** | Desde abril de 2025, vía OTA `unlock-prod` comunitaria. Acepta OTA dev; SSH. |
| Prototipos (DVT/PVT) | CPU sin fusibles; casos especiales. |

¿Qué hace el desbloqueo? Sustituye `ABOOT`, `recovery` y `recoveryfs` por versiones que permiten
OTA de desarrollo. Con eso se gana SSH root, servidores de depuración y la posibilidad de instalar CFW.

- Info y estado: <https://github.com/kercre123/unlocking-vector> (archivado; `README-old.md` explica el porqué técnico)
- Herramienta de desbloqueo: <https://unlock-prod.skittle.dev/>
- Clave SSH global de los robots dev: `ssh_root_key` en el repo `unlocking-vector`

## WireOS (CFW base recomendado)

Firmware comunitario mantenido, basado en el código 2.0.1.6076, actualizado a Yocto moderno.
Repo: <https://github.com/os-vector/wire-os> · Código de `/anki`: <https://github.com/os-vector/wire-os-victor>

Mejoras: wake-word Porcupine personalizable, servidor `wired` (:8080), detección/reconocimiento facial
YuNet + MobileFaceNet acelerados por GPU, TensorFlow Lite y OpenCV 4.12 modernos, Clang 20, kernel 4.9,
ABI hardfp, correcciones de cámara/pantalla, ojos arcoíris.

### Instalación

- **Producción desbloqueado** (cualquiera):
  - Web: <https://websetup.froggitti.net/> o <https://websetup.skittle.dev> → *Custom Firmware* → WireOS
    (robot en recuperación: 15 s en el cargador).
  - Terminal BLE en recuperación: `ota-start http://ota.pvic.xyz/vic/latest/dev.ota`
  - Por SSH desde otro CFW: `update-os http://ota.pvic.xyz/vic/latest/dev.ota`
- **OSKR**:
  ```sh
  systemctl stop anki-robot.target
  mount -o rw,remount,exec /data
  curl -o /data/update-engine http://ota.pvic.xyz/update-engine
  chmod +rwx /data/update-engine
  /data/update-engine http://ota.pvic.xyz/vic/latest/oskr.ota -v
  ```

### Compilar WireOS

Requisitos: **Linux** x86_64 o aarch64 (en Windows → WSL2 con disco suficiente o una VM), mínimo
4 núcleos / 8 GB RAM / 100 GB; recomendado 8+ núcleos / 16+ GB / 200+ GB. Docker recomendado.

```bash
git clone https://github.com/os-vector/wire-os --recurse-submodules
cd wire-os
./build/build.sh -bt dev -v <incremento>     # salida: ./_build/3.0.1.<incremento>.ota
```

Una OTA completa tarda ~50 min desde cero. Para iterar, **compilar solo `wire-os-victor`** y desplegarlo
por SSH sobre un robot que ya tenga WireOS.

### Otros CFW (derivados)

Viccyware, purplOS, redOS, RainbOS, ClaudOS, 1.6-rebuild → <https://os-vector.github.io/vector-docs/2.-Available-CFW/1-WireOS.html>

### Crear nuestro propio CFW

Guía paso a paso (fork, desarrollo, ejemplo "añadir un color de ojos"):
<https://os-vector.github.io/vector-docs/6.-Make-Your-Own-CFW/1.%20prerequisites.html>

## Código fuente histórico

- `kercre123/victor` — fuente completa de Vector (rama `snowboy` compilable con Docker + git-lfs:
  `./wire/build-d.sh`, salida en `./_build/vicos/Release/`). Repo **muy grande**.
- `kercre123/vic-yocto` — capa Yocto anterior a WireOS.
