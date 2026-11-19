"""Vigila si Vector anuncia modo emparejamiento ('p' en el 4º byte de manufacturer data).

Uso: python scripts/ble_modo_emparejamiento.py [segundos]   (por defecto 120)
Mientras corre, prueba en el robot: doble pulsación del botón en la base.
"""
import asyncio
import sys
import time

from bleak import BleakScanner


async def main(limit):
    last = None
    end = time.time() + limit

    def cb(d, a):
        nonlocal last
        if not (d.name or a.local_name or "").startswith("Vector"):
            return
        for cid, data in a.manufacturer_data.items():
            full = cid.to_bytes(2, "little") + data  # vector-web-setup indexa incluyendo el company id
            state = "EMPAREJAMIENTO" if len(full) > 3 and full[3] == ord("p") else "normal"
            if state != last:
                last = state
                print(time.strftime("%H:%M:%S"), d.name, full.hex(), "->", state, flush=True)

    async with BleakScanner(cb):
        print(f"Vigilando {limit} s...", flush=True)
        while time.time() < end and last != "EMPAREJAMIENTO":
            await asyncio.sleep(0.5)
    print("¡Listo! Lanza ahora: node tools\\vector-ble-cli\\index.js" if last == "EMPAREJAMIENTO"
          else "No ha entrado en modo emparejamiento.")


asyncio.run(main(int(sys.argv[1]) if len(sys.argv) > 1 else 120))
