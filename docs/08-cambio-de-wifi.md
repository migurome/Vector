# 08 · Protocolo de cambio de red Wi-Fi

Cuando cambiemos de router o de casa. Tiempo estimado: 5 minutos.

## Requisitos de la red nueva

- **2,4 GHz** (Vector no ve 5 GHz). Vale una red con 2,4 y 5 GHz bajo el mismo nombre.
- **WPA2-Personal**. Nada de portales cautivos (hoteles) ni WPA3 exclusivo.
- El **PC con wire-pod y el robot en la misma red**.

## Pasos

1. **PC a la red nueva.** En Windows, marca la red como **privada** (*Configuración → Red e Internet →
   Wi-Fi → propiedades de la red → Red privada*). En una red pública el firewall puede bloquear a wire-pod.
2. **wire-pod en marcha**: abrir *WirePod* desde el menú Inicio y comprobar `http://localhost:8080`.
3. **Robot en modo emparejamiento**: en la base, **doble pulsación** del botón. Dura ~1 minuto.
   (Para confirmarlo: `python scripts\ble_modo_emparejamiento.py`, debe decir `EMPAREJAMIENTO`.)
4. **Cambiar la red** desde PowerShell:
   ```powershell
   cd <carpeta del proyecto>\tools\vector-ble-cli
   node index.js --wifi "NOMBRE_RED" "CONTRASEÑA"
   ```
5. Escribe el **PIN** que aparece en la cara del robot. La herramienta hace `wifi-scan`,
   `wifi-connect`, `wifi-ip` y `status`, y termina sola.
6. Comprueba `wifi state: online` y la `IPv4`. **No hay que tocar wire-pod**: cuando el robot se conecta,
   wire-pod anota la nueva IP automáticamente (`chipper/pkg/vars/vars.go`, `RecordBot`).
7. Verifica en la web del proyecto (`python web\server.py` → <http://localhost:8090>) que el estado pasa
   a **En línea**, y prueba «Hey Vector, ¿qué hora es?».

## Si algo falla

| Síntoma | Solución |
|---|---|
| `No llega el saludo del robot` | Ctrl+C, espera 5 s y relanza. |
| `Pairing failed` | El robot salió del modo emparejamiento: repite la doble pulsación y lanza enseguida. |
| La red no aparece en `wifi-scan` | Es de 5 GHz o está oculta. |
| `online` pero la web dice «sin conexión» | Red marcada como pública en Windows o aislamiento de clientes en el router (redes de invitados). |
| Vector no responde a la voz | wire-pod cerrado: abrir *WirePod* desde Inicio. |

Solo si el robot pierde la autenticación (p. ej. tras un borrado de datos): en el prompt interactivo
(`node index.js`, sin `--wifi`) ejecutar `anki-auth 2vMhFgktH3Jrbemm2WHkfGN`.
