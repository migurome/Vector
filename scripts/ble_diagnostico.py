"""Diagnóstico Bluetooth de Vector: busca el robot, conecta y espera el primer mensaje.

Uso (robot en modo recuperación, Chrome cerrado):  python scripts/ble_diagnostico.py
Requiere: pip install bleak
"""
import asyncio

from bleak import BleakClient, BleakScanner

VECTOR_SERVICE = "0000fee3-0000-1000-8000-00805f9b34fb"
# Nombres según vector-web-setup: la web escribe en "read" y recibe notificaciones en "write".
CHAR_TO_ROBOT = "7d2a4bda-d29b-4152-b725-2491478c5cd7"
CHAR_FROM_ROBOT = "30619f2d-0f54-41bd-a65a-7588d8c85b45"


async def main():
    print("Buscando robots Vector (10 s)...")
    found = await BleakScanner.discover(timeout=10, return_adv=True)
    vectors = [(d, adv) for d, adv in found.values()
               if (d.name or adv.local_name or "").startswith("Vector")
               or VECTOR_SERVICE in adv.service_uuids]
    if not vectors:
        print("NO se encuentra ningún Vector. ¿Está en modo recuperación y cerca?")
        return
    for d, adv in vectors:
        print(f"  {d.name or adv.local_name}  {d.address}  RSSI={adv.rssi}")

    device = vectors[0][0]
    print(f"\nConectando con {device.name} (timeout 30 s)...")
    try:
        async with BleakClient(device, timeout=30) as client:
            print("Conectado. Servicios:")
            for s in client.services:
                print("  ", s.uuid)
            got = asyncio.Event()

            def on_msg(_, data: bytearray):
                print("  <- mensaje del robot:", data.hex())
                got.set()

            await client.start_notify(CHAR_FROM_ROBOT, on_msg)
            print("Esperando el saludo del robot (15 s)...")
            try:
                await asyncio.wait_for(got.wait(), 15)
                print("\nOK: el Bluetooth funciona; el problema está en la web/Chrome.")
            except asyncio.TimeoutError:
                print("\nConecta pero el robot NO envía nada: probablemente firmware/estado del robot.")
    except Exception as e:
        print(f"\nFALLO al conectar: {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
