# 09 · Desbloqueo: preparación, fallos y rescate (Fase 8)

> Complementa a [06 · Firmware y desbloqueo](06-firmware-y-desbloqueo.md). Nada de esto se ha aplicado
> todavía al robot: es el plan y el kit para hacerlo con red de seguridad.

## 1. Kit de rescate (antes de tocar nada)

```powershell
.venv\Scripts\python scripts\backup_rescate.py            # destino por defecto: E:\vector-rescate (USB)
```

Solo lee: copia `%APPDATA%\wire-pod` (sin el modelo de voz), `~/.anki_vector` (certificado del SDK), la
versión del firmware, las caras que conoce y sus fotos; y descarga y verifica 4 OTA:

| OTA | Para qué |
|---|---|
| `2.0.1.6086ep.ota` | El firmware que lleva hoy: volver exactamente a como está |
| `Revert-To-Prod.ota` | Deshacer el desbloqueo (devuelve el arranque y la recuperación originales) |
| `Unlock-Prod.ota` | Desbloquear |
| `WireOS.ota` | Firmware comunitario |

`ota/SHA256SUMS.txt` guarda la huella y la versión de cada una. Verificadas el 2026-11-19:

| OTA | Versión que declara | Firma |
|---|---|---|
| `2.0.1.6086ep.ota` | 2.0.1.6086ep | firmada |
| `Unlock-Prod.ota` | 5.0.0.0-unlocker | firmada |
| `Revert-To-Prod.ota` | 5.0.0.0-relocker | sin firma |
| `WireOS.ota` | 3.0.2.34d | sin firma |

Consecuencia: **un robot bloqueado solo acepta las firmadas**. `Revert-To-Prod` y `WireOS` solo se
pueden instalar una vez desbloqueado; mientras siga bloqueado, la única vuelta atrás es la `6086ep`. El kit tiene certificados: **no va a git**.
Repetirlo justo antes de desbloquear (las OTA ya bajadas no se descargan otra vez).

## 2. Lista previa

- [ ] Kit de rescate hecho hoy y la USB conectada.
- [ ] Batería llena y el robot **en el cargador todo el proceso** (no quitarlo hasta que termine).
- [ ] Wi-Fi de 2,4 GHz estable con Internet; el PC sin suspensión mientras dure.
- [ ] Nada usando el robot: comportamientos parados, web en modo libre.
- [ ] Bluetooth del PC funcionando con `tools/vector-ble-cli` (el navegador no sirve en este PC).

## 3. Plan

1. **Recuperación**: en el cargador, mantener el botón ~15 s hasta que las 2 luces se pongan azul oscuro.
   Mostrará `anki.com/v` (es el sistema mínimo de fábrica, el mismo que usamos el primer día).
2. **Conectar**: `node index.js` en `tools/vector-ble-cli`, emparejar con el PIN de su pantalla,
   `wifi-connect` y `wifi-ip` (debe tener IP).
3. **Punto de no retorno** — `ota-start http://websetup.skittle.dev:8000/static/firmware/utility/Unlock-Prod.ota`
   y no tocarlo (~7 min). El robot descarga la OTA él solo: si se corta el Bluetooth, la instalación sigue.
4. **Comprobar** que arranca. Después, WireOS: otra vez recuperación y
   `ota-start http://websetup.skittle.dev:8000/static/firmware/custom%20firmware/WireOS`.
5. **wire-pod**: *Bot Setup* → «Set up OSKR/dev bot», autenticar; luego `scripts/configurar_sdk.py` y
   comprobar la web (pulsar «Reconectar» si da 401).

## 4. Qué puede fallar y qué hacer

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| La herramienta no encuentra el robot | No está en recuperación o en modo emparejamiento | Repetir los 15 s en el cargador; doble pulsación; reiniciar el Bluetooth del PC |
| «Pairing failed» o se corta el saludo | Fuera de modo emparejamiento o PIN caducado (15 s) | Volver a entrar y teclear el PIN en cuanto salga |
| `wifi-ip` sin IP | Red de 5 GHz o contraseña mal | Red de 2,4 GHz; repetir `wifi-connect` |
| `ota-start` se queda en 0 % o da error de descarga | Sin Internet en el robot o el servidor comunitario caído | Servir la OTA desde el PC (ver 5) |
| «Downgrade not allowed» u otro error de versión | No arrancó en recuperación | Volver a recuperación y repetir |
| Se corta a mitad (luz, batería, Wi-Fi) | El robot tiene dos particiones y una recuperación: si la nueva falla, arranca de otra | Dejarlo cargar, entrar en recuperación y repetir el `ota-start` |
| Arranca pero wire-pod no lo reconoce | Tras el cambio hay que darlo de alta otra vez | *Bot Setup* → OSKR/dev bot; autenticar; `configurar_sdk.py` |
| La web da 401 o «cert does not exist» | Certificado nuevo en el robot | `configurar_sdk.py` y «Reconectar» en la web |
| Errores 800, 850–852 o 920–921 en la cara | Datos de usuario corruptos | **Borrar datos de usuario** (ver 6) |
| WireOS no convence o va mal | — | Recuperación → `Revert-To-Prod.ota` → recuperación → `2.0.1.6086ep.ota` |
| Pantalla negra, ni arranca ni entra en recuperación | Batería agotada… o fallo grave | Dejarlo 30–60 min en el cargador y reintentar. Si nada: es el riesgo real, sin arreglo por software |

## 5. Servir las OTA desde el PC (si los servidores comunitarios no responden)

```powershell
cd E:\vector-rescate\ota
python -m http.server 8000          # el firewall de Windows debe permitir Python en la red privada
```

Y en la herramienta BLE: `ota-start http://<IP-del-PC>:8000/Unlock-Prod.ota` (la IP del PC con `ipconfig`).
El robot y el PC deben estar en la misma red.

## 6. Borrar datos de usuario (reseteo de fábrica)

Borra caras, ajustes, Wi-Fi y certificado; **no** cambia el firmware ni deshace el desbloqueo.
Procedimiento de Anki (pendiente de comprobar en nuestro robot): en el cargador, doble pulsación del botón,
subir y bajar el brazo hasta ver «CLEAR USER DATA?», girar una rueda hasta CONFIRM y subir y bajar el brazo.
Después: Wi-Fi y autenticación con `vector-ble-cli`, `configurar_sdk.py` y volver a presentarle las caras.

## Fuentes

- Guía de desbloqueo: <https://unlock-prod.skittle.dev/> · instalador: <https://websetup.skittle.dev/>
- WireOS: <https://os-vector.github.io/vector-docs/2.%20Available%20CFW/1.%20WireOS.html>
- Recuperación de firmware (DDL): <https://support.anki.bot/article/383-performing-a-firmware-recovery-reset>
- «Downgrade not allowed»: <https://support.anki.bot/article/377-firmware-downgrade-not-allowed-error>
- Códigos de error: `third_party/randym32__Anki.Vector.Documentation/documents/troubleshooting/`
