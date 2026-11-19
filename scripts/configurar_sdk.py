"""Configura el SDK Python de Vector sin depender de los servidores de DDL.

El asistente oficial (python -m anki_vector.configure) pide el certificado del robot a wire-pod, que solo
lo tiene si lo descargó de DDL. Aquí lo leemos directamente del robot (su certificado TLS del puerto 443)
y reutilizamos las funciones del asistente para autenticar y escribir ~/.anki_vector/sdk_config.ini.

Uso (con el robot encendido y wire-pod abierto):
    .venv\\Scripts\\python.exe scripts\\configurar_sdk.py
IP, nº de serie y nombre se obtienen solos (wire-pod + certificado del robot).
"""
import json
import ssl
import sys
import urllib.request
from pathlib import Path

from cryptography import x509
from anki_vector.configure.__main__ import save_cert, user_authentication, write_config

WIREPOD = "http://localhost:8080"
TOKEN = "2vMhFgktH3Jrbemm2WHkfGN"  # token fijo que usa wire-pod para autorizar al SDK


def main():
    info = json.load(urllib.request.urlopen(WIREPOD + "/api-sdk/get_sdk_info", timeout=10))
    bot = info["robots"][0]
    esn, ip = bot["esn"], bot["ip_address"]

    pem = ssl.get_server_certificate((ip, 443), timeout=15).encode()
    cert = x509.load_pem_x509_certificate(pem)
    name = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value
    if not name.startswith("Vector-"):
        sys.exit(f"Certificado inesperado (CN={name}); ¿es la IP del robot?")
    print(f"Robot {name} en {ip}")

    cert_file = save_cert(pem, name, esn, Path.home() / ".anki_vector")
    guid = user_authentication(TOKEN, pem, ip, name)
    write_config(esn, cert_file, ip, name, guid)
    print("SDK configurado.")


if __name__ == "__main__":
    main()
