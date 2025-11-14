import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List

import requests
from dotenv import load_dotenv

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.utils import descargar_archivo, descargar_archivos_concurrente, guardar_json


def consulta_rcel(
    mrbot_user: str,
    mrbot_api_key: str,
    base_url: str,
    rcel_endpoint: str,
    desde: str = "01/01/2024",
    hasta: str = "31/12/2024",
    cuit_inicio_sesion: str = "20123456780",
    representado_nombre: str = "Empresa Ejemplo S.A.",
    representado_cuit: str = "30876543210",
    contrasena: str = "mi_contraseña_secreta",
    b64_pdf: bool = False,
    minio_upload: bool = True,
) -> Dict[str, Any]:
    """
    Ejecuta la consulta de facturas emitidas por el representado desde la API de Mrbot para RCEL.

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
        b64_pdf (bool): solicitar el PDF en base64.
        minio_upload (bool): solicitar carga a MinIO.

    Returns:
        Dict[str, Any]: JSON retornado por la API con los datos de facturas.
    """

    url = f"{base_url.rstrip('/')}/{rcel_endpoint.lstrip('/')}/consulta"

    payload = json.dumps({
        "desde": desde,
        "hasta": hasta,
        "cuit_representante": cuit_inicio_sesion,
        "nombre_rcel": representado_nombre,
        "representado_cuit": representado_cuit,
        "clave": contrasena,
        "b64_pdf": b64_pdf,
        "minio_upload": minio_upload,
    })

    headers = {
        "x-api-key": mrbot_api_key,
        "email": mrbot_user,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    response = requests.post(url, headers=headers, data=payload)
    try:
        parsed = response.json()
    except ValueError:
        response.raise_for_status()
        raise

    print(response.text)
    return parsed


def validar_respuesta_rcel(response: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Asegura que la respuesta indica éxito y retorna el listado de facturas emitidas.

    Si la API devuelve éxito falso, levanta un RuntimeError con los mensajes de error recibidos.
    """

    if response.get("success"):
        return response.get("facturas_emitidas", [])

    detail = response.get("detail")

    mensajes: List[str] = []
    error_code = None

    if isinstance(detail, dict):
        posibles_claves_msg = ("message", "msg", "detail")
        for clave in posibles_claves_msg:
            val = detail.get(clave)
            if isinstance(val, str):
                mensajes.append(val)
            elif isinstance(val, list):
                mensajes.extend(str(v) for v in val)

        error_code = detail.get("error_code") or detail.get("type")

    elif isinstance(detail, list):
        for item in detail:
            if not isinstance(item, dict):
                continue
            msg = item.get("message") or item.get("msg") or item.get("detail")
            if msg:
                mensajes.append(str(msg))
            if not error_code:
                error_code = item.get("error_code") or item.get("type")

    elif isinstance(detail, str):
        mensajes.append(detail)

    if not mensajes:
        top_msg = response.get("message") or response.get("detail")
        if isinstance(top_msg, str):
            mensajes.append(top_msg)

    mensaje_base = " | ".join(mensajes) if mensajes else "Respuesta sin detalles."
    codigo = f" ({error_code})" if error_code else ""

    raise RuntimeError(f"Consulta RCEL fallida{codigo}: {mensaje_base}")


def iter_urls_facturas(facturas: Iterable[Dict[str, Any]]) -> Iterable[str]:
    """Devuelve las URLs que contienen `URL_MINIO` dentro de las facturas retornadas."""

    for factura in facturas:
        url = factura.get("URL_MINIO")
        if url:
            yield url


def main() -> None:
    load_dotenv()

    mrbot_user = os.getenv("MRBOT_USER")
    mrbot_api_key = os.getenv("MRBOT_API_KEY")
    base_url = os.getenv("BASE_URL")
    rcel_endpoint = os.getenv("RCEL_ENDPOINT")
    desde = os.getenv("RCEL_DESDE_EJEMPLO")
    hasta = os.getenv("RCEL_HASTA_EJEMPLO")
    cuit_inicio_sesion = os.getenv("CUIT_REPRESENTADO_EJEMPLO")
    representado_nombre = os.getenv("RCEL_DENOMINACION_EJEMPLO")
    representado_cuit = os.getenv("CUIT_REPRESENTANTE_EJEMPLO")
    contrasena = os.getenv("CLAVE_REPRESENTANTE_EJEMPLO")

    assert mrbot_user and mrbot_api_key and base_url and rcel_endpoint, "Faltan credenciales obligatorias"

    response = consulta_rcel(
        mrbot_user=mrbot_user,
        mrbot_api_key=mrbot_api_key,
        base_url=base_url,
        rcel_endpoint=rcel_endpoint,
        desde=desde,
        hasta=hasta,
        cuit_inicio_sesion=cuit_inicio_sesion,
        representado_nombre=representado_nombre,
        representado_cuit=representado_cuit,
        contrasena=contrasena,
    )

    try:
        facturas = validar_respuesta_rcel(response)
    except RuntimeError as exc:
        print(str(exc))
        return

    if not facturas:
        print("La consulta RCEL no devolvió facturas.")
        return

    directorio_objetivo = f"descargas_rcel/{representado_cuit}"

    descargas = []
    facturas_con_metadata = {}
    
    for factura in facturas:
        url_pdf = factura.get("URL_MINIO")
        if url_pdf:
            descargas.append((url_pdf, None, directorio_objetivo))
            facturas_con_metadata[url_pdf] = factura
        else:
            print(f"Factura sin URL_MINIO: {factura.get('NUMERO_FACTURA', 'N/A')}")
    
    if descargas:
        rutas_descargadas = descargar_archivos_concurrente(descargas)
        
        for ruta in rutas_descargadas:
            for url, metadata in facturas_con_metadata.items():
                if url in ruta or os.path.basename(ruta) in url:
                    guardar_json(metadata, ruta)
                    break


if __name__ == "__main__":
    main()
