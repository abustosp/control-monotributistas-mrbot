import json
import os
import re
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv
from requests.models import Response

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


def descargar_archivo(
    url: str,
    nombre_archivo: None | str = None
    ) -> None:
    """
    Descarga un recurso binario via URL conservando el nombre sugerido por el servidor cuando sea posible.

    Args:
        url (str): URL desde donde se descarga el archivo.
        nombre_archivo (Optional[str]): nombre local en el que guardar el archivo.
    """
    # Descargar en streaming y determinar nombre sugerido por el servidor (Content-Disposition)
    response = requests.get(url, stream=True)
    response.raise_for_status()

    # Intentar obtener filename desde Content-Disposition
    filename = None
    cd = response.headers.get('content-disposition')

    # soporta: filename="name.ext"  y filename*=UTF-8''name.ext
    if cd:
        m = re.search(r"filename\*?=(?:UTF-8''|\"?)([^\";]+)\"?", cd, flags=re.IGNORECASE)
        if m:
            filename = m.group(1)

    # Si no hay header o no se pudo extraer, extraer desde la URL (y decodificar)
    if not filename:
        from urllib.parse import unquote, urlparse
        path = urlparse(url).path
        filename = unquote(path.rsplit('/', 1)[-1]) or 'downloaded_file'

    # Si se pasó un nombre explícito, respetarlo; si no, usar el sugerido
    save_as = nombre_archivo if nombre_archivo else filename

    with open(save_as, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)

    print(f"Archivo guardado como: {save_as}")


def extraer_url_minio(response: Dict[str, Any], tipo: str) -> Optional[str]:
    """
    Extrae la URL de descarga alojada en MinIO para un tipo de comprobante.

    Args:
        response (Dict[str, Any]): JSON retornado por `consulta_mis_comprobantes`.
        tipo (str): `emitidos` o `recibidos`.

    Returns:
        Optional[str]: URL de descarga si está presente, de lo contrario `None`.
    """

    clave_directa = f"mis_comprobantes_{tipo}_url_minio"
    url = response.get(clave_directa)
    if url:
        return url

    nodo = response.get("descargas_minio", {}).get(tipo, [])
    if nodo:
        return nodo[0].get("url_descarga")

    return None


def main() -> None:
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

    mce_url = extraer_url_minio(response, "emitidos")
    mcr_url = extraer_url_minio(response, "recibidos")

    if mce_url:
        descargar_archivo(mce_url)
    else:
        print("Saltando descarga de emitidos porque no hay URL.")

    if mcr_url:
        descargar_archivo(mcr_url)
    else:
        print("Saltando descarga de recibidos porque no hay URL.")


if __name__ == "__main__":
    main()

load_dotenv()


MRBOT_USER = os.getenv("MRBOT_USER")
MRBOT_API_KEY = os.getenv("MRBOT_API_KEY")

BASE_URL = os.getenv("BASE_URL")

MIS_COMPROBANTES_ENDPOINT = os.getenv("MIS_COMPROBANTES_ENDPOINT")
RCEL_ENDPOINT = os.getenv("RCEL_ENDPOINT")

MC_DESDE_EJEMPLO = os.getenv("MC_DESDE_EJEMPLO")
MC_HASTA_EJEMPLO = os.getenv("MC_HASTA_EJEMPLO")
RCEL_DESDE_EJEMPLO = os.getenv("RCEL_DESDE_EJEMPLO")
RCEL_HASTA_EJEMPLO = os.getenv("RCEL_HASTA_EJEMPLO")
RCEL_DENOMINACION_EJEMPLO = os.getenv("RCEL_DENOMINACION_EJEMPLO")
DENOMIACION_EJEMPLO = os.getenv("DENOMIACION_EJEMPLO")
CUIT_REPRESENTANTE_EJEMPLO = os.getenv("CUIT_REPRESENTANTE_EJEMPLO")
CLAVE_REPRESENTANTE_EJEMPLO = os.getenv("CLAVE_REPRESENTANTE_EJEMPLO")
CUIT_REPRESENTADO_EJEMPLO = os.getenv("CUIT_REPRESENTADO_EJEMPLO")


response = consulta_mis_comprobantes(
    mrbot_user=MRBOT_USER,
    mrbot_api_key=MRBOT_API_KEY,
    base_url=BASE_URL,
    mis_comprobantes_endpoint=MIS_COMPROBANTES_ENDPOINT,
    desde=MC_DESDE_EJEMPLO,
    hasta=MC_HASTA_EJEMPLO,
    cuit_inicio_sesion=CUIT_REPRESENTADO_EJEMPLO,
    representado_nombre=DENOMIACION_EJEMPLO,
    representado_cuit=CUIT_REPRESENTANTE_EJEMPLO,
    contrasena=CLAVE_REPRESENTANTE_EJEMPLO,
    )

# Extraer URL de los comprimidos desde la respuesta (soporta ambos formatos)
ejemplo_minio_mce = None
ejemplo_minio_mcr = None

if isinstance(response, dict):
    # Preferir claves directas del ejemplo JSON
    ejemplo_minio_mce = response.get('mis_comprobantes_emitidos_url_minio') or None
    ejemplo_minio_mcr = response.get('mis_comprobantes_recibidos_url_minio') or None

    # Si no están, intentar el formato con 'descargas_minio' con listas
    if not ejemplo_minio_mce:
        try:
            ejemplo_minio_mce = response.get('descargas_minio', {}).get('emitidos', [])[0].get('url_descarga')
        except Exception:
            ejemplo_minio_mce = None
    if not ejemplo_minio_mcr:
        try:
            ejemplo_minio_mcr = response.get('descargas_minio', {}).get('recibidos', [])[0].get('url_descarga')
        except Exception:
            ejemplo_minio_mcr = None

if not ejemplo_minio_mce:
    print("No se encontró URL para emitidos en la respuesta")
if not ejemplo_minio_mcr:
    print("No se encontró URL para recibidos en la respuesta")


# Llamadas condicionales para descargar ejemplos
if ejemplo_minio_mce:
    descargar_archivo(ejemplo_minio_mce)
else:
    print("Saltando descarga de emitidos porque no hay URL.")

if ejemplo_minio_mcr:
    descargar_archivo(ejemplo_minio_mcr)
else:
    print("Saltando descarga de recibidos porque no hay URL.")
