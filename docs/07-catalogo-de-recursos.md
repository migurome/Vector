# 07 · Catálogo de recursos

Todos los repos marcados ✅ se comprobaron accesibles en noviembre de 2026. Los de `repos.txt` se
pueden clonar con `scripts/clone_repos.ps1`.

## Servidor / voz

| Recurso | Qué es |
|---|---|
| ✅ [kercre123/wire-pod](https://github.com/kercre123/wire-pod) | Servidor local de voz y autenticación (Go). **Pieza central.** |
| ✅ [kercre123/WirePod](https://github.com/kercre123/WirePod) | Empaquetado/instaladores de wire-pod (Windows, macOS, deb, APK). |
| ✅ [digital-dream-labs/chipper](https://github.com/digital-dream-labs/chipper) | Servidor de voz original de DDL (base de wire-pod). |
| ✅ [digital-dream-labs/vector-cloud](https://github.com/digital-dream-labs/vector-cloud) | Código de `vic-cloud` / `vic-gateway` (Go) que corre en el robot. |
| ✅ [digital-dream-labs/hugh](https://github.com/digital-dream-labs/hugh) | Librerías comunes Go de DDL (logging, gRPC…). |
| ✅ [digital-dream-labs/escape-pod-extension](https://github.com/digital-dream-labs/escape-pod-extension) | Ejemplo de extensión para la Escape Pod oficial. |

## SDKs

| Recurso | Qué es |
|---|---|
| ✅ [kercre123/wirepod-vector-python-sdk](https://github.com/kercre123/wirepod-vector-python-sdk) · [PyPI](https://pypi.org/project/wirepod-vector-sdk/) | SDK Python para wire-pod. **Recomendado.** |
| ✅ [anki/vector-python-sdk](https://github.com/anki/vector-python-sdk) | SDK Python original + `.proto` + docs + ejemplos. |
| ✅ [cyb3rdog/vector-python-sdk](https://github.com/cyb3rdog/vector-python-sdk) | Fork comunitario del SDK Python. |
| ✅ [fforchino/vector-go-sdk](https://github.com/fforchino/vector-go-sdk) | SDK Go usado por los plugins de wire-pod. |
| ✅ [digital-dream-labs/vector-go-sdk](https://github.com/digital-dream-labs/vector-go-sdk) | SDK Go oficial DDL (alpha). |
| ✅ [randym32/Anki.Vector.SDK](https://github.com/randym32/Anki.Vector.SDK) | SDK .NET/C#. |
| ✅ [anki/cozmo-python-sdk](https://github.com/anki/cozmo-python-sdk) | SDK de Cozmo (referencia, comparte diseño). |

## Firmware

| Recurso | Qué es |
|---|---|
| ✅ [os-vector/wire-os](https://github.com/os-vector/wire-os) | Build completo del CFW WireOS (Yocto → OTA). |
| ✅ [os-vector/wire-os-victor](https://github.com/os-vector/wire-os-victor) | Código de `/anki` (engine, anim, robot…) de WireOS. **Donde se desarrolla.** |
| ✅ [kercre123/victor](https://github.com/kercre123/victor) | Fuente histórica de Vector. |
| ✅ [kercre123/vic-yocto](https://github.com/kercre123/vic-yocto) | Capa Yocto anterior. |
| ✅ [kercre123/unlocking-vector](https://github.com/kercre123/unlocking-vector) | Desbloqueo: explicación, binarios, prototipos, clave SSH. |
| ✅ [digital-dream-labs/vector-web-setup](https://github.com/digital-dream-labs/vector-web-setup) | Configuración por Web Bluetooth (protocolo BLE). |

## Documentación

| Recurso | Qué es |
|---|---|
| ✅ [os-vector/vector-docs](https://github.com/os-vector/vector-docs) · [web](https://os-vector.github.io/vector-docs/) | Documentación comunitaria actual: arquitectura, particiones, hardware, CFW. |
| ✅ [randym32/Anki.Vector.Documentation](https://github.com/randym32/Anki.Vector.Documentation) · [web](https://randym32.github.io/Anki.Vector.Documentation/) | Documentación técnica extensa (Randall Maas). |
| [Vector-TRM.pdf](https://randym32.github.io/Vector-TRM.pdf) | Technical Reference Manual: hardware, protocolos, formatos de ficheros. |
| [wire-pod wiki](https://github.com/kercre123/wire-pod/wiki) | Instalación, troubleshooting, desarrollo. |
| [support.anki.bot](https://support.anki.bot/article/361-vector-developer-tools) | Soporte DDL: herramientas de desarrollo, Escape Pod. |
| [iFixit Anki Vector](https://www.ifixit.com/Device/Anki_Vector) | Reparación (batería, orugas, pantalla). |

## Herramientas web (uso puntual)

| URL | Uso |
|---|---|
| <https://wp.pvic.xyz/> | Emparejar robot de producción con wire-pod (OTA `ep`). |
| <https://unlock-prod.skittle.dev/> | Desbloquear robot de producción. |
| <https://websetup.froggitti.net/> · <https://websetup.skittle.dev> | Web setup dev / instalar CFW. |
| <https://vector-web-setup.anki.bot> | Web setup oficial alojado por DDL. |
| <http://ota.pvic.xyz/vic/latest/> | OTAs de WireOS (`dev.ota`, `oskr.ota`). |

## Comunidad

- Reddit: <https://www.reddit.com/r/AnkiVector/>
- Discord de wire-pod / Project Victor (enlazados desde los README de los repos).
