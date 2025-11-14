import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

import requests
from dotenv import load_dotenv

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.utils import descargar_archivo, descargar_archivos_concurrente, extraccion_urls_minio

def consulta_mis_comprobantes(
    mrbot_user: str,
    mrbot_api_key: str,
    base_url: str,
    mis_comprobantes_endpoint: str,
    desde: str = "01/01/2024",
    hasta: str = "31/12/2024",
    cuit_inicio_sesion: str = "20123456780",
    representado_nombre: str = "Empresa Ejemplo S.A.",
    representado_cuit: str = "30876543210",
    contrasena: str = "mi_contraseña_secreta",
    descarga_emitidos: bool = True,
    descarga_recibidos: bool = True,
    b64: bool = False,
    carga_s3: bool = False,
    carga_minio: bool = True,
    carga_json: bool = False,
    proxy_request: bool = False,
) -> Dict[str, Any]:
    """
    Solicita los comprobantes cargados por el representado a la API de Mrbot y devuelve el JSON recibido.

    La respuesta incluye la información para descargar los ZIP de emitidos y/o recibidos, ya sea
    como URLs directas o listados dentro de un nodo `descargas_minio`.

    Args:
        mrbot_user (str): email que identifica al usuario del cliente.
        mrbot_api_key (str): API key asociada al usuario.
        base_url (str): URL base de Mrbot.
        mis_comprobantes_endpoint (str): endpoint para `mis_comprobantes`.
        desde (str): fecha inicial del rango a consultar.
        hasta (str): fecha final del rango a consultar.
        cuit_inicio_sesion (str): CUIT utilizado para iniciar sesión.
        representado_nombre (str): nombre del representado.
        representado_cuit (str): CUIT del representado.
        contrasena (str): contraseña del representado.
        descarga_emitidos (bool): incluir emitidos en la descarga.
        descarga_recibidos (bool): incluir recibidos en la descarga.
        b64 (bool): solicitar el archivo en base64 en lugar de binario.
        carga_s3 (bool): solicitar carga a S3 además de MinIO.
        carga_minio (bool): solicitar carga a MinIO.
        carga_json (bool): solicitar la respuesta en JSON (sin ZIP).
        proxy_request (bool): solicitar envío vía proxy.

    Returns:
        Dict[str, Any]: JSON retornado por la API con los metadatos de descarga.
    """

    url = f"{base_url.rstrip('/')}/{mis_comprobantes_endpoint.lstrip('/')}/consulta"

    payload = json.dumps({
        "desde": desde,
        "hasta": hasta,
        "cuit_inicio_sesion": cuit_inicio_sesion,
        "representado_nombre": representado_nombre,
        "representado_cuit": representado_cuit,
        "contrasena": contrasena,
        "descarga_emitidos": descarga_emitidos,
        "descarga_recibidos": descarga_recibidos,
        "b64": b64,
        "carga_s3": carga_s3,
        "carga_minio": carga_minio,
        "carga_json": carga_json,
        "proxy_request": proxy_request,
    })

    headers = {
        "x-api-key": mrbot_api_key,
        "email": mrbot_user,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    response = requests.post(url, headers=headers, data=payload)
    response.raise_for_status()

    print(response.text)
    return response.json()


def test_caller_mc() -> None:
    load_dotenv()

    mrbot_user = os.getenv("MRBOT_USER")
    mrbot_api_key = os.getenv("MRBOT_API_KEY")
    base_url = os.getenv("BASE_URL")
    mis_comprobantes_endpoint = os.getenv("MIS_COMPROBANTES_ENDPOINT")
    desde = os.getenv("MC_DESDE_EJEMPLO")
    hasta = os.getenv("MC_HASTA_EJEMPLO")
    cuit_inicio_sesion = os.getenv("CUIT_REPRESENTADO_EJEMPLO")
    representado_nombre = os.getenv("DENOMIACION_EJEMPLO")
    representado_cuit = os.getenv("CUIT_REPRESENTANTE_EJEMPLO")
    contrasena = os.getenv("CLAVE_REPRESENTANTE_EJEMPLO")

    assert mrbot_user and mrbot_api_key and base_url and mis_comprobantes_endpoint, "Faltan credenciales obligatorias"

    response = consulta_mis_comprobantes(
        mrbot_user=mrbot_user,
        mrbot_api_key=mrbot_api_key,
        base_url=base_url,
        mis_comprobantes_endpoint=mis_comprobantes_endpoint,
        desde=desde,
        hasta=hasta,
        cuit_inicio_sesion=cuit_inicio_sesion,
        representado_nombre=representado_nombre,
        representado_cuit=representado_cuit,
        contrasena=contrasena,
    )

    urls = extraccion_urls_minio(response)

    descargas = []
    for tipo, enlace in urls.items():
        if not enlace:
            print(f"Saltando descarga de {tipo} porque no hay URL.")
            continue
        descargas.append((enlace, None, "descargas_mis_comprobantes"))
    
    if descargas:
        descargar_archivos_concurrente(descargas)
    
if __name__ == "__main__":
    test_caller_mc()
