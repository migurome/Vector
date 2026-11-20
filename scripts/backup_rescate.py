"""Kit de rescate de Vector antes de desbloquearlo (Fase 8). Solo lee del robot: no cambia nada.

Uso:  .venv\\Scripts\\python scripts\\backup_rescate.py [destino]        (por defecto E:\\vector-rescate)

Crea en el destino:
  ota/                    las OTA para volver atrás o reinstalar (se descargan una vez; se verifican)
  ota/SHA256SUMS.txt      huella de cada fichero y versión que declara su manifest.ini
  AAAAMMDD-HHMM/wire-pod/ datos de wire-pod (%APPDATA%\\wire-pod sin el modelo de voz)
  AAAAMMDD-HHMM/anki_vector/  certificado y configuración del SDK (~/.anki_vector)
  AAAAMMDD-HHMM/robot/    versión del firmware, caras que conoce y sus fotos (necesita el SDK y el robot encendido)

Contiene certificados y datos del robot: NO subirlo a git ni a sitios públicos.
"""
import configparser
import hashlib
import io
import os
import pathlib
import shutil
import sys
import tarfile
import time
import urllib.request

WEBSETUP = "http://websetup.skittle.dev:8000/static/firmware/"
OTAS = {  # fichero local -> URL (comprobadas el 2026-11-19)
    "2.0.1.6086ep.ota": "http://ota.pvic.xyz/ep/2.0.1.6086ep.ota",          # el firmware que lleva ahora
    "Revert-To-Prod.ota": WEBSETUP + "utility/Revert-To-Prod.ota",          # deshace el desbloqueo
    "Unlock-Prod.ota": WEBSETUP + "utility/Unlock-Prod.ota",
    "WireOS.ota": WEBSETUP + "custom%20firmware/WireOS",
}


def log(msg):
    print(time.strftime("%H:%M:%S"), msg, flush=True)


def descargar(url, destino):
    """Descarga a .part y renombra al terminar; si ya está completo (mismo tamaño que el servidor), no hace nada."""
    with urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=30) as r:
        total = int(r.headers["Content-Length"])
    if destino.exists() and destino.stat().st_size == total:
        log(f"{destino.name}: ya descargado")
        return
    parte = destino.with_suffix(destino.suffix + ".part")
    log(f"{destino.name}: descargando {total / 1e6:.0f} MB")
    with urllib.request.urlopen(url, timeout=60) as r, open(parte, "wb") as f:
        hecho, aviso = 0, 0
        while bloque := r.read(1 << 20):
            f.write(bloque)
            hecho += len(bloque)
            if hecho - aviso >= 25 << 20:
                aviso = hecho
                log(f"  {destino.name}: {100 * hecho // total} %")
    if parte.stat().st_size != total:
        raise IOError(f"{destino.name}: descarga incompleta ({parte.stat().st_size} de {total} bytes)")
    parte.replace(destino)


def verificar(ota):
    """Comprueba que es un tar de OTA completo y devuelve (sha256, update_version)."""
    with tarfile.open(ota) as t:
        miembros = t.getmembers()  # recorre el fichero entero: falla si está truncado
        nombres = [m.name for m in miembros]
        assert nombres[0] == "manifest.ini", f"{ota.name}: no parece una OTA ({nombres[:3]})"
        ini = configparser.ConfigParser()
        ini.read_string(t.extractfile("manifest.ini").read().decode())
        # manifest.sha256 (firma) solo lo llevan las OTA para robots bloqueados; Revert-To-Prod no
        imagenes = [n for n in nombres if n.endswith(".img.gz")]
        assert int(ini["META"]["num_images"]) == len(imagenes), f"{ota.name}: faltan imágenes"
        firma = "firmada" if "manifest.sha256" in nombres else "sin firma"
    h = hashlib.sha256()
    with open(ota, "rb") as f:
        while bloque := f.read(1 << 20):
            h.update(bloque)
    return h.hexdigest(), f'{ini["META"]["update_version"]}, {firma}'


def copiar_pc(dest):
    wirepod = pathlib.Path(os.environ["APPDATA"]) / "wire-pod"
    shutil.copytree(wirepod, dest / "wire-pod", ignore=shutil.ignore_patterns("vosk"))
    shutil.copytree(pathlib.Path.home() / ".anki_vector", dest / "anki_vector")
    log("Copiados los datos de wire-pod y del SDK")


def copiar_robot(dest):
    try:
        import anki_vector
    except ImportError:
        log("AVISO: sin SDK (ejecuta con .venv\\Scripts\\python); no copio fotos ni caras")
        return
    from PIL import Image
    carpeta = dest / "robot"
    (carpeta / "fotos").mkdir(parents=True)
    with anki_vector.Robot() as robot:
        v = robot.get_version_state()
        caras = robot.faces.request_enrolled_names().faces
        (carpeta / "robot.txt").write_text(
            f"Firmware: {v.os_version}\nMotor: {v.engine_build_id}\n\nCaras que conoce:\n"
            + "".join(f"  {c.face_id}: {c.name}\n" for c in caras), encoding="utf-8")
        fotos = robot.photos.photo_info
        for p in fotos:
            datos = robot.photos.get_photo(p.photo_id).image
            Image.open(io.BytesIO(datos)).save(carpeta / "fotos" / f"foto-{p.photo_id}.png")
    log(f"Robot: firmware {v.os_version}, {len(caras)} caras, {len(fotos)} fotos")


def main():
    raiz = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else r"E:\vector-rescate")
    ota = raiz / "ota"
    ota.mkdir(parents=True, exist_ok=True)
    dest = raiz / time.strftime("%Y%m%d-%H%M")
    dest.mkdir()
    copiar_pc(dest)
    try:
        copiar_robot(dest)
    except Exception as e:  # robot apagado o sin conexión: las OTA siguen siendo lo importante
        log(f"AVISO: no he podido copiar del robot ({str(e).splitlines()[0]}); repite con el robot encendido")
    lineas = []
    for nombre, url in OTAS.items():
        descargar(url, ota / nombre)
        sha, version = verificar(ota / nombre)
        lineas.append(f"{sha}  {nombre}  (update_version={version})  {url}")
        log(f"{nombre}: OK, versión {version}")
    (ota / "SHA256SUMS.txt").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    log(f"Kit de rescate completo en {raiz}")


if __name__ == "__main__":
    main()
