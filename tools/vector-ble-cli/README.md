# vector-ble-cli

Configura Vector por Bluetooth **desde el terminal**, sin Chrome (útil cuando Web Bluetooth se cuelga en
Windows). Reutiliza el protocolo RTS de [digital-dream-labs/vector-web-setup](https://github.com/digital-dream-labs/vector-web-setup)
(`vendor/`, licencia MIT) y sustituye `navigator.bluetooth` por el paquete npm `webbluetooth`.

Cambios sobre el original: `vendor/rtsV2Handler.js` amplía de 3 s a 15 s la espera del PIN.

## Uso

```powershell
cd tools\vector-ble-cli
npm install
node index.js            # o: node index.js G4C7  (filtra por nombre)
$env:DEBUG=1; node index.js   # muestra los mensajes crudos del robot
```

1. Robot en la base, en modo emparejamiento (doble pulsación del botón, o modo recuperación 15 s).
2. Escribe el PIN que aparece en la cara del robot.
3. Comandos útiles en el prompt `vector>`:

| Comando | Qué hace |
|---|---|
| `wifi-scan` | Lista redes |
| `wifi-connect "SSID" "contraseña"` | Conecta a la Wi-Fi |
| `wifi-ip` | IP del robot |
| `status` | Versión de firmware, estado |
| `ota-start http://ota.pvic.xyz/ep/2.0.1.6086ep.ota` | Instala el firmware compatible con wire-pod (el mismo que usa wp.pvic.xyz) |
| `ota-progress` | Progreso de la OTA |
| `help` | Todos los comandos |
