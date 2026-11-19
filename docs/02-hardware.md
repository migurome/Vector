# 02 · Hardware

Vector tiene dos placas principales: **headboard** (el "cerebro", Linux) y **bodyboard** (microcontrolador
que mueve motores y lee sensores). Se comunican por UART ("spine").

## Headboard

| Componente | Detalle |
|---|---|
| SoC | Qualcomm **APQ8009** (MSM8909v2 sin módem), 4× Cortex-A7 hasta 1,3 GHz. **Limitado a 533 MHz** de fábrica por calor/consumo (cpufreq permite subirlo, con riesgo de sobrecalentamiento). |
| GPU | Adreno 304 (WireOS la usa para detección facial). |
| Memoria | eMCP Kingston 04EMCP04-NL3DM627: **4 GB eMMC + 512 MB DDR3**. |
| Pantalla (cara) | 1.0: **184×96** RGB565 por SPI · 2.0: **160×80** RGB565 con bytes intercambiados. |
| Cámara | 1.0: GC1066 1280×720, 90° FoV · 2.0: BF2253L 1600×1200 (peor en baja luz). |
| Wi-Fi / BLE | WCN3610, solo 2,4 GHz 802.11n. |
| PMIC | Qualcomm PM8916. |
| IMU | Bosch BMI160. |
| Micrófonos | 4 micrófonos (array) — el audio pasa por el bodyboard hacia la cabeza. |

## Bodyboard

| Componente | Detalle |
|---|---|
| MCU | **STM32F030C8** (8 KB RAM, 64 KB flash). Empaqueta datos de sensores y aplica comandos de motores/LEDs. |
| Sensores de precipicio | 4 sensores de proximidad Lite-On. |
| Distancia (ToF) | ST VL53L0X (láser). |
| Motores | 4 (2 ruedas/orugas, cabeza, brazo) con encoder cada uno; bobinado personalizado. |
| Táctil | Sensor capacitivo en la espalda. |
| LEDs | Barra de la espalda (backpack). |
| Batería | Li-ion FullRiver **320 mAh** (2.0 añade compartimento extraíble). |

Accesorio: **cubo** con acelerómetro y LEDs, conectado por BLE.

## 1.0 vs 2.0

Prácticamente idénticos salvo pantalla, cámara y batería. Todo el CFW moderno (WireOS y derivados)
funciona en ambos porque parte del firmware oficial 2.0.1, que soporta las dos revisiones.

## Seguridad de arranque (importante para firmware)

- La CPU de producción tiene una clave fusible: el bootloader (ABOOT) solo acepta imágenes firmadas.
- Las OTA llevan un `manifest.sha256` firmado. Sin la clave privada no se pueden instalar OTA modificadas
  en un robot **bloqueado**. Ver [06-firmware](06-firmware-y-desbloqueo.md) para el desbloqueo.

## Fuentes y lectura profunda

- Hardware (os-vector docs): <https://os-vector.github.io/vector-docs/5.-Hardware/index.html>
- **Vector Technical Reference Manual** (Randall Maas, PDF muy completo): <https://randym32.github.io/Vector-TRM.pdf>
- Placas (Randall Maas): <https://randym32.github.io/Anki.Vector.Documentation/boards/vector%20boards.html>
- Guías de reparación iFixit: <https://www.ifixit.com/Device/Anki_Vector>
- Teardown: <https://www.eeworldonline.com/teardown-anki-cozmo-vector/>
