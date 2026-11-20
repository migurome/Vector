# 04 · wire-pod: servidor local para Vector

wire-pod (kercre123, MIT) reimplementa los servidores de voz y autenticación de DDL a partir del
`chipper` que DDL liberó. Funciona con Vector 1.0 y 2.0 **de producción** (sin desbloquear).

- Código: <https://github.com/kercre123/wire-pod> · Instaladores: <https://github.com/kercre123/WirePod/releases/latest>
- Wiki: <https://github.com/kercre123/wire-pod/wiki>

## Instalación

| Plataforma | Cómo |
|---|---|
| **Windows 10/11** | `WirePodInstaller-vX.Y.Z.exe` (SmartScreen: "Más información" → "Ejecutar de todas formas"). |
| macOS 11+ | `WirePod-vX.Y.Z.dmg`. |
| Debian/Ubuntu/Raspberry Pi OS | `sudo apt install -y ./wirepod_<arch>-X.Y.Z.deb` (Pi 5 → arm64). |
| Otro Linux | `git clone https://github.com/kercre123/wire-pod` → `sudo STT=vosk ./setup.sh` → `sudo ./chipper/start.sh` (servicio: `sudo ./setup.sh daemon-enable`). |
| Android 6+ | APK; desactivar optimización de batería. |
| Docker | `compose.yaml` del repo; requiere nombre mDNS `escapepod.local`. |

Interfaz web de configuración: **`http://<ip-del-servidor>:8080`**.

> Recomendación: un servidor siempre encendido (Raspberry Pi 4/5 o un mini-PC). Si va en un PC con
> Windows, el robot pierde la voz cuando el PC se apaga.

## Emparejar un robot de producción

1. Robot en el cargador → mantener el botón **~15 s** hasta que vuelvan las luces (modo recuperación,
   pantalla `anki.com/v` o `ddl.io/v`).
2. En Chrome con Bluetooth: <https://wp.pvic.xyz/> → emparejar con `vector-wirepod-setup` → el robot
   descarga una OTA con soporte *Escape Pod* (versión terminada en **`ep`**).
3. **Borrar datos de usuario** después (evita comportamientos raros).
4. Comprobar en la pantalla CCIS que el firmware termina en `ep`.
5. En wire-pod → *Bot Setup* → **ACTIVATE / AUTHENTICATE** (reintentar a los ~20 s si falla).

Robots desbloqueados (OSKR/dev/WireOS): *Bot Setup* → "Set up OSKR/dev bot" y luego autenticar.

## Nuestra experiencia (19-11-2026, Windows 11, robot G4C7, firmware de fábrica)

Lo que funcionó cuando la web `wp.pvic.xyz` se quedaba colgada en Chrome/Edge (y Bot Setup de wire-pod
no encontraba el robot por Bluetooth):

1. **Modelo de voz**: wire-pod se quedó descargando el modelo Vosk (0 bytes, GitHub inestable). Solución:
   bajar `https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip` y descomprimirlo como
   `%APPDATA%\wire-pod\vosk\models\es-ES\model\`. Sin modelo, wire-pod no abre el puerto 443.
2. **Wi-Fi 2,4 GHz**: Vector no ve 5 GHz. Los routers Movistar Wi-Fi 6 emiten ambas bandas con el mismo
   nombre: sirve. El punto de acceso del POCO M6 Pro no permitía elegir banda.
3. **Modo emparejamiento ≠ pantalla `anki.com/v`**: el robot solo acepta emparejar si anuncia `p` en el
   4º byte de *manufacturer data* (`f8057670`). Se activa con **doble pulsación** en la base y dura ~1 min.
   Comprobarlo con `scripts/ble_modo_emparejamiento.py`.
4. **Emparejar desde terminal** con [`tools/vector-ble-cli`](../tools/vector-ble-cli/README.md):
   PIN → `wifi-connect` → `ota-start http://ota.pvic.xyz/ep/2.0.1.6086ep.ota` (firmware de fábrica,
   RTS v2) → tras reiniciar, PIN de nuevo → `anki-auth 2vMhFgktH3Jrbemm2WHkfGN` (token que usa wire-pod,
   `chipper/pkg/wirepod/setup/ble.go`). Resultado: `AuthorizedAsSecondary` y el robot aparece en
   `%APPDATA%\wire-pod\jdocs\botSdkInfo.json` como `activated: true`.
5. **Cambio de IP (20-11-2026)**: el router dio al robot otra IP (.36) y la suya (.34) al PC. wire-pod
   seguía usando la de `botSdkInfo.json`, se conectaba a sí mismo y fallaba con `unknown service
   Anki.Vector.external_interface.ExternalInterface`. wire-pod no tiene API para cambiarla y la guarda en
   memoria. «Reconectar» de la web lo resuelve: busca el robot en la red por su certificado (`Vector-XXXX`),
   para wire-pod, cambia la IP en el fichero, lo relanza y vuelve a ejecutar `scripts/configurar_sdk.py`.
   Para evitarlo: reservar la IP del robot en el DHCP del router.

## Extender wire-pod

### Plugins (Go)

Un plugin es un `.go` en `package main` que exporta:

```go
var Utterances = []string{"haz un baile"}   // "*" = recibir todas las frases
var Name = "Mi plugin"

// Devuelve (intent, textoParaDecir). Si texto != "" Vector lo dice; si ambos vacíos sigue el flujo normal.
func Action(transcribedText string, botSerial string, guid string, target string) (string, string) {
    return "", "¡Hola desde mi plugin!"
}
```

```bash
go build -buildmode=plugin -ldflags "-w -s" -o miplugin.so miplugin.go
# copiar a chipper/plugins/ y reiniciar wire-pod
```

Para mover el robot desde un plugin, usar `github.com/fforchino/vector-go-sdk` (paquetes `vector` y
`vectorpb`, **no** `sdk_wrapper`) con `vector.New(vector.WithSerialNo(..), vector.WithTarget(..), vector.WithToken(..))`.

Los plugins Go solo se cargan en Linux/macOS (limitación de `-buildmode=plugin`).

### Otros puntos de extensión

- **Intents personalizados** desde la web de configuración (frase → intent / script).
- **STT**: Vosk (por defecto), Whisper.cpp (recomendado en máquina potente, CUDA/Metal), Coqui.
  Referencia para añadir uno: `chipper/pkg/wirepod/stt/coqui/`.
- **"Knowledge graph" / preguntas abiertas**: wire-pod permite conectar un proveedor LLM
  (configurable en la web) para que Vector responda preguntas.

## Fuentes

- <https://github.com/kercre123/wire-pod/wiki/Installation>
- <https://github.com/kercre123/wire-pod/wiki/For-Developers-and-Tinkerers>
- <https://github.com/kercre123/wire-pod/wiki/Troubleshooting>
