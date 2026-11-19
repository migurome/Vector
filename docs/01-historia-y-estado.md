# 01 · Historia y estado actual

## Cronología

| Fecha | Hito |
|---|---|
| 2018 (ago) | Anki lanza Vector (versión 1.0), sucesor de Cozmo, con chip Qualcomm y nube propia. |
| 2019 (abr) | Anki cierra. |
| 2019 (dic) | Digital Dream Labs (DDL) compra los activos de Anki. |
| 2020–2022 | DDL lanza Vector 2.0, suscripción de nube, el programa **OSKR** (desbloqueo oficial para desarrolladores) y publica en GitHub parte del software de servidor: `chipper`, `vector-cloud`, `vector-web-setup`, `hugh`, `escape-pod-extension`, `vector-go-sdk`. |
| 2023 | Fallos prolongados de los servidores de DDL. La comunidad crea **wire-pod** (kercre123), basado en `chipper`. |
| 2024 | Se filtra/aparece el código fuente del firmware (2.0.1.6076); reportes de que DDL restaura parcialmente la nube en noviembre. |
| 2025 (abr) | Según `kercre123/unlocking-vector`, **cualquier Vector de producción puede desbloquearse fácilmente** (unlock-prod OTA). |
| 2025–2026 | **WireOS** (os-vector) se convierte en la base de firmware personalizado (CFW) mantenida; aparecen derivados (Viccyware, purplOS, redOS, RainbOS, ClaudOS…). |

## Estado en 2026 (resumen práctico)

- **No dependas de la nube de DDL.** Su disponibilidad es irregular y requiere suscripción. La comunidad
  trata **wire-pod** como el estándar de facto.
- **El robot sigue siendo programable** vía gRPC (SDK) contra un robot autenticado con wire-pod.
- **El firmware es modificable**: hay código fuente compilable (WireOS) y un método de desbloqueo para
  robots de producción.
- DDL sigue vendiendo la *Escape Pod* oficial (servidor local de pago); wire-pod la sustituye gratis.

## Fuentes

- Historia comunitaria: <https://os-vector.github.io/vector-docs/1.-History/history-of-anki.html>
- Estado de desbloqueo: <https://github.com/kercre123/unlocking-vector>
- Restauración de servidores 2024: <https://www.originofbots.com/news/digital-dream-labs-restores-vector-server-access-november-2024-revives-discontinued-robot>
